#!/usr/bin/env python3
"""Build the American Chairs site into plain HTML files in the repo root.

    python3 tools/build.py

Edit the settings and content in this file, then re-run it. The generated
.html files are committed so GitHub Pages can serve them as-is.
"""
import html
import json
import os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

# --------------------------------------------------------------------------
# Settings: fill these in when you have them. Empty = "coming soon".
# --------------------------------------------------------------------------
SITE_NAME = "American Chairs"
CONTACT_EMAIL = ""   # e.g. "support@yourdomain.com"
CONTACT_PHONE = ""   # e.g. "1-800-555-0100"
LAST_UPDATED = "November 17, 2026"

AI_CAPTION = "AI concept rendering &ndash; not a photo of the actual product"

# --------------------------------------------------------------------------
# The chairs we intend to carry (from research/us-made-chair-brands.md)
# --------------------------------------------------------------------------
CHAIRS = [
    {
        "slug": "concept-3150hr",
        "brand": "Concept Seating",
        "model": "3150HR 24/7 Operator Chair",
        "built": "Milwaukee, Wisconsin",
        "origin": "The maker says its chairs are &ldquo;handcrafted in Milwaukee, Wisconsin.&rdquo;",
        "capacity": "550 lbs",
        "duty": "24/7 intensive use",
        "price": "$1,957 &ndash; $4,400",
        "warranty": "6-year warranty, even in 24/7 use",
        "features": [
            "Heavy-duty <b>7-leg steel base</b> for extra stability",
            "Articulating, adjustable headrest",
            "Dymetrol&reg; suspension seat",
            "The workhorse of 911 dispatch centers and 24/7 control rooms",
        ],
        "ideal": "Dispatchers, all-night gamers, big &amp; tall users",
        "featured": True,
    },
    {
        "slug": "np-big-tall-247",
        "brand": "Neutral Posture",
        "model": "Big &amp; Tall 24/7 Chair (BTC10100)",
        "built": "Bryan, Texas",
        "origin": "Built at the maker&rsquo;s factory in Bryan, Texas. Exact country-of-origin wording will be confirmed with the maker, model by model, before launch.",
        "capacity": "500 lbs",
        "duty": "24/7 intensive use",
        "price": "$1,372 &ndash; $2,075",
        "warranty": "5-year warranty, even in 24/7 use",
        "features": [
            "Extra-wide <b>27&quot; seat</b> (23&quot; on the Jr. model)",
            "Steel-reinforced frame",
            "28&quot; heavy-duty base",
            "Oversized padded arms, optional headrest",
        ],
        "ideal": "Big &amp; tall gamers, programmers and remote workers",
        "featured": True,
    },
    {
        "slug": "era-chairman",
        "brand": "ERA Office Chairs",
        "model": "The Chairman 2-Piece Executive",
        "built": "Cerritos, California",
        "origin": "Cut, sewn and upholstered by hand onto steel frames in Cerritos, California (per California&rsquo;s Made in California manufacturer directory). Made to order: 8&ndash;12 weeks.",
        "capacity": "500 lbs",
        "duty": "24/7 rated",
        "price": "$3,689 &ndash; $3,989",
        "warranty": "",
        "features": [
            "Extra-wide <b>26&quot; seat</b> with seat slider",
            "Thick wrap-around pillow headrest",
            "Padded flip-up arms",
            "Steel inner frame on a 30&quot; base",
        ],
        "ideal": "Executives and big &amp; tall users who want plush comfort",
        "featured": False,
    },
    {
        "slug": "bodybilt-captain-3500",
        "brand": "BodyBilt",
        "model": "Captain 24/7 Chair (3500 Series)",
        "built": "Navasota, Texas",
        "origin": "The maker says its products are &ldquo;made in the USA in Navasota, Texas.&rdquo;",
        "capacity": "300 or 500 lbs, depending on configuration",
        "cap_short": "300 or 500 lbs",
        "duty": "24/7 intensive use",
        "price": "About $3,728",
        "warranty": "",
        "features": [
            "SKYDEX&reg; seat cushioning",
            "Optima 24/7 heavy-duty arms with padded tops",
            "Optional neck roll",
            "27&quot; Marquis base in black or polished chrome",
        ],
        "ideal": "Command centers, executives, long-shift professionals",
        "featured": False,
    },
    {
        "slug": "bodybilt-gx4",
        "brand": "BodyBilt",
        "model": "GX4 Gaming Chair",
        "built": "Navasota, Texas",
        "origin": "The maker says its products are &ldquo;made in the USA in Navasota, Texas.&rdquo;",
        "capacity": "Up to 500 lbs per the maker (confirm by configuration)",
        "cap_short": "Up to 500 lbs",
        "duty": "Long-session gaming",
        "price": "About $1,033",
        "warranty": "",
        "features": [
            "Extra-wide seat (22% wider, per the maker)",
            "Real office-chair ergonomics &ndash; no racing-seat bucket",
            "Contoured, upholstered back",
            "One of the very few gaming chairs built in America",
        ],
        "ideal": "Serious gamers and streamers",
        "featured": True,
    },
    {
        "slug": "seating-monterey-550",
        "brand": "Seating Inc.",
        "model": "Monterey II 550",
        "built": "Nunda, New York",
        "origin": "The maker says chairs are &ldquo;built to your order&hellip; at our factory in Western New York.&rdquo;",
        "capacity": "550 lbs",
        "duty": "Generous Fit line",
        "price": "Call for quote",
        "warranty": "15-year warranty",
        "features": [
            "550 Generous Fit line with reinforced steel substructure",
            "Fixed arms",
            "Built to order by a family-owned, woman-owned American company",
        ],
        "ideal": "Big &amp; tall users who want a long warranty",
        "featured": False,
    },
]

