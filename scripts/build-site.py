#!/usr/bin/env python3
"""Builds the static nosh7.com marketing site into ./site (no dependencies).

Run from the repo root:  python3 scripts/build-site.py
Facts (prices, calories, slots, delivery) come from bot-notes.md. If they change
there, change them in the PLANS / FACTS blocks below and rebuild.
"""
import html
import json
import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "site")
SITE = "https://nosh7.com"
LOGIN = "https://app.nosh7.com/customer.html"
ORDER = "https://start.nosh7.in"
PHONE = "+91 97129 89498"
PHONE_TEL = "+919712989498"
WHATSAPP = "https://wa.me/919712989498"
EMAIL = "07nosh@gmail.com"
FSSAI = "20723038000600"
ADDRESS = "5A Akshat Avenue, Ramdevnagar Road, Satellite, Ahmedabad, Gujarat 380015"
ZOMATO = "https://link.zomato.com/xqzv/rshare?id=4824355730563e1b"
SWIGGY = "https://www.swiggy.com/city/ahmedabad/nosh-7-vastrapur-rest1152457"
LASTMOD = "2026-10-08"

SLOTS = ["9:30 AM to 11:30 AM", "11:30 AM to 1:30 PM", "4:30 PM to 6:30 PM", "6:30 PM to 8:30 PM"]

# name, slug, track, calories, protein, trial, monthly, per-meal monthly, blurb
# Real customer reviews only. Paste them here exactly as customers wrote them:
# dict(name="Customer name", text="Review text", rating=5, source="Google", date="2026-09-01")
# The Reviews section on the home page appears only when this list is not empty.
REVIEWS = []

PLANS = [
    dict(name="Healthy Fresh", track="healthy-fresh", cal="about 425", protein="20g+", trial=1250, monthly=4999, per=200,
         trial_per=250, blurb="Balanced everyday food. High protein, high fibre, low carb.", img="plan-healthy-fresh.webp"),
    dict(name="Low Sugar", track="low-sugar", cal="about 425", protein="20g+", trial=1250, monthly=4999, per=200,
         trial_per=250, blurb="Diabetic friendly meals with controlled carbs and no added sugar.", page="/diabetic-friendly-meals-ahmedabad/"),
    dict(name="Weight Loss", track="weight-loss", cal="about 500", protein="30g+", trial=1445, monthly=5999, per=240,
         trial_per=289, blurb="Higher protein, low carb, with 50g paneer in every meal.", page="/weight-loss-meal-plan-ahmedabad/"),
    dict(name="Muscle Gain", track="high-protein", cal="about 575", protein="40g+", trial=1650, monthly=6999, per=280,
         trial_per=330, blurb="Our highest protein bowl, with 100g low-fat paneer.", page="/high-protein-meal-plan-ahmedabad/"),
    dict(name="Vegan", track="vegan", cal="about 420", protein="plant protein", trial=1445, monthly=5975, per=239,
         trial_per=289, blurb="100 percent plant based, no dairy, high fibre.", page="/vegan-meal-plan-ahmedabad/"),
    dict(name="Fruit Dish Pack", track="fruit-pack", cal="about 220", protein="n/a", trial=1250, monthly=5250, per=210,
         trial_per=250, blurb="Fresh cut seasonal fruit, no added sugar.", img="plan-fruit.webp"),
]

NAV = [("Plans", "/plans/"), ("Weight loss", "/weight-loss-meal-plan-ahmedabad/"),
       ("Diabetic friendly", "/diabetic-friendly-meals-ahmedabad/"), ("Delivery areas", "/delivery-areas-ahmedabad/"),
       ("FAQ", "/faq/"), ("Contact", "/contact/")]

E = html.escape


def rs(n):
    return "Rs " + format(n, ",")


def order_link(track=None):
    return ORDER + ("/?track=" + track if track else "")


