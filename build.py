#!/usr/bin/env python3
"""Static site generator for NYE in Gold Coast.

Edit data/events.json (and the CONFIG block below), then run:
    python3 build.py
The complete site is written to ./docs, which Vercel serves as-is (see vercel.json).
"""
import json
import shutil
from datetime import date
from html import escape
from pathlib import Path

# --------------------------------------------------------------------------------------
# CONFIG: change these before going live
# --------------------------------------------------------------------------------------
CONFIG = {
    "site_name": "NYE in Gold Coast",
    "site_url": "https://nyeingoldcoast.com",   # your live domain, no trailing slash
    "contact_email": "aj@metatapdigital.com",
    "listing_price": 599,                              # AUD, inc GST
    # Listing submissions are emailed to contact_email via FormSubmit (no account needed;
    # the first submission sends a one-time activation email to that inbox).
    "form_endpoint": "https://formsubmit.co/ajax/aj@metatapdigital.com",
    # Stripe Payment Link (or similar) for the $599 listing fee. While it still contains
    # "YOUR_", submitters see a thank-you message and you email them an invoice instead.
    "payment_link": "https://buy.stripe.com/YOUR_PAYMENT_LINK",
    "year": 2026,
    "next_year": 2027,
}

ROOT = Path(__file__).parent
OUT = ROOT / "docs"
EVENTS = json.loads((ROOT / "data" / "events.json").read_text())
TODAY = date.today().isoformat()
Y, NY = CONFIG["year"], CONFIG["next_year"]
URL = CONFIG["site_url"]

CATEGORY_LABELS = {
    "party": "Parties",
    "dining": "Dinners",
    "fine-dining": "Fine dining",
    "cruise": "Cruises",
    "rooftop": "Rooftops",
    "beachfront": "Beachfront",
    "broadwater": "Broadwater & marina",
    "family": "Family-friendly",
    "budget": "Under $200",
    "vantage": "Fireworks events",
    "free": "Free",
}
AREAS = sorted({e["area"] for e in EVENTS})

NAV = [
    ("/", "Home"),
    ("/#directory", "All events"),
    ("/new-years-eve-dinner-gold-coast/", "Dinners"),
    ("/new-years-eve-cruises-gold-coast/", "Cruises"),
    ("/new-years-eve-parties-gold-coast/", "Parties"),
    ("/gold-coast-fireworks-locations/", "Fireworks"),
    ("/plan-your-night/", "Plan"),
]


def j(obj):
    return json.dumps(obj, ensure_ascii=False, indent=1).replace("</", "<\\/")


def money(n):
    return "Free" if n == 0 else f"${n:,.0f}"


import random as _r
_r.seed(7)
# Gold Coast skyline: a dense strip of beachfront towers with Q1's spire, over the surf.
_TOWERS = []
_x = 0
while _x < 1440:
    w = _r.randint(22, 44)
    centre = abs(_x - 640) / 640                      # taller towers cluster around "Surfers"
    h = int(_r.randint(40, 70) + (1 - min(centre, 1)) * _r.randint(30, 90))
    _TOWERS.append(f'<rect x="{_x}" y="{198 - h}" width="{w}" height="{h}"/>')
    _x += w + _r.randint(2, 10)
SKYLINE = """<svg class="skyline" viewBox="0 0 1440 230" preserveAspectRatio="xMidYMax slice" aria-hidden="true">
<defs><linearGradient id="sk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0c0a26"/><stop offset="1" stop-color="#07061a"/></linearGradient>
<linearGradient id="wt" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1a1450" stop-opacity=".9"/><stop offset="1" stop-color="#07061a"/></linearGradient></defs>
<g fill="url(#sk)">""" + "".join(_TOWERS) + """
<path d="M612 198 L612 46 Q622 30 632 46 L632 198Z"/><rect x="620.5" y="4" width="3" height="34"/>
<rect x="700" y="62" width="34" height="136"/><rect x="560" y="74" width="30" height="124"/>
</g>
<rect x="0" y="198" width="1440" height="32" fill="url(#wt)"/>
<path d="M0 206 Q40 201 80 206 T160 206 T240 206 T320 206 T400 206 T480 206 T560 206 T640 206 T720 206 T800 206 T880 206 T960 206 T1040 206 T1120 206 T1200 206 T1280 206 T1360 206 T1440 206" fill="none" stroke="#2a2170" stroke-width="1.5" opacity=".7"/>
</svg>"""


def countdown(mini=False):
    units = [("d", "Days"), ("h", "Hours"), ("m", "Minutes"), ("s", "Seconds")]
    inner = "".join(
        f'<div class="cd-unit"><div class="cd-num" data-u="{k}">--</div><div class="cd-label">{v}</div></div>'
        for k, v in units
    )
    return f'<div class="countdown{" mini" if mini else ""}" data-countdown role="timer" aria-label="Countdown to midnight, New Year\'s Eve {Y} on the Gold Coast">{inner}</div>'


def layout(path, title, description, body, schema=None, og_type="website", active=None):
    canonical = URL + path
    schemas = [
        {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": CONFIG["site_name"],
            "url": URL + "/",
            "potentialAction": {
                "@type": "SearchAction",
                "target": URL + "/?q={search_term_string}#directory",
                "query-input": "required name=search_term_string",
            },
        }
    ] if path == "/" else []
    schemas += schema or []
    cur = ' aria-current="page"'
    nav = "".join(
        f'<li><a href="{h}"{cur if h == (active or path) else ""}>{t}</a></li>' for h, t in NAV
    )
    ld = "".join(f'<script type="application/ld+json">{j(s)}</script>' for s in schemas)
    return f"""<!doctype html>
<html lang="en-AU">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)}</title>
<meta name="description" content="{escape(description)}">
<link rel="canonical" href="{canonical}">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta name="geo.region" content="AU-QLD"><meta name="geo.placename" content="Gold Coast">
<meta property="og:type" content="{og_type}"><meta property="og:site_name" content="{CONFIG['site_name']}">
<meta property="og:title" content="{escape(title)}"><meta property="og:description" content="{escape(description)}">
<meta property="og:url" content="{canonical}"><meta property="og:image" content="{URL}/og.png"><meta property="og:locale" content="en_AU">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="{URL}/og.png">
<meta name="theme-color" content="#07061a">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700;800&family=Playfair+Display:wght@700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/style.css">
{ld}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="nav"><div class="wrap">
<a class="logo" href="/">NYE <span>in Gold Coast</span></a>
<nav aria-label="Main"><ul>{nav}</ul></nav>
<a class="btn btn-primary btn-sm" href="/list-your-event/">List your event</a>
<button class="menu-btn" aria-label="Menu" aria-expanded="false">☰</button>
</div></header>
<main id="main">
{body}
</main>
<footer><div class="wrap">
<div class="fgrid">
<div><a class="logo" href="/">NYE <span>in Gold Coast</span></a>
<p class="muted">The independent guide to New Year's Eve {Y} on the Gold Coast: free beach fireworks, Broadwater cruises, dinners and parties, all in one place.</p>
{countdown(mini=True)}</div>
<div><h4>Explore</h4><ul>
<li><a href="/#directory">All NYE events</a></li><li><a href="/new-years-eve-dinner-gold-coast/">NYE dinners</a></li>
<li><a href="/new-years-eve-cruises-gold-coast/">NYE cruises</a></li><li><a href="/new-years-eve-parties-gold-coast/">NYE parties</a></li>
<li><a href="/family-new-years-eve-gold-coast/">Family NYE</a></li></ul></div>
<div><h4>Plan</h4><ul>
<li><a href="/gold-coast-fireworks-locations/">Fireworks locations</a></li><li><a href="/plan-your-night/">Fireworks times</a></li>
<li><a href="/plan-your-night/#transport">Transport</a></li><li><a href="/#faq">FAQ</a></li></ul></div>
<div><h4>Venues</h4><ul>
<li><a href="/list-your-event/">List your event: ${CONFIG['listing_price']}</a></li>
<li><a href="mailto:{CONFIG['contact_email']}">{CONFIG['contact_email']}</a></li></ul></div>
</div>
<p class="fine">NYE in Gold Coast is an independent guide and is not affiliated with the City of Gold Coast, Destination Gold Coast or any official New Year's Eve event. Prices and details are supplied by venues or based on published information and may change. Prices marked 2025 are last year's and are a guide only. Always confirm with the venue before booking. We acknowledge the Kombumerri people and the Yugambeh Language Region, Traditional Custodians of the land and waters of the Gold Coast. © {Y} {CONFIG['site_name']}.</p>
</div></footer>
<script src="/main.js" defer></script>
</body>
</html>"""


