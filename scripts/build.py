#!/usr/bin/env python3
"""Generate the static site from data/clubs.json.

Usage:  python3 scripts/build.py

Writes index.html, register/index.html, 404.html and clubs/<slug>/index.html for every club. Clubs marked
"custom_page": true keep their hand-written clubs/<slug>/index.html.
No dependencies beyond the Python 3 standard library.
"""
import hashlib
import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLUBS = json.loads((ROOT / "data" / "clubs.json").read_text(encoding="utf-8"))

ICONS = {
    "instagram": "fa-brands fa-instagram",
    "facebook": "fa-brands fa-facebook-f",
    "youtube": "fa-brands fa-youtube",
    "linkedin": "fa-brands fa-linkedin-in",
    "x": "fa-brands fa-x-twitter",
    "globe": "fa-solid fa-globe",
}
SOCIAL_NAMES = {"instagram": "Instagram", "facebook": "Facebook", "youtube": "YouTube",
                "linkedin": "LinkedIn", "x": "X", "globe": "Website"}
CATEGORY_ICONS = {
    "Cultural": "fa-solid fa-music", "Service": "fa-solid fa-hand-holding-heart", "Creative": "fa-solid fa-camera",
    "Entrepreneurship": "fa-solid fa-rocket", "Academic": "fa-solid fa-infinity", "Literary": "fa-solid fa-feather-pointed",
    "Technical": "fa-solid fa-microchip", "Communication": "fa-solid fa-microphone-lines", "Environment": "fa-solid fa-leaf",
}

e = escape


def v(rel):
    """Cache-busting query string: changes whenever the file's contents change."""
    digest = hashlib.sha1((ROOT / rel).read_bytes()).hexdigest()[:8]
    return f"{rel}?v={digest}"


def photo_count(c):
    return len(c.get("gallery", [])) + sum(len(h.get("images", [])) for h in c.get("highlights", []))


def head(title, description, root, styles=(), body_class="", body_style=""):
    extra = "".join(f'  <link rel="stylesheet" href="{root}{v("assets/css/" + x)}">\n' for x in styles)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{e(title)}</title>
  <meta name="description" content="{e(description)}">
  <meta name="theme-color" content="#1b0a12">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{e(title)}">
  <meta property="og:description" content="{e(description)}">
  <link rel="icon" type="image/png" href="{root}assets/img/favicon.png">
  <script>document.documentElement.classList.add('js')</script>
  <link rel="preload" href="{root}assets/vendor/fonts/inter-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="{root}assets/vendor/fonts/fraunces-latin-600-normal.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="{root}assets/vendor/fonts/fonts.css">
  <link rel="stylesheet" href="{root}assets/vendor/fontawesome/css/fontawesome.min.css">
  <link rel="stylesheet" href="{root}assets/vendor/fontawesome/css/solid.min.css">
  <link rel="stylesheet" href="{root}assets/vendor/fontawesome/css/brands.min.css">
  <link rel="stylesheet" href="{root}{v('assets/css/style.css')}">
{extra}</head>
<body class="{body_class}"{f' style="{body_style}"' if body_style else ""}>
<a class="skip-link" href="#main">Skip to content</a>
"""


def header(root, current=None):
    links = [
        ("clubs", "Clubs", f"{root}index.html#clubs"),
        ("about", "About", f"{root}index.html#about"),
        ("moments", "Moments", f"{root}index.html#moments"),
        ("join", "How to join", f"{root}index.html#join"),
    ]
    items = "\n".join(f'        <li><a href="{href}">{label}</a></li>' for _, label, href in links)
    reg_current = ' aria-current="page"' if current == "register" else ""
    quick = "".join(f'<a href="{root}clubs/{c["slug"]}/">{e(c["name"])}</a>' for c in CLUBS)
    return f"""<header class="site-header">
  <div class="wrap">
    <a class="brand" href="{root}index.html" aria-label="AMRITA Student Hub home">
      <img class="logo-dark" src="{root}assets/img/logo-dark.png" alt="Amrita Vishwa Vidyapeetham" width="142" height="40">
      <img class="logo-light" src="{root}assets/img/logo.png" alt="" width="142" height="40">
      <span>Student Hub</span>
    </a>
    <button class="nav-toggle" type="button" aria-label="Open menu" aria-expanded="false" aria-controls="site-nav"><span class="bars"></span></button>
    <nav class="nav" id="site-nav" aria-label="Main">
      <ul>
{items}
        <li><a class="btn btn-primary" href="{root}register/"{reg_current}>Register <i class="fa-solid fa-arrow-right" aria-hidden="true"></i></a></li>
      </ul>
      <div class="nav-extra"><p>Jump to a club</p><div>{quick}</div></div>
    </nav>
  </div>
  <div class="progress-bar" aria-hidden="true"></div>