FAQS = [
    ("What is NOSH7?",
     "NOSH7 is a pure vegetarian kitchen in Satellite, Ahmedabad that delivers fresh, healthy diet meals on subscription. "
     "Every meal is 400 to 450 grams, high in protein and fibre and low in carbs."),
    ("How much does a meal subscription cost?",
     "A trial is 5 meals and a month is 25 meals. Healthy Fresh and Low Sugar are Rs 1,250 for the trial and Rs 4,999 for a month "
     "(Rs 200 a meal). Weight Loss is Rs 1,445 and Rs 5,999. Muscle Gain is Rs 1,650 and Rs 6,999. Vegan is Rs 1,445 and Rs 5,975. "
     "The Fruit Dish Pack is Rs 1,250 and Rs 5,250. The longer the pack, the lower the price per meal."),
    ("Is NOSH7 pure vegetarian?",
     "Yes. It is a pure veg kitchen and we serve no non-vegetarian food at all. Vegan, Jain and Swaminarayan versions are also available."),
    ("Do you deliver Jain and Swaminarayan meals?",
     "Yes. Regular, Jain and Swaminarayan versions are available on most plans, and you choose at checkout. A Jain meal has no onion, garlic, "
     "ginger, beetroot, carrot, potato or mushroom. Jain is not offered on the Fruit Dish Pack."),
    ("Are the meals suitable for weight loss?",
     "Yes. The Weight Loss plan is about 500 calories with 30g+ protein, high fibre and low carbs, and includes 50g paneer. "
     "Most NOSH7 bowls are 380 to 450 calories, which makes them a complete low calorie meal."),
    ("Are the meals suitable for diabetics?",
     "The Low Sugar plan is made to be diabetic friendly: about 425 calories, 20g+ protein, high fibre and no added sugar. "
     "It is food, not medical advice, so please check with your doctor about your own diet."),
    ("Which areas of Ahmedabad do you deliver to?",
     "Delivery is free within 5 km of Iscon Cross Road, which covers Satellite, Prahlad Nagar, Bodakdev and Vastrapur. "
     "Beyond 5 km it is Rs 10 per km. Enter your address at start.nosh7.in and it confirms straight away whether we reach you."),
    ("What are the delivery timings?",
     "There are four slots every day: 9:30 to 11:30 AM, 11:30 AM to 1:30 PM, 4:30 to 6:30 PM and 6:30 to 8:30 PM. "
     "You choose your slot when you order."),
    ("Can I skip, pause or cancel a delivery?",
     "Yes, in the app, before the cut-off. The cut-off is 2 hours before your slot starts. Unused meals stay in your balance "
     "when a delivery is cancelled before the cut-off."),
    ("Can I choose or change the daily menu?",
     "The menu is fixed each day and we do not cook to order. A change is possible only if you tell us in advance, and a customisation "
     "costs Rs 49 per meal because that item is cooked, packed and handled separately."),
    ("What are the add-ons?",
     "Per meal: fruit bowl Rs 169, extra paneer 50g Rs 40 (+10g protein), paneer 100g Rs 80 (+20g protein), and a healthy drink for Rs 49 "
     "(ABC juice, mint lemonade, nimbu sharbat, chia fresca or green apple detox)."),
    ("How do I pay?",
     "UPI, card or netbanking at checkout. Cash on delivery is available on subscription plans only. Tell us in advance if you want to pay cash."),
    ("Is there a discount?",
     "Promo code HEALTHY gives Rs 150 off the trial plan. If you refer a friend, you get Rs 200 cashback in your wallet when they subscribe."),
    ("Do you offer single day orders?",
     "Subscriptions start at 5 meals. For a single day, order NOSH7 on Zomato or Swiggy."),
    ("Do you offer refunds?",
     "We do not offer refunds or returns. If something was wrong with a delivery, tell us and the team will look into it."),
    ("How do existing customers manage their plan?",
     "Use the Login button on this site. In the app you can see meals left, skip or cancel a delivery, pause and resume, renew, "
     "change address or slot, and download bills."),
]


def faq_html(items):
    return "".join(
        f'<details class="faq"><summary>{E(q)}</summary><p>{E(a)}</p></details>' for q, a in items)


def faq_schema(items):
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q,
                            "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in items]}


BUSINESS = {
    "@context": "https://schema.org", "@type": "Restaurant", "@id": SITE + "/#business",
    "name": "NOSH7", "url": SITE + "/", "logo": SITE + "/logo.png", "image": SITE + "/img/plan-healthy-fresh.webp",
    "description": "Pure vegetarian healthy meal subscription in Ahmedabad. Fresh, high protein, low carb diet meals delivered daily.",
    "telephone": PHONE_TEL, "email": EMAIL, "servesCuisine": ["Indian", "Healthy", "Vegetarian", "Vegan", "Jain"],
    "priceRange": "Rs 200 to Rs 280 per meal", "hasMenu": SITE + "/plans/",
    "address": {"@type": "PostalAddress", "streetAddress": "5A Akshat Avenue, Ramdevnagar Road, Satellite",
                "addressLocality": "Ahmedabad", "addressRegion": "Gujarat", "postalCode": "380015", "addressCountry": "IN"},
    "geo": {"@type": "GeoCoordinates", "latitude": 23.0299, "longitude": 72.5119},
    "areaServed": ["Satellite", "Prahlad Nagar", "Bodakdev", "Vastrapur", "Ahmedabad"],
    "identifier": {"@type": "PropertyValue", "name": "FSSAI licence", "value": FSSAI},
    "sameAs": ["https://nosh7.in", ZOMATO, SWIGGY],
    "alternateName": "NOSH7 (nosh7.in)",
}