# --------------------------------------------------------------------------------------
# Components
# --------------------------------------------------------------------------------------
def card(e, i):
    cats = " ".join(e["categories"])
    search = " ".join([e["name"], e["venue"], e["suburb"], e["area"], " ".join(e["categories"]), e["blurb"]]).lower()
    tags = "".join(f'<span class="tag">{CATEGORY_LABELS.get(c, c)}</span>' for c in e["categories"][:3])
    price = e["price_from"]
    price_html = (
        "Free<small>see details</small>" if price == 0
        else f"{money(price)}<small>from, per person</small>" if price
        else "TBA<small>see venue</small>"
    )
    return f"""<article class="card{' featured' if e.get('featured') else ''}" data-cats="{cats}" data-area="{escape(e['area'])}" data-price="{price if price is not None else ''}" data-featured="{1 if e.get('featured') else 0}" data-order="{i}" data-search="{escape(search)}">
{'<span class="badge">Featured</span>' if e.get('featured') else ''}
<div class="loc">📍 {escape(e['suburb'] if e['suburb'] in e['area'] else e['suburb'] + ' · ' + e['area'])}</div>
<h3><a href="/events/{e['slug']}/">{escape(e['name'])}</a></h3>
<p>{escape(e['blurb'])}</p>
<div class="tags"><span class="tag fw">🎆 {escape(e['fireworks'])}</span>{tags}</div>
<div class="meta"><div class="price">{price_html}</div>
<div class="actions"><a class="btn btn-ghost btn-sm" href="/events/{e['slug']}/">Details</a><a class="btn btn-primary btn-sm" href="{e['url']}" target="_blank" rel="noopener sponsored">Book</a></div></div>
</article>"""


def directory(events, heading, sub, show_filters=True, anchor="directory"):
    used = []
    for e in events:
        for c in e["categories"]:
            if c not in used:
                used.append(c)
    order = [c for c in CATEGORY_LABELS if c in used]
    chips = '<button class="chip" data-cat="all" aria-pressed="true">All</button>' + "".join(
        f'<button class="chip" data-cat="{c}" aria-pressed="false">{CATEGORY_LABELS[c]}</button>' for c in order
    )
    areas = '<option value="all">All areas</option>' + "".join(
        f'<option>{escape(a)}</option>' for a in AREAS if any(e["area"] == a for e in events)
    )
    filters = f"""<div class="filters" role="group" aria-label="Filter by type">{chips}</div>
<div class="toolbar"><input id="q" type="search" placeholder="Search venue, suburb, vibe…" aria-label="Search events">
<select id="area" aria-label="Filter by area">{areas}</select>
<select id="sort" aria-label="Sort"><option value="featured">Sort: Featured</option><option value="low">Price: low to high</option><option value="high">Price: high to low</option></select></div>
<p class="count" aria-live="polite"></p>""" if show_filters else ""
    cards = "".join(card(e, i) for i, e in enumerate(events))
    return f"""<section id="{anchor}" data-directory><div class="wrap">
<div class="section-head"><h2>{heading}</h2><p>{sub}</p></div>
{filters}
<div class="grid">{cards}</div>
<p class="empty">No events match that search. Try another filter, or <a href="/list-your-event/">list yours</a>.</p>
</div></section>"""


def season_section(p):
    months = [
        ("October", "Planning begins",
         "Big parties, cruises and rooftop events release first-tier tickets, and people start searching \"New Year's Eve Gold Coast\". Early birds lock in their plans and groups start comparing options.",
         "List now and you're live for the whole season, from day one."),
        ("November", "Comparing &amp; booking",
         "Locals and holidaymakers compare prices, inclusions and fireworks views side by side. This is when beachfront tables, cruises and party tickets get booked.",
         "Your page, with its price, inclusions and a Book button, wins the comparison."),
        ("December", "Peak searches &amp; last-minute rush",
         "Search interest hits its peak as summer holidaymakers arrive. People chase the last tables, final release tiers and late tickets right up to 31 December.",
         "Sell your remaining tickets and late seatings while demand is at its highest."),
    ]
    cards = "".join(
        f'''<div class="card season-card"><span class="season-step">{i + 1}</span><div class="loc">{m}</div><h3>{t}</h3><p>{d}</p>
<p class="season-win">✦ {w}</p></div>''' for i, (m, t, d, w) in enumerate(months)
    )
    return f"""<section id="season"><div class="wrap">
<div class="section-head"><span class="eyebrow">The NYE search season</span>
<h2>The Gold Coast books New Year's Eve in <span class="grad">three months</span></h2>
<p>Every year, searches like "New Year's Eve Gold Coast", "Gold Coast fireworks New Year's Eve" and "NYE dinner Gold Coast" climb from October and peak in the final weeks of December. That's when people choose a venue and buy tickets. If your event isn't in front of them then, they book somewhere else.</p></div>
<div class="season-bar" aria-hidden="true"><span style="--h:34%">Oct</span><span style="--h:62%">Nov</span><span style="--h:100%">Dec</span></div>
<p class="muted" style="text-align:center;font-size:.8rem;margin:-6px 0 30px">Shows the typical seasonal pattern of search interest, not exact volumes.</p>
<div class="grid">{cards}</div>
<div class="band" style="margin-top:40px">
<div><h2>One listing. The whole season.</h2><p>At typical Gold Coast NYE prices of $150–$550 a head, a handful of bookings covers your ${p} listing. Everything after that is profit, with zero commission.</p></div>
<a class="btn" href="#form">Claim your spot →</a></div>
</div></section>"""


def list_band():
    return f"""<section><div class="wrap"><div class="band">
<div><h2>Selling NYE tickets on the Gold Coast?</h2><p>October to December is when locals and holidaymakers search for their Gold Coast New Year's Eve plans. Get your event in front of them for ${CONFIG['listing_price']} flat, with no commission.</p></div>
<a class="btn" href="/list-your-event/">List your event →</a></div></div></section>"""


def item_list(events, name):
    return {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": name,
        "numberOfItems": len(events),
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "url": f"{URL}/events/{e['slug']}/", "name": e["name"]}
            for i, e in enumerate(events)
        ],
    }


def breadcrumbs(*pairs):
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": URL + p} for i, (n, p) in enumerate(pairs)
        ],
    }


