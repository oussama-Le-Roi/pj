# Whop launch kit — AI Client Acquisition Kit

This directory is a **ready-to-sell digital product**, written for Arabic-speaking freelancers and small service businesses. It is deliberately practical: it contains client outreach templates, discovery questions, proposal wording, delivery checklists, and AI prompts. It makes no income guarantees.

## Product chosen

**Title:** AI Client Acquisition Kit — Arabic Freelancer Edition  
**Headline:** Ready-to-use Arabic templates and AI prompts to organize outreach, proposals, and client delivery.  
**Suggested price:** US$9 one-time  
**Audience:** Arabic-speaking freelancers who sell design, development, marketing, writing, or virtual-assistant services.

The complete customer download is [`deliverable/AI-Client-Acquisition-Kit-AR.md`](deliverable/AI-Client-Acquisition-Kit-AR.md). It can be converted to PDF or included in a ZIP before delivery.

## What the automation does

`publish_products.py` uses Whop's product API to create the product with its title, headline, description, price, and product route. It is safe by default:

- Without `--live`, it only prints the request body (**dry run**).
- With `--live`, it creates the product in the specified Whop company.
- `--publish` additionally requests publishing. Publishing is an external, consequential action and is intentionally opt-in.

It does **not** fabricate reviews, customers, or earnings. It also cannot upload a customer file/access experience because delivery setup depends on the seller's Whop configuration. Add the customer download to the product's Content/experience in Whop before publishing, or set up a hosted delivery URL.

## Run

1. Create a Whop company and generate a company API key with product creation permission.
2. Copy the environment example at the repository root and populate the two Whop variables locally. Never commit keys.
3. Check the generated listing without changing Whop:

   ```bash
   python whop/publish_products.py
   ```

4. Create the draft product:

   ```bash
   python whop/publish_products.py --live
   ```

5. After adding the download/access experience and reviewing checkout settings, publish it:

   ```bash
   python whop/publish_products.py --live --publish
   ```

The script requires `WHOP_API_KEY` and `WHOP_COMPANY_ID` (the latter begins with `biz_`). API details: https://docs.whop.com/api-reference/products/create-product


> A GitHub Actions launcher is prepared locally but cannot be uploaded by the current GitHub connection because it lacks the `workflows` permission. The product files and local launcher below are fully usable now.

## Customer-facing files

- `listing.json`: the exact listing copy and price sent to the API.
- `deliverable/AI-Client-Acquisition-Kit-AR.md`: the product customers receive.
- `deliverable/README.txt`: concise usage and licensing notice for the customer.

## Honest marketing note

The kit helps with workflow and communication; it is not a promise of clients, revenue, or business success. Do not make those claims on the product page.
