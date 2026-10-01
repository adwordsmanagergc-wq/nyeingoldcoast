# NYE in Gold Coast

An independent guide to New Year's Eve on the Gold Coast (Queensland): a live countdown to midnight AEST, an events directory with filters, free fireworks locations, a planning guide, and a paid **List your event** page ($599).

## How it works

- `data/events.json`: every listing (name, venue, suburb, area, categories, price, inclusions, booking URL, `featured`).
- `src/style.css`, `src/main.js`: the design, the countdown, the fireworks animation, the directory filters and the listing form.
- `build.py`: generates the full static site into `docs/`.

```bash
python3 build.py                     # rebuild docs/
cd docs && python3 -m http.server    # preview at http://localhost:8000
```

`build.py` generates:

- Home page: countdown, filterable directory, timeline, fireworks locations and FAQ
- Category landing pages: `/new-years-eve-dinner-gold-coast/`, `/new-years-eve-cruises-gold-coast/`, `/new-years-eve-parties-gold-coast/` and `/family-new-years-eve-gold-coast/`
- Fireworks locations page (`/gold-coast-fireworks-locations/`)
- Planning guide: times, transport, road closures and accessibility
- List-your-event page with the $599 offer and an intake form
- One SEO page per event, with `Event` schema
- `sitemap.xml`, `robots.txt`, `404.html` and the OG image

## Before going live: edit `CONFIG` in `build.py`

| Key | What to set |
| --- | --- |
| `site_url` | `https://nyeingoldcoast.com` (used for canonical URLs, the sitemap and OG tags) |
| `contact_email` | `aj@metatapdigital.com`: the inbox for listing requests |
| `form_endpoint` | `https://formsubmit.co/ajax/aj@metatapdigital.com`: emails each listing request to that inbox |
| `payment_link` | A Stripe Payment Link for $599 AUD. After the form saves, the buyer is redirected here with their email prefilled |

The first submission triggers a one-time FormSubmit activation email to `aj@metatapdigital.com`. Click the link in it, and every request after that arrives as a formatted email. Until `payment_link` is set, submitters see a thank-you message and you send them an invoice.

## Countdown timezone

The Gold Coast is on AEST (UTC+10) all year, with no daylight saving. `src/main.js` targets `2026-12-31T14:00:00Z`, which is midnight on 1 January 2027 in Queensland.

## Listing data

Most Gold Coast venues had not published NYE 2026 packages at launch (October 2026), so many listings carry 2025 prices marked "(2025 price, TBC)". Update `price_from`, `price_text` and `url` as 2026 packages are released.

## Adding a paid listing

Add an entry to `data/events.json`. Set `"featured": true` if you want it pinned to the top with a badge. Then run `python3 build.py` and deploy.

## Deploying (Vercel)

`vercel.json` tells Vercel to serve the pre-built `docs/` folder. No build step runs, so always run `python3 build.py` and commit `docs/` before pushing.

1. On vercel.com, choose **Add New → Project**, import the `nyeingoldcoast` repository and click **Deploy**. No settings need changing.
2. Under **Project → Settings → Domains**, add `nyeingoldcoast.com` and `www.nyeingoldcoast.com`, then set the DNS records Vercel shows at your registrar (usually an A record `76.76.21.21` for the apex and a CNAME `cname.vercel-dns.com` for `www`). `vercel.json` already redirects `www` to the apex.
3. Every push to the production branch redeploys the site automatically.

After launch, submit `https://nyeingoldcoast.com/sitemap.xml` in Google Search Console.

To regenerate `og.png`, open `docs/og.html` at 1200×630 and screenshot it.