CSS = """
:root{--lime:#bdec4f;--green:#159a52;--green-d:#0f7a40;--ink:#14210f;--muted:#566450;--bg:#f6f9ef;--card:#fff;--line:#e2e9d5;--r:16px}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink);font:17px/1.65 system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;-webkit-font-smoothing:antialiased}
img{max-width:100%;height:auto;display:block}
a{color:var(--green-d)}
.wrap{max-width:1080px;margin:0 auto;padding:0 20px}
header.top{background:#fff;border-bottom:1px solid var(--line);position:sticky;top:0;z-index:20}
.bar{display:flex;align-items:center;gap:18px;padding:10px 0}
.brand{display:flex;align-items:center;gap:10px;font-weight:800;font-size:22px;letter-spacing:-.02em;color:var(--ink);text-decoration:none}
.brand img{width:36px;height:36px;border-radius:8px}.brand b{color:var(--green)}
nav.main{display:flex;gap:4px;margin-left:auto;overflow-x:auto;scrollbar-width:none}
nav.main a{padding:8px 11px;border-radius:10px;color:var(--ink);text-decoration:none;font-weight:600;font-size:15px;white-space:nowrap}
nav.main a:hover{background:var(--bg)}
.btn{display:inline-block;padding:11px 20px;border-radius:12px;font-weight:700;text-decoration:none;font-size:16px;border:2px solid var(--ink);color:var(--ink);background:#fff}
.btn.pri{background:var(--lime);border-color:var(--lime)}.btn.pri:hover{filter:brightness(.95)}
.btn.sm{padding:8px 14px;font-size:14.5px}
.hero{padding:44px 0 36px;background:linear-gradient(180deg,#eaf3d3,var(--bg))}
.hero .grid{display:grid;grid-template-columns:1.15fr .85fr;gap:32px;align-items:center}
h1{font-size:clamp(30px,5vw,46px);line-height:1.12;margin:0 0 14px;letter-spacing:-.025em}
h2{font-size:clamp(24px,3.4vw,32px);line-height:1.2;margin:0 0 12px;letter-spacing:-.02em}
h3{font-size:19px;margin:0 0 6px}
.lead{font-size:19px;color:var(--muted);margin:0 0 20px}
.cta{display:flex;flex-wrap:wrap;gap:10px;margin:18px 0}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin:18px 0 0;padding:0;list-style:none}
.chips li{background:#fff;border:1px solid var(--line);border-radius:999px;padding:6px 13px;font-size:14.5px;font-weight:600}
.eyebrow{font-size:12px;letter-spacing:2.5px;text-transform:uppercase;font-weight:700;color:var(--muted);margin:0 0 8px}\n.accent{color:var(--green)}\na.track{text-decoration:none;color:inherit;display:block}a.track:hover{border-color:var(--green)}.go{font-weight:700;color:var(--green-d)}\n.certs{display:flex;gap:14px;align-items:center;flex-wrap:wrap}.certs h3{margin:0}.certs img{height:40px;width:auto;max-width:45%;flex:none}.certs>div{min-width:0}\n.heroimg{border-radius:24px;overflow:hidden;box-shadow:0 18px 40px rgba(70,90,30,.18);aspect-ratio:1/1;background:#fff}
.heroimg img{width:100%;height:100%;object-fit:cover}
section{padding:40px 0}section.alt{background:#fff;border-top:1px solid var(--line);border-bottom:1px solid var(--line)}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:16px}
.card{background:var(--card);border:1px solid var(--line);border-radius:var(--r);padding:20px}
.cards.four{grid-template-columns:repeat(auto-fit,minmax(230px,1fr))}\n.review{margin:0}.review blockquote{margin:8px 0;font-size:16px}.review figcaption{font-weight:700;font-size:14.5px}.stars{color:#e0a800;letter-spacing:2px}\n.card .price{font-size:26px;font-weight:800;letter-spacing:-.02em}.card .price small{font-size:14px;font-weight:600;color:var(--muted)}
.card ul{padding-left:18px;margin:8px 0}.card .meta{color:var(--muted);font-size:15px}
.steps{counter-reset:s;display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px;padding:0;list-style:none}
.steps li{counter-increment:s;background:var(--card);border:1px solid var(--line);border-radius:var(--r);padding:18px}
.steps li::before{content:counter(s);display:inline-grid;place-items:center;width:30px;height:30px;border-radius:50%;background:var(--lime);font-weight:800;margin-bottom:8px}
table{width:100%;border-collapse:collapse;background:#fff;border:1px solid var(--line);border-radius:12px;overflow:hidden;font-size:15.5px}
th,td{padding:11px 12px;border-bottom:1px solid var(--line);text-align:left}th{background:#f1f7e2}
.tw{overflow-x:auto}
details.faq{background:#fff;border:1px solid var(--line);border-radius:12px;padding:4px 16px;margin:10px 0}
details.faq summary{cursor:pointer;font-weight:700;padding:12px 0}details.faq p{margin:0 0 14px;color:#2b3a24}
.crumbs{font-size:14px;color:var(--muted);padding:16px 0 0}.crumbs a{color:var(--muted)}
.note{font-size:14px;color:var(--muted)}
.band{background:var(--ink);color:#fff;border-radius:24px;padding:32px;text-align:center}
.band h2{color:#fff}.band p{color:#cfd9c4}
footer{background:#10190c;color:#c6d1bb;padding:36px 0 26px;margin-top:40px;font-size:15px}
footer a{color:#e3efd2}footer h4{color:#fff;margin:0 0 8px}
footer .cols{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:24px}
footer ul{list-style:none;padding:0;margin:0}footer li{margin:5px 0}
.fine{border-top:1px solid #2a3822;margin-top:24px;padding-top:16px;font-size:13.5px}
@media(max-width:760px){.hero .grid{grid-template-columns:1fr}.heroimg{order:-1;aspect-ratio:16/10}.bar{flex-wrap:wrap}nav.main{order:3;width:100%;margin-left:0}.bar .actions{margin-left:auto}}
.actions{display:flex;gap:8px;margin-left:8px}
"""


def head(title, desc, path, extra_schema=None, og_img="/img/plan-healthy-fresh.webp"):
    url = SITE + path
    schemas = [BUSINESS] + (extra_schema or [])
    ld = "".join(f'<script type="application/ld+json">{json.dumps(s, ensure_ascii=False)}</script>' for s in schemas)
    return f"""<!doctype html>
<html lang="en-IN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#bdec4f">
<meta name="geo.region" content="IN-GJ"><meta name="geo.placename" content="Ahmedabad">
<meta property="og:type" content="website"><meta property="og:site_name" content="NOSH7">
<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{url}"><meta property="og:image" content="{SITE}{og_img}">
<meta property="og:locale" content="en_IN">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/svg+xml" href="/favicon.svg"><link rel="apple-touch-icon" href="/logo.png">
<link rel="stylesheet" href="/style.css">
{ld}
</head>
<body>
<header class="top"><div class="wrap bar">
<a class="brand" href="/"><img src="/logo.png" alt="NOSH7 logo" width="36" height="36"><span>NOSH<b>7</b></span></a>
<nav class="main" aria-label="Main">{"".join(f'<a href="{h}">{E(n)}</a>' for n, h in NAV)}</nav>
<div class="actions"><a class="btn sm" href="{LOGIN}" rel="nofollow">Login</a><a class="btn sm pri" href="{ORDER}">Order now</a></div>
</div></header>
<main>
"""