</header>
"""


def footer(root, scripts=()):
    campuses = ["Amritapuri", "Amaravati", "Bengaluru", "Chennai", "Coimbatore", "Faridabad", "Kochi", "Mysuru"]
    campus_li = "\n".join(f'          <li><a href="https://www.amrita.edu/campus/{c.lower()}/">{c}</a></li>' for c in campuses[:6])
    half = (len(CLUBS) + 1) // 2
    club_li = "\n".join(f'          <li><a href="{root}clubs/{c["slug"]}/">{e(c["name"])}</a></li>' for c in CLUBS[:half])
    club_li2 = "\n".join(f'          <li><a href="{root}clubs/{c["slug"]}/">{e(c["name"])}</a></li>' for c in CLUBS[half:])
    extra = "".join(f'<script src="{root}{v("assets/js/" + x)}" defer></script>\n' for x in scripts)
    return f"""<footer class="site-footer">
  <div class="wrap">
    <div class="footer-top">
      <div class="footer-brand">
        <img src="{root}assets/img/logo.png" alt="Amrita Vishwa Vidyapeetham" width="149" height="42" loading="lazy">
        <p>Every student club at Amrita Vishwa Vidyapeetham, Coimbatore, in one place. Find your people, then go make something.</p>
        <div class="footer-social">
          <a href="https://www.instagram.com/amrita_university/" aria-label="Amrita on Instagram"><i class="fa-brands fa-instagram"></i></a>
          <a href="https://www.facebook.com/AmritaUniversity" aria-label="Amrita on Facebook"><i class="fa-brands fa-facebook-f"></i></a>
          <a href="https://x.com/AMRITAedu" aria-label="Amrita on X"><i class="fa-brands fa-x-twitter"></i></a>
          <a href="https://www.linkedin.com/school/amrita-vishwa-vidyapeetham-official/" aria-label="Amrita on LinkedIn"><i class="fa-brands fa-linkedin-in"></i></a>
        </div>
      </div>
      <div>
        <h4>Clubs</h4>
        <ul>
{club_li}
        </ul>
      </div>
      <div>
        <h4>&nbsp;</h4>
        <ul>
{club_li2}
        </ul>
      </div>
      <div>
        <h4>Amrita</h4>
        <ul>
          <li><a href="{root}register/">Register for clubs</a></li>
          <li><a href="https://www.amrita.edu/admissions/">Admissions</a></li>
          <li><a href="https://www.amrita.edu/events/">Events</a></li>
{campus_li}
        </ul>
      </div>
    </div>
    <p class="footer-word" aria-hidden="true">Student Hub</p>
    <div class="footer-bottom">
      <span>A student project showcasing clubs at Amrita Vishwa Vidyapeetham. Not an official university website.</span>
      <span>Club names, logos and photos belong to their clubs.</span>
    </div>
  </div>
