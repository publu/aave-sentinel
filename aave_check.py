#!/usr/bin/env python3
"""Aave Sentinel — multichain position monitor with rich terminal UI."""

import json
import sys
import urllib.request

# ── Aave v3 Pool Contracts ────────────────────────────────
CHAINS = {
    'Ethereum': {
        'rpcs': ['https://ethereum-rpc.publicnode.com', 'https://eth.drpc.org'],
        'pool': '0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2',
        'chain_id': 1,
    },
    'Polygon': {
        'rpcs': ['https://polygon.drpc.org', 'https://polygon-bor-rpc.publicnode.com'],
        'pool': '0x794a61358D6845594F94dc1DB02A252b5b4814aD',
        'chain_id': 137,
    },
    'Arbitrum': {
        'rpcs': ['https://arb1.arbitrum.io/rpc', 'https://arbitrum.drpc.org'],
        'pool': '0x794a61358D6845594F94dc1DB02A252b5b4814aD',
        'chain_id': 42161,
    },
    'Optimism': {
        'rpcs': ['https://mainnet.optimism.io', 'https://optimism.drpc.org'],
        'pool': '0x794a61358D6845594F94dc1DB02A252b5b4814aD',
        'chain_id': 10,
    },
    'Base': {
        'rpcs': ['https://mainnet.base.org', 'https://base.drpc.org'],
        'pool': '0xA238Dd80C259a72e81d7e4664a9801593F98d1c5',
        'chain_id': 8453,
    },
    'Avalanche': {
        'rpcs': ['https://api.avax.network/ext/bc/C/rpc'],
        'pool': '0x794a61358D6845594F94dc1DB02A252b5b4814aD',
        'chain_id': 43114,
    },
    'Gnosis': {
        'rpcs': ['https://rpc.gnosischain.com'],
        'pool': '0xb50201558B00496A145fE76f7424749556E326D8',
        'chain_id': 100,
    },
    'BNB Chain': {
        'rpcs': ['https://bsc-rpc.publicnode.com', 'https://bsc.drpc.org'],
        'pool': '0x6807dc923806fE8Fd134338EABCA509979a7e0cB',
        'chain_id': 56,
    },
    'Scroll': {
        'rpcs': ['https://rpc.scroll.io'],
        'pool': '0x11fCfe756c05AD438e312a7fd934381537D3cFfe',
        'chain_id': 534352,
    },
}

# getUserAccountData(address) selector
SELECTOR = '0xbf92857c'

# ── ANSI Colors ───────────────────────────────────────────
CYAN = "\033[38;2;0;200;255m"
DIM_CYAN = "\033[38;2;0;120;160m"
RED = "\033[38;2;255;60;60m"
ORANGE = "\033[38;2;255;165;0m"
YELLOW = "\033[38;2;255;255;0m"
GREEN = "\033[38;2;0;255;65m"
WHITE = "\033[97m"
DIM = "\033[2m"
BOLD = "\033[1m"
RESET = "\033[0m"
MAGENTA = "\033[38;2;200;100;255m"

def c(s): return f"{CYAN}{s}{RESET}"
def dc(s): return f"{DIM_CYAN}{s}{RESET}"
def r(s): return f"{RED}{s}{RESET}"
def o(s): return f"{ORANGE}{s}{RESET}"
def y(s): return f"{YELLOW}{s}{RESET}"
def g(s): return f"{GREEN}{s}{RESET}"
def w(s): return f"{WHITE}{BOLD}{s}{RESET}"
def dim(s): return f"{DIM}{s}{RESET}"
def m(s): return f"{MAGENTA}{s}{RESET}"

# ── Box Drawing ───────────────────────────────────────────
BOX_TL = "┌"
BOX_TR = "┐"
BOX_BL = "└"
BOX_BR = "┘"
BOX_H  = "─"
BOX_V  = "│"
BOX_LT = "├"
BOX_RT = "┤"