def foot():
    return f"""</main>
<footer><div class="wrap">
<div class="cols">
<div><h4>NOSH7</h4><p>Pure vegetarian healthy meal subscription in Ahmedabad. Fresh, high protein, low carb, delivered daily.</p>
<p>FSSAI Lic. No. {FSSAI}</p></div>
<div><h4>Meal plans</h4><ul>
<li><a href="/plans/">All plans and prices</a></li>
<li><a href="/weight-loss-meal-plan-ahmedabad/">Weight loss meals</a></li>
<li><a href="/diabetic-friendly-meals-ahmedabad/">Diabetic friendly meals</a></li>
<li><a href="/high-protein-meal-plan-ahmedabad/">High protein meals</a></li>
<li><a href="/vegan-meal-plan-ahmedabad/">Vegan meals</a></li>
<li><a href="/jain-meal-delivery-ahmedabad/">Jain meals</a></li></ul></div>
<div><h4>Delivery</h4><ul>
<li><a href="/delivery-areas-ahmedabad/">Delivery areas</a></li>
<li><a href="/healthy-tiffin-service-satellite-ahmedabad/">Satellite, Ahmedabad</a></li>
<li><a href="/faq/">FAQ</a></li><li><a href="/contact/">Contact</a></li></ul></div>
<div><h4>Contact</h4><ul>
<li><a href="tel:{PHONE_TEL}">{PHONE}</a></li>
<li><a href="{WHATSAPP}">WhatsApp us</a></li>
<li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
<li><a href="{LOGIN}" rel="nofollow">Customer login</a></li>
<li><a href="https://app.nosh7.com/privacy.html">Privacy policy</a></li></ul></div>
</div>
<div class="fine">NOSH7 is one business with two websites: <a href="https://nosh7.in">nosh7.in</a> and nosh7.com. Same kitchen, same plans, same team.<br>{E(ADDRESS)}. &copy; NOSH7. Meals are food, not medical advice.</div>
</div></footer>
</body></html>"""


def cta_band(title="Start with a 5 meal trial", text="Pick your plan and slot, check that we reach your address, and pay by UPI or card.", track=None):
    return f"""<section><div class="wrap"><div class="band"><h2>{E(title)}</h2><p>{E(text)}</p>
<div class="cta" style="justify-content:center"><a class="btn pri" href="{order_link(track)}">Order now</a>
<a class="btn" style="background:transparent;color:#fff;border-color:#fff" href="{LOGIN}" rel="nofollow">Existing customer? Login</a></div>
<p class="note" style="color:#aebca2">Promo code HEALTHY gives Rs 150 off the trial plan.</p></div></div></section>"""


def crumbs(*items):
    parts = ['<a href="/">Home</a>'] + [f'<a href="{h}">{E(n)}</a>' if h else E(n) for n, h in items]
    return f'<div class="wrap crumbs">{" / ".join(parts)}</div>'


def plan_card(p):
    link = p.get("page")
    more = f'<p><a href="{link}">More about {E(p["name"])}</a></p>' if link else ""
    return f"""<div class="card"><h3>{E(p["name"])}</h3><p class="meta">{E(p["blurb"])}</p>
<div class="price">{rs(p["monthly"])} <small>/ 25 meals ({rs(p["per"])} a meal)</small></div>
<p class="meta">5 meal trial {rs(p["trial"])} ({rs(p["trial_per"])} a meal)</p>
<p class="meta">{E(p["cal"])} calories, {E(p["protein"])} protein</p>
<a class="btn pri sm" href="{order_link(p["track"])}">Choose {E(p["name"])}</a>{more}</div>"""


def reviews_html():
    if not REVIEWS:
        return ""
    cards = "".join(
        f'<figure class="card review"><div class="stars" aria-label="{r["rating"]} out of 5">{"&#9733;" * int(r["rating"])}</div>'
        f'<blockquote>{E(r["text"])}</blockquote><figcaption>{E(r["name"])}'
        f'{" on " + E(r["source"]) if r.get("source") else ""}</figcaption></figure>' for r in REVIEWS)
    return f'<section class="alt"><div class="wrap"><h2>What our customers say</h2><div class="cards">{cards}</div></div></section>'


PAGES = {}


def add(path, title, desc, body, schema=None, og=None):
    PAGES[path] = (title, desc, body, schema or [], og)


# ---------------------------------------------------------------- home
TRACKS = [("Healthy Fresh", "healthy-fresh", "Balanced everyday meals"), ("Weight Loss", "weight-loss", "High protein, low carb"),
          ("Muscle Gain", "high-protein", "40g+ protein with paneer"), ("Low Sugar", "low-sugar", "Diabetic friendly"),
          ("Vegan", "vegan", "100% plant based"), ("Fruit Dish Pack", "fruit-pack", "Fresh cut seasonal fruit")]
BENEFITS = [("Cooked fresh every morning", "prepared daily in our Ahmedabad kitchen, never frozen"),
            ("High protein, fully balanced", "20g+ protein in every meal, high fiber, low carb"),
            ("Free delivery within 5 km", "small per-km charge beyond that, shown before you pay"),
            ("Regular and Jain options", "pick your preference while ordering, no extra cost")]