# --------------------------------------------------------------------------------------
# Content: FAQ, timeline, vantage points
# --------------------------------------------------------------------------------------
FAQ = [
    (f"What time are the Gold Coast New Year's Eve fireworks in {Y}?",
     f"On Thursday 31 December {Y} the City of Gold Coast normally runs two free beach displays: an early family show and a midnight show. In 2025 Surfers Paradise and Broadbeach (Kurrawa Park) had fireworks at 8pm and midnight, Coolangatta at 9pm and midnight, Broadwater Parklands and Coomera at 8pm, Varsity Lakes at 8:30pm and Paradise Point at 9pm. The {Y} program is usually confirmed in December, so check the council's website closer to the night."),
    ("Where is the best place to watch the fireworks on the Gold Coast?",
     "Surfers Paradise beach is the main event, with the biggest crowd and both shows. Kurrawa Park in Broadbeach has more room to spread out, and Coolangatta Beach is the relaxed southern option. For families, the 8pm shows at Broadwater Parklands, Coomera, Varsity Lakes and Paradise Point are quieter and end early. For a guaranteed view without a crowd, book a beachfront bar, a rooftop like SkyPoint or a Broadwater cruise."),
    ("Are the Gold Coast NYE fireworks free?",
     "Yes. All of the City of Gold Coast fireworks on the beaches and in the parklands are free and you don't need a ticket. Just turn up early to get a good spot. Some private venues, such as Southport Sharks, La Luna Beach Club and InterContinental Sanctuary Cove, run their own displays too."),
    ("How much does a New Year's Eve cruise on the Gold Coast cost?",
     "Broadwater NYE cruises are good value. In 2025 family cruises started from about $89 per child and $169 per adult, while adults-only midnight party cruises ran from about $179 to $400 per person. Sea World Cruises has already published $269 per adult for 2026, including a 4-hour drinks package. See our <a href=\"/new-years-eve-cruises-gold-coast/\">Gold Coast NYE cruises</a> list."),
    ("Where can I have dinner on New Year's Eve on the Gold Coast?",
     "Popular NYE dinners include Haven and LiTO at Mondrian and Rick Shores in Burleigh Heads, MĀRE in Main Beach, Norté in Mermaid Beach, T'ang Court at The Langham and Nineteen at The Star. Prices in 2025 ranged from about $99 for an early banquet to $550 for an all-inclusive seafood dinner. Early sittings are cheaper and suit families. See our <a href=\"/new-years-eve-dinner-gold-coast/\">NYE dinners on the Gold Coast</a> list."),
    ("What time should I arrive for the beach fireworks?",
     "For the midnight show at Surfers Paradise, the beach fills through the evening, so aim to arrive by about 9pm for a good spot on the sand. For the 8pm family shows, arrive in the late afternoon and make a picnic of it. Kurrawa Park and Coolangatta are usually easier to find space at."),
    ("Is public transport free on New Year's Eve on the Gold Coast?",
     "In 2025 the Queensland Government made all Translink public transport free from 8pm on New Year's Eve until 5:30am on New Year's Day, with 50 cent fares at other times. G:link trams ran every 7–8 minutes through the night and extra buses ran across the city. Check translink.com.au for the 2026 arrangements before you go."),
    ("Can I drink alcohol on the beach on New Year's Eve?",
     "No. Drinking alcohol in public places, including Gold Coast beaches, foreshores and parks, is generally against the law in Queensland, and police are out in force on New Year's Eve. Council family events such as New Year's Eve by the Sea at Broadwater Parklands are alcohol-free. If you want a drink with the fireworks, book a licensed beachfront bar, restaurant or cruise. Glass is not allowed on the beach."),
    ("What are the best family-friendly NYE options on the Gold Coast?",
     "The early 8pm fireworks at Surfers Paradise, Kurrawa Park, Broadwater Parklands and Coomera are made for kids. Free community events with rides, food trucks and entertainment run at Broadwater Parklands, Coomera, Varsity Lakes, Paradise Point, Miami and Robina Town Centre. Spirit of Gold Coast runs a family cruise for the 8pm show, and several restaurants offer early sittings with child pricing."),
    ("Is NYE in Gold Coast the official Gold Coast New Year's Eve website?",
     "No. NYE in Gold Coast is an independent guide and event directory. The free fireworks are run by the City of Gold Coast. We bring together the official fireworks information and bookable dinners, cruises and parties so you can plan the whole night in one place."),
    ("How do I list my New Year's Eve event on NYE in Gold Coast?",
     f"It's a one-off ${CONFIG['listing_price']} fee with no commission. Your event gets its own optimised page, a place in our directory and category pages, and a direct link to your booking page. <a href=\"/list-your-event/\">List your event here</a>."),
    ("Why does Coolangatta celebrate New Year an hour after Tweed Heads?",
     "Queensland doesn't use daylight saving, but New South Wales does. Tweed Heads, just over the border from Coolangatta, reaches midnight at 11pm Queensland time. The Gold Coast's own midnight fireworks run at midnight Queensland time (AEST)."),
]

def faq_html(items):
    return "".join(f"<details><summary>{escape(q)}</summary><p>{a}</p></details>" for q, a in items)


def faq_schema(items):
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in items
        ],
    }


TIMELINE = [
    ("Afternoon", "Families head to the beach and parklands. Free community events at Broadwater Parklands, Miami and Robina start from about 4pm."),
    ("5pm – 6pm", "Entertainment starts at Paradise Point, Varsity Lakes and Coomera. Early dinner sittings begin across the coast."),
    ("Around 6pm", "In recent years The Esplanade and Orchid Avenue in Surfers Paradise closed to traffic from 6pm and became pedestrian zones."),
    ("8:00pm", "Family fireworks at Surfers Paradise, Kurrawa Park Broadbeach, Broadwater Parklands and Coomera (2025 times)."),
    ("8:30pm – 9:00pm", "Fireworks at Varsity Lakes (8:30pm), then Coolangatta, Paradise Point and Southport Sharks (9pm). In 2025 public transport became free from 8pm."),
    ("Late evening", "Parties, rooftops and cruises are in full swing. The beach at Surfers Paradise fills up for the main show."),
    ("Midnight", f"Midnight fireworks at Surfers Paradise, Kurrawa Park and Coolangatta, plus private displays at The Star, Main Beach marina and Sanctuary Cove, to welcome {NY}."),
    ("After midnight", "G:link and extra buses run through the night. In 2025 free travel ran until 5:30am. Allow time for queues."),
]

def timeline_html():
    return '<div class="timeline">' + "".join(
        f'<div class="tl"><b>{t}</b><p>{d}</p></div>' for t, d in TIMELINE
    ) + "</div>"


VANTAGE = [
    ("Surfers Paradise Foreshore", "Surfers Paradise", "8pm & midnight over the ocean", "free", "The main event and the biggest crowd; G:link to Cypress Ave, Cavill Ave or Surfers Paradise"),
    ("Kurrawa Park & beachfront", "Broadbeach", "8pm & midnight", "free", "More room to spread out; G:link to Broadbeach North or South"),
    ("Coolangatta Beach", "Coolangatta", "9pm & midnight (QLD time)", "free", "Relaxed southern option; Tweed Heads (NSW) is an hour ahead"),
    ("Broadwater Parklands (The Great Lawn)", "Southport", "8pm over the Broadwater", "af", "Alcohol-free family event with bands and food trucks from 4pm"),
    ("Paradise Point Parklands", "Paradise Point", "9pm", "free", "Local Broadwater favourite; entertainment from 5pm"),
    ("Coomera Sports Park", "Coomera", "8pm", "free", "Park & Ride shuttle from Dreamworld in 2025"),
    ("Lake Orr waterfront", "Varsity Lakes", "8:30pm over the lake", "free", "New Year's Eve by the Lake; family event from 5:30pm"),
    ("Thorn Park", "Miami", "Early evening", "free", "Miami Twilight NYE, 4pm – 8pm"),
    ("The Promenade, Robina Town Centre", "Robina", "Around 8pm (check time)", "free", "Carnival rides and family entertainment"),
    ("Southport Sharks oval", "Southport", "9pm & midnight", "free", "Club's own display; seafood buffet ticketed"),
    ("SkyPoint, Level 77 Q1", "Surfers Paradise", "From 230m up", "paid", "Ticketed party; NYE Climb from $179 for 2026"),
    ("On the Broadwater", "Southport to Main Beach", "From the water", "paid", "Book a cruise for 8pm or midnight"),
]
PILL = {
    "free": '<span class="pill free">Free</span>',
    "af": '<span class="pill af">Free · alcohol-free</span>',
    "paid": '<span class="pill paid">Paid ticket</span>',
    "check": '<span class="pill af">Check entry</span>',
}

