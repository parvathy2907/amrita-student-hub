#!/usr/bin/env python3
"""Generate the static site from data/clubs.json.

Usage:  python3 scripts/build.py

Writes index.html and clubs/<slug>/index.html for every club. Clubs marked
"custom_page": true keep their hand-written clubs/<slug>/index.html.
No dependencies beyond the Python 3 standard library.
"""
import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLUBS = json.loads((ROOT / "data" / "clubs.json").read_text(encoding="utf-8"))
REGISTER_URL = "https://sanjanav2102.github.io/AMRITA-student-clubs-website/Login/index.html"

ICONS = {
    "instagram": "fa-brands fa-instagram",
    "facebook": "fa-brands fa-facebook-f",
    "youtube": "fa-brands fa-youtube",
    "linkedin": "fa-brands fa-linkedin-in",
    "x": "fa-brands fa-x-twitter",
    "globe": "fa-solid fa-globe",
}

e = escape


def head(title, description, root):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{e(title)}</title>
  <meta name="description" content="{e(description)}">
  <meta property="og:title" content="{e(title)}">
  <meta property="og:description" content="{e(description)}">
  <link rel="icon" type="image/png" href="{root}assets/img/favicon.png">
  <link rel="preload" href="{root}assets/vendor/fonts/inter-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="{root}assets/vendor/fonts/fonts.css">
  <link rel="stylesheet" href="{root}assets/vendor/fontawesome/css/fontawesome.min.css">
  <link rel="stylesheet" href="{root}assets/vendor/fontawesome/css/solid.min.css">
  <link rel="stylesheet" href="{root}assets/vendor/fontawesome/css/brands.min.css">
  <link rel="stylesheet" href="{root}assets/css/style.css">
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
"""


def header(root, current=None):
    links = [
        ("Clubs", f"{root}index.html#clubs"),
        ("About", f"{root}index.html#about"),
        ("Events", "https://www.amrita.edu/events/"),
        ("Admissions", "https://www.amrita.edu/admissions/"),
    ]
    items = "\n".join(f'        <li><a href="{href}">{label}</a></li>' for label, href in links)
    return f"""<header class="site-header">
  <div class="wrap">
    <a class="brand" href="{root}index.html">
      <img src="{root}assets/img/logo-dark.png" alt="Amrita Vishwa Vidyapeetham" width="142" height="40">
      <span>Student Hub</span>
    </a>
    <button class="nav-toggle" aria-label="Menu" aria-expanded="false" aria-controls="site-nav"><i class="fa-solid fa-bars"></i></button>
    <nav class="nav" id="site-nav" aria-label="Main">
      <ul>
{items}
        <li><a class="btn" href="{REGISTER_URL}" target="_blank" rel="noopener">Register</a></li>
      </ul>
    </nav>
  </div>
</header>
"""


def footer(root):
    campuses = ["Amritapuri", "Amaravati", "Bengaluru", "Chennai", "Coimbatore", "Faridabad", "Kochi", "Mysuru"]
    campus_li = "\n".join(
        f'          <li><a href="https://www.amrita.edu/campus/{c.lower()}/">{c}</a></li>' for c in campuses
    )
    club_li = "\n".join(
        f'          <li><a href="{root}clubs/{c["slug"]}/">{e(c["name"])}</a></li>' for c in CLUBS[:6]
    )
    return f"""<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div>
        <h4>Campuses</h4>
        <ul>
{campus_li}
        </ul>
      </div>
      <div>
        <h4>Clubs</h4>
        <ul>
{club_li}
          <li><a href="{root}index.html#clubs">All clubs &rarr;</a></li>
        </ul>
      </div>
      <div>
        <h4>Apply</h4>
        <ul>
          <li><a href="https://www.amrita.edu/admissions/">Admissions</a></li>
          <li><a href="https://www.amrita.edu/admissions/btech/">B.Tech applications</a></li>
          <li><a href="https://www.amrita.edu/contact/">Contact Amrita</a></li>
        </ul>
      </div>
      <div>
        <h4>Follow Amrita</h4>
        <div class="footer-social">
          <a href="https://www.facebook.com/AmritaUniversity" aria-label="Facebook"><i class="fa-brands fa-facebook-f"></i></a>
          <a href="https://x.com/AMRITAedu" aria-label="X"><i class="fa-brands fa-x-twitter"></i></a>
          <a href="https://www.instagram.com/amrita_university/" aria-label="Instagram"><i class="fa-brands fa-instagram"></i></a>
          <a href="https://www.linkedin.com/school/amrita-vishwa-vidyapeetham-official/" aria-label="LinkedIn"><i class="fa-brands fa-linkedin-in"></i></a>
        </div>
      </div>
    </div>
    <div class="footer-bottom">A student UI design project showcasing clubs at Amrita Vishwa Vidyapeetham. Not an official university website.</div>
  </div>
