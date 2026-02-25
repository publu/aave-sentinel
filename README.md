# Aave Sentinel

Monitor [Aave v3](https://aave.com) positions across 9 EVM chains. Health factors, collateral, debt, liquidation warnings — with rich terminal UI.

Agent skill for [cryptoskills.sh](https://cryptoskills.sh/skill/aave-sentinel).

## Install

```bash
curl -sL https://raw.githubusercontent.com/publu/aave-sentinel/master/aave_check.py -o /tmp/aave_check.py
```

## Commands

```
check <address>       Scan all chains for Aave v3 positions
chains                List supported chains with pool addresses
ghost                 Show the Aave ghost
```

Shorthand: `aave_check.py 0xYourAddress` (same as `check`)

## Examples

```bash
# Full multichain position scan
python3 /tmp/aave_check.py 0xYourAddressHere

# List supported chains
python3 /tmp/aave_check.py chains

# Show the ghost
python3 /tmp/aave_check.py ghost
```

## Screenshot

```
  $ aave-sentinel
  ✓ Connected to Aave v3

  ██████╗  ██████╗ ██╗   ██╗███████╗
  ██╔══██╗██╔══██╗██║   ██║██╔════╝
  ███████║███████║██║   ██║█████╗
  ██╔══██║██╔══██║╚██╗ ██╔╝██╔══╝
  ██║  ██║██║  ██║ ╚████╔╝ ███████╗
  ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚══════╝
            Multichain Position Monitor

    ╔══════════╗
    ║  ◉    ◉  ║
    ║    ──    ║
    ║  AAVE    ║
    ╚╦══╦══╦══╝
     ╚══╩══╝

  aave> check 0xABCD...EF01

  ┌── Arbitrum (ID: 42161) ──────────────────────────────┐
  │                                                      │
  │ Collateral:       $25,435.34                         │
  │ Debt:             $17,610.95                         │
  │ Available:        $1,773.32                          │
  │ LTV:              76.2%                              │
  │ Liq Threshold:    80.8%                              │
  │                                                      │
  ├──────────────────────────────────────────────────────┤
  │                                                      │
  │ Health Factor:    1.1664                             │
  │ ████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │
  │ ▓▓▓▓▓▓░░░░ Moderate                                 │
  │                                                      │
  │ △ Consider adding collateral                         │
  │                                                      │
  └──────────────────────────────────────────────────────┘
```

## Supported Chains

| Chain | ID | Pool |
|-------|----|------|
| Ethereum | 1 | `0x8787...A4E2` |
| Polygon | 137 | `0x794a...14aD` |
| Arbitrum | 42161 | `0x794a...14aD` |
| Optimism | 10 | `0x794a...14aD` |
| Base | 8453 | `0xA238...d1c5` |
| Avalanche | 43114 | `0x794a...14aD` |
| Gnosis | 100 | `0xb502...26D8` |
| BNB Chain | 56 | `0x6807...e0cB` |
| Scroll | 534352 | `0x11fC...cFfe` |

## Health Factor Guide

| Range | Status | Bar | Action |
|-------|--------|-----|--------|
| > 2.0 | Safe | `▓▓░░░░░░░░` | Chill |
| 1.5 - 2.0 | Healthy | `▓▓▓▓░░░░░░` | Monitor |
| 1.1 - 1.5 | Moderate | `▓▓▓▓▓▓░░░░` | Add collateral |
| 1.0 - 1.1 | DANGER | `▓▓▓▓▓▓▓▓░░` | Act now |
| < 1.0 | LIQUIDATABLE | `▓▓▓▓▓▓▓▓▓▓` | You're getting rekt |

## How It Works

- Calls `getUserAccountData` on Aave v3 Pool contracts via public RPCs
- Decodes collateral, debt, available borrows, LTV, liquidation threshold, health factor
- Multiple RPC fallbacks per chain for reliability
- Only reports chains where you have an active position
- Positions with debt sorted by health factor (riskiest first)

## Requirements

Python 3.6+ — no external dependencies.

## License

MIT
