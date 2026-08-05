#!/usr/bin/env python3
"""
Shopify connector + Upgrade tasks for GadgetsN.Store
- Test connection
- Clean mr.gf999 / Nexus Gadgets references
- Update shop name to GadgetsN.Store (logo text fix)
- Prepare hero random product logic (theme asset upload)
- Review system verification helpers
"""
import os
import sys
import json
import requests

# Load .env if exists
if os.path.exists(".env"):
    with open(".env", encoding="utf-8") as fh:
        for line in fh:
            line=line.strip()
            if line and not line.startswith("#") and "=" in line:
                k,_,v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip().strip('"\''))

# Also support web/.env.local for Firebase etc
for env_path in [".env", "web/.env", "web/.env.local"]:
    if os.path.exists(env_path):
        with open(env_path, encoding="utf-8") as fh:
            for line in fh:
                line=line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k,_,v = line.partition("=")
                    os.environ.setdefault(k.strip(), v.strip().strip('"\''))

STORE_URL = os.environ.get("SHOPIFY_STORE_URL", "").strip().rstrip("/")
ACCESS_TOKEN = os.environ.get("SHOPIFY_ACCESS_TOKEN", "").strip()
ADMIN_EMAIL = "oussamabriedj2001@gmail.com"

BANNED_TERMS = ["mr.gf999", "mr.gf", "nexus gadgets", "nexus", "gf999"]
TARGET_NAME = "GadgetsN.Store"
TARGET_VENDOR = "GadgetsN.Store"

def get_headers(token=None):
    return {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": token or ACCESS_TOKEN
    }

def normalize_store_url(url: str) -> str:
    url = url.strip().replace("https://","").replace("http://","").rstrip("/")
    if not url:
        return ""
    if url.endswith(".myshopify.com"):
        return f"https://{url}"
    # If custom domain like gadgetsn.store, we still need myshopify domain for API
    # Try to keep as is but admin API only works on .myshopify.com
    # So if it's gadgetsn.store, user must provide myshopify domain: bys-user-store-252316-0ygfe56b.myshopify.com or ngadgets-store
    if "." in url and not url.endswith(".myshopify.com"):
        # Assume custom domain, try to infer? Return as is, API call will fail and we instruct
        return f"https://{url}"
    return f"https://{url}.myshopify.com"