# --------------------------------------------------------------------------
# Made-in-USA brand guide (public version of the research)
# --------------------------------------------------------------------------
BRANDS = [
    ("Concept Seating", "Milwaukee area, Wisconsin", "&ldquo;Handcrafted in Milwaukee, Wisconsin&rdquo;",
     "24/7 dispatch chairs rated to 550 lbs; 800 lb bariatric model"),
    ("ERA Office Chairs", "Cerritos, California", "Hand cut, sewn and upholstered on steel frames in California (Made in California directory)",
     "Made-to-order 500 lb big &amp; tall executive chairs"),
    ("Seating Inc.", "Nunda, New York", "&ldquo;Built to your order&hellip; at our factory in Western New York&rdquo;",
     "400 lb Super Duty and 550 lb Generous Fit lines, 15-year warranty"),
    ("Neutral Posture", "Bryan, Texas", "Factory in Bryan, Texas &ndash; ask for each model&rsquo;s exact origin wording",
     "500 lb Big &amp; Tall 24/7 chair"),
    ("BodyBilt", "Navasota, Texas", "&ldquo;Made in the USA in Navasota, Texas&rdquo;",
     "24/7 Captain chairs and office-style gaming chairs"),
    ("Via Seating", "Sparks, Nevada", "&ldquo;Manufactured in Sparks, Nevada&rdquo; (some components imported)",
     "Brisbane HD 24/7, rated 350&ndash;450 lbs"),
    ("Herman Miller", "West Michigan", "Gaming chairs &ldquo;made in the U.S.&rdquo;",
     "Aeron, Mirra and the Embody Gaming chair"),
    ("Haworth", "Bruce, Mississippi (Fern)", "&ldquo;Assembled in the USA&rdquo;",
     "Fern and Zody task chairs"),
    ("Knoll", "East Greenville, Pennsylvania", "Generation chair manufactured in East Greenville",
     "Generation task chair"),
    ("Allsteel", "Muscatine, Iowa", "Acuity data sheet lists Muscatine as the manufacturing location",
     "Acuity; Lyric Large &amp; Tall (400 lbs)"),
    ("Humanscale", "New Jersey", "&ldquo;Made in New Jersey of U.S. and imported materials&rdquo; (retailer listing)",
     "Freedom chair"),
]


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
NAV = [
    ("index.html", "Home"),
    ("chairs.html", "The Chairs"),
    ("made-in-usa.html", "Made in USA Guide"),
    ("about.html", "About Us"),
    ("support.html", "Shipping &amp; Returns"),
    ("dealers.html", "For Manufacturers"),
    ("credits.html", "Photo Credits"),
]


def chair_img(slug):
    path = f"img/chairs/{slug}.jpg"
    if os.path.exists(os.path.join(ROOT, path)):
        return path, True
    return "img/retro/coming_soon.gif", False


