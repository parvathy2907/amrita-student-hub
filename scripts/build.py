#!/usr/bin/env python3
"""Generate the static site from data/clubs.json.

Usage:  python3 scripts/build.py

Writes index.html, register/index.html and clubs/<slug>/index.html for every club. Clubs marked
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

e = escape


def v(rel):
    """Cache-busting query string: changes whenever the file's contents change."""
    digest = hashlib.sha1((ROOT / rel).read_bytes()).hexdigest()[:8]
    return f"{rel}?v={digest}"


def head(title, description, root, styles=()):
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
  <link rel="stylesheet" href="{root}{v('assets/css/style.css')}">
{"".join(f'  <link rel="stylesheet" href="{root}{v("assets/css/" + x)}">\n' for x in styles)}</head>
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
        <li><a class="btn" href="{root}register/">Register</a></li>
      </ul>
    </nav>
  </div>
</header>
"""


def footer(root, scripts=()):
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
<script src="{root}{v('assets/js/main.js')}" defer></script>
{"".join(f'<script src="{root}{v("assets/js/" + x)}" defer></script>\n' for x in scripts)}</body>
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
          <p>Sign up for up to three clubs with your college email. It takes two minutes.</p>
        </div>
        <a class="button" href="register/">Register now</a>
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
        <a class="button" href="{root}register/?club={c['slug']}">Register now</a>
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
    html += header(root)
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
              <p>Use your college email so the clubs can verify you're a student.</p>
            </div>
            <div class="grid-2">
              <div class="fl full" data-field="name">
                <input type="text" id="name" name="name" autocomplete="name" placeholder="e.g. Ananya Menon" aria-describedby="name-error">
                <label for="name">Full name</label><i class="icon fa-solid fa-user" aria-hidden="true"></i>
                <p class="error" id="name-error"></p>
              </div>
              <div class="fl" data-field="email">
                <input type="email" id="email" name="email" autocomplete="email" placeholder="name@cb.students.amrita.edu" aria-describedby="email-hint email-error">
                <label for="email">College email</label><i class="icon fa-solid fa-envelope" aria-hidden="true"></i>
                <p class="hint" id="email-hint">Must end in amrita.edu</p>
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
    for i, club in enumerate(CLUBS):
        if not club.get("custom_page"):
            build_club(i, club)
    print(f"Built index.html, register/ and {sum(not c.get('custom_page') for c in CLUBS)} club pages.")
