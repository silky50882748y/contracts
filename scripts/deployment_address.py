#!/usr/bin/env python3
"""Print the deployed contract ID for a contract on a network.

Reads deployments/<network>.json (written by scripts/deploy_all.sh), which is
the single source of truth for deployed contract IDs.

Usage: scripts/deployment_address.py <contract> [--network testnet]
Exits non-zero if the contract is not deployed on the network.
"""
import argparse
import json
import sys
from pathlib import Path

DEPLOYMENTS_DIR = Path(__file__).resolve().parent.parent / "deployments"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("contract", help="contract name, e.g. watcher-registry")
    parser.add_argument("--network", default="testnet")
    args = parser.parse_args()

    manifest = DEPLOYMENTS_DIR / f"{args.network}.json"
    try:
        data = json.loads(manifest.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: cannot read {manifest}: {exc}", file=sys.stderr)
        return 1

    contract_id = data.get("contracts", {}).get(args.contract, {}).get("contract_id")
    if not contract_id:
        print(f"error: {args.contract} is not deployed on {args.network}", file=sys.stderr)
        return 1

    print(contract_id)
    return 0


if __name__ == "__main__":
    sys.exit(main())