def contact_line():
    parts = []
    if CONTACT_EMAIL:
        parts.append(f'E-mail: <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a>')
    else:
        parts.append("E-mail: <i>coming soon</i>")
    parts.append(f"Phone: {CONTACT_PHONE}" if CONTACT_PHONE else "Toll-free line: <i>coming soon</i>")
    return " &nbsp;|&nbsp; ".join(parts)


def notify_button(subject):
    if CONTACT_EMAIL:
        return f'<a class="btn" href="mailto:{CONTACT_EMAIL}?subject={html.escape(subject)}">E-mail me when it&rsquo;s available</a>'
    return '<span class="btn" title="Contact details coming soon">Notify me &ndash; coming soon</span>'


def page(filename, title, body, description):
    nav = "\n".join(
        f'      <a href="{href}"{" class=\"here\"" if href == filename else ""}>{label}</a>'
        for href, label in NAV
    )
    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<meta name="description" content="{description}">
<title>{title} - {SITE_NAME}</title>
<link rel="stylesheet" href="style.css">
<link rel="icon" href="img/retro/flag_small.gif">
</head>
<body>
<div class="page" id="top">

  <div class="header">
    <div class="row">
      <img class="flag" src="img/retro/flag_wave.gif" alt="">
      <a href="index.html"><img class="logo" src="img/retro/logo.png" alt="{SITE_NAME} - Proudly American-Owned"></a>
      <img class="flag" src="img/retro/flag_wave.gif" alt="">
    </div>
  </div>

  <div class="marquee">
    <marquee scrollamount="5">&#9733; WELCOME TO {SITE_NAME.upper()}! &#9733; HEAVY-DUTY OFFICE &amp; GAMING CHAIRS BUILT IN THE U.S.A. &#9733; 100% AMERICAN-OWNED &#9733; RATED UP TO 550 LBS &amp; 24/7 USE &#9733; GRAND OPENING COMING SOON! &#9733;</marquee>
  </div>

  <div class="poc"><b>PROOF OF CONCEPT:</b> this website is a preview. No orders are being accepted yet, and {SITE_NAME} is not currently an authorized dealer of the brands shown.</div>

  <div class="cols">
    <div class="nav">
      <div class="navtitle">&#9733; MAIN MENU &#9733;</div>
{nav}
      <div class="side">
        <img src="img/retro/flag_wave_big.gif" alt="Waving American flag" width="140">
        <img src="img/retro/btn_american_owned.gif" width="88" height="31" alt="American Owned">
        <img src="img/retro/btn_buy_american.gif" width="88" height="31" alt="Buy American!">
        <p><b>Sit Like<br>An American!</b></p>
      </div>
    </div>

    <div class="content">
{body}
    </div>
  </div>

  <div class="footer">
    <div class="buttons">
      <img src="img/retro/btn_american_owned.gif" width="88" height="31" alt="American Owned">
      <img src="img/retro/btn_freedom.gif" width="88" height="31" alt="Powered by Freedom">
      <img src="img/retro/btn_poc.gif" width="88" height="31" alt="Proof of Concept">
      <img src="img/retro/btn_800x600.gif" width="88" height="31" alt="Best viewed at 800x600">
    </div>
    <p>[ {" | ".join(f'<a href="{h}">{l}</a>' for h, l in NAV)} ]</p>
    <p>{contact_line()}</p>
    <p>&copy; 2026 {SITE_NAME} &ndash; An American-owned small business. &nbsp; <img src="img/retro/flag_small.gif" width="24" height="13" alt="" style="vertical-align:middle"></p>
    <p class="tiny">Proof of concept. No products are for sale. Brand and model names are trademarks of their respective owners and are used only to describe products we hope to carry; no endorsement is implied. Images labeled &ldquo;AI concept rendering&rdquo; are illustrations, not photos of the actual products. Prices are typical U.S. retail ranges and will follow each maker&rsquo;s minimum advertised price.</p>
    <p class="tiny">This page last updated {LAST_UPDATED}.</p>
  </div>