def vantage_table(rows=None):
    rows = rows or VANTAGE
    body = "".join(
        f"<tr><td><b>{n}</b></td><td>{a}</td><td>{v}</td><td>{PILL[t]}</td><td class='muted'>{note}</td></tr>"
        for n, a, v, t, note in rows
    )
    return f"""<div class="table-wrap"><table><thead><tr><th>Location</th><th>Area</th><th>Fireworks</th><th>Entry</th><th>Good to know</th></tr></thead>
<tbody>{body}</tbody></table></div>"""


# --------------------------------------------------------------------------------------
# Pages
# --------------------------------------------------------------------------------------
def page_home():
    featured = [e for e in EVENTS if e.get("featured")]
    rest = [e for e in EVENTS if not e.get("featured")]
    ordered = featured + rest
    n = len(EVENTS)
    body = f"""
<section class="hero"><canvas id="fw" aria-hidden="true"></canvas>{SKYLINE}
<div class="wrap">
<span class="eyebrow">Thursday 31 December {Y} · Gold Coast, Queensland</span>
<h1>New Year's Eve Gold Coast {Y}<br><span class="grad">fireworks, parties &amp; dinners</span></h1>
<p class="lead">The best NYE events on the Gold Coast in one place: free beach fireworks, Broadwater cruises, beachfront dinners and rooftop parties. Compare, choose and book your night to welcome {NY}.</p>
{countdown()}
<p class="cd-note">until the midnight fireworks over Surfers Paradise (AEST)</p>
<div class="cta-row"><a class="btn btn-primary" href="#directory">Browse {n} NYE events</a><a class="btn btn-ghost" href="/gold-coast-fireworks-locations/">Free fireworks locations</a></div>
</div></section>

<div class="wrap"><div class="facts">
<div class="fact"><b>8:00pm</b><span>Family fireworks at Surfers Paradise &amp; Broadbeach (2025)</span></div>
<div class="fact"><b>Midnight</b><span>Main fireworks over the beach, Queensland time</span></div>
<div class="fact"><b>10+</b><span>free fireworks locations across the city</span></div>
<div class="fact"><b>{n}</b><span>dinners, cruises, parties &amp; free events listed</span></div>
</div></div>

{directory(ordered, f"Every Gold Coast NYE {Y} event in one directory", "Filter by type, area or budget. Every listing shows what's included, which fireworks you'll see and a direct booking link.")}

{list_band()}

<section class="alt"><div class="wrap two">
<div><h2>Your Gold Coast NYE {Y}, <span class="grad">hour by hour</span></h2>
<p class="muted">Timings are based on the City of Gold Coast's 2025 program and recent years. The {Y} program is usually confirmed in December. Use this to plan when to arrive, eat and move.</p>
<a class="btn btn-ghost" href="/plan-your-night/">Full planning guide →</a></div>
{timeline_html()}
</div></section>

<section><div class="wrap">
<div class="section-head"><h2>Gold Coast fireworks locations</h2><p>Where to watch the free New Year's Eve fireworks on the Gold Coast, from Surfers Paradise beach to the Broadwater, with times and what you need to know.</p></div>
{vantage_table(VANTAGE[:8])}
<p style="text-align:center;margin-top:24px"><a class="btn btn-ghost" href="/gold-coast-fireworks-locations/">See all fireworks locations →</a></p>
</div></section>

<section class="alt"><div class="wrap">
<div class="section-head"><h2>Find your kind of NYE</h2></div>
<div class="grid">
<div class="card"><h3><a href="/new-years-eve-dinner-gold-coast/">🍽️ NYE dinners on the Gold Coast</a></h3><p>From $99 early banquets to $550 oceanfront seafood feasts at Burleigh.</p><a href="/new-years-eve-dinner-gold-coast/">Browse dinners →</a></div>
<div class="card"><h3><a href="/new-years-eve-cruises-gold-coast/">🛥️ Broadwater NYE cruises</a></h3><p>Family cruises for the 8pm show and adults-only party boats for midnight.</p><a href="/new-years-eve-cruises-gold-coast/">Browse cruises →</a></div>
<div class="card"><h3><a href="/new-years-eve-parties-gold-coast/">🎉 NYE parties &amp; rooftops</a></h3><p>SkyPoint, Surfers Paradise beach clubs, Burleigh Pavilion and The Star.</p><a href="/new-years-eve-parties-gold-coast/">Browse parties →</a></div>
<div class="card"><h3><a href="/family-new-years-eve-gold-coast/">👨‍👩‍👧 Family-friendly NYE</a></h3><p>8pm fireworks, free community events, family cruises and early sittings.</p><a href="/family-new-years-eve-gold-coast/">Browse family events →</a></div>
</div></div></section>

<section id="faq"><div class="wrap">
<div class="section-head"><h2>New Year's Eve Gold Coast {Y}: FAQ</h2></div>
<div class="faq">{faq_html(FAQ)}</div>
</div></section>
"""
    return layout(
        "/",
        f"New Year's Eve Gold Coast {Y}: Fireworks, Events & Parties | NYE in Gold Coast",
        f"Plan New Year's Eve {Y} on the Gold Coast: live countdown, fireworks times and locations (8pm & midnight), plus {n} NYE dinners, Broadwater cruises, parties and free family events.",
        body,
        schema=[item_list(ordered, f"Gold Coast New Year's Eve {Y} events"), faq_schema(FAQ),
                {"@context": "https://schema.org", "@type": "Organization", "name": CONFIG["site_name"], "url": URL + "/",
                 "logo": URL + "/favicon.svg", "email": CONFIG["contact_email"]}],
    )