def box_top(width, title=""):
    if title:
        inner = f" {title} "
        line = BOX_H * 2 + inner + BOX_H * (width - 4 - len(title))
    else:
        line = BOX_H * (width - 2)
    return dc(f"  {BOX_TL}{line}{BOX_TR}")

def box_mid(width):
    return dc(f"  {BOX_LT}{BOX_H * (width - 2)}{BOX_RT}")

def box_bottom(width):
    return dc(f"  {BOX_BL}{BOX_H * (width - 2)}{BOX_BR}")

def box_empty(width):
    return f"  {dc(BOX_V)}{' ' * (width - 2)}{dc(BOX_V)}"

def box_text(text, width, color_fn=c):
    pad = width - 4 - len(text)
    return f"  {dc(BOX_V)} {color_fn(text)}{' ' * max(pad, 0)} {dc(BOX_V)}"

def box_kv(label, value, width, val_color=c):
    col1 = 18
    l = f"{label}:"
    l_padded = l.ljust(col1)
    val_str = str(value)
    remaining = width - 4 - col1 - len(val_str)
    return f"  {dc(BOX_V)} {dc(l_padded)}{val_color(val_str)}{' ' * max(remaining, 0)} {dc(BOX_V)}"

# ── ASCII Art ─────────────────────────────────────────────
LOGO = r"""
  ██████╗  ██████╗ ██╗   ██╗███████╗
 ██╔══██╗██╔══██╗██║   ██║██╔════╝
 ███████║███████║██║   ██║█████╗
 ██╔══██║██╔══██║╚██╗ ██╔╝██╔══╝
 ██║  ██║██║  ██║ ╚████╔╝ ███████╗
 ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚══════╝"""

GHOST = r"""
    ╔══════════╗
    ║  ◉    ◉  ║
    ║    ──    ║
    ║  AAVE    ║
    ╚╦══╦══╦══╝
     ╚══╩══╝"""

def print_header(cmd_text=""):
    print()
    print(f"  {c('$')} {w('aave-sentinel')}")
    print(f"  {c('✓')} {dc('Connected to Aave v3')}")
    for line in LOGO.strip().split("\n"):
        print(f"  {CYAN}{line}{RESET}")
    print(f"  {DIM_CYAN}{'Multichain Position Monitor':>38}{RESET}")
    if cmd_text:
        print()
        print(f"  {dc('aave>')} {w(cmd_text)}")
    print()


# ── RPC Helpers ───────────────────────────────────────────
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
    req = urllib.request.Request(rpc, data=payload, headers={
        'Content-Type': 'application/json',
        'User-Agent': 'aave-sentinel/1.0',
    })
    resp = json.loads(urllib.request.urlopen(req, timeout=10).read())
    result = resp.get('result', '0x')
    if result and result != '0x' and len(result) > 10:
        return result[2:]
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


def fmt_usd(val):
    if val >= 1_000_000_000:
        return f"${val / 1_000_000_000:,.2f}B"
    elif val >= 1_000_000:
        return f"${val / 1_000_000:,.2f}M"
    elif val >= 1_000:
        return f"${val:,.0f}"
    elif val >= 0.01:
        return f"${val:,.2f}"
    else:
        return "$0.00"


# ── Health Factor Visuals ─────────────────────────────────
def risk_label(hf: float) -> tuple:
    """Returns (label, color_fn, bar)."""
    if hf == float('inf'):
        return 'No debt', c, '░░░░░░░░░░'
    if hf > 2.0:
        filled = 2
        return 'Safe', g, '▓▓░░░░░░░░'
    if hf > 1.5:
        filled = 4
        return 'Healthy', g, '▓▓▓▓░░░░░░'
    if hf > 1.1:
        filled = 6
        return 'Moderate', o, '▓▓▓▓▓▓░░░░'
    if hf > 1.0:
        filled = 8
        return 'DANGER', r, '▓▓▓▓▓▓▓▓░░'
    return 'LIQUIDATABLE', r, '▓▓▓▓▓▓▓▓▓▓'