</div>
</body>
</html>
"""
    with open(os.path.join(ROOT, filename), "w") as f:
        f.write(doc)
    print("wrote", filename)


def product_card(c):
    img, is_ai = chair_img(c["slug"])
    cap = AI_CAPTION if is_ai else "Official photo coming soon"
    feats = "\n".join(f"          <li>{x}</li>" for x in c["features"])
    warranty = f"<br><b>Warranty:</b> {c['warranty']}" if c["warranty"] else ""
    return f"""
      <a name="{c['slug']}" id="{c['slug']}"></a>
      <div class="product">
        <div class="pic">
          <img src="{img}" alt="{c['brand']} {c['model']}" width="300">
          <div class="cap">{cap}</div>
        </div>
        <div class="info">
          <h3>{c['brand']} {c['model']}</h3>
          <div class="made"><img src="img/retro/flag_small.gif" width="24" height="13" alt="">BUILT IN {c['built'].upper()}</div>
          <p class="small"><i>{c['origin']}</i></p>
          <p><b>Weight capacity:</b> {c['capacity']}<br><b>Rated for:</b> {c['duty']}{warranty}<br><b>Great for:</b> {c['ideal']}</p>
          <ul>
{feats}
          </ul>
          <p><span class="price">Est. retail: {c['price']}</span></p>
          <p><span class="status blink">COMING SOON</span> &nbsp; {notify_button(c['brand'] + ' ' + html.unescape(c['model']))}</p>
        </div>
      </div>"""


# --------------------------------------------------------------------------
# Pages
# --------------------------------------------------------------------------
def build_index():
    featured = [c for c in CHAIRS if c["featured"]]
    cells = []
    for c in featured:
        img, is_ai = chair_img(c["slug"])
        cells.append(f"""
        <td align="center" width="33%">
          <img src="img/retro/new.gif" width="46" height="28" alt="New!"><br>
          <a href="chairs.html#{c['slug']}"><img src="{img}" alt="{c['brand']} {c['model']}" width="180"></a><br>
          <b><a href="chairs.html#{c['slug']}">{c['brand']}<br>{c['model']}</a></b><br>
          <span class="small">Built in {c['built']}<br>Holds {c.get('cap_short', c['capacity'])}</span>
        </td>""")
    hero, hero_ai = chair_img("hero-gaming-setup")
    hero_html = ""
    if hero_ai:
        hero_html = f"""
      <div class="photo">
        <img src="{hero}" alt="A heavy-duty office chair at a gaming and work desk with a small American flag" width="560">
        <div class="cap">{AI_CAPTION}</div>
      </div>"""
    body = f"""
      <p class="center"><img src="img/retro/under_construction.gif" width="468" height="60" alt="Pardon our dust! This site is a proof of concept."></p>

      <h1>Welcome to {SITE_NAME}!</h1>
      <p class="center"><b>Heavy-duty office, task &amp; gaming chairs <span class="red">BUILT IN THE U.S.A.</span><br>
      Hand-picked and supported by an <span class="blue">American-owned</span> small business.</b></p>
{hero_html}
      <img class="rule" src="img/retro/star_bar.gif" width="600" height="18" alt="">

      <h2>&#9733; Featured Chairs &#9733;</h2>
      <div class="tablewrap">
      <table class="retro featured">
        <tr>{''.join(cells)}
        </tr>
      </table>
      </div>
      <p class="center"><a href="chairs.html"><b>&gt;&gt; See ALL the chairs! &lt;&lt;</b></a></p>

      <h2>Who Sits Here?</h2>
      <ul class="stars">
        <li><b>Gamers &amp; streamers</b> who put in 8, 10, 12-hour sessions</li>
        <li><b>Software engineers &amp; remote workers</b> who sit for a living</li>
        <li><b>911 dispatchers &amp; 24/7 control rooms</b> where a chair never gets a day off</li>
        <li><b>Big &amp; tall folks</b> who are tired of chairs that give up &ndash; our picks are rated <b>400 to 550 lbs</b></li>
      </ul>

      <h2>Why Buy American-Made?</h2>
      <table class="retro">
        <tr><th>&#9733; Built to last</th><td>24/7 &ldquo;intensive use&rdquo; ratings and warranties of 5 to 15 years.</td></tr>
        <tr><th>&#9733; Parts &amp; service</th><td>Replacement parts come from factories here at home, not overseas.</td></tr>
        <tr><th>&#9733; American jobs</th><td>Your chair is cut, sewn and assembled by workers in Wisconsin, Texas, California and New York.</td></tr>
        <tr><th>&#9733; Honest labels</th><td>We use each maker&rsquo;s exact country-of-origin wording. No fuzzy flag-waving on imported goods. <a href="made-in-usa.html">Learn more</a>.</td></tr>
      </table>

      <div class="box blue">
        <h3><img src="img/retro/star_spin.gif" width="18" height="18" alt=""> Are you a manufacturer or sales rep?</h3>
        <p>We&rsquo;d love to carry your American-made seating. <a href="dealers.html"><b>Click here for dealer inquiries!</b></a></p>
      </div>

      <p class="center"><img src="img/retro/flag_wave_big.gif" alt="Waving American flag" width="200"></p>
      <p class="center small"><i>&ldquo;Built to outlast the grind.&rdquo;</i></p>