CATEGORY_PAGES = [
    {
        "path": "/new-years-eve-dinner-gold-coast/",
        "filter": lambda e: "dining" in e["categories"] or "fine-dining" in e["categories"],
        "title": f"NYE Dinner Gold Coast {Y}: New Year's Eve Restaurants & Set Menus",
        "h1": f"New Year's Eve dinners on the Gold Coast {Y}",
        "desc": f"The best New Year's Eve dinners on the Gold Coast for {Y}: beachfront restaurants in Burleigh, Broadbeach and Main Beach, NYE set menus and early family sittings, with prices and booking links.",
        "intro": "A table with a view of the ocean or the Broadwater is the most relaxed way to see in the new year on the Gold Coast. Early sittings usually finish in time for the 8pm fireworks and suit families, while late sittings come with drinks packages that run past midnight.",
        "tips": ["Book early. Beachfront tables at Burleigh and Main Beach sell out by December.", "Early sittings ($99–$220 in 2025) are the best value and often have child pricing.", "Check whether the restaurant can actually see a fireworks display. Burleigh had no council show in 2025.", "Use the free late-night public transport (offered in 2025) rather than driving."],
    },
    {
        "path": "/new-years-eve-cruises-gold-coast/",
        "filter": lambda e: "cruise" in e["categories"],
        "title": f"New Year's Eve Cruise Gold Coast {Y}: Broadwater Fireworks Cruises",
        "h1": f"Gold Coast New Year's Eve cruises {Y}",
        "desc": f"Compare New Year's Eve cruises on the Gold Coast Broadwater for {Y}: family fireworks cruises for 8pm and adults-only midnight party boats from Southport, Surfers Paradise and Main Beach.",
        "intro": "The Broadwater is calm, sheltered and close to the fireworks, which makes a cruise one of the best ways to see in the new year on the Gold Coast. You can choose an early family cruise for the 8pm show or an adults-only party boat with drinks and canapés for midnight.",
        "tips": ["Choose your show: family cruises are timed for 8pm, party cruises for midnight.", "Check where you board. Departures are from Southport, Surfers Paradise and Main Beach.", "Most midnight cruises are 18+ and need photo ID.", "Cruises sell out. YOT Club's 2025 White Party sold out before the night."],
    },
    {
        "path": "/new-years-eve-parties-gold-coast/",
        "filter": lambda e: "party" in e["categories"] or "rooftop" in e["categories"],
        "title": f"NYE Parties Gold Coast {Y}: Best New Year's Eve Parties & Rooftops",
        "h1": f"The best New Year's Eve parties on the Gold Coast {Y}",
        "desc": f"The Gold Coast's best New Year's Eve parties for {Y}: SkyPoint, Surfers Paradise beach clubs, rooftops, Burleigh Pavilion and The Star, with prices, inclusions and tickets.",
        "intro": "From Level 77 of Q1 to the beach bars of Burleigh and Kirra, these are the best NYE parties on the Gold Coast. Surfers Paradise has the most choice within walking distance of the midnight fireworks, while Burleigh and Mermaid Beach lean to rooftops and beach clubs.",
        "tips": ["First-release tickets are the cheapest, so buy early.", "Check whether drinks are included or pay as you go.", "Most parties are 18+, and Surfers Paradise and Broadbeach venues scan ID late at night.", "If the fireworks matter, pick a venue near Surfers Paradise, Broadbeach or Coolangatta."],
    },
    {
        "path": "/family-new-years-eve-gold-coast/",
        "filter": lambda e: "family" in e["categories"] or "vantage" in e["categories"],
        "title": f"Family New Year's Eve Gold Coast {Y}: Kid-Friendly NYE & 8pm Fireworks",
        "h1": f"Family-friendly New Year's Eve on the Gold Coast {Y}",
        "desc": f"Kid-friendly ways to celebrate New Year's Eve {Y} on the Gold Coast: free 8pm fireworks, alcohol-free community events, family cruises and restaurants with early sittings.",
        "intro": "The Gold Coast is one of the easiest places in Australia for a family New Year's Eve. The City of Gold Coast runs free early fireworks across the city, and several community events have food trucks, rides and kids activities, so you can see a full show and be home before midnight.",
        "tips": ["Aim for an 8pm display with younger kids.", "Broadwater Parklands is an alcohol-free family event, a good choice for little ones.", "Pack hats, sunscreen, water, a picnic rug and ear protection.", "Agree on a meeting point in case anyone gets separated."],
    },
]

def page_category(c):
    events = [e for e in EVENTS if c["filter"](e)]
    events.sort(key=lambda e: (not e.get("featured"), e["price_from"] if e["price_from"] is not None else 1e9))
    tips = "".join(f"<li>{t}</li>" for t in c["tips"])
    body = f"""
<section class="hero small"><canvas id="fw" aria-hidden="true"></canvas>{SKYLINE}
<div class="wrap"><span class="eyebrow">NYE {Y} · Gold Coast</span><h1>{c['h1']}</h1>
<p class="lead">{c['intro']}</p>{countdown(mini=True)}</div></section>
<section style="padding-bottom:0"><div class="wrap two">
<div class="panel"><h2 style="font-size:1.5rem">Booking tips</h2><ul class="ticks">{tips}</ul></div>
<div><h2 style="font-size:1.5rem">{len(events)} options, compared</h2><p class="muted">Every listing shows a "from" price, what's included and which fireworks you'll see. Prices are per person and based on published packages, so always confirm the current price with the venue.</p>
<a class="btn btn-primary" href="/list-your-event/">Add your venue: ${CONFIG['listing_price']}</a></div>
</div></section>
{directory(events, c['h1'], 'Filter and sort to find your night.')}
{list_band()}"""
    return layout(
        c["path"], c["title"] + " | NYE in Gold Coast", c["desc"], body,
        schema=[item_list(events, c["h1"]), breadcrumbs(("Home", "/"), (c["h1"], c["path"]))],
    )


def page_event(e):
    path = f"/events/{e['slug']}/"
    inc = "".join(f"<li>{escape(x)}</li>" for x in e["includes"])
    cats = ", ".join(CATEGORY_LABELS.get(c, c) for c in e["categories"])
    related = [x for x in EVENTS if x["slug"] != e["slug"] and (x["area"] == e["area"] or set(x["categories"]) & set(e["categories"]))][:3]
    offer = {"@type": "Offer", "url": e["url"], "priceCurrency": "AUD", "availability": "https://schema.org/InStock",
             "validFrom": f"{Y}-01-01"}
    if e["price_from"] is not None:
        offer["price"] = e["price_from"]
    schema = {
        "@context": "https://schema.org",
        "@type": "Event",
        "name": f"{e['name']} – New Year's Eve {Y}",
        "description": e["blurb"] + " Includes: " + "; ".join(e["includes"]) + ".",
        "startDate": f"{Y}-12-31",
        "endDate": f"{NY}-01-01",
        "eventStatus": "https://schema.org/EventScheduled",
        "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
        "image": [f"{URL}/og.png"],
        "location": {
            "@type": "Place", "name": e["venue"],
            "address": {"@type": "PostalAddress", "addressLocality": e["suburb"], "addressRegion": "QLD", "addressCountry": "AU"},
        },
        "organizer": {"@type": "Organization", "name": e["venue"].split(",")[0], "url": e["url"]},
        "offers": offer,
    }
    body = f"""
<section class="event-hero"><div class="wrap">
<nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> › <a href="/#directory">NYE events</a> › {escape(e['name'])}</nav>
<span class="eyebrow">New Year's Eve {Y} · {escape(e['suburb'])}</span>
<h1 style="font-size:clamp(2rem,5vw,3.4rem)">{escape(e['name'])}</h1>
<p class="lead muted" style="font-size:1.15rem;max-width:760px">{escape(e['blurb'])}</p>
</div></section>
<section style="padding-top:10px"><div class="wrap event-layout">
<div>
<div class="panel"><h2 style="font-size:1.5rem">What's included</h2><ul class="ticks">{inc}</ul></div>
<div class="prose" style="margin-top:30px">
<h2 style="font-size:1.5rem">About {escape(e['name'])}</h2>
<p>{escape(e['name'])} is at {escape(e['venue'])} in {escape(e['suburb'])} ({escape(e['area'])}). It's one of the {escape(cats.lower())} options for New Year's Eve {Y} on the Gold Coast. Fireworks: <b>{escape(e['fireworks'])}</b>. Age: <b>{escape(e['age'])}</b>.</p>
<p>Planning the rest of your night? Check the <a href="/plan-your-night/">fireworks times and transport tips</a> or compare <a href="/gold-coast-fireworks-locations/">free fireworks locations across the Gold Coast</a>.</p>
<p class="notice">Details are based on the venue's most recently published NYE information (often from {Y - 1}) and can change. Confirm the price, times and inclusions with {escape(e['venue'].split(',')[0])} before booking. Are you the venue? <a href="/list-your-event/">Claim and upgrade this listing</a>.</p>
</div></div>
<aside class="side panel">
<div class="price" style="font-size:2rem">{"Free" if e['price_from']==0 else money(e['price_from']) if e['price_from'] else "TBA"}<small>{escape(e['price_text'])}</small></div>
<dl><dt>Date</dt><dd>Thursday 31 December {Y}</dd><dt>Time</dt><dd>{escape(e['time'])}</dd>
<dt>Where</dt><dd>{escape(e['venue'])}</dd><dt>Fireworks</dt><dd>🎆 {escape(e['fireworks'])}</dd><dt>Age</dt><dd>{escape(e['age'])}</dd></dl>
<a class="btn btn-primary" style="width:100%;justify-content:center" href="{e['url']}" target="_blank" rel="noopener sponsored">Book with the venue →</a>
<div style="margin-top:20px">{countdown(mini=True)}</div>
</aside>
</div></section>
<section class="alt"><div class="wrap"><div class="section-head"><h2>You might also like</h2></div>
<div class="grid">{''.join(card(x, i) for i, x in enumerate(related))}</div></div></section>
{list_band()}"""
    return layout(
        path,
        (f"{e['name']} {Y}" if "NYE" in e["name"] or "New Year" in e["name"] else f"{e['name']} NYE {Y}")
        + f" – {e['suburb']} | NYE in Gold Coast",
        f"{e['name']} New Year's Eve {Y} in {e['suburb']}: {e['price_text']}. {e['blurb']}"[:300],
        body, og_type="article", active="/#directory",
        schema=[schema, breadcrumbs(("Home", "/"), ("NYE events", "/#directory"), (e["name"], path))],
    )