def health_bar(hf: float, width=20) -> str:
    """Visual health bar — green at high HF, red at low."""
    if hf == float('inf'):
        return f"{DIM_CYAN}{'─' * width}{RESET}"

    # Clamp to 0-3 range for display
    ratio = min(max(hf - 1.0, 0) / 2.0, 1.0)
    filled = int(ratio * width)
    empty = width - filled

    if hf > 1.5:
        color = GREEN
    elif hf > 1.1:
        color = ORANGE
    else:
        color = RED

    return f"{color}{'█' * filled}{DIM}{'░' * empty}{RESET}"


# ── Commands ──────────────────────────────────────────────

def cmd_check(args):
    """Scan all chains for Aave v3 positions."""
    if not args:
        print(f"  {o('Usage:')} aave_check.py check <address>")
        print(f"  {dim('Example: aave_check.py check 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045')}")
        return

    address = args[0]
    if not address.startswith('0x') or len(address) != 42:
        print(f"  {r('✗')} Invalid Ethereum address")
        return

    short_addr = f"{address[:6]}...{address[-4:]}"
    print_header(f"check {short_addr}")

    print(f"  {c('⟳')} {dc('Scanning 9 chains...')}")
    print()

    calldata = build_calldata(address)
    positions = []

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

        position['chain'] = chain_name
        position['chain_id'] = cfg['chain_id']
        positions.append(position)

    if not positions:
        W = 52
        print(box_top(W, "Scan Complete"))
        print(box_empty(W))
        print(box_text("No Aave v3 positions found", W, color_fn=o))
        print(box_empty(W))
        print(box_bottom(W))
        print()
        print(f"  {dim(address)}")
        print()
        return

    # Sort: positions with debt first (by health factor ascending), then no-debt by collateral
    with_debt = sorted([p for p in positions if p['has_debt']], key=lambda x: x['health_factor'])
    no_debt = sorted([p for p in positions if not p['has_debt']], key=lambda x: x['collateral_usd'], reverse=True)
    positions = with_debt + no_debt

    total_collateral = sum(p['collateral_usd'] for p in positions)
    total_debt = sum(p['debt_usd'] for p in positions)

    # Print each position
    W = 56

    for pos in positions:
        hf = pos['health_factor']
        label, color_fn, risk_bar = risk_label(hf)

        print(box_top(W, f"{pos['chain']} (ID: {pos['chain_id']})"))
        print(box_empty(W))
        print(box_kv("Collateral", fmt_usd(pos['collateral_usd']), W, val_color=w))
        print(box_kv("Debt", fmt_usd(pos['debt_usd']), W,
                      val_color=r if pos['has_debt'] else dc))
        print(box_kv("Available", fmt_usd(pos['available_usd']), W, val_color=c))
        print(box_kv("LTV", f"{pos['ltv_pct']:.1f}%", W))
        print(box_kv("Liq Threshold", f"{pos['liq_threshold_pct']:.1f}%", W))
        print(box_empty(W))

        if pos['has_debt']:
            print(box_mid(W))
            print(box_empty(W))

            # Health factor with visual bar
            hf_str = f"{hf:.4f}"
            hf_label = f"Health Factor:"
            pad = W - 4 - len(hf_label) - len(hf_str) - 1
            print(f"  {dc(BOX_V)} {dc(hf_label)} {color_fn(hf_str)}{' ' * max(pad, 0)} {dc(BOX_V)}")

            # Health bar
            bar = health_bar(hf, width=W - 6)
            print(f"  {dc(BOX_V)} {bar}  {dc(BOX_V)}")

            # Risk label
            risk_display = f"{risk_bar} {label}"
            risk_pad = W - 4 - len(risk_display)
            print(f"  {dc(BOX_V)} {color_fn(risk_display)}{' ' * max(risk_pad, 0)} {dc(BOX_V)}")

            print(box_empty(W))

            # Liquidation warning
            if hf < 1.1:
                warn = "⚠ LIQUIDATION IMMINENT" if hf < 1.0 else "⚠ CRITICAL — ACT NOW"
                warn_pad = W - 4 - len(warn)
                print(f"  {dc(BOX_V)} {r(warn)}{' ' * max(warn_pad, 0)} {dc(BOX_V)}")
                print(box_empty(W))
            elif hf < 1.5:
                warn = "△ Consider adding collateral"
                warn_pad = W - 4 - len(warn)
                print(f"  {dc(BOX_V)} {o(warn)}{' ' * max(warn_pad, 0)} {dc(BOX_V)}")
                print(box_empty(W))
        else:
            print(box_mid(W))
            print(box_empty(W))
            hf_label = "Health Factor:"
            hf_str = "∞  No debt"
            pad = W - 4 - len(hf_label) - len(hf_str) - 1
            print(f"  {dc(BOX_V)} {dc(hf_label)} {c(hf_str)}{' ' * max(pad, 0)} {dc(BOX_V)}")
            print(box_empty(W))

        print(box_bottom(W))
        print()

    # Summary
    if len(positions) > 1:
        print(box_top(W, "Summary"))
        print(box_empty(W))
        print(box_kv("Positions", str(len(positions)), W))
        print(box_kv("Total Collateral", fmt_usd(total_collateral), W, val_color=w))
        print(box_kv("Total Debt", fmt_usd(total_debt), W,
                      val_color=r if total_debt > 0 else dc))
        if total_collateral > 0:
            net = total_collateral - total_debt
            print(box_kv("Net Value", fmt_usd(net), W,
                          val_color=g if net > 0 else r))
        print(box_empty(W))
        print(box_bottom(W))
        print()

    print(f"  {dim(address)}")
    print()