</footer>
<script src="{root}assets/js/main.js" defer></script>
</body>
</html>
"""


def card(c, root):
    return f"""      <a class="card" href="{root}clubs/{c['slug']}/" data-category="{e(c['category'])}">
        <div class="card-media"><img src="{root}assets/img/cards/{c['card']}" alt="" loading="lazy" width="800" height="500"></div>
        <div class="card-body">
          <div class="tag">{e(c['category'])}</div>
          <h3>{e(c['name'])}</h3>
          <p>{e(c['tagline'])}</p>
          <span class="more">Explore club &rarr;</span>
        </div>
      </a>"""


def build_home():
    root = ""
    cats = ["All"] + sorted({c["category"] for c in CLUBS})
    chips = "\n".join(
        f'        <button class="chip" data-filter="{e(cat)}" aria-pressed="{str(cat == "All").lower()}">{e(cat)}</button>'
        for cat in cats
    )
    cards = "\n".join(card(c, root) for c in CLUBS)
    html = head("AMRITA Student Hub — Student Clubs",
                "Discover every student club at Amrita Vishwa Vidyapeetham, Coimbatore: music, dance, tech, service, literature and more.",
                root)
    html += header(root)
    html += f"""<main id="main">
  <section class="hero" style="background-image:url('assets/img/hero.jpg')">
    <div class="wrap">
      <span class="eyebrow">Amrita Vishwa Vidyapeetham &middot; Coimbatore</span>
      <h1>Find your club.</h1>
      <p>{len(CLUBS)} student clubs for music, dance, technology, service, literature and more — all in one place.</p>
    </div>
  </section>

  <section class="section" id="about">
    <div class="wrap prose">
      <h2>Student clubs at Amrita</h2>
      <p>To further the overall development of students, participation in a wide range of extra-curricular, social and community development activities is encouraged. Associations like Toastmasters, GDSC and Srishti, along with clubs like Elite, Anantham, Intel IoT and the Photography Club, help bring out students' creative talents and promote team spirit.</p>
      <p>Associations like NSS (National Service Scheme) and the Nature Club give students a platform to engage in humanitarian and environmental work.</p>
    </div>
  </section>

  <section class="section" id="clubs">
    <div class="wrap">
      <div class="section-head">
        <h2>Explore clubs</h2>
      </div>
      <div class="toolbar">
        <div class="chips" role="group" aria-label="Filter by category">
{chips}
        </div>
        <label class="search">
          <i class="fa-solid fa-magnifying-glass" aria-hidden="true"></i>
          <input id="club-search" type="search" placeholder="Search clubs" aria-label="Search clubs">
        </label>
      </div>
      <div class="grid" id="club-grid">
{cards}
      </div>
      <p class="empty" id="no-results" hidden>No clubs match that search.</p>
    </div>
  </section>

  <section class="section">
    <div class="wrap">
      <div class="cta">
        <div>
          <h2>Ready to join?</h2>
          <p>Register with your college email to sign up for clubs.</p>
        </div>
        <a class="button" href="{REGISTER_URL}" target="_blank" rel="noopener">Register now</a>
      </div>
    </div>
  </section>
