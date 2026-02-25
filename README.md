# aave-sentinel

Monitor Aave v3 positions across all major EVM chains. Check health factors, collateral, debt, and get liquidation warnings.

## Install as Agent Skill

```bash
curl -sL https://raw.githubusercontent.com/publu/aave-sentinel/master/aave-sentinel.md >> ~/.claude/skills/aave-sentinel.md
```

Then just ask: _"check my aave position for 0x..."_

## Standalone Usage

```bash
python3 aave_check.py 0xYourAddressHere
```

No dependencies — uses only Python standard library.

## Supported Chains

Ethereum, Polygon, Arbitrum, Optimism, Base, Avalanche, Gnosis, BNB Chain, Scroll

## What it does

- Calls `getUserAccountData` on Aave v3 Pool contracts via public RPCs
- Decodes collateral, debt, available borrows, LTV, liquidation threshold, health factor
- Tries multiple RPC endpoints per chain for reliability
- Only reports chains where you have an active position

## Output

```
=== Arbitrum — Aave v3 ===
  Collateral:    $25,435.34
  Debt:          $17,610.95
  Available:     $1,773.32
  LTV:           76.2%
  Liq Threshold: 80.8%
  Health Factor: 1.1664  [Moderate risk]
```

## Health Factor Guide

| Range | Status | What to do |
|-------|--------|------------|
| > 2.0 | Safe | Chill |
| 1.5 - 2.0 | Healthy | Monitor |
| 1.1 - 1.5 | Moderate risk | Consider adding collateral |
| 1.0 - 1.1 | Danger | Act now |
| < 1.0 | Liquidatable | You're getting rekt |

## License

MIT