</footer>
<script src="{root}{v('assets/js/main.js')}" defer></script>
{extra}</body>
</html>
"""


def club_card(c, root, i=0):
    photos, vids = photo_count(c), len(c.get("videos", []))
    counts = ""
    if photos or vids:
        bits = []
        if photos:
            bits.append(f'<span><i class="fa-solid fa-image" aria-hidden="true"></i>{photos}</span>')
        if vids:
            bits.append(f'<span><i class="fa-solid fa-play" aria-hidden="true"></i>{vids}</span>')
        counts = f'<div class="counts">{"".join(bits)}</div>'
    return f"""      <a class="club-card-home" href="{root}clubs/{c['slug']}/" data-category="{e(c['category'])}" data-reveal style="--d:{(i % 4) * 0.07:.2f}s">
        <div class="media"><img src="{root}assets/img/cards/{c['card']}" alt="" loading="lazy" width="800" height="600"><span class="tag">{e(c['category'])}</span>{counts}</div>
        <div class="body">
          <h3>{e(c['name'])}</h3>
          <p>{e(c['tagline'])}</p>
          <span class="more">Explore club <i class="fa-solid fa-arrow-right" aria-hidden="true"></i></span>
        </div>
      </a>"""


def cta_band(root, title, text, slug=None):
    href = f"{root}register/" + (f"?club={slug}" if slug else "")
    return f"""  <section class="section tight">
    <div class="wrap">
      <div class="cta-band" data-reveal="zoom">
        <span class="kicker light">Registrations open</span>
        <h2>{title}</h2>
        <p>{e(text)}</p>
        <div class="actions">
          <a class="btn btn-gold" href="{href}">Register now <i class="fa-solid fa-arrow-right" aria-hidden="true"></i></a>
          <a class="btn btn-ghost" href="{root}index.html#clubs">Browse all clubs</a>
        </div>
      </div>
    </div>
  </section>"""


def build_home():
    root = ""
    cats = sorted({c["category"] for c in CLUBS})
    total_photos = sum(photo_count(c) for c in CLUBS)
    total_videos = sum(len(c.get("videos", [])) for c in CLUBS)

    cards = [f"assets/img/cards/{c['card']}" for c in CLUBS]
    cols = [cards[i::5] + cards[(i + 2) % 5::5] for i in range(5)]
    wall = "\n".join('      <div class="wall-col">' + "".join(f'<img src="{s}" alt="">' for s in col * 2) + "</div>" for col in cols)

    chips = "\n".join(
        f'          <button class="chip" type="button" data-filter="{e(cat)}" aria-pressed="{str(cat == "All").lower()}">{e(cat)}</button>'
        for cat in ["All"] + cats
    )
    ribbon_items = "".join(f'<a href="clubs/{c["slug"]}/">{e(c["name"])}</a>' for c in CLUBS)
    groups = [
        ("Create", "fa-solid fa-palette", "Music, dance, writing, photography and film.", ["Cultural", "Creative", "Literary"], "Cultural"),
        ("Build", "fa-solid fa-code", "Code, hardware, start-ups, maths and public speaking.", ["Technical", "Entrepreneurship", "Academic", "Communication"], "Technical"),
        ("Serve", "fa-solid fa-hand-holding-heart", "Volunteering, conservation and community work.", ["Service", "Environment"], "Service"),
    ]
    tiles = []
    for n, (title, icon, text, cat_list, first) in enumerate(groups):
        names = ", ".join(c["name"] for c in CLUBS if c["category"] in cat_list)
        tiles.append(f"""        <a class="pillar-tile" href="#clubs" data-filter-link="{first}" data-reveal="right" style="--d:{n * 0.1:.1f}s">
          <span class="ic"><i class="{icon}" aria-hidden="true"></i></span>
          <span><h3>{title}</h3><p>{e(names)}</p></span>
          <i class="go fa-solid fa-arrow-right" aria-hidden="true"></i>
        </a>""")

    moments = sorted((ROOT / "assets/img/moments").glob("*.jpg"))
    names = {c["slug"]: c["name"] for c in CLUBS}
    def mrow(items):
        cells = "".join(
            f'<a class="moment" href="clubs/{m.name.split("__")[0]}/" tabindex="-1"><img src="assets/img/moments/{m.name}" alt="" loading="lazy"><span>{e(names.get(m.name.split("__")[0], ""))}</span></a>'
            for m in items
        )
        return cells * 2
    row1, row2 = moments[0::2], moments[1::2]

    html = head("AMRITA Student Hub — Find your club",
                "Discover every student club at Amrita Vishwa Vidyapeetham, Coimbatore: music, dance, tech, service, literature and more.",
                root, body_class="overlay")
    html += header(root)
    html += f"""<main id="main">
  <section class="hero-home" aria-label="Introduction">
    <div class="wall" aria-hidden="true" data-parallax="0.18">
{wall}
    </div>
    <div class="wrap">
      <span class="kicker light fade-in" style="--d:.1s">Amrita Vishwa Vidyapeetham &middot; Coimbatore</span>
      <h1 class="line-reveal"><span class="line"><span>Where campus</span></span><span class="line" style="--i:1"><span><em>comes alive.</em></span></span></h1>
      <p class="hero-lead fade-in" style="--d:.55s">{len(CLUBS)} student clubs for music, dance, code, service, words and everything in between. Find the ones that feel like yours.</p>
      <div class="hero-actions fade-in" style="--d:.7s">
        <a class="btn btn-gold" href="#clubs">Explore clubs <i class="fa-solid fa-arrow-down" aria-hidden="true"></i></a>
        <a class="btn btn-ghost" href="register/">Join a club <i class="fa-solid fa-arrow-right" aria-hidden="true"></i></a>
      </div>
      <dl class="hero-stats fade-in" style="--d:.85s">
        <div><dt>student clubs</dt><dd data-count="{len(CLUBS)}" data-delay="900">{len(CLUBS)}</dd></div>
        <div><dt>categories</dt><dd data-count="{len(cats)}" data-delay="900">{len(cats)}</dd></div>
        <div><dt>photos to explore</dt><dd data-count="{total_photos}" data-delay="900">{total_photos}<sup>+</sup></dd></div>
        <div><dt>videos</dt><dd data-count="{total_videos}" data-delay="900">{total_videos}</dd></div>
      </dl>
      <a class="scroll-cue" href="#about">Scroll</a>
    </div>
  </section>

  <div class="ribbon" aria-label="All clubs">
    <div class="ribbon-track">{ribbon_items}{ribbon_items.replace('<a ', '<a tabindex="-1" aria-hidden="true" ')}</div>
  </div>

  <section class="section" id="about">
    <div class="wrap about-grid">
      <div class="about-copy">
        <span class="kicker" data-reveal>Life beyond the classroom</span>
        <p class="about-statement" data-reveal style="--d:.08s">The best part of college often happens <em>after</em> the last lecture.</p>
        <p data-reveal style="--d:.16s">To further the overall development of students, Amrita encourages participation in a wide range of extra-curricular, social and community activities. Associations like Toastmasters, GDSC and Srishti, along with clubs like Elite, Anantham, Intel IoT and the Photography Club, bring out creative talent and build team spirit.</p>
        <p data-reveal style="--d:.24s">NSS and the Nature Club give students a platform for humanitarian and environmental work, on campus and beyond.</p>
      </div>
      <div class="pillar-list">
        <span class="kicker" data-reveal>What are you into?</span>
{chr(10).join(tiles)}
      </div>
    </div>
  </section>

  <section class="section clubs-section" id="clubs">
    <div class="wrap">
      <div class="section-head">
        <div><span class="kicker" data-reveal>The directory</span><h2 data-reveal style="--d:.08s">Explore every club</h2></div>
        <p data-reveal style="--d:.16s">Filter by what you love, or search by name. Each club has its own page with photos, events and how to join.</p>
      </div>
      <div class="toolbar" data-reveal>
        <div class="chips" role="group" aria-label="Filter clubs by category">
{chips}
        </div>
        <label class="search">
          <i class="fa-solid fa-magnifying-glass" aria-hidden="true"></i>
          <input id="club-search" type="search" placeholder="Search clubs" aria-label="Search clubs" autocomplete="off">
        </label>
      </div>
      <div class="club-grid-home" id="club-grid" aria-live="polite">
{chr(10).join(club_card(c, root, i) for i, c in enumerate(CLUBS))}
      </div>
      <p class="empty" id="no-results" hidden><i class="fa-solid fa-magnifying-glass" aria-hidden="true"></i>No clubs match that. Try another word or category.</p>
    </div>
  </section>

  <section class="section moments" id="moments">
    <div class="wrap">
      <div class="section-head">
        <div><span class="kicker light" data-reveal>Moments</span><h2 data-reveal style="--d:.08s">Life on campus, in frames</h2></div>
        <p data-reveal style="--d:.16s">Performances, hackathons, drives and late-night rehearsals. Tap a photo to visit the club behind it.</p>
      </div>
    </div>
    <div class="moment-row">{mrow(row1)}</div>
    <div class="moment-row reverse">{mrow(row2)}</div>
  </section>

  <section class="section" id="join">
    <div class="wrap">
      <div class="section-head">
        <div><span class="kicker" data-reveal>How to join</span><h2 data-reveal style="--d:.08s">Three steps. Two minutes.</h2></div>
        <p data-reveal style="--d:.16s">One form signs you up for up to three clubs. The coordinators take it from there.</p>
      </div>
      <div class="steps-row">
        <div class="step-card" data-reveal><span class="ic"><i class="fa-solid fa-compass" aria-hidden="true"></i></span><h3>Explore</h3><p>Browse the clubs, look through their photos and find the ones that click.</p></div>
        <div class="step-card" data-reveal style="--d:.1s"><span class="ic"><i class="fa-solid fa-pen-to-square" aria-hidden="true"></i></span><h3>Register</h3><p>Fill in one short form with your details and pick up to three clubs.</p></div>
        <div class="step-card" data-reveal style="--d:.2s"><span class="ic"><i class="fa-solid fa-people-group" aria-hidden="true"></i></span><h3>Show up</h3><p>Coordinators reach out about inductions. Turn up, meet people, make things.</p></div>
      </div>
    </div>
  </section>