add("/", "NOSH7 | Healthy Meal Subscription in Ahmedabad | Pure Veg Diet Meals Delivered Daily",
    "Pure veg healthy meal subscription in Ahmedabad. High protein, low carb meals of 400 to 450 grams, delivered fresh daily from Satellite. "
    "Weight loss, diabetic friendly, vegan and Jain options. Trial from Rs 1,250.",
    f"""
<section class="hero"><div class="wrap grid"><div>
<p class="eyebrow">Fresh meal subscription, Ahmedabad</p>
<h1>Healthy meals, cooked <span class="accent">fresh daily</span></h1>
<p class="lead">Pick your meal track, choose a plan and slot, and we deliver fresh to your door across Ahmedabad. NOSH7 is a pure vegetarian kitchen in Satellite, and every meal is 400 to 450 grams.</p>
<div class="cta"><a class="btn pri" href="{ORDER}">Start your plan</a><a class="btn" href="{LOGIN}" rel="nofollow">Existing customer? Login</a></div>
<ul class="chips"><li>100% pure veg</li><li>FSSAI registered kitchen</li><li>Trial from Rs 1,250</li></ul>
</div><div class="heroimg"><img src="/img/plan-healthy-fresh.webp" width="600" height="600" alt="NOSH7 healthy meal bowl with brown rice, tofu, corn, broccoli and fresh salad"></div></div></section>

<section><div class="wrap"><h2>What are you eating for?</h2>
<div class="cards">{"".join(f'<a class="card track" href="{order_link(t)}"><h3>{E(n)}</h3><p class="meta">{E(d)}</p><span class="go">Choose</span></a>' for n, t, d in TRACKS)}</div>
<p class="note">Prices start at Rs 1,250 for a 5 meal trial and Rs 4,999 for 25 meals. <a href="/plans/">See all plans and prices</a>.</p></div></section>

<section class="alt"><div class="wrap"><div class="cards four">
{"".join(f'<div class="card"><h3>{E(t)}</h3><p class="meta">{E(d)}</p></div>' for t, d in BENEFITS)}</div></div></section>

{reviews_html()}
<section><div class="wrap"><div class="cards four">
<div class="card certs"><img src="/assets/fssai-logo.svg" alt="FSSAI logo" height="40"><div><h3>FSSAI Registered Kitchen</h3><p class="meta">Lic. No. {FSSAI}</p></div></div>
<div class="card certs"><img src="/assets/razorpay-logo.svg" alt="Razorpay logo" height="40"><div><h3>Payments by Razorpay</h3><p class="meta">100% secure, UPI, cards, netbanking</p></div></div>
<div class="card"><h3>Questions? Chat with us</h3><p class="meta">Call or WhatsApp {PHONE}</p><a class="btn sm" href="{WHATSAPP}">WhatsApp</a></div>
<div class="card"><h3>Same NOSH7, two websites</h3><p class="meta">nosh7.com and <a href="https://nosh7.in">nosh7.in</a> are the same business, run from one kitchen in Satellite.</p></div>
<div class="card"><h3>Already a customer?</h3><p class="meta">Skip, pause, renew, change your slot or address.</p><a class="btn pri sm" href="{LOGIN}" rel="nofollow">Login</a></div>
</div></div></section>
""", [{"@context": "https://schema.org", "@type": "WebSite", "name": "NOSH7", "url": SITE + "/"}])

# ---------------------------------------------------------------- plans
rows = "".join(
    f'<tr><td><strong>{E(p["name"])}</strong></td><td>{E(p["cal"])}</td><td>{E(p["protein"])}</td><td>{rs(p["trial"])}</td><td>{rs(p["monthly"])}</td><td>{rs(p["per"])}</td></tr>'
    for p in PLANS)
offers = [{"@context": "https://schema.org", "@type": "Product", "name": f'NOSH7 {p["name"]} meal plan (25 meals)',
           "description": p["blurb"], "brand": {"@type": "Brand", "name": "NOSH7"},
           "image": SITE + "/img/plan-healthy-fresh.webp",
           "offers": {"@type": "Offer", "priceCurrency": "INR", "price": str(p["monthly"]), "availability": "https://schema.org/InStock",
                      "url": order_link(p["track"])}} for p in PLANS]
add("/plans/", "Meal Plans and Prices | NOSH7 Healthy Meal Subscription Ahmedabad",
    "NOSH7 meal plan prices in Ahmedabad: Healthy Fresh, Low Sugar, Weight Loss, Muscle Gain, Vegan and Fruit Dish Pack. Trial of 5 meals from Rs 1,250, monthly 25 meals from Rs 4,999.",
    f"""{crumbs(("Plans", None))}
<section><div class="wrap"><h1>Meal plans and prices</h1>
<p class="lead">Every plan is pure vegetarian, 400 to 450 grams a meal and delivered fresh in the slot you choose. A trial is 5 meals. A month is 25 meals.</p>
<div class="tw"><table><thead><tr><th>Plan</th><th>Calories</th><th>Protein</th><th>5 meal trial</th><th>25 meals</th><th>Per meal (25)</th></tr></thead><tbody>{rows}</tbody></table></div>
<p class="note">Prices include the meal. Delivery is free within 5 km of Iscon Cross Road, then Rs 10 per km. Live prices are always at <a href="{ORDER}">start.nosh7.in</a>.</p></div></section>
<section class="alt"><div class="wrap"><h2>Pick a plan</h2><div class="cards">{"".join(plan_card(p) for p in PLANS)}</div></div></section>
<section><div class="wrap"><h2>Add-ons and extras</h2><ul>
<li>Fruit bowl: Rs 169 per meal</li><li>Extra paneer 50g: Rs 40 (+10g protein). Paneer 100g: Rs 80 (+20g protein)</li>
<li>Healthy drink: Rs 49 (ABC juice, mint lemonade, nimbu sharbat, chia fresca or green apple detox)</li>
<li>Menu customisation: Rs 49 per meal, with advance notice</li></ul>
<h2>Offers</h2><ul><li>Promo code <strong>HEALTHY</strong> gives Rs 150 off the trial plan.</li><li>Refer a friend: Rs 200 cashback to your wallet when they subscribe.</li></ul>
<h2>Just want one meal?</h2><p>Subscriptions start at 5 meals. For a single day, order on <a href="{ZOMATO}" rel="nofollow noopener">Zomato</a> or <a href="{SWIGGY}" rel="nofollow noopener">Swiggy</a>.</p></div></section>
{cta_band()}""", offers)


