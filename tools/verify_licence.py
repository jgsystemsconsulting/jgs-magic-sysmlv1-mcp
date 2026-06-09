#!/usr/bin/env python3
# Copyright (c) 2026 JG Systems Consulting Ltd. All Rights Reserved.
"""Verify a jgs-sysmlv2 licence file against an Ed25519 public key."""
import argparse
import base64
import sys
from datetime import date
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.exceptions import InvalidSignature


def load_public_key(pub_path: Path) -> Ed25519PublicKey:
    raw = base64.b64decode(pub_path.read_text().strip())
    return Ed25519PublicKey.from_public_bytes(raw)


def verify(pub_path: Path, lic_path: Path) -> dict:
    """Verify licence file. Returns dict with tier, customer, expiry, valid, reason."""
    content = lic_path.read_text()
    lines = content.strip().split("\n")

    sig_line = [l for l in lines if l.startswith("signature=")]
    if not sig_line:
        return {"valid": False, "reason": "No signature found"}

    sig_b64 = sig_line[0].split("=", 1)[1]
    signature = base64.b64decode(sig_b64)

    # Payload is everything before the signature line
    sig_idx = content.index("signature=")
    payload = content[:sig_idx]

    public_key = load_public_key(pub_path)
    try:
        public_key.verify(signature, payload.encode("utf-8"))
    except InvalidSignature:
        return {"valid": False, "reason": "Signature verification failed"}

    # Parse fields
    fields = {}
    for line in lines:
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            fields[k.strip()] = v.strip()

    # Check expiry
    expires = fields.get("expires", "")
    if expires:
        try:
            exp_date = date.fromisoformat(expires)
            if exp_date < date.today():
                return {
                    "valid": False,
                    "reason": f"Licence expired on {expires}",
                    **fields,
                }
        except ValueError:
            return {"valid": False, "reason": f"Invalid expiry date: {expires}"}

    return {"valid": True, "reason": "OK", **fields}


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify a licence file")
    parser.add_argument("--pub", type=Path, required=True, help="Path to public key")
    parser.add_argument("--lic", type=Path, required=True, help="Path to .lic file")
    args = parser.parse_args()

    result = verify(args.pub, args.lic)
    if result["valid"]:
        print(f"VALID — tier={result.get('tier', '?')}, "
              f"customer={result.get('customer', '?')}, "
              f"expires={result.get('expires', '?')}")
        sys.exit(0)
    else:
        print(f"INVALID — {result['reason']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