"""
    page("index.html", "Home", body,
         "American-owned retailer of heavy-duty, American-made office, task and gaming chairs. Proof of concept.")


def build_chairs():
    cards = "\n".join(product_card(c) for c in CHAIRS)
    rows = "\n".join(
        f"        <tr><td><a href=\"#{c['slug']}\">{c['brand']} {c['model']}</a></td><td>{c['built']}</td>"
        f"<td>{c.get('cap_short', c['capacity'])}</td><td>{c['price']}</td></tr>"
        for c in CHAIRS
    )
    body = f"""
      <h1>The Chairs</h1>
      <p class="center"><b>Every chair below is built in an American factory and rated for heavy, long-hour use.</b></p>
      <div class="box">
        <p class="small"><b>Please note:</b> this is a proof-of-concept catalog. Pictures marked
        &ldquo;AI concept rendering&rdquo; were made with Google Gemini from written descriptions; they are
        <u>not</u> photos of the actual products. We&rsquo;ll replace them with each maker&rsquo;s official
        photography once we&rsquo;re an authorized dealer. Prices are typical U.S. retail ranges, not offers.</p>
      </div>

      <h2>Quick Comparison</h2>
      <div class="tablewrap">
      <table class="retro">
        <tr><th>Chair</th><th>Built in</th><th>Holds</th><th>Est. retail</th></tr>
{rows}
      </table>
      </div>

      <img class="rule" src="img/retro/rwb_bar.gif" width="600" height="9" alt="">
{cards}

      <p class="center"><a href="#top">Back to top</a> &nbsp;|&nbsp; <a href="made-in-usa.html">How we check &ldquo;Made in USA&rdquo;</a></p>
"""
    page("chairs.html", "The Chairs", body,
         "Heavy-duty American-made office, task and gaming chairs rated 300 to 550 lbs.")


def build_made_in_usa():
    with open(os.path.join(ROOT, "tools", "stock_credits.json")) as f:
        stock = json.load(f)
    rows = "\n".join(
        f"        <tr><td><b>{b}</b></td><td>{where}</td><td>{says}</td><td>{known}</td></tr>"
        for b, where, says, known in BRANDS
    )
    gallery = "\n".join(
        f"""        <div class="photo"><img src="{s['file']}" alt="{s['title']}" width="200"><div class="cap">{s['title']}<br>Photo: {s['creator']}, <a href="{s['license_url']}">{s['license']}</a></div></div>"""
        for s in stock
    )
    eagle, eagle_ai = chair_img("eagle-clipart")
    eagle_html = f'<p class="center"><img src="{eagle}" alt="Bald eagle clip art" width="160"></p>' if eagle_ai else ""
    body = f"""
      <h1>The &ldquo;Made in U.S.A.&rdquo; Guide</h1>
{eagle_html}
      <p class="center"><b>Who still builds office chairs in America? We looked it up so you don&rsquo;t have to.</b></p>

      <h2>How to Read a &ldquo;Made in USA&rdquo; Claim</h2>
      <p>The Federal Trade Commission has strict rules about the words &ldquo;Made in USA.&rdquo; Here&rsquo;s the plain-English version:</p>
      <table class="retro">
        <tr><th>The label says&hellip;</th><th>What it means</th></tr>
        <tr><td><b>&ldquo;Made in USA&rdquo;</b></td><td>&ldquo;All or virtually all&rdquo; of the product &ndash; parts, processing and labor &ndash; is from the U.S.</td></tr>
        <tr><td><b>&ldquo;Assembled in USA&rdquo;</b></td><td>The final, substantial assembly happened here, but some parts may be imported.</td></tr>
        <tr><td><b>&ldquo;Made in USA of U.S. and imported parts&rdquo;</b></td><td>A qualified claim: built here, with a meaningful share of imported content.</td></tr>
      </table>
      <p>That&rsquo;s why every chair on our site shows the <b>maker&rsquo;s own wording</b> about where it is built, and why we never
      put flags next to imported products. Some famous &ldquo;American&rdquo; brands build many of their chairs in other countries &ndash;
      always check the country-of-origin label.</p>

      <img class="rule" src="img/retro/star_bar.gif" width="600" height="18" alt="">

      <h2>American Chair Makers</h2>
      <div class="tablewrap">
      <table class="retro">
        <tr><th>Brand</th><th>Where it&rsquo;s built</th><th>What the maker says</th><th>Known for</th></tr>
{rows}
      </table>
      </div>
      <p class="tiny">Compiled November 2026 from makers&rsquo; published materials, retailer listings and state manufacturer directories.
      Origin can vary by model; always confirm the specific chair.</p>

      <h2>American Design Classics</h2>
      <p>Herman Miller has been building furniture in West Michigan for over a century. Its Aeron and Mirra chairs are icons of
      American office design:</p>
      <div class="gallery">
{gallery}
      </div>