# ---------------------------------------------------------------- goal pages
def goal_page(path, title, desc, h1, lead, plan_name, sections, faqs, track):
    plan = next(p for p in PLANS if p["name"] == plan_name)
    secs = "".join(f"<h2>{E(h)}</h2>{b}" for h, b in sections)
    body = f"""{crumbs((h1, None))}
<section><div class="wrap"><h1>{E(h1)}</h1><p class="lead">{E(lead)}</p>
<div class="cta"><a class="btn pri" href="{order_link(track)}">Start the {E(plan_name)} plan</a><a class="btn" href="/plans/">Compare all plans</a></div>
<div class="cards" style="margin:18px 0">
<div class="card"><h3>{E(plan["cal"].title())} calories</h3><p class="meta">per meal</p></div>
<div class="card"><h3>{E(plan["protein"])} protein</h3><p class="meta">high fibre, low carb</p></div>
<div class="card"><h3>{rs(plan["monthly"])}</h3><p class="meta">25 meals, {rs(plan["per"])} a meal</p></div>
<div class="card"><h3>{rs(plan["trial"])}</h3><p class="meta">5 meal trial</p></div></div>
{secs}</div></section>
<section class="alt"><div class="wrap"><h2>Questions</h2>{faq_html(faqs)}</div></section>
{cta_band(track=track)}"""
    add(path, title, desc, body, [faq_schema(faqs)])


goal_page("/weight-loss-meal-plan-ahmedabad/",
          "Weight Loss Meal Plan in Ahmedabad | High Protein Low Carb Veg Meals | NOSH7",
          "Pure veg weight loss meal plan in Ahmedabad. About 500 calories, 30g+ protein, high fibre, low carb, with 50g paneer in every meal. Delivered fresh daily. Trial Rs 1,445.",
          "Weight loss meal plan in Ahmedabad",
          "Portion controlled, high protein vegetarian meals delivered to your door, so a calorie deficit does not mean starving or cooking twice.",
          "Weight Loss",
          [("What is in a Weight Loss meal", "<p>Each meal is about 500 calories with 30g or more of protein, high fibre and low carbs, and includes 50g of paneer. The bowl is 400 to 450 grams, so you stay full. The menu is fixed each day and sent on WhatsApp.</p>"),
           ("Who it is for", "<p>People who want to lose weight steadily with real food. If you train as well, you can add extra paneer (50g for Rs 40, +10g protein) to any meal, or move to the <a href=\"/high-protein-meal-plan-ahmedabad/\">Muscle Gain plan</a>.</p>"),
           ("Why meal delivery helps weight loss", "<ul><li>Fixed portions remove the daily guessing</li><li>High protein and fibre keep hunger down</li><li>Low carb, low oil cooking</li><li>No temptation to order out when you are tired</li></ul><p class=\"note\">Results depend on your overall diet, sleep and activity. This is food, not medical advice.</p>"),
           ("Price", f"<p>Trial of 5 meals: {rs(1445)} ({rs(289)} a meal). Monthly pack of 25 meals: {rs(5999)} ({rs(240)} a meal). Delivery is free within 5 km of Iscon Cross Road.</p>")],
          [FAQS[4], FAQS[1], FAQS[9]], "weight-loss")

goal_page("/diabetic-friendly-meals-ahmedabad/",
          "Diabetic Friendly Meals in Ahmedabad | Low Sugar Veg Meal Plan | NOSH7",
          "Low sugar, diabetic friendly vegetarian meals delivered daily in Ahmedabad. About 425 calories, 20g+ protein, high fibre, no added sugar. Trial Rs 1,250, monthly Rs 4,999.",
          "Diabetic friendly meals in Ahmedabad",
          "A low sugar vegetarian meal plan with controlled carbs, high fibre and steady protein, delivered fresh every day.",
          "Low Sugar",
          [("What is in a Low Sugar meal", "<p>About 425 calories, 20g or more of protein and high fibre, with no added sugar and low carbs. Bowls are 400 to 450 grams. The menu is fixed each day and sent on WhatsApp.</p>"),
           ("Why it suits people managing diabetes", "<ul><li>High fibre, low carb cooking</li><li>No added sugar in the meals</li><li>Consistent portions and timings from the slot you choose</li><li>Jain and Swaminarayan versions available</li></ul><p class=\"note\">NOSH7 meals are food, not medical advice. Please check with your doctor or dietitian about your own diet.</p>"),
           ("Price", f"<p>Trial of 5 meals: {rs(1250)} ({rs(250)} a meal). Monthly pack of 25 meals: {rs(4999)} ({rs(200)} a meal).</p>")],
          [FAQS[5], FAQS[3], FAQS[7]], "low-sugar")