def cmd_chains(args):
    """List supported chains with pool addresses."""
    print_header("chains")

    print(f"  {c('✓')} {w(str(len(CHAINS)))} {dc('chains supported')}")
    print()

    W = 62

    print(box_top(W, "Aave v3 Pools"))
    print(box_empty(W))

    for name, cfg in CHAINS.items():
        chain_id = cfg['chain_id']
        pool = cfg['pool']
        short_pool = f"{pool[:6]}...{pool[-4:]}"
        label = f"{name} ({chain_id})"
        if len(label) > 22:
            label = label[:22]
        val = short_pool
        pad = W - 4 - len(label) - len(val) - 1
        print(f"  {dc(BOX_V)} {c(label)}{' ' * max(pad, 1)}{dc(val)} {dc(BOX_V)}")

    print(box_empty(W))
    print(box_bottom(W))
    print()
    print(f"  {dim('Pool addresses: Aave v3 getUserAccountData')}")
    print(f"  {dim('Multiple RPC fallbacks per chain for reliability')}")
    print()


def cmd_ghost(args):
    """Show the Aave ghost."""
    print()
    for line in GHOST.strip().split("\n"):
        print(f"  {CYAN}{line}{RESET}")
    print()


# ── CLI Entry ─────────────────────────────────────────────

COMMANDS = {
    "check": (cmd_check, "Scan positions <address>"),
    "chains": (cmd_chains, "List supported chains"),
    "ghost": (cmd_ghost, "Show the Aave ghost"),
}


def main():
    # Allow bare address as shorthand: aave_check.py 0x...
    if len(sys.argv) == 2 and sys.argv[1].startswith('0x') and len(sys.argv[1]) == 42:
        cmd_check([sys.argv[1]])
        return

    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print_header()
        for line in GHOST.strip().split("\n"):
            print(f"  {CYAN}{line}{RESET}")
        print()
        print(f"  {w('Usage:')} aave_check.py <command> [args]")
        print()
        for name, (_, desc) in COMMANDS.items():
            print(f"    {c(name):<28} {dc(desc)}")
        print()
        print(f"  {dc('Shorthand:')} aave_check.py 0xAddress")
        print()
        sys.exit(1)

    cmd = sys.argv[1]
    fn, _ = COMMANDS[cmd]
    fn(sys.argv[2:])


if __name__ == "__main__":
    main()