def page_vantage():
    vp = [e for e in EVENTS if "vantage" in e["categories"]]
    faq = FAQ[1:3] + FAQ[5:6] + FAQ[7:8] + FAQ[11:12]
    body = f"""
<section class="hero small"><canvas id="fw" aria-hidden="true"></canvas>{SKYLINE}
<div class="wrap"><span class="eyebrow">NYE {Y} · Free fireworks</span>
<h1>Gold Coast fireworks locations, New Year's Eve {Y}</h1>
<p class="lead">Where to watch the Gold Coast New Year's Eve fireworks: Surfers Paradise beach, Kurrawa Park in Broadbeach, Coolangatta and the Broadwater, plus the early 8pm family shows. All free, with times and tips for each spot.</p></div></section>
<section><div class="wrap">
<div class="section-head"><h2>Fireworks locations at a glance</h2><p>Times are from the City of Gold Coast's 2025 program and community event organisers. The {Y} program is usually announced in December, so check official updates before you go.</p></div>
{vantage_table()}
</div></section>
{directory(vp, "Free NYE fireworks events", "Free community celebrations with fireworks, food trucks and family entertainment. No tickets needed.", show_filters=False)}
<section class="alt"><div class="wrap prose">
<h2>How to choose where to watch</h2>
<p><b>For the big night</b>, Surfers Paradise beach has both shows, the biggest crowd and dozens of bars and restaurants behind the sand. Catch the G:link to Cypress Avenue, Cavill Avenue or Surfers Paradise station.</p>
<p><b>For more space</b>, Kurrawa Park in Broadbeach has the same 8pm and midnight shows with grass to spread out on, and Coolangatta Beach is the laid-back southern option at 9pm and midnight.</p>
<p><b>With kids</b>, choose an early show: Broadwater Parklands and Coomera at 8pm, Varsity Lakes at 8:30pm or Paradise Point at 9pm. Broadwater Parklands is alcohol-free.</p>
<p><b>For a guaranteed view without the crowd</b>, book a <a href="/new-years-eve-cruises-gold-coast/">Broadwater cruise</a>, a beachfront bar on the Esplanade or a spot at SkyPoint, 230 metres above Surfers Paradise.</p>
<h2>What to bring</h2>
<ul><li>Picnic rug or low beach chair</li><li>Water, snacks, hats and sunscreen for the afternoon</li><li>Charged phone and a power bank</li><li>Insect repellent for the parklands</li><li>No glass and no alcohol on the beach or in public parks</li></ul>
</div></section>
<section id="faq"><div class="wrap"><div class="section-head"><h2>Fireworks FAQ</h2></div><div class="faq">{faq_html(faq)}</div></div></section>
{list_band()}"""
    return layout(
        "/gold-coast-fireworks-locations/",
        f"Gold Coast Fireworks New Year's Eve {Y}: Locations & Times | NYE in Gold Coast",
        f"Where to watch the Gold Coast New Year's Eve fireworks in {Y}: Surfers Paradise, Broadbeach, Coolangatta, Broadwater Parklands and more, with 8pm, 9pm and midnight times and arrival tips.",
        body, schema=[faq_schema(faq), item_list(vp, "Free Gold Coast NYE fireworks events"),
                      breadcrumbs(("Home", "/"), ("Fireworks locations", "/gold-coast-fireworks-locations/"))],
    )