{cta_band(root, "Ready to find <em>your people?</em>", "Registrations are open for every club. It takes about two minutes.")}
</main>
"""
    html += footer(root)
    (ROOT / "index.html").write_text(html, encoding="utf-8")


def related_clubs(c, n=3):
    others = [x for x in CLUBS if x["slug"] != c["slug"]]
    same = [x for x in others if x["category"] == c["category"]]
    idx = CLUBS.index(c)
    after = [CLUBS[(idx + k) % len(CLUBS)] for k in range(1, len(CLUBS))]
    out = []
    for x in same + after:
        if x not in out:
            out.append(x)
    return out[:n]


def build_club(i, c):
    root = "../../"
    name = c["name"]
    slug = c["slug"]
    photos, vids = photo_count(c), len(c.get("videos", []))
    n_events = len(c.get("highlights", []))
    socials = c.get("socials", [])
    about = list(c.get("about", []))
    lead = about.pop(0) if about else c["tagline"]
    cat_icon = CATEGORY_ICONS.get(c["category"], "fa-solid fa-star")

    tabs = [("about", "About")]
    parts = []

    # --- About + at a glance
    pillars = ""
    if c.get("pillars"):
        pillars = '      <div class="pillars">\n' + "\n".join(
            f'        <div class="pillar" data-reveal style="--d:{k * 0.1:.1f}s"><span class="num">0{k + 1}</span><h3>{e(p["heading"])}</h3><p>{e(p["text"])}</p></div>'
            for k, p in enumerate(c["pillars"])
        ) + "\n      </div>"
    glance_rows = [("Category", c["category"])]
    if c.get("full_name"):
        glance_rows.insert(0, ("Full name", c["full_name"]))
    if photos:
        glance_rows.append(("Photos", str(photos)))
    if vids:
        glance_rows.append(("Videos", str(vids)))
    glance_dl = "".join(f"<div><dt>{e(k)}</dt><dd>{e(val)}</dd></div>" for k, val in glance_rows)
    glance_soc = ""
    if socials:
        glance_soc = '<div class="socials">' + "".join(
            f'<a href="{e(s["url"])}" target="_blank" rel="noopener" aria-label="{e(name)} on {SOCIAL_NAMES[s["type"]]}"><i class="{ICONS[s["type"]]}"></i></a>' for s in socials
        ) + "</div>"
    prose = "\n".join(f'          <p data-reveal>{e(p)}</p>' for p in about)
    parts.append(f"""  <section class="section" id="about">
    <div class="wrap club-about">
      <div>
        <span class="kicker" data-reveal>About {e(name)}</span>
        <p class="lead-in" data-reveal style="--d:.08s">{e(lead)}</p>
        <div class="prose">
{prose}
        </div>
      </div>
      <aside class="glance" data-reveal="right">
        <h3>At a glance</h3>
        <dl>{glance_dl}</dl>
        {glance_soc}
        <a class="btn btn-primary" href="{root}register/?club={slug}">Join {e(name)} <i class="fa-solid fa-arrow-right" aria-hidden="true"></i></a>
      </aside>
    </div>
  </section>""")

    # --- What you'll do (GDSC keeps its Connect / Learn / Grow pillars as the activities)
    if c.get("activities"):
        acts = "\n".join(
            f"""        <article class="activity" data-reveal style="--d:{k * 0.1:.1f}s">
          <span class="ic"><i class="{a['icon']}" aria-hidden="true"></i></span>
          <h3>{e(a['title'])}</h3>
          <p>{e(a['text'])}</p>
        </article>"""
            for k, a in enumerate(c["activities"])
        )
        tabs.append(("do", "What you'll do"))
        parts.append(f"""  <section class="section" id="do" style="padding-top:0">
    <div class="wrap">
      <div class="section-head"><div><span class="kicker" data-reveal>What you'll do</span><h2 data-reveal style="--d:.08s">Life as a member</h2></div><p data-reveal style="--d:.16s">A taste of what {e(name)} gets up to through the year.</p></div>
      <div class="activities">
{acts}
      </div>
{pillars if not c.get("activities") else ""}
    </div>
  </section>""")

    # --- Highlights
    if c.get("highlights"):
        tabs.append(("highlights", "Highlights"))
        blocks = []
        for k, h in enumerate(c["highlights"]):
            body = []
            for s in h["sections"]:
                if s.get("heading"):
                    body.append(f'          <h4>{e(s["heading"])}</h4>')
                body.append(f'          <p>{e(s["text"])}</p>')
            if h.get("quote"):
                body.append(f'          <blockquote>{e(h["quote"])}</blockquote>')
            date = f'          <span class="date"><i class="fa-solid fa-calendar" aria-hidden="true"></i>{e(h["date"])}</span>\n' if h.get("date") else ""
            imgs = "\n".join(
                f'          <a href="{im}" data-lightbox="{im}"><img src="{im}" alt="{e(h["title"])}" loading="lazy"></a>' for im in h.get("images", [])
            )
            blocks.append(f"""      <article class="highlight{' flip' if k % 2 else ''}" data-reveal>
        <div>
{date}          <h3>{e(h['title'])}</h3>
{chr(10).join(body)}
        </div>
        <div class="highlight-media">
{imgs}
        </div>
      </article>""")
        parts.append(f"""  <section class="section" id="highlights" style="padding-top:0">
    <div class="wrap">
      <div class="section-head"><div><span class="kicker" data-reveal>Highlights</span><h2 data-reveal style="--d:.08s">Moments worth remembering</h2></div></div>
{chr(10).join(blocks)}
    </div>
  </section>""")

    # --- Gallery
    if c.get("gallery"):
        tabs.append(("gallery", "Gallery"))
        items = "\n".join(
            f'        <button type="button" data-lightbox="{im}" aria-label="Open photo {n} of {len(c["gallery"])}" data-reveal style="--d:{(n % 3) * 0.06:.2f}s"><img src="{im}" alt="{e(name)} photo {n}" loading="lazy"></button>'
            for n, im in enumerate(c["gallery"], 1)
        )
        parts.append(f"""  <section class="section" id="gallery" style="padding-top:0">
    <div class="wrap">
      <div class="section-head"><div><span class="kicker" data-reveal>Gallery</span><h2 data-reveal style="--d:.08s">Through the lens</h2></div><p data-reveal style="--d:.16s">{len(c["gallery"])} photos. Click any one to view it full screen, then use the arrow keys or swipe.</p></div>
      <div class="masonry">
{items}
      </div>
    </div>
  </section>""")

    # --- Videos
    if c.get("videos"):
        tabs.append(("videos", "Videos"))
        vids_html = "\n".join(
            f"""        <div class="video-card" data-reveal style="--d:{k * 0.1:.1f}s">
          <video src="{vd}" poster="{vd[:-4]}-poster.jpg" playsinline preload="none"></video>
          <button class="play" type="button" aria-label="Play {e(name)} video {k + 1}"><span><i class="fa-solid fa-play" aria-hidden="true"></i></span><em>{e(name)} &middot; video {k + 1}</em></button>
        </div>"""
            for k, vd in enumerate(c["videos"])
        )
        parts.append(f"""  <section class="section" id="videos" style="padding-top:0">
    <div class="wrap">
      <div class="section-head"><div><span class="kicker" data-reveal>Videos</span><h2 data-reveal style="--d:.08s">See it in motion</h2></div></div>
      <div class="videos">
{vids_html}
      </div>
    </div>
  </section>""")

    # --- Follow
    if socials:
        tabs.append(("follow", "Follow"))
        cards = "\n".join(
            f"""        <a class="social-card" href="{e(s['url'])}" target="_blank" rel="noopener" data-reveal style="--d:{k * 0.08:.2f}s">
          <span class="ic {s['type']}"><i class="{ICONS[s['type']]}" aria-hidden="true"></i></span>
          <span><small>{SOCIAL_NAMES[s['type']]}</small><strong>{e(s['label'])}</strong></span>
          <i class="go fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i>
        </a>"""
            for k, s in enumerate(socials)
        )
        parts.append(f"""  <section class="section" id="follow" style="padding-top:0">
    <div class="wrap">
      <div class="section-head"><div><span class="kicker" data-reveal>Stay in the loop</span><h2 data-reveal style="--d:.08s">Follow {e(name)}</h2></div></div>
      <div class="follow-grid">
{cards}
      </div>
    </div>
  </section>""")

    # --- Related clubs
    tabs.append(("more", "More clubs"))
    rel = related_clubs(c)
    parts.append(f"""  <section class="section clubs-section" id="more">
    <div class="wrap">
      <div class="section-head"><div><span class="kicker" data-reveal>Keep exploring</span><h2 data-reveal style="--d:.08s">You might also like</h2></div><a class="btn btn-outline" href="{root}index.html#clubs" data-reveal>All clubs <i class="fa-solid fa-arrow-right" aria-hidden="true"></i></a></div>
      <div class="related">
{chr(10).join(club_card(x, root, k) for k, x in enumerate(rel))}
      </div>
    </div>
  </section>""")

    # --- Finale: join + next club
    nxt = CLUBS[(i + 1) % len(CLUBS)]
    parts.append(f"""  <section class="section tight">
    <div class="wrap finale">
      <div class="join-card" data-reveal="left">
        <span class="kicker light">Registrations open</span>
        <h2>Want to join <em>{e(name)}?</em></h2>
        <p>Register in about two minutes. The coordinators will get in touch about inductions and the next meet-up.</p>
        <div class="actions">
          <a class="btn btn-gold" href="{root}register/?club={slug}">Register now <i class="fa-solid fa-arrow-right" aria-hidden="true"></i></a>
          <a class="btn btn-ghost" href="{root}index.html#clubs">Browse all clubs</a>
        </div>
      </div>
      <a class="next-club" href="../{nxt['slug']}/" data-reveal="right">
        <img src="{root}assets/img/cards/{nxt['card']}" alt="" loading="lazy">
        <small>Next club</small>
        <strong>{e(nxt['name'])} <i class="fa-solid fa-arrow-right" aria-hidden="true"></i></strong>
        <span>{e(nxt['tagline'])}</span>
      </a>
    </div>
  </section>""")

    # --- Hero
    chips = []
    insta = next((s for s in socials if s["type"] == "instagram"), None)
    if insta:
        chips.append(f'<span><i class="fa-brands fa-instagram" aria-hidden="true"></i>{e(insta["label"])}</span>')
    follow_btn = ""
    if socials:
        s0 = socials[0]
        follow_btn = f'<a class="btn btn-ghost" href="{e(s0["url"])}" target="_blank" rel="noopener"><i class="{ICONS[s0["type"]]}" aria-hidden="true"></i> Follow</a>'
    stack_src = list(c.get("stack") or (c.get("gallery") or [])[:3])
    while len(stack_src) < 3:
        stack_src.append(c["hero"])
    stack = "".join(
        f'<figure class="p{k + 1}"><img src="{src}" alt="" {"" if k == 2 else "loading=\"lazy\" "}></figure>' for k, src in enumerate(stack_src)
    )
    badge_txt = f"{photos} photos" if photos else c["category"]
    badge_sub = (f"{vids} video{'s' if vids != 1 else ''}" if vids else "Club gallery") if photos else "Student club"

    # --- Stats strip
    stats = [(cat_icon, None, c["category"], "Category")]
    if photos:
        stats.append(("fa-solid fa-image", photos, None, "Photos"))
    if vids:
        stats.append(("fa-solid fa-play", vids, None, "Videos" if vids != 1 else "Video"))
    if n_events:
        stats.append(("fa-solid fa-calendar-check", n_events, None, "Featured events" if n_events != 1 else "Featured event"))
    if socials:
        stats.append(("fa-solid fa-share-nodes", len(socials), None, "Social channels" if len(socials) != 1 else "Social channel"))
    stat_html = "".join(
        f'<div class="stat" data-reveal style="--d:{k * 0.07:.2f}s"><span class="ic"><i class="{ic}" aria-hidden="true"></i></span><div>'
        + (f'<b data-count="{num}">{num}</b>' if num is not None else f"<b style=\"font-size:1.15rem\">{e(txt)}</b>")
        + f"<span>{label}</span></div></div>"
        for k, (ic, num, txt, label) in enumerate(stats)
    )
    tab_links = "".join(f'<li><a href="#{tid}">{label}</a></li>' for tid, label in tabs)
    sub = f"{e(c['full_name'])} — {e(c['tagline'])}" if c.get("full_name") else e(c["tagline"])

    title = f"{name} — AMRITA Student Hub"
    html = head(title, c["tagline"], root, body_class="overlay club-page", body_style=f"--accent:{c['accent']}")
    html += header(root)
    html += f"""<main id="main">
  <section class="club-hero2" aria-label="{e(name)}">
    <div class="bg" style="background-image:url('{c['hero']}')" data-parallax="0.15"></div>
    <div class="hero-word" aria-hidden="true">{e(name)}</div>
    <div class="wrap hero-grid">
      <div>
        <nav class="crumbs fade-in" style="--d:.1s" aria-label="Breadcrumb"><a href="{root}index.html#clubs"><i class="fa-solid fa-arrow-left" aria-hidden="true"></i> All clubs</a><i class="sep fa-solid fa-chevron-right" aria-hidden="true"></i><span>{e(name)}</span></nav>
        <span class="cat-pill fade-in" style="--d:.2s"><i class="{cat_icon}" aria-hidden="true"></i>{e(c['category'])}</span>
        <h1 class="line-reveal{' long' if len(name) > 10 else ''}"><span class="line"><span>{e(name)}</span></span></h1>
        <p class="sub fade-in" style="--d:.45s">{sub}</p>
        {('<div class="meta-chips fade-in" style="--d:.6s">' + ''.join(chips) + '</div>') if chips else ''}
        <div class="hero-actions-club fade-in" style="--d:.7s">
          <a class="btn btn-gold" href="{root}register/?club={slug}">Join {e(name)} <i class="fa-solid fa-arrow-right" aria-hidden="true"></i></a>
          {follow_btn}
        </div>
      </div>
      <div class="photo-stack" aria-hidden="true">
        <div class="float" style="position:absolute;inset:0">{stack}</div>
        <div class="stack-badge"><span class="ic"><i class="{cat_icon}"></i></span><span>{e(badge_txt)}<small>{e(badge_sub)}</small></span></div>
      </div>
    </div>
  </section>
  <section class="stat-strip" aria-label="{e(name)} in numbers"><div class="wrap">{stat_html}</div></section>
  <nav class="tabs" aria-label="On this page">
    <div class="wrap">
      <ul>{tab_links}</ul>
      <a class="btn btn-primary" href="{root}register/?club={slug}">Join <i class="fa-solid fa-arrow-right" aria-hidden="true"></i></a>
    </div>
  </nav>
{chr(10).join(parts)}
</main>
<div class="join-bar" aria-hidden="true"><strong><small>Interested?</small>{e(name)}</strong><a class="btn" href="{root}register/?club={slug}" tabindex="-1">Join <i class="fa-solid fa-arrow-right" aria-hidden="true"></i></a></div>
"""
    html += footer(root)
    out = ROOT / "clubs" / slug / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")


def build_404():
    root = "/"
    html = head("Page not found — AMRITA Student Hub", "This page doesn't exist.", root)
    html += header(root)
    html += f"""<main id="main" class="not-found">
  <div class="wrap">
    <p class="big" data-reveal="zoom">404</p>
    <h1 data-reveal style="--d:.1s">Lost somewhere on campus?</h1>
    <p data-reveal style="--d:.2s">The page you're looking for has moved or never existed. Let's get you back to the clubs.</p>
    <div class="actions" data-reveal style="--d:.3s">
      <a class="btn btn-primary" href="{root}">Back to home <i class="fa-solid fa-arrow-right" aria-hidden="true"></i></a>
      <a class="btn btn-outline" href="{root}index.html#clubs">Browse clubs</a>
    </div>
  </div>