"""
    page("made-in-usa.html", "Made in USA Guide", body,
         "Which office chair brands are still built in the USA, and how to read a Made in USA label.")


def build_about():
    body = """
      <h1>About Us</h1>
      <p class="center"><img src="img/retro/flag_wave_big.gif" alt="Waving American flag" width="180"></p>

      <h2>Our Story</h2>
      <p>{name} is a small, <b>American-owned</b> business with a simple idea: people who sit for a living deserve chairs
      that are built to last &ndash; and built here at home.</p>
      <p>Most &ldquo;gaming chairs&rdquo; are imported racing seats with thin foam and peeling faux leather. Meanwhile, American
      factories in Wisconsin, Texas, California and New York quietly build chairs for 911 dispatch centers that are rated for
      <b>24 hours a day, 7 days a week</b>, and for people up to <b>550 lbs</b>. We think gamers, coders and remote
      workers deserve to know those chairs exist.</p>

      <h2>Our Promise</h2>
      <ul class="stars">
        <li><b>Honest labels.</b> We use each maker&rsquo;s exact country-of-origin wording. Period.</li>
        <li><b>Heavy-duty first.</b> We focus on chairs rated for 24/7 use and big &amp; tall users.</li>
        <li><b>Real people.</b> When we open, your call or e-mail will be answered by a real person in the U.S.</li>
        <li><b>Straight pricing.</b> We follow each maker&rsquo;s advertised pricing. No fake &ldquo;90% off&rdquo; sales.</li>
      </ul>

      <div class="box">
        <h3>Status: Under Construction</h3>
        <p>This site is a proof of concept. We are not yet taking orders and are not yet an authorized dealer of the brands shown.
        Check back soon!</p>
      </div>
""".replace("{name}", SITE_NAME)
    page("about.html", "About Us", body, f"About {SITE_NAME}, an American-owned seating retailer.")


def build_support():
    body = """
      <h1>Shipping, Returns &amp; Warranty</h1>
      <div class="box"><p class="small"><b>DRAFT POLICIES:</b> these will be finalized, and matched to each manufacturer&rsquo;s terms,
      before we accept any orders.</p></div>

      <h2>Shipping</h2>
      <ul class="stars">
        <li>Chairs ship directly from the manufacturer in the U.S.</li>
        <li>Many chairs are <b>built to order</b>. Lead times range from about 1 week to 12 weeks depending on the maker
        (for example, ERA chairs take about 8&ndash;12 weeks). Each product page will show its lead time.</li>
        <li>Shipping cost will be shown before you pay. No surprises.</li>
      </ul>

      <h2>Returns</h2>
      <ul class="stars">
        <li>Unused chairs in original packaging may be returned within <b>30 days</b> of delivery.</li>
        <li>Opened, non-defective returns may carry a <b>restocking fee of 15%&ndash;25%</b>, matching the manufacturer&rsquo;s fee.
        The exact fee will be shown on each product page <u>before</u> you buy.</li>
        <li>Made-to-order or custom-upholstered chairs may be final sale. This will also be shown before you buy.</li>
        <li><b>No restocking fee, ever, on defective or damaged chairs.</b> We&rsquo;ll make it right.</li>
        <li>Please inspect your delivery and report any freight damage within 48 hours.</li>
      </ul>

      <h2>Warranty</h2>
      <p>Every chair carries its manufacturer&rsquo;s warranty &ndash; often 5 to 15 years, including 24/7 use on intensive-use models.
      We handle the paperwork with the factory for you.</p>

      <h2>Contact</h2>
      <p>{contact}</p>