</main>
"""
    html += footer(root)
    (ROOT / "index.html").write_text(html, encoding="utf-8")


def build_club(i, c):
    root = "../../"
    name = c["name"]
    full = c.get("full_name")
    title = f"{name} — AMRITA Student Hub"
    desc = c["tagline"]
    parts = []

    about = "\n".join(f"        <p>{e(p)}</p>" for p in c.get("about", []))
    pillars = ""
    if c.get("pillars"):
        pillars = '      <div class="pillars">\n' + "\n".join(
            f'        <div class="pillar"><h3>{e(p["heading"])}</h3><p>{e(p["text"])}</p></div>' for p in c["pillars"]
        ) + "\n      </div>"
    parts.append(f"""  <section class="section" id="about">
    <div class="wrap">
      <h2>About {e(name)}</h2>
      <div class="prose">
{about}
      </div>
{pillars}
    </div>
  </section>""")

    if c.get("highlights"):
        blocks = []
        for h in c["highlights"]:
            body = []
            for s in h["sections"]:
                if s.get("heading"):
                    body.append(f'        <h4>{e(s["heading"])}</h4>')
                body.append(f'        <p>{e(s["text"])}</p>')
            if h.get("quote"):
                body.append(f'        <blockquote>&ldquo;{e(h["quote"])}&rdquo;</blockquote>')
            date = f'        <div class="date">{e(h["date"])}</div>\n' if h.get("date") else ""
            imgs = "\n".join(
                f'        <a href="{im}" data-lightbox="{im}"><img src="{im}" alt="{e(h["title"])}" loading="lazy"></a>'
                for im in h.get("images", [])
            )
            blocks.append(f"""      <article class="highlight">
        <div>
{date}        <h3>{e(h['title'])}</h3>
{chr(10).join(body)}
        </div>
        <div class="highlight-media">
{imgs}
        </div>
      </article>""")
        parts.append(f"""  <section class="section" id="highlights">
    <div class="wrap">
      <h2>Highlights</h2>
{chr(10).join(blocks)}
    </div>
  </section>""")

    if c.get("gallery"):
        items = "\n".join(
            f'        <button type="button" data-lightbox="{im}" aria-label="Open photo {n} of {len(c["gallery"])}"><img src="{im}" alt="{e(name)} photo {n}" loading="lazy"></button>'
            for n, im in enumerate(c["gallery"], 1)
        )
        parts.append(f"""  <section class="section" id="gallery">
    <div class="wrap">
      <h2>Gallery</h2>
      <div class="gallery">
{items}
      </div>
    </div>
  </section>""")

    if c.get("videos"):
        vids = "\n".join(
            f'        <video src="{v}" poster="{v[:-4]}-poster.jpg" muted loop playsinline controls preload="none" data-autoplay></video>'
            for v in c["videos"]
        )
        parts.append(f"""  <section class="section" id="videos">
    <div class="wrap">
      <h2>Videos</h2>
      <div class="videos">
{vids}
      </div>
    </div>
  </section>""")

    if c.get("socials"):
        links = "\n".join(
            f'        <a class="social" href="{e(s["url"])}" target="_blank" rel="noopener"><i class="{ICONS[s["type"]]}" aria-hidden="true"></i>{e(s["label"])}</a>'
            for s in c["socials"]
        )
        parts.append(f"""  <section class="section" id="follow">
    <div class="wrap">
      <h2>Follow {e(name)}</h2>
      <div class="socials">
{links}
      </div>
    </div>
  </section>""")

    prev_c = CLUBS[i - 1]
    next_c = CLUBS[(i + 1) % len(CLUBS)]
    parts.append(f"""  <section class="section">
    <div class="wrap">
      <div class="cta">
        <div>
          <h2>Want to join {e(name)}?</h2>
          <p>Register with your college email to sign up.</p>
        </div>
        <a class="button" href="{REGISTER_URL}" target="_blank" rel="noopener">Register now</a>
      </div>
    </div>
  </section>
  <section class="section">
    <div class="wrap pager">
      <a class="prev" href="../{prev_c['slug']}/"><small>&larr; Previous club</small><strong>{e(prev_c['name'])}</strong></a>
      <a class="next" href="../{next_c['slug']}/"><small>Next club &rarr;</small><strong>{e(next_c['name'])}</strong></a>
    </div>
  </section>""")

    subtitle = f"\n      <p>{e(full)}</p>" if full else f"\n      <p>{e(c['tagline'])}</p>"
    html = head(title, desc, root) + header(root)
    html += f"""<main id="main">
  <section class="hero" style="background-image:url('{c['hero']}')">
    <div class="wrap">
      <a class="back-link" href="{root}index.html#clubs"><i class="fa-solid fa-arrow-left" aria-hidden="true"></i> All clubs</a><br>
      <span class="eyebrow">{e(c['category'])}</span>
      <h1>{e(name)}</h1>{subtitle}
    </div>
  </section>
{chr(10).join(parts)}
</main>
"""
    html += footer(root)
    out = ROOT / "clubs" / c["slug"] / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")


if __name__ == "__main__":
    build_home()
    for i, club in enumerate(CLUBS):
        if not club.get("custom_page"):
            build_club(i, club)
    print(f"Built index.html and {sum(not c.get('custom_page') for c in CLUBS)} club pages.")