goal_page("/high-protein-meal-plan-ahmedabad/",
          "High Protein Meal Plan in Ahmedabad | Pure Veg Muscle Gain Meals | NOSH7",
          "High protein vegetarian meal plan in Ahmedabad for muscle gain. About 575 calories, 40g+ protein with 100g low-fat paneer per meal, delivered fresh daily. Trial Rs 1,650.",
          "High protein meal plan in Ahmedabad",
          "Our highest protein bowl for people who train, built on low-fat paneer, so you can hit your protein without a non-veg diet.",
          "Muscle Gain",
          [("What is in a Muscle Gain meal", "<p>About 575 calories and 40g or more of protein, high fibre, with 100g of low-fat paneer in every bowl. Add another 50g or 100g of paneer for Rs 40 or Rs 80 per meal when you order.</p>"),
           ("Who it is for", "<p>Anyone lifting or training hard who is vegetarian. Not training for size? The <a href=\"/weight-loss-meal-plan-ahmedabad/\">Weight Loss plan</a> is lighter at about 500 calories.</p>"),
           ("Price", f"<p>Trial of 5 meals: {rs(1650)} ({rs(330)} a meal). Monthly pack of 25 meals: {rs(6999)} ({rs(280)} a meal).</p>")],
          [FAQS[2], FAQS[9], FAQS[1]], "high-protein")

goal_page("/vegan-meal-plan-ahmedabad/",
          "Vegan Meal Plan in Ahmedabad | Plant Based Meal Delivery | NOSH7",
          "Vegan meal subscription in Ahmedabad. About 420 calories, plant protein, high fibre, low carb, delivered fresh daily from Satellite. Trial Rs 1,445, monthly Rs 5,975.",
          "Vegan meal plan in Ahmedabad",
          "Plant based meals with no dairy, built around tofu and vegetables and delivered fresh every day.",
          "Vegan",
          [("What is in a Vegan meal", "<p>About 420 calories with plant protein, high fibre and low carbs. Bowls are 400 to 450 grams. The menu is fixed each day and sent on WhatsApp.</p>"),
           ("Price", f"<p>Trial of 5 meals: {rs(1445)} ({rs(289)} a meal). Monthly pack of 25 meals: {rs(5975)} ({rs(239)} a meal).</p>")],
          [FAQS[2], FAQS[7], FAQS[1]], "vegan")

# ---------------------------------------------------------------- jain
add("/jain-meal-delivery-ahmedabad/", "Jain Meal Delivery in Ahmedabad | Healthy Jain Tiffin Subscription | NOSH7",
    "Jain and Swaminarayan healthy meals delivered daily in Ahmedabad. No onion, garlic, ginger, beetroot, carrot, potato or mushroom. High protein, low carb. Trial from Rs 1,250.",
    f"""{crumbs(("Jain meals", None))}
<section><div class="wrap"><h1>Jain meal delivery in Ahmedabad</h1>
<p class="lead">Healthy, high protein Jain and Swaminarayan meals from a pure vegetarian kitchen, delivered daily.</p>
<div class="cta"><a class="btn pri" href="{ORDER}">Order a Jain plan</a></div>
<h2>What a Jain meal means at NOSH7</h2>
<p>A Jain meal has no onion, garlic, ginger, beetroot, carrot, potato or mushroom. We prepare Jain and Swaminarayan versions by changing the ingredients, so the meal is still balanced and high in protein and fibre.</p>
<h2>Available on</h2><p>Healthy Fresh, Low Sugar, Weight Loss and Muscle Gain, and most other plans. Choose Regular, Jain or Swaminarayan at checkout. Jain is not offered on the Fruit Dish Pack.</p>
<h2>Drinks</h2><p>Healthy drinks are available too, including a Jain version, for Rs 49 per meal.</p>
<div class="cards" style="margin-top:18px">{"".join(plan_card(p) for p in PLANS if p["name"] in ("Healthy Fresh", "Low Sugar", "Weight Loss", "Muscle Gain"))}</div></div></section>
<section class="alt"><div class="wrap"><h2>Questions</h2>{faq_html([FAQS[3], FAQS[2], FAQS[7]])}</div></section>
{cta_band()}""", [faq_schema([FAQS[3], FAQS[2], FAQS[7]])])

# ---------------------------------------------------------------- areas
AREAS = ["Satellite", "Prahlad Nagar", "Bodakdev", "Vastrapur"]
area_secs = "".join(
    f'<h2 id="{a.lower().replace(" ", "-")}">Healthy meal delivery in {a}, Ahmedabad</h2>'
    f'<p>{a} falls within our free delivery radius of 5 km from Iscon Cross Road. Choose any of the four daily slots and your plan, and the meal arrives fresh from our Satellite kitchen.</p>'
    for a in AREAS)
add("/delivery-areas-ahmedabad/", "Delivery Areas in Ahmedabad | Satellite, Prahlad Nagar, Bodakdev, Vastrapur | NOSH7",
    "NOSH7 delivers healthy meals in Ahmedabad: Satellite, Prahlad Nagar, Bodakdev and Vastrapur. Free delivery within 5 km of Iscon Cross Road, Rs 10 per km beyond.",
    f"""{crumbs(("Delivery areas", None))}
<section><div class="wrap"><h1>Where we deliver in Ahmedabad</h1>
<p class="lead">Free delivery within 5 km of Iscon Cross Road. Beyond that it is Rs 10 per km.</p>
<div class="cta"><a class="btn pri" href="{ORDER}">Check my address</a></div>
<p>Enter your address at <a href="{ORDER}">start.nosh7.in</a> and it confirms straight away whether we reach you and what delivery costs.</p>
<h2>Delivery slots</h2><ul>{"".join(f"<li>{s}</li>" for s in SLOTS)}</ul>
<p>You choose your slot when you order. Cut-off for changes is 2 hours before the slot starts.</p>
{area_secs}
<p>Not on the list? Many addresses beyond 5 km are covered with a small distance fee. <a href="/contact/">Ask us</a>.</p></div></section>
{cta_band()}""", [faq_schema([FAQS[6], FAQS[7]])])