""".replace("{contact}", contact_line())
    page("support.html", "Shipping & Returns", body, "Draft shipping, returns and warranty policies.")


def build_dealers():
    body = """
      <h1>Attention Manufacturers &amp; Reps!</h1>
      <p class="center"><b>We want to sell your American-made seating.</b></p>

      <h2>Who We Are</h2>
      <p>{name} is an American-owned online specialty retailer focused on one niche: <b>heavy-duty, 24/7 and big &amp; tall
      seating</b> for gamers, software engineers, remote workers and 24/7 operations. Our whole pitch is
      &ldquo;built in America, built to last&rdquo; &ndash; so we only want to carry chairs that are.</p>

      <h2>Our Commitments to You</h2>
      <table class="retro">
        <tr><th>&#9733; Pricing</th><td>We honor your minimum advertised price (MAP) policy.</td></tr>
        <tr><th>&#9733; Channels</th><td>We sell only on our own website. No Amazon, eBay or discount marketplaces.</td></tr>
        <tr><th>&#9733; Accuracy</th><td>We use your official photography, specifications and exact country-of-origin wording.</td></tr>
        <tr><th>&#9733; Support</th><td>Tier-1 customer support handled in the U.S., by us.</td></tr>
        <tr><th>&#9733; Content</th><td>We&rsquo;ll purchase a demo chair to create our own reviews and video demonstrations.</td></tr>
        <tr><th>&#9733; Drop ship</th><td>We&rsquo;re set up for factory drop shipping direct to the end customer.</td></tr>
      </table>

      <h2>Get in Touch</h2>
      <p>{contact}</p>
      <p class="small">This website is a proof of concept prepared for dealer applications. The product listings show how we would
      present your chairs; they are not live offers.</p>
""".replace("{name}", SITE_NAME).replace("{contact}", contact_line())
    page("dealers.html", "For Manufacturers", body, "Dealer inquiries for American seating manufacturers.")


def build_credits():
    with open(os.path.join(ROOT, "tools", "stock_credits.json")) as f:
        stock = json.load(f)
    stock_rows = "\n".join(
        f"""        <tr><td><img src="{s['file']}" width="60" alt=""></td><td>&ldquo;{s['title']}&rdquo;</td><td>{s['creator']}</td>
          <td><a href="{s['license_url']}">{s['license']}</a></td><td><a href="{s['source_url']}">Source</a></td></tr>"""
        for s in stock
    )
    body = f"""
      <h1>Photo Credits</h1>

      <h2>Stock Photos</h2>
      <p>These photos are used under Creative Commons licenses. They are shown at reduced size; no other changes were made.</p>
      <div class="tablewrap">
      <table class="retro">
        <tr><th></th><th>Title</th><th>Photographer</th><th>License</th><th>Original</th></tr>
{stock_rows}
      </table>
      </div>

      <h2>AI-Generated Images</h2>
      <p>Images labeled <b>&ldquo;AI concept rendering&rdquo;</b> were generated with <b>Google Gemini</b> from written descriptions
      of each chair. They are illustrations to show how our catalog will look. They are <u>not</u> photographs of the actual
      products and may differ from them. They will be replaced with official manufacturer photography.</p>

      <h2>Graphics</h2>
      <p>The flags, banners, buttons and other retro graphics on this site were drawn from scratch for {SITE_NAME}.</p>

      <h2>Trademarks</h2>
      <p class="small">All brand and model names are trademarks of their respective owners. They are used only to identify products
      we intend to carry. {SITE_NAME} is not affiliated with, endorsed by, or currently an authorized dealer of any brand shown.</p>
"""
    page("credits.html", "Photo Credits", body, "Photo credits, licenses and AI image disclosure.")


if __name__ == "__main__":
    build_index()
    build_chairs()
    build_made_in_usa()
    build_about()
    build_support()
    build_dealers()
    build_credits()
