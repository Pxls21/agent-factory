"""S0-12: SBOM pin-diff conformance checker.

Asserts:
  1. LICENSE-DECISION.md, THIRD-PARTY-NOTICES.md, and SBOM.yaml all exist.
  2. Every commit pin in SBOM.yaml matches upstream.lock.yaml exactly.
  3. The SBOM documents an update procedure.

Exit 0 + "PASS" on success; exit 1 + reason on failure.
"""
import sys
from pathlib import Path

import yaml


def main():
    if len(sys.argv) != 2:
        print("usage: check_pin_diff.py <repo-root>")
        return 1

    root = Path(sys.argv[1]).resolve()

    for name in ("LICENSE-DECISION.md", "THIRD-PARTY-NOTICES.md", "SBOM.yaml"):
        if not (root / name).exists():
            print(f"sbom-missing-file: {name} does not exist")
            return 1

    sbom_text = (root / "SBOM.yaml").read_text()
    if "update procedure" not in sbom_text.lower():
        print("sbom-missing-update-procedure: no update procedure documented in SBOM.yaml")
        return 1

    sbom = yaml.safe_load(sbom_text)
    lock = yaml.safe_load((root / "upstream.lock.yaml").read_text())

    lock_pins = {}
    for section in ("selected_core", "selected_later_planes",
                     "development_and_reference", "not_selected_as_stock_runtimes"):
        entries = lock.get(section, {})
        if not entries:
            continue
        for name, info in entries.items():
            commit = info.get("commit")
            if commit is not None:
                lock_pins[name] = str(commit)

    sbom_pins = {}
    for comp in sbom.get("components", []):
        name = comp.get("name")
        commit = comp.get("commit")
        if name and commit is not None:
            sbom_pins[name] = str(commit)

    if not sbom_pins:
        print("sbom-empty: SBOM.yaml has no component pins")
        return 1

    for name, sbom_commit in sorted(sbom_pins.items()):
        lock_commit = lock_pins.get(name)
        if lock_commit is None:
            print(f"sbom-pin-drift: {name} is in SBOM but not in upstream.lock.yaml")
            return 1
        if sbom_commit != lock_commit:
            print(f"sbom-pin-drift: pin differs from upstream.lock.yaml for {name}")
            return 1

    for name in sorted(lock_pins):
        if name not in sbom_pins:
            print(f"sbom-pin-drift: {name} is in upstream.lock.yaml but missing from SBOM")
            return 1

    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