add("/healthy-tiffin-service-satellite-ahmedabad/", "Healthy Tiffin Service in Satellite, Ahmedabad | Daily Diet Meals | NOSH7",
    "NOSH7 is a pure veg healthy tiffin and meal subscription kitchen in Satellite, Ahmedabad. Fresh high protein, low carb meals delivered daily with free delivery within 5 km.",
    f"""{crumbs(("Satellite", None))}
<section><div class="wrap"><h1>Healthy tiffin service in Satellite, Ahmedabad</h1>
<p class="lead">Our kitchen is at {E(ADDRESS)}, so Satellite meals travel the shortest distance and arrive freshest.</p>
<div class="cta"><a class="btn pri" href="{ORDER}">Start your plan</a><a class="btn" href="/plans/">Plans and prices</a></div>
<h2>A tiffin that counts calories and protein</h2>
<p>NOSH7 is a diet tiffin: every meal is 400 to 450 grams, pure vegetarian, high in protein and fibre and low in carbs. Choose a goal plan for <a href="/weight-loss-meal-plan-ahmedabad/">weight loss</a>, <a href="/diabetic-friendly-meals-ahmedabad/">diabetic friendly eating</a> or <a href="/high-protein-meal-plan-ahmedabad/">muscle gain</a>.</p>
<h2>Delivery in Satellite</h2><p>Free within 5 km of Iscon Cross Road. Slots: {", ".join(SLOTS[:-1])} and {SLOTS[-1]}.</p>
<h2>Nearby areas</h2><p>We also deliver to <a href="/delivery-areas-ahmedabad/#prahlad-nagar">Prahlad Nagar</a>, <a href="/delivery-areas-ahmedabad/#bodakdev">Bodakdev</a> and <a href="/delivery-areas-ahmedabad/#vastrapur">Vastrapur</a>.</p></div></section>
{cta_band()}""")

# ---------------------------------------------------------------- faq, contact
add("/faq/", "FAQ | NOSH7 Healthy Meal Subscription Ahmedabad",
    "Answers about NOSH7 meal plans, prices, delivery areas and slots, Jain and vegan options, cut-off, payment and refunds.",
    f"""{crumbs(("FAQ", None))}<section><div class="wrap"><h1>Frequently asked questions</h1>{faq_html(FAQS)}</div></section>{cta_band()}""",
    [faq_schema(FAQS)])

add("/contact/", "Contact NOSH7 | Healthy Meal Delivery Ahmedabad",
    "Contact NOSH7 in Satellite, Ahmedabad: call or WhatsApp +91 97129 89498, email 07nosh@gmail.com, or log in to manage your plan.",
    f"""{crumbs(("Contact", None))}<section><div class="wrap"><h1>Contact NOSH7</h1>
<div class="cards">
<div class="card"><h3>Call or WhatsApp</h3><p><a href="tel:{PHONE_TEL}">{PHONE}</a></p><p><a class="btn pri sm" href="{WHATSAPP}">Chat on WhatsApp</a></p></div>
<div class="card"><h3>Email</h3><p><a href="mailto:{EMAIL}">{EMAIL}</a></p></div>
<div class="card"><h3>Kitchen</h3><p>{E(ADDRESS)}</p></div>
<div class="card"><h3>Existing customer</h3><p>Manage your plan, skip or pause deliveries and download bills.</p><p><a class="btn sm" href="{LOGIN}" rel="nofollow">Login</a></p></div>
</div>
<p class="note">FSSAI Lic. No. {FSSAI}</p></div></section>""")


# ---------------------------------------------------------------- write
def write(path, content):
    full = os.path.join(OUT, path.lstrip("/"))
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)


def apply_review_schema():
    if REVIEWS:
        BUSINESS["review"] = [{"@type": "Review", "author": {"@type": "Person", "name": r["name"]}, "reviewBody": r["text"],
                               "reviewRating": {"@type": "Rating", "ratingValue": str(r["rating"]), "bestRating": "5"}} for r in REVIEWS]


def main():
    apply_review_schema()
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    for path, (title, desc, body, schema, og) in PAGES.items():
        out = path + "index.html"
        write(out, head(title, desc, path, schema, og or "/img/plan-healthy-fresh.webp") + body + foot())
    write("/style.css", CSS.strip() + "\n")
    write("/404.html", head("Page not found | NOSH7", "Page not found.", "/404.html") +
          f'<section><div class="wrap"><h1>Page not found</h1><p><a href="/">Go to the NOSH7 home page</a> or <a href="/plans/">see plans</a>.</p></div></section>' + foot())
    for src, dst in [("logo.png", "logo.png"), ("favicon.svg", "favicon.svg"),
                     ("img/plan-healthy-fresh.webp", "img/plan-healthy-fresh.webp"), ("img/plan-fruit.webp", "img/plan-fruit.webp"),
                     ("assets/fssai-logo.svg", "assets/fssai-logo.svg"), ("assets/razorpay-logo.svg", "assets/razorpay-logo.svg")]:
        os.makedirs(os.path.dirname(os.path.join(OUT, dst)) or OUT, exist_ok=True)
        shutil.copy(os.path.join(ROOT, src), os.path.join(OUT, dst))
    urls = "".join(f"  <url><loc>{SITE}{p}</loc><lastmod>{LASTMOD}</lastmod></url>\n" for p in PAGES)
    write("/sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + "</urlset>\n")
    write("/robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
    write("/CNAME", "nosh7.com")
    write("/README.md", "Generated by scripts/build-site.py. Do not edit by hand, edit the script and rebuild.\n"
          "To go live, publish this folder as the root of a GitHub Pages site with custom domain nosh7.com.\n")
    print(f"built {len(PAGES)} pages into {OUT}")


if __name__ == "__main__":
    main()
