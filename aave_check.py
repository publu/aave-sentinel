#!/usr/bin/env python3
"""
aave-sentinel: Check Aave v3 positions across all major chains.

Usage:
    python3 aave_check.py <address>
    python3 aave_check.py 0xYourAddress

Reports collateral, debt, health factor, and liquidation risk
for every chain where a position is found.
"""
import json
import sys
import urllib.request

CHAINS = {
    'Ethereum': {
        'rpcs': ['https://ethereum-rpc.publicnode.com', 'https://eth.drpc.org'],
        'pool': '0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2',
    },
    'Polygon': {
        'rpcs': ['https://polygon.drpc.org', 'https://polygon-bor-rpc.publicnode.com'],
        'pool': '0x794a61358D6845594F94dc1DB02A252b5b4814aD',
    },
    'Arbitrum': {
        'rpcs': ['https://arb1.arbitrum.io/rpc', 'https://arbitrum.drpc.org'],
        'pool': '0x794a61358D6845594F94dc1DB02A252b5b4814aD',
    },
    'Optimism': {
        'rpcs': ['https://mainnet.optimism.io', 'https://optimism.drpc.org'],
        'pool': '0x794a61358D6845594F94dc1DB02A252b5b4814aD',
    },
    'Base': {
        'rpcs': ['https://mainnet.base.org', 'https://base.drpc.org'],
        'pool': '0xA238Dd80C259a72e81d7e4664a9801593F98d1c5',
    },
    'Avalanche': {
        'rpcs': ['https://api.avax.network/ext/bc/C/rpc'],
        'pool': '0x794a61358D6845594F94dc1DB02A252b5b4814aD',
    },
    'Gnosis': {
        'rpcs': ['https://rpc.gnosischain.com'],
        'pool': '0xb50201558B00496A145fE76f7424749556E326D8',
    },
    'BNB Chain': {
        'rpcs': ['https://bsc-rpc.publicnode.com', 'https://bsc.drpc.org'],
        'pool': '0x6807dc923806fE8Fd134338EABCA509979a7e0cB',
    },
    'Scroll': {
        'rpcs': ['https://rpc.scroll.io'],
        'pool': '0x11fCfe756c05AD438e312a7fd934381537D3cFfe',
    },
}

# getUserAccountData(address) selector
SELECTOR = '0xbf92857c'


def build_calldata(address: str) -> str:
    addr = address.lower().replace('0x', '')
    return SELECTOR + '000000000000000000000000' + addr


def eth_call(rpc: str, pool: str, calldata: str) -> str | None:
    payload = json.dumps({
        'jsonrpc': '2.0',
        'method': 'eth_call',
        'params': [{'to': pool, 'data': calldata}, 'latest'],
        'id': 1,
    }).encode()
    req = urllib.request.Request(rpc, data=payload, headers={'Content-Type': 'application/json'})
    resp = json.loads(urllib.request.urlopen(req, timeout=10).read())
    result = resp.get('result', '0x')
    if result and result != '0x' and len(result) > 10:
        return result[2:]  # strip 0x
    return None


def decode_account_data(data: str) -> dict | None:
    if len(data) < 384:
        return None
    collateral = int(data[0:64], 16)
    debt = int(data[64:128], 16)
    available = int(data[128:192], 16)
    liq_threshold = int(data[192:256], 16)
    ltv = int(data[256:320], 16)
    health_factor_raw = int(data[320:384], 16)

    if collateral == 0 and debt == 0:
        return None

    return {
        'collateral_usd': collateral / 1e8,
        'debt_usd': debt / 1e8,
        'available_usd': available / 1e8,
        'ltv_pct': ltv / 100,
        'liq_threshold_pct': liq_threshold / 100,
        'health_factor': health_factor_raw / 1e18 if debt > 0 else float('inf'),
        'has_debt': debt > 0,
    }


def risk_label(hf: float) -> str:
    if hf == float('inf'):
        return 'No debt'
    if hf > 2.0:
        return 'Safe'
    if hf > 1.5:
        return 'Healthy'
    if hf > 1.1:
        return 'Moderate risk'
    if hf > 1.0:
        return 'DANGER'
    return 'LIQUIDATABLE'


def check_address(address: str):
    calldata = build_calldata(address)
    found_any = False

    for chain_name, cfg in CHAINS.items():
        result = None
        for rpc in cfg['rpcs']:
            try:
                result = eth_call(rpc, cfg['pool'], calldata)
                if result:
                    break
            except Exception:
                continue

        if not result:
            continue

        position = decode_account_data(result)
        if not position:
            continue

        found_any = True
        hf = position['health_factor']
        risk = risk_label(hf)

        print(f'=== {chain_name} — Aave v3 ===')
        print(f'  Collateral:    ${position["collateral_usd"]:,.2f}')
        print(f'  Debt:          ${position["debt_usd"]:,.2f}')
        print(f'  Available:     ${position["available_usd"]:,.2f}')
        print(f'  LTV:           {position["ltv_pct"]:.1f}%')
        print(f'  Liq Threshold: {position["liq_threshold_pct"]:.1f}%')
        if position['has_debt']:
            print(f'  Health Factor: {hf:.4f}  [{risk}]')
        else:
            print(f'  Health Factor: inf  [No debt]')
        print()

    if not found_any:
        print(f'No Aave v3 positions found for {address}')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python3 aave_check.py <address>')
        print('Example: python3 aave_check.py 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045')
        sys.exit(1)

    address = sys.argv[1]
    if not address.startswith('0x') or len(address) != 42:
        print('Error: Invalid Ethereum address')
        sys.exit(1)

    print(f'Scanning Aave v3 positions for {address}...\n')
    check_address(address)