def test_connection(store_url=None, access_token=None):
    store_url = store_url or STORE_URL
    access_token = access_token or ACCESS_TOKEN
    if not store_url or not access_token:
        return {"ok": False, "error": "SHOPIFY_STORE_URL or SHOPIFY_ACCESS_TOKEN missing"}
    base = normalize_store_url(store_url)
    url = f"{base}/admin/api/2024-10/shop.json"
    try:
        resp = requests.get(url, headers=get_headers(access_token), timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            shop = data.get("shop", {})
            return {"ok": True, "shop": shop, "base_url": base}
        else:
            return {"ok": False, "status": resp.status_code, "body": resp.text[:2000]}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def list_products(limit=50, store_url=None, access_token=None):
    store_url = store_url or STORE_URL
    access_token = access_token or ACCESS_TOKEN
    base = normalize_store_url(store_url)
    url = f"{base}/admin/api/2024-10/products.json?limit={limit}"
    resp = requests.get(url, headers=get_headers(access_token), timeout=20)
    resp.raise_for_status()
    return resp.json()

def search_products_to_clean(store_url=None, access_token=None):
    """Find products containing banned terms"""
    try:
        data = list_products(limit=250, store_url=store_url, access_token=access_token)
        to_clean = []
        for p in data.get("products", []):
            hay = f"{p.get('title','')} {p.get('vendor','')} {p.get('product_type','')} {p.get('tags','')}".lower()
            for term in BANNED_TERMS:
                if term in hay:
                    to_clean.append({"id": p["id"], "title": p["title"], "vendor": p.get("vendor"), "handle": p["handle"], "matched_term": term})
                    break
        return to_clean
    except Exception as e:
        return {"error": str(e)}

def clean_store_content(dry_run=True, store_url=None, access_token=None):
    """
    - Finds products with banned terms (mr.gf999, Nexus etc)
    - Updates vendor to GadgetsN.Store
    - Updates shop name (requires shop.json PUT)
    - In dry_run mode only lists, does not delete
    """
    store_url = store_url or STORE_URL
    access_token = access_token or ACCESS_TOKEN
    base = normalize_store_url(store_url)
    
    print(f"🔍 Scanning for banned terms {BANNED_TERMS} in {base} ...")
    candidates = search_products_to_clean(store_url, access_token)
    if isinstance(candidates, dict) and "error" in candidates:
        print(f"❌ Error listing: {candidates['error']}")
        return candidates

    print(f"Found {len(candidates)} products matching banned terms")
    for c in candidates:
        print(f"  - {c['id']} | {c['title']} | vendor={c['vendor']} | term={c['matched_term']}")

    if dry_run:
        print("\n⚠️ Dry run - no changes made. Run with dry_run=False to apply fixes")
        return {"dry_run": True, "found": candidates}

    # Apply fixes
    fixed = []
    for prod in candidates:
        pid = prod["id"]
        try:
            # Update vendor to GadgetsN.Store
            url = f"{base}/admin/api/2024-10/products/{pid}.json"
            payload = {"product": {"id": pid, "vendor": TARGET_VENDOR}}
            r = requests.put(url, headers=get_headers(access_token), json=payload, timeout=15)
            if r.status_code == 200:
                print(f"✅ Fixed vendor for {pid}")
                fixed.append(pid)
            else:
                print(f"⚠️ Failed fix {pid}: {r.status_code} {r.text[:300]}")
        except Exception as e:
            print(f"❌ Exception fixing {pid}: {e}")

    # Also update shop name if possible
    try:
        url = f"{base}/admin/api/2024-10/shop.json"
        # Shopify shop name update not always allowed via API, but try
        payload = {"shop": {"name": TARGET_NAME}}
        # This endpoint is not writable for name in newer APIs, but we attempt
        r = requests.put(url, headers=get_headers(access_token), json=payload, timeout=15)
        print(f"Shop name update attempt: {r.status_code}")
    except Exception as e:
        print(f"Shop name update error: {e}")

    return {"fixed": fixed, "found_count": len(candidates)}

def update_shop_settings(store_url=None, access_token=None):
    """Set shop name, customer email, etc"""
    base = normalize_store_url(store_url or STORE_URL)
    print(f"Updating shop settings for {base} ...")
    # Example: update shop description / customer email
    # This requires additional scopes

def upload_theme_assets(store_url=None, access_token=None):
    """
    Upload logo.svg, trust-badges, hero-random snippets via Asset API
    Requires theme ID - fetch active theme
    """
    base = normalize_store_url(store_url or STORE_URL)
    token = access_token or ACCESS_TOKEN
    try:
        # Get themes
        r = requests.get(f"{base}/admin/api/2024-10/themes.json", headers=get_headers(token), timeout=15)
        r.raise_for_status()
        themes = r.json().get("themes", [])
        active = next((t for t in themes if t.get("role")=="main"), themes[0] if themes else None)
        if not active:
            return {"error": "No theme found"}
        theme_id = active["id"]
        print(f"Active theme: {active['name']} (ID {theme_id})")

        assets = [
            ("assets/logo.svg", "shopify-upgrade/assets/logo.svg"),
            ("snippets/logo-text.liquid", "shopify-upgrade/snippets/logo-text.liquid"),
            ("snippets/hero-random.liquid", "shopify-upgrade/snippets/hero-random.liquid"),
            ("snippets/trust-badges.liquid", "shopify-upgrade/snippets/trust-badges.liquid"),
            ("snippets/reviews-verified.liquid", "shopify-upgrade/snippets/reviews-verified.liquid"),
        ]
        results = []
        for key, local_path in assets:
            if not os.path.exists(local_path):
                print(f"Skip {local_path} not found")
                continue
            with open(local_path, "r", encoding="utf-8") as fh:
                content = fh.read()
            payload = {"asset": {"key": key, "value": content}}
            url = f"{base}/admin/api/2024-10/themes/{theme_id}/assets.json"
            resp = requests.put(url, headers=get_headers(token), json=payload, timeout=20)
            results.append({"key": key, "status": resp.status_code, "ok": resp.status_code<300})
            print(f"Upload {key}: {resp.status_code}")

        return {"theme_id": theme_id, "results": results}
    except Exception as e:
        return {"error": str(e)}

def fix_login_profile_instructions():
    print("""
=== FIX LOGIN / LOGOUT / PROFILE ===

1. Shopify Admin > Settings > Customer accounts:
   - Enable 'New customer accounts' (recommended)
   - Enable 'Show login link in header'

2. Online Store > Themes > Edit Code > layout/theme.liquid
   Check {% if shop.customer_accounts_enabled %}
   - Ensure account link points to /account not custom page

3. Firebase Auth for profile (web app):
   - In web/src/lib/firebase.js set real config from Firebase Console
   - Enable Google provider, add authorized domain gadgetsn.store
   - Only oussamabriedj2001@gmail.com can access /admin

4. Current web app (web/) already fixes login:
   - AuthContext handles login/logout/profile via Firebase + localStorage fallback
   - Account page shows orders, points, wishlist
   - Test: npm run dev -> /login -> login as oussamabriedj2001@gmail.com -> /admin works

5. Shopify customer sync:
   - Use Shopify Customer API to sync Shopify customers to Firebase
   - See shopify-upgrade/functions/reviewInvite.js for canReview check (requires auth)
""")

def print_full_upgrade_plan():
    print(f"""
=== GadgetsN.Store Full Upgrade Plan ===

TARGET: {TARGET_NAME} (domain: gadgetsn.store)
ADMIN ONLY: {ADMIN_EMAIL} via Firebase Google
BANNED TO CLEAN: {BANNED_TERMS}

Steps:
1. Logo text fix: GadgetsN.Store SVG + logo-text.liquid
2. Hero random product: hero-random.liquid -> random product url
3. Trust badges: trust-badges.liquid (8 badges, shipping details)
4. Reviews verified only: reviews-verified.liquid + reviewInvite.js
   - Only delivered orders can review
   - Photo optional but incentivized 50pts + REVIEW10 coupon
   - Email automation 3 days after delivery (AliExpress style)
5. Login/profile fix: Firebase Auth + new customer accounts
6. Fill all buttons: Map every # to real collection/product/page
7. Multilanguage: EN/FR/AR ready
8. Make main interface: Deploy web/ to Vercel, set as proxy or primary domain

Run:
  SHOPIFY_STORE_URL=bys-user-store-252316-0ygfe56b.myshopify.com SHOPIFY_ACCESS_TOKEN=shpat_... python shopify_client.py --clean --upload-assets --test

For theme only (no token): Copy shopify-upgrade/snippets/* to your Dawn theme manually.
""")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="GadgetsN.Store Shopify Upgrade Tool")
    parser.add_argument("--test", action="store_true", help="Test connection")
    parser.add_argument("--scan", action="store_true", help="Scan for banned terms mr.gf999 etc")
    parser.add_argument("--clean", action="store_true", help="Clean banned terms (updates vendor)")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Dry run for clean (default true)")
    parser.add_argument("--apply", action="store_true", help="Apply clean (disable dry run)")
    parser.add_argument("--upload-assets", action="store_true", help="Upload logo and snippets to active theme")
    parser.add_argument("--plan", action="store_true", help="Print full upgrade plan")

    args = parser.parse_args()

    if len(sys.argv)==1 or args.test:
        print("Testing Shopify connection...")
        print(json.dumps(test_connection(), indent=2, ensure_ascii=False))

    if args.scan:
        print(json.dumps(search_products_to_clean(), indent=2, ensure_ascii=False))

    if args.clean:
        dry = not args.apply
        result = clean_store_content(dry_run=dry)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    if args.upload_assets:
        print(json.dumps(upload_theme_assets(), indent=2, ensure_ascii=False))

    if args.plan or len(sys.argv)==1:
        print_full_upgrade_plan()
        fix_login_profile_instructions()