def page_plan():
    faq = [FAQ[0], FAQ[6], FAQ[7], FAQ[8], FAQ[11]]
    body = f"""
<section class="hero small"><canvas id="fw" aria-hidden="true"></canvas>{SKYLINE}
<div class="wrap"><span class="eyebrow">Planning guide</span>
<h1>Plan your Gold Coast NYE {Y}</h1>
<p class="lead">Fireworks times, the run sheet for the night, getting there on the G:link and buses, road closures, alcohol rules, accessibility and what to bring.</p>
{countdown(mini=True)}</div></section>
<section><div class="wrap two" style="align-items:start">
<div><h2>Fireworks times &amp; the night's schedule</h2><p class="muted">Times are based on the 2025 program. The City of Gold Coast usually publishes the final {Y} program in December. All times are Queensland time (AEST, no daylight saving).</p></div>
{timeline_html()}
</div></section>
<section class="alt" id="transport"><div class="wrap prose">
<h2>Getting there: public transport</h2>
<p>Public transport is the easiest way to get to the beach on New Year's Eve. In 2025 the Queensland Government made all Translink services free from 8pm on New Year's Eve until 5:30am on New Year's Day, with 50 cent fares at other times. The G:link light rail ran every 7–8 minutes through the night and extra buses ran across the Gold Coast.</p>
<ul><li>Plan your trip on <a href="https://translink.com.au" rel="noopener" target="_blank">translink.com.au</a> and check the {Y} New Year's Eve arrangements in December.</li>
<li>For Surfers Paradise, use the G:link stations at Cypress Avenue, Cavill Avenue or Surfers Paradise. For Broadbeach, use Broadbeach North or Broadbeach South.</li>
<li>For Coomera, the 2025 Park &amp; Ride ran from Dreamworld with buses every 10 minutes between 5pm and 9:30pm.</li>
<li>After midnight, expect queues at the tram stops. Taxis and rideshare are available but in high demand, with surge pricing.</li></ul>
<h2 id="roads">Road closures &amp; driving</h2>
<p>In recent years The Esplanade in Surfers Paradise (between the Peppers Soul and Hanlan Street roundabouts) and Orchid Avenue closed to traffic from 6pm on 31 December until 4am on 1 January, with detours via Staghorn Avenue and Clifford Street. Parking near the beach fills early. If you drive, park further out, for example in Southport, and take the G:link in. Check the City of Gold Coast and Queensland Police for {Y} closures.</p>
<h2 id="alcohol">Alcohol &amp; safety rules</h2>
<p>Drinking alcohol in public places, including beaches, the foreshore and parks, is generally not allowed in Queensland, and there is a large police presence on New Year's Eve. Glass is not allowed on the beach. Council family events like New Year's Eve by the Sea at Broadwater Parklands are alcohol-free. Surfers Paradise and Broadbeach are Safe Night Precincts, where many late-night venues scan ID on entry, so bring photo ID if you're heading out.</p>
<h2 id="boating">Boating on the Broadwater</h2>
<p>The Broadwater is busy on New Year's Eve. Private boats must follow Maritime Safety Queensland rules, keep clear of fireworks barges and have a sober skipper. For most people a licensed <a href="/new-years-eve-cruises-gold-coast/">NYE cruise</a> is the easiest way to see the show from the water.</p>
<h2 id="accessibility">Accessibility</h2>
<p>The G:link is step-free at every station, and the Surfers Paradise and Broadbeach foreshores have paved paths close to the sand. Beach viewing on soft sand can be hard going, so the Esplanade path and Kurrawa Park are better options for wheelchairs and prams. Many venues in our directory have step-free access. Contact the venue to confirm.</p>
<h2>Safety &amp; wellbeing</h2>
<ul><li>Drink plenty of water. It's usually hot and humid in late December.</li><li>Agree on a meeting point with your group.</li><li>Swim only between the flags, and never swim at night after the lifeguards have gone.</li><li>Keep pets inside and secure. Fireworks scare animals.</li><li>Follow police and staff directions, and look after your mates.</li></ul>
</div></section>
<section id="faq"><div class="wrap"><div class="section-head"><h2>Planning FAQ</h2></div><div class="faq">{faq_html(faq)}</div></div></section>
{list_band()}"""
    return layout(
        "/plan-your-night/",
        f"Gold Coast NYE {Y} Fireworks Times, Transport & Road Closures | NYE in Gold Coast",
        f"Gold Coast New Year's Eve {Y} planning guide: 8pm, 9pm and midnight fireworks times, free public transport and G:link, Surfers Paradise road closures, alcohol rules and what to bring.",
        body, schema=[faq_schema(faq), breadcrumbs(("Home", "/"), ("Plan your night", "/plan-your-night/"))],
    )


def page_list():
    p = CONFIG["listing_price"]
    has_pay = "YOUR_" not in CONFIG["payment_link"]
    form_sub = (f"Fill this in, then pay ${p} securely. We'll publish your page and email you the link." if has_pay
                else f"Fill this in and we'll email you a ${p} invoice within one business day. Your page goes live once it's paid.")
    submit_label = f"Continue to payment: ${p} →" if has_pay else "Send my listing request →"
    cats = "".join(f'<option value="{k}">{v}</option>' for k, v in CATEGORY_LABELS.items() if k not in ("budget", "free"))
    faq = [
        ("What do I get for $" + str(p) + "?", "A dedicated event page built for search, with Google Event structured data. You also get a listing in our main directory and the matching category pages (dinners, cruises, parties, family), a direct link to your own booking page, and edits until 31 December."),
        ("Why should I list now rather than in December?", "Search interest in Gold Coast New Year's Eve builds from October and peaks in the final weeks of December. Listing early means your page is live and indexed by Google for the whole season, not just the last-minute rush. New pages can take days or weeks to rank, so the earlier you're in, the more of the season you capture. It's the same $" + str(p) + " whenever you list."),
        ("Do you take commission on bookings?", "No. Guests book directly with you through your own link, and you keep 100% of every ticket."),
        ("How long does my listing stay live?", f"Your listing stays live until New Year's Day {NY}, then rolls into our archive. Previous listers get first right to renew for next year."),
        ("How fast will my listing go live?", "Usually within one business day of payment. We'll email you the link."),
        ("Can I update prices or details?", "Yes. Email us any changes (sold-out tiers, price releases, new acts) and we'll update your page."),
    ]
    body = f"""
<section class="hero small"><canvas id="fw" aria-hidden="true"></canvas>{SKYLINE}
<div class="wrap"><span class="eyebrow">For venues, promoters &amp; cruise operators</span>
<h1>List your New Year's Eve event</h1>
<p class="lead">October, November and December are when locals and holidaymakers search for their Gold Coast New Year's Eve plans. Put your NYE {Y} event in front of people typing "New Year's Eve Gold Coast", "NYE Gold Coast", "NYE dinner Gold Coast" and "New Year's Eve cruise Gold Coast" while they're choosing where to spend the night.</p>
{countdown(mini=True)}
<p class="cd-note" style="margin-top:0">left to sell. The NYE search season is on now.</p>
<div class="cta-row"><a class="btn btn-primary" href="#form">List my event: ${p}</a><a class="btn btn-ghost" href="#season">Why now?</a></div></div></section>
{season_section(p)}
<section><div class="wrap two" style="align-items:start">
<div>
<h2>Why list with <span class="grad">NYE in Gold Coast</span>?</h2>
<ul class="ticks">
<li><b>High-intent visitors.</b> People only visit a NYE guide when they're about to book.</li>
<li><b>Your own SEO page.</b> Each event gets a dedicated page with Google Event schema, which can make it eligible for event rich results.</li>
<li><b>Listed where people browse.</b> You appear in the main directory plus every matching category: dinners, cruises, parties and family.</li>
<li><b>Zero commission.</b> Guests click straight through to your booking page.</li>
<li><b>Updates until NYE.</b> Change prices, add tiers or mark sold-out tiers whenever you like.</li>
<li><b>Our name is the search.</b> NYE in Gold Coast is built around the exact phrases people type into Google, so every page targets them.</li>
<li><b>Countdown traffic.</b> Interest builds from October and peaks in December, right when you're selling.</li>
</ul>
</div>
<div class="pricing">
<span class="eyebrow">NYE {Y} listing</span>
<div class="amount"><sup>$</sup>{p}</div>
<p class="muted">AUD inc GST · one-off · no commission</p>
<ul class="ticks">
<li>Dedicated event page + Google Event schema</li>
<li>Directory &amp; category page placement</li>
<li>Direct "Book" button to your site</li>
<li>Unlimited edits until 31 Dec {Y}</li>
<li>Live within 1 business day</li>
</ul>
<a class="btn btn-primary" href="#form" style="width:100%;justify-content:center">List my event →</a>
</div>
</div></section>
<section class="alt" id="form"><div class="wrap" style="max-width:860px">
<div class="section-head"><h2>Your event details</h2><p>{form_sub}</p></div>
<form class="listing panel" data-endpoint="{CONFIG['form_endpoint']}" data-payment="{CONFIG['payment_link']}" data-email="{CONFIG['contact_email']}">
<div><label for="f-name">Event name *</label><input id="f-name" name="event_name" required></div>
<div><label for="f-venue">Venue *</label><input id="f-venue" name="venue" required></div>
<div><label for="f-suburb">Suburb *</label><input id="f-suburb" name="suburb" required></div>
<div><label for="f-cat">Type *</label><select id="f-cat" name="category" required>{cats}</select></div>
<div><label for="f-price">Price from (AUD pp)</label><input id="f-price" name="price_from" inputmode="decimal" placeholder="e.g. 249"></div>
<div><label for="f-time">Times</label><input id="f-time" name="times" placeholder="e.g. 7pm – 1am"></div>
<div><label for="f-fw">Fireworks view</label><select id="f-fw" name="fireworks"><option>Both 8pm &amp; midnight</option><option>Midnight only</option><option>Early show only (8pm or 9pm)</option><option>Partial / nearby</option><option>No view</option></select></div>
<div><label for="f-age">Age</label><select id="f-age" name="age"><option>18+</option><option>All ages</option><option>Family-friendly</option></select></div>
<div class="full"><label for="f-url">Booking URL *</label><input id="f-url" name="booking_url" type="url" required placeholder="https://"></div>
<div class="full"><label for="f-desc">Description &amp; inclusions *</label><textarea id="f-desc" name="description" required placeholder="What makes your night special? Food, drinks, DJs, views…"></textarea></div>
<div><label for="f-contact">Contact name *</label><input id="f-contact" name="contact_name" required></div>
<div><label for="f-email">Email *</label><input id="f-email" name="email" type="email" required></div>
<div><label for="f-phone">Phone</label><input id="f-phone" name="phone" type="tel"></div>
<div><label for="f-abn">Business / ABN</label><input id="f-abn" name="business"></div>
<input type="hidden" name="_subject" value="New NYE in Gold Coast listing request (${p})">
<input type="hidden" name="_template" value="table"><input type="text" name="_honey" style="display:none" tabindex="-1" autocomplete="off" aria-hidden="true">
<div class="full"><button class="btn btn-primary" type="submit">{submit_label}</button>
<p class="form-status muted" aria-live="polite" style="margin:12px 0 0"></p></div>
</form>
</div></section>
<section><div class="wrap"><div class="section-head"><h2>Listing FAQ</h2></div><div class="faq">{faq_html(faq)}</div></div></section>"""
    service = {
        "@context": "https://schema.org", "@type": "Service", "name": f"NYE {Y} event listing",
        "provider": {"@type": "Organization", "name": CONFIG["site_name"], "url": URL + "/"},
        "areaServed": "Gold Coast, QLD",
        "offers": {"@type": "Offer", "price": p, "priceCurrency": "AUD", "url": URL + "/list-your-event/"},
    }
    return layout(
        "/list-your-event/",
        f"List Your New Year's Eve Event on the Gold Coast – ${p} | NYE in Gold Coast",
        f"Promote your Gold Coast New Year's Eve {Y} party, dinner or cruise. ${p} flat fee, no commission: a dedicated SEO event page, directory placement and a direct booking link.",
        body, schema=[service, faq_schema(faq), breadcrumbs(("Home", "/"), ("List your event", "/list-your-event/"))],
    )


