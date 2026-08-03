#!/usr/bin/env python3
"""Create the prepared Whop product. Defaults to a no-network dry run.

Usage:
    python whop/publish_products.py
    python whop/publish_products.py --live
    python whop/publish_products.py --live --publish

The seller, not this script, remains responsible for product delivery, tax,
refund, checkout, and Whop policy compliance.
"""

import argparse
import json
import os
import sys
import uuid
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
LISTING_PATH = Path(__file__).with_name("listing.json")
API_ROOT = os.getenv("WHOP_API_BASE", "https://api.whop.com/api/v1").rstrip("/")


def load_dotenv() -> None:
    """Read local .env without adding a dependency or overwriting real env vars."""
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def product_payload(listing: dict, company_id: str) -> dict:
    """Map the local, human-readable listing to Whop's create-product shape."""
    return {
        "company_id": company_id,
        "title": listing["title"],
        "headline": listing["headline"],
        "description": listing["description"],
        "route": listing["route"],
        "send_welcome_message": listing.get("send_welcome_message", True),
        "metadata": {
            "customer_delivery": "Upload whop/deliverable as product content before publishing.",
            "suggested_currency": listing.get("currency", "usd"),
        },
        "plan_options": {
            # A billing period of 0 is Whop's one-time plan value in this API.
            "billing_period": listing["billing_period"],
            "initial_price": listing["initial_price"],
            "renewal_price": listing["renewal_price"],
        },
    }


def request(method: str, path: str, token: str, **kwargs) -> dict:
    response = requests.request(
        method,
        f"{API_ROOT}{path}",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Idempotency-Key": str(uuid.uuid4()),
        },
        timeout=30,
        **kwargs,
    )
    try:
        body = response.json()
    except ValueError:
        body = {"raw_response": response.text}
    if not response.ok:
        raise RuntimeError(f"Whop API returned HTTP {response.status_code}: {json.dumps(body)}")
    return body


def main() -> int:
    parser = argparse.ArgumentParser(description="Create the prepared Whop listing safely.")
    parser.add_argument("--live", action="store_true", help="create the product (otherwise prints a dry run)")
    parser.add_argument("--publish", action="store_true", help="publish after creation; requires --live")
    args = parser.parse_args()
    if args.publish and not args.live:
        parser.error("--publish requires --live")

    load_dotenv()
    listing = json.loads(LISTING_PATH.read_text(encoding="utf-8"))
    company_id = os.getenv("WHOP_COMPANY_ID", "").strip()
    payload = product_payload(listing, company_id or "biz_REPLACE_ME")

    print("Prepared Whop listing:\n")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if not args.live:
        print("\nDRY RUN: no request was sent. Run with --live only after adding delivery content.")
        return 0

    token = os.getenv("WHOP_API_KEY", "").strip()
    if not token or not company_id:
        print("WHOP_API_KEY and WHOP_COMPANY_ID are required for --live.", file=sys.stderr)
        return 2
    if not company_id.startswith("biz_"):
        print("WHOP_COMPANY_ID must start with biz_.", file=sys.stderr)
        return 2

    created = request("POST", "/products", token, json=payload)
    product = created.get("data", created)
    product_id = product.get("id")
    print(f"\nCreated Whop product: {product_id or json.dumps(created)}")
    if args.publish:
        if not product_id:
            raise RuntimeError("Whop response did not include a product ID; refusing to publish.")
        request("POST", f"/products/{product_id}/publish", token)
        print(f"Published Whop product: {product_id}")
    else:
        print("Product remains a draft. Review delivery and checkout, then run with --live --publish.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, requests.RequestException, RuntimeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1)
