# Aave Sentinel

Monitor Aave v3 positions across all major chains. Check health factors, collateral, debt, and get liquidation warnings.

## Usage

When the user asks to check their Aave position, health factor, or monitor their lending positions, use this skill.

### Commands

- **Check position**: "check my aave position for 0x..."
- **Health factor**: "what's my health factor on aave?"
- **Multi-chain scan**: "scan all chains for aave positions"

## How to Check Positions

Use the `aave_check.py` script included in this repo, or make direct RPC calls.

### Direct RPC Method

Call `getUserAccountData(address)` on the Aave v3 Pool contract. Function selector: `0xbf92857c`.

**Calldata format:**
```
0xbf92857c + 000000000000000000000000 + <address without 0x prefix>
```

**Example curl:**
```bash
curl -s -X POST <RPC_URL> \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_call","params":[{"to":"<POOL_ADDRESS>","data":"0xbf92857c000000000000000000000000<ADDRESS>"},"latest"],"id":1}'
```

### Aave v3 Pool Addresses by Chain

| Chain | Pool Address | RPC |
|-------|-------------|-----|
| Ethereum | `0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2` | `https://ethereum-rpc.publicnode.com` |
| Polygon | `0x794a61358D6845594F94dc1DB02A252b5b4814aD` | `https://polygon.drpc.org` |
| Arbitrum | `0x794a61358D6845594F94dc1DB02A252b5b4814aD` | `https://arb1.arbitrum.io/rpc` |
| Optimism | `0x794a61358D6845594F94dc1DB02A252b5b4814aD` | `https://mainnet.optimism.io` |
| Base | `0xA238Dd80C259a72e81d7e4664a9801593F98d1c5` | `https://base-rpc.publicnode.com` |
| Avalanche | `0x794a61358D6845594F94dc1DB02A252b5b4814aD` | `https://api.avax.network/ext/bc/C/rpc` |
| Gnosis | `0xb50201558B00496A145fE76f7424749556E326D8` | `https://rpc.gnosischain.com` |
| BNB Chain | `0x6807dc923806fE8Fd134338EABCA509979a7e0cB` | `https://bsc-rpc.publicnode.com` |
| Scroll | `0x11fCfe756c05AD438e312a7fd934381537D3cFfe` | `https://rpc.scroll.io` |

### Decoding the Response

`getUserAccountData` returns 6 values, each 32 bytes (64 hex chars):

| Offset | Field | Unit |
|--------|-------|------|
| 0-64 | totalCollateralBase | USD with 8 decimals (divide by 1e8) |
| 64-128 | totalDebtBase | USD with 8 decimals |
| 128-192 | availableBorrowsBase | USD with 8 decimals |
| 192-256 | currentLiquidationThreshold | basis points (divide by 100 for %) |
| 256-320 | ltv | basis points |
| 320-384 | healthFactor | 18 decimals (divide by 1e18) |

### Health Factor Interpretation

| Health Factor | Status | Action |
|--------------|--------|--------|
| > 2.0 | Safe | No action needed |
| 1.5 - 2.0 | Healthy | Monitor regularly |
| 1.1 - 1.5 | Moderate risk | Consider adding collateral or repaying debt |
| 1.0 - 1.1 | Danger | Immediate action required |
| < 1.0 | Liquidatable | Position can be liquidated |

### Fallback RPCs

Some public RPCs rate-limit or block requests. If one fails, try alternatives:
- **Ethereum**: `https://eth.drpc.org`, `https://rpc.ankr.com/eth`
- **Polygon**: `https://polygon.drpc.org`, `https://polygon-rpc.com`
- **Arbitrum**: `https://arb1.arbitrum.io/rpc`, `https://arbitrum.drpc.org`
- **Base**: `https://base.drpc.org`, `https://mainnet.base.org`

## Output Format

When reporting positions, use this format:

```
=== <CHAIN> — Aave v3 ===
  Collateral:    $XX,XXX.XX
  Debt:          $XX,XXX.XX
  Available:     $XX,XXX.XX
  LTV:           XX.X%
  Liq Threshold: XX.X%
  Health Factor: X.XXXX
```

If no position found on a chain, just skip it — don't list empty chains.

Always flag positions with health factor below 1.5.