</main>
"""
    html += footer(root)
    (ROOT / "404.html").write_text(html, encoding="utf-8")

PROGRAMMES = [
    "B.Tech", "M.Tech", "Integrated M.Sc", "M.Sc", "BCA / MCA", "B.Com / M.Com",
    "BBA / MBA", "B.A. / M.A.", "Ph.D", "Other",
]


def build_register():
    root = "../"
    cards = [f"{root}assets/img/cards/{c['card']}" for c in CLUBS]
    cols = [cards[i::3] for i in range(3)]
    wall = "\n".join(
        '      <div class="wall-col">' + "".join(f'<img src="{src}" alt="">' for src in col * 2) + "</div>"
        for col in cols
    )
    n_cats = len({c["category"] for c in CLUBS})
    options = "\n".join(f'              <option>{e(p)}</option>' for p in PROGRAMMES)
    years = "\n".join(
        f'            <input type="radio" id="year-{y}" name="year" value="{label}"><label for="year-{y}">{label}</label>'
        for y, label in [("1", "1st year"), ("2", "2nd year"), ("3", "3rd year"), ("4", "4th year"), ("5", "5th year / PG")]
    )
    club_cards = "\n".join(
        f"""          <label class="club-card" style="animation-delay:{i * 35}ms">
            <input type="checkbox" name="clubs" value="{c['slug']}" data-name="{e(c['name'])}" data-img="{root}assets/img/cards/{c['card']}">
            <span class="face"><img src="{root}assets/img/cards/{c['card']}" alt="" loading="lazy"><span class="meta"><strong>{e(c['name'])}</strong><small>{e(c['category'])}</small></span></span>
            <span class="check" aria-hidden="true"><i class="fa-solid fa-check"></i></span>
          </label>"""
        for i, c in enumerate(CLUBS)
    )
    html = head("Register — AMRITA Student Hub",
                "Sign up for student clubs at Amrita Vishwa Vidyapeetham, Coimbatore, in three quick steps.",
                root, styles=("register.css",))
    html += header(root, current="register")
    html += f"""<main id="main" class="reg">
  <section class="reg-stage" aria-label="Introduction">
    <div class="wall" aria-hidden="true">
{wall}
    </div>
    <div>
      <p class="reg-kicker fade-up"><span class="dot"></span> Registrations open</p>
      <h1 class="reg-title"><span class="line"><span>Find your</span></span><span class="line"><span><em>people.</em></span></span></h1>
      <p class="reg-lead fade-up d1">Music, dance, code, service, words. Pick up to three clubs and the coordinators will take it from there.</p>
      <dl class="reg-stats fade-up d2">
        <div><dt>clubs</dt><dd data-count="{len(CLUBS)}">{len(CLUBS)}</dd></div>
        <div><dt>categories</dt><dd data-count="{n_cats}">{n_cats}</dd></div>
        <div><dt>steps to join</dt><dd data-count="3">3</dd></div>
      </dl>
    </div>
  </section>

  <section class="reg-panel" aria-label="Registration form">
    <div class="reg-panel-inner">
      <div class="progress fade-up d1" id="progress">
        <div class="progress-track"><div class="progress-fill" id="progress-fill"></div></div>
        <ol>
          <li class="active" data-step="1"><span class="bubble">1<i class="fa-solid fa-check"></i></span><span class="label">About you</span></li>
          <li data-step="2"><span class="bubble">2<i class="fa-solid fa-check"></i></span><span class="label">Your clubs</span></li>
          <li data-step="3"><span class="bubble">3<i class="fa-solid fa-check"></i></span><span class="label">Review</span></li>
        </ol>
      </div>

      <form id="register-form" novalidate>
        <div class="alert" id="form-alert" role="alert"><i class="fa-solid fa-circle-exclamation" aria-hidden="true"></i><span></span></div>

        <div class="steps-viewport">
          <!-- Step 1 -->
          <div class="step active" data-step="1">
            <div class="step-head">
              <span class="count">Step 1 of 3</span>
              <h2>Let's get to know you</h2>
              <p>A few details so the club coordinators know who you are.</p>
            </div>
            <div class="grid-2">
              <div class="fl full" data-field="name">
                <input type="text" id="name" name="name" autocomplete="name" placeholder="e.g. Ananya Menon" aria-describedby="name-error">
                <label for="name">Full name</label><i class="icon fa-solid fa-user" aria-hidden="true"></i>
                <p class="error" id="name-error"></p>
              </div>
              <div class="fl" data-field="email">
                <input type="email" id="email" name="email" autocomplete="email" placeholder="name@cb.students.amrita.edu" aria-describedby="email-hint email-error">
                <label for="email">Email</label><i class="icon fa-solid fa-envelope" aria-hidden="true"></i>
                <p class="hint" id="email-hint">Your amrita.edu email is preferred</p>
                <p class="error" id="email-error"></p>
              </div>
              <div class="fl" data-field="roll">
                <input type="text" id="roll" name="roll" placeholder="CB.EN.U4CSE23001" autocapitalize="characters" spellcheck="false" aria-describedby="roll-hint roll-error">
                <label for="roll">Roll number</label><i class="icon fa-solid fa-id-card" aria-hidden="true"></i>
                <p class="hint" id="roll-hint">e.g. CB.EN.U4CSE23001</p>
                <p class="error" id="roll-error"></p>
              </div>
              <div class="fl" data-field="programme">
                <select id="programme" name="programme" aria-describedby="programme-error">
                  <option value=""></option>
{options}
                </select>
                <label for="programme">Programme</label><i class="icon fa-solid fa-chevron-down" aria-hidden="true"></i>
                <p class="error" id="programme-error"></p>
              </div>
              <div class="fl" data-field="phone">
                <input type="tel" id="phone" name="phone" autocomplete="tel" inputmode="tel" placeholder="98765 43210" aria-describedby="phone-hint phone-error">
                <label for="phone">Mobile <span class="opt">(optional)</span></label><i class="icon fa-solid fa-phone" aria-hidden="true"></i>
                <p class="hint" id="phone-hint">For WhatsApp group invites</p>
                <p class="error" id="phone-error"></p>
              </div>
              <fieldset class="pill-group full" data-field="year">
                <legend>Year of study</legend>
                <div class="pills">
{years}
                </div>
                <p class="error"></p>
              </fieldset>
            </div>
            <div class="step-nav">
              <p class="kbd-hint">Press <kbd>Enter</kbd> to continue</p>
              <button type="button" class="btn-next" data-next>Choose clubs <i class="fa-solid fa-arrow-right" aria-hidden="true"></i></button>
            </div>
          </div>

          <!-- Step 2 -->
          <div class="step" data-step="2">
            <div class="step-head">
              <span class="count">Step 2 of 3</span>
              <h2>Pick up to three clubs</h2>
              <p>Not sure? Choose what sounds fun. You can always join more later.</p>
            </div>
            <div class="club-grid" role="group" aria-label="Clubs">
{club_cards}
            </div>
            <div class="tray" data-field="clubs" aria-live="polite">
              <span class="tray-label">Your picks <b id="pick-count">0</b>/3</span>
              <div class="slots" id="slots"></div>
              <p class="error"></p>
            </div>
            <div class="step-nav">
              <button type="button" class="btn-back" data-back><i class="fa-solid fa-arrow-left" aria-hidden="true"></i> Back</button>
              <button type="button" class="btn-next" data-next>Review <i class="fa-solid fa-arrow-right" aria-hidden="true"></i></button>
            </div>
          </div>

          <!-- Step 3 -->
          <div class="step" data-step="3">
            <div class="step-head">
              <span class="count">Step 3 of 3</span>
              <h2>Almost there</h2>
              <p>Check your details, add a note for the clubs if you like, and send it off.</p>
            </div>
            <dl class="review" id="review"></dl>
            <div class="fl" data-field="why">
              <textarea id="why" name="why" maxlength="500" placeholder="Skills you'd like to learn, past experience, ideas for events…"></textarea>
              <label for="why">Why do you want to join? <span class="opt">(optional)</span></label>
              <span class="counter" id="why-count">0 / 500</span>
            </div>
            <div class="consent-wrap" data-field="consent">
              <label class="consent"><input type="checkbox" id="consent" name="consent"><span class="box" aria-hidden="true"><i class="fa-solid fa-check"></i></span><span>I agree to share these details with the clubs I've picked so they can contact me.</span></label>
              <p class="error"></p>
            </div>
            <div class="step-nav">
              <button type="button" class="btn-back" data-back><i class="fa-solid fa-arrow-left" aria-hidden="true"></i> Back</button>
              <button type="submit" class="btn-next" id="submit-btn"><i class="fa-solid fa-paper-plane" aria-hidden="true"></i> Submit registration</button>
            </div>
          </div>
        </div>
      </form>

      <div class="success" id="register-success" hidden>
        <svg class="check-anim" viewBox="0 0 84 84" aria-hidden="true"><circle cx="42" cy="42" r="40"/><path d="M26 43 l11 11 l21 -23"/></svg>
        <h2 tabindex="-1">You're in, <span data-first-name></span>!</h2>
        <p>Your registration is on its way to the club coordinators. Keep an eye on <strong data-email></strong> for induction dates.</p>
        <div class="pass-wrap">
          <div class="pass" id="pass">
            <div class="pass-top"><img src="{root}assets/img/logo.png" alt="Amrita"><span>Member pass</span></div>
            <p class="pass-name" data-pass-name></p>
            <p class="pass-sub" data-pass-sub></p>
            <div class="pass-clubs" data-pass-clubs></div>
            <div class="pass-foot">
              <div><small>Roll number</small><b data-pass-roll></b></div>
              <div class="barcode" data-barcode aria-hidden="true"></div>
            </div>
          </div>
        </div>
        <div class="success-actions">
          <a class="btn-next" href="{root}index.html#clubs">Explore your clubs <i class="fa-solid fa-arrow-right" aria-hidden="true"></i></a>
          <button type="button" class="btn-outline" id="register-again">Register someone else</button>
        </div>
        <p class="demo-note" id="demo-note" hidden>Demo mode: this form isn't connected to a database yet, so this registration wasn't stored.</p>
      </div>
    </div>
  </section>
</main>
<canvas id="confetti" aria-hidden="true"></canvas>
"""
    html += footer(root, scripts=("register.js",))
    out = ROOT / "register" / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")

if __name__ == "__main__":
    build_home()
    build_register()
    build_404()
    for i, club in enumerate(CLUBS):
        if not club.get("custom_page"):
            build_club(i, club)
    print(f"Built index.html, register/, 404.html and {sum(not c.get('custom_page') for c in CLUBS)} club pages.")