def page_404():
    body = f"""<section class="hero small"><canvas id="fw" aria-hidden="true"></canvas>{SKYLINE}<div class="wrap">
<h1>This page fizzled out</h1><p class="lead">The page you're after isn't here, but the fireworks still are.</p>{countdown()}
<div class="cta-row"><a class="btn btn-primary" href="/">Back to all NYE events</a></div></div></section>"""
    return layout("/404.html", "Page not found | NYE in Gold Coast", "Page not found.", body).replace(
        'content="index,follow', 'content="noindex,follow')


FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#07061a"/><g stroke-linecap="round" stroke-width="4"><path d="M32 32 32 8" stroke="#ffc94d"/><path d="M32 32 53 20" stroke="#ff4fa3"/><path d="M32 32 53 44" stroke="#8b5cff"/><path d="M32 32 32 56" stroke="#41e3ff"/><path d="M32 32 11 44" stroke="#ffc94d"/><path d="M32 32 11 20" stroke="#ff4fa3"/></g><circle cx="32" cy="32" r="5" fill="#fff"/></svg>"""

OG_HTML = f"""<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@500;700&family=Playfair+Display:wght@800&display=swap" rel="stylesheet">
<style>body{{margin:0;width:1200px;height:630px;background:radial-gradient(ellipse at 50% 120%,#2a1a6b,transparent 60%),radial-gradient(ellipse at 85% 0%,#3a0f4d,transparent 55%),#07061a;color:#fff;font-family:Inter,sans-serif;position:relative;overflow:hidden}}
.t{{position:absolute;left:70px;top:90px;right:70px}}h1{{font-family:'Playfair Display',serif;font-size:96px;margin:0;line-height:1}}
.g{{background:linear-gradient(120deg,#ffc94d,#ff4fa3 50%,#8b5cff);-webkit-background-clip:text;color:transparent}}
p{{font-size:34px;color:#cfc9ff;margin:24px 0 0}}.b{{display:inline-block;margin-top:30px;padding:12px 26px;border-radius:99px;background:linear-gradient(120deg,#ffc94d,#ff4fa3);color:#14062b;font-weight:700;font-size:26px}}
.s{{position:absolute;bottom:0;left:0;width:100%}}.dot{{position:absolute;border-radius:50%}}</style></head><body>
<div class="t"><h1>NYE <span class="g">in Gold Coast</span></h1><p>Fireworks · Cruises · Dinners · Parties<br>New Year's Eve {Y} on the Gold Coast</p><span class="b">Countdown to {NY} →</span></div>
{SKYLINE.replace('class="skyline"', 'class="s"')}
<script>for(let k=0;k<4;k++){{const cx=830+k*95,cy=90+(k%2)*110,c=['#ffc94d','#ff4fa3','#8b5cff','#41e3ff'][k];for(let i=0;i<48;i++){{const a=i/48*6.283,r=30+Math.random()*40,d=document.createElement('div');d.className='dot';d.style.cssText=`left:${{cx+Math.cos(a)*r}}px;top:${{cy+Math.sin(a)*r}}px;width:4px;height:4px;background:${{c}};box-shadow:0 0 8px ${{c}}`;document.body.appendChild(d)}}}}</script>
</body></html>"""


def build():
    if OUT.exists():
        og_keep = (OUT / "og.png").read_bytes() if (OUT / "og.png").exists() else None
        shutil.rmtree(OUT)
    else:
        og_keep = None
    OUT.mkdir()
    pages = {"/": page_home(), "/gold-coast-fireworks-locations/": page_vantage(),
             "/plan-your-night/": page_plan(), "/list-your-event/": page_list()}
    for c in CATEGORY_PAGES:
        pages[c["path"]] = page_category(c)
    for e in EVENTS:
        pages[f"/events/{e['slug']}/"] = page_event(e)
    for path, html in pages.items():
        f = OUT / path.strip("/") / "index.html" if path != "/" else OUT / "index.html"
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(html)
    (OUT / "404.html").write_text(page_404())
    shutil.copy(ROOT / "src" / "style.css", OUT / "style.css")
    shutil.copy(ROOT / "src" / "main.js", OUT / "main.js")
    (OUT / "favicon.svg").write_text(FAVICON)
    (OUT / "og.html").write_text(OG_HTML)
    if og_keep:
        (OUT / "og.png").write_bytes(og_keep)
    (OUT / ".nojekyll").write_text("")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nDisallow: /og.html\n\nSitemap: {URL}/sitemap.xml\n")
    prio = lambda p: "1.0" if p == "/" else "0.6" if p.startswith("/events/") else "0.8"
    sm = "".join(
        f"<url><loc>{URL}{p}</loc><lastmod>{TODAY}</lastmod><changefreq>weekly</changefreq><priority>{prio(p)}</priority></url>\n"
        for p in pages
    )
    (OUT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{sm}</urlset>\n')
    print(f"Built {len(pages)} pages into {OUT}")


if __name__ == "__main__":
    build()
