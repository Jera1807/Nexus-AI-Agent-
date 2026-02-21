from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.tenant.onboarding import scaffold_tenant


def main() -> int:
    parser = argparse.ArgumentParser(description="Create tenant config scaffold")
    parser.add_argument("--tenant-id", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--language", default="de")
    parser.add_argument("--timezone", default="Europe/Berlin")
    parser.add_argument("--config-root", default="configs/tenants")
    args = parser.parse_args()

    tenant_root = Path(args.config_root) / args.tenant_id
    written = scaffold_tenant(
        tenant_root=tenant_root,
        tenant_id=args.tenant_id,
        business_name=args.name,
        language=args.language,
        timezone=args.timezone,
    )

    print(f"Tenant scaffold ready: {tenant_root}")
    if written:
        print("Created files:")
        for f in written:
            print(f"- {f}")
    else:
        print("No new files created (tenant already exists).")

    print("Next steps: intents/tools/channels anpassen, KB füllen, Tests laufen lassen.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
