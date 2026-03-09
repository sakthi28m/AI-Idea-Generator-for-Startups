from flask import Flask, render_template, request, redirect, url_for, session, g
import random
import sqlite3
import os
import json
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "startup_secret_key_2026"

USER_EMAIL = "admin@gmail.com"
USER_PASSWORD = "1234"

DB_PATH = os.path.join(os.path.dirname(__file__), "data.db")

# Ensure DB exists and provide helper
def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
    return db


def init_db():
    if not os.path.exists(DB_PATH):
        db = sqlite3.connect(DB_PATH)
        cur = db.cursor()
        # users: id, email, password_hash
        cur.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
        """)
        # favorites: id, user_email, idea_json, created_at
        cur.execute("""
        CREATE TABLE favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT NOT NULL,
            idea_json TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """)
        # history: id, user_email, domain, count, duration, investment, created_at
        cur.execute("""
        CREATE TABLE history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT NOT NULL,
            domain TEXT,
            count INTEGER,
            duration INTEGER,
            investment INTEGER,
            created_at TEXT NOT NULL
        )
        """)
        # create demo user
        demo_hash = generate_password_hash(USER_PASSWORD)
        cur.execute("INSERT INTO users (email, password_hash) VALUES (?,?)", (USER_EMAIL, demo_hash))
        db.commit()
        db.close()


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

# initialize DB file if missing
init_db()

problem_statements = [
    "small businesses struggle to reach the right customers online",
    "students find it hard to choose the right career path",
    "freelancers waste time managing invoices and clients manually",
    "farmers do not get real-time crop health insights",
    "people face difficulty tracking their mental wellness consistently",
    "local shops lose customers because they lack digital presence",
    "startups struggle to validate product ideas quickly",
    "urban commuters face confusion with changing bus and train timings"
]

audiences = [
    "college students",
    "working professionals",
    "startup founders",
    "small business owners",
    "farmers",
    "freelancers",
    "parents",
    "urban commuters"
]

solutions = [
    "an AI-powered recommendation engine",
    "a smart chatbot assistant",
    "a predictive analytics platform",
    "an AI mentor system",
    "an automated mobile-first dashboard",
    "a voice-enabled virtual assistant",
    "a personalized idea validation tool",
    "a real-time decision support app"
]

monetization_models = [
    "monthly subscription plans",
    "freemium with premium AI insights",
    "commission per successful lead",
    "B2B SaaS licensing",
    "pay-per-use model",
    "enterprise dashboard subscriptions",
    "ad-free premium memberships",
    "white-label business plans"
]

unique_features = [
    "personalized AI suggestions",
    "real-time market trend analysis",
    "smart competitor comparison",
    "pitch deck generation",
    "voice-based interaction",
    "multilingual support",
    "predictive growth scoring",
    "auto-generated customer personas"
]

taglines = [
    "Build smarter. Launch faster.",
    "Ideas powered by intelligence.",
    "From concept to company with AI.",
    "Your startup idea, reimagined by AI.",
    "Innovate faster with creative intelligence.",
    "Turning domains into disruptive startups."
]

startup_names_prefix = [
    "Nova", "Spark", "Vision", "Next", "Grow", "Hyper", "Alpha", "Bright",
    "Smart", "Neo", "Launch", "Pulse", "Aero", "Orbit", "Flow", "Elevate"
]

startup_names_suffix = [
    "Labs", "AI", "Hive", "Works", "Base", "Bot", "Grid", "Sense",
    "Pilot", "Forge", "Bridge", "Boost", "Loop", "Nest", "Sphere", "Sync"
]


def generate_startup_name(domain):
    first = random.choice(startup_names_prefix)
    second = random.choice(startup_names_suffix)
    domain_part = domain.strip().title().replace(" ", "")
    styles = [
        f"{first}{second}",
        f"{domain_part}{second}",
        f"{first}{domain_part}",
        f"{domain_part}{first}",
        f"{first}{domain_part}{second}"
    ]
    return random.choice(styles)


def generate_idea_variant(domain, strategy=None):
    """Generate a single idea variant. strategy can influence how pieces are combined."""
    selected_problem = random.choice(problem_statements)
    selected_audience = random.choice(audiences)
    selected_solution = random.choice(solutions)
    selected_monetization = random.choice(monetization_models)
    selected_feature = random.choice(unique_features)
    selected_tagline = random.choice(taglines)
    startup_name = generate_startup_name(domain)

    # Different template styles to diversify output
    idea_templates = [
        f"{startup_name} is {selected_solution} for {selected_audience} in the {domain} space. It solves the problem that {selected_problem}. The platform stands out with {selected_feature} and earns revenue through {selected_monetization}.",
        f"In the {domain} domain, {startup_name} helps {selected_audience} by offering {selected_solution}. It addresses a major issue where {selected_problem}. Its USP is {selected_feature}, and the business can scale using {selected_monetization}.",
        f"{startup_name} is a creative startup idea for {domain}. It is built for {selected_audience} and uses {selected_solution} to solve how {selected_problem}. With {selected_feature}, it becomes more powerful, while revenue comes from {selected_monetization}.",
        f"A futuristic startup in {domain}, {startup_name} uses {selected_solution} for {selected_audience}. It focuses on solving the challenge that {selected_problem}. The most exciting feature is {selected_feature}, and its monetization strategy is {selected_monetization}."
    ]

    # Strategy modifiers (lightweight, local heuristics to diversify content)
    if strategy == "problem_first":
        idea = f"Problem: {selected_problem}. Solution: {selected_solution} for {selected_audience}. {startup_name} provides {selected_feature} and monetizes via {selected_monetization}."
    elif strategy == "market_first":
        idea = f"Market: {domain} — {selected_audience} need {selected_solution}. {startup_name} delivers {selected_feature}, turning value into {selected_monetization}."
    else:
        idea = random.choice(idea_templates)

    # estimate initial investment as numeric value and formatted display
    ivalue = estimate_initial_investment(domain, selected_feature)
    ivalue_display = f"${ivalue:,}"

    return {
        "startup_name": startup_name,
        "domain": domain,
        "idea": idea,
        "audience": selected_audience,
        "feature": selected_feature,
        "monetization": selected_monetization,
        "tagline": selected_tagline,
        # estimate fields for detail view
        "initial_investment_value": ivalue,
        "initial_investment": ivalue_display,
        "best_platform": pick_best_platform(selected_feature),
        "projected_annual_revenue": estimate_annual_revenue(domain, selected_feature),
        "peak_period": estimate_peak_period(domain)
    }


def generate_ideas(domain, count=4, strategy=None):
    """Generate `count` distinct idea variants with optional strategy. Attempts to reduce repetition by ensuring uniqueness where possible."""
    results = []
    attempts = 0
    max_attempts = count * 6
    seen_texts = set()

    while len(results) < count and attempts < max_attempts:
        attempts += 1
        candidate = generate_idea_variant(domain, strategy=strategy)
        text = candidate["idea"]
        # simple uniqueness filter
        if text in seen_texts:
            continue
        seen_texts.add(text)
        results.append(candidate)

    # If we couldn't find enough unique ones, allow duplicates but shuffle
    if len(results) < count:
        while len(results) < count:
            results.append(generate_idea_variant(domain, strategy=strategy))

    random.shuffle(results)
    return results


# --- Lightweight heuristics for detail fields ---
def estimate_initial_investment(domain, feature):
    """Return a rough USD estimate as an integer based on domain/feature complexity."""
    base = 20000
    if "enterprise" in domain.lower() or "b2b" in domain.lower():
        base = 50000
    if "voice" in feature or "real-time" in feature or "predictive" in feature:
        base += 30000
    # add randomness and return integer value
    return random.randint(int(base * 0.6), int(base * 1.6))


def pick_best_platform(feature):
    platforms = ["Mobile app", "Web app", "SaaS dashboard", "Marketplace", "Mobile + Web"]
    # heuristic
    if "voice" in feature:
        return "Mobile app (voice-native)"
    if "dashboard" in feature or "analytics" in feature:
        return "SaaS dashboard"
    return random.choice(platforms)


def estimate_annual_revenue(domain, feature):
    # simple projection based on domain buzz
    mult = 120000
    if "fin" in domain.lower():
        mult = 300000
    if "health" in domain.lower():
        mult = 200000
    return f"~${random.randint(int(mult*0.6), int(mult*1.8)):,} / year"


def estimate_peak_period(domain):
    # Return either a season (e.g. "Spring (Mar-May)") or a month range (e.g. "June - August")
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    seasons = {
        "Spring": ("March", "May"),
        "Summer": ("June", "August"),
        "Autumn": ("September", "November"),
        "Winter": ("December", "February")
    }

    # Heuristic: certain domains have seasonal peaks
    low = domain.lower()
    if any(w in low for w in ["agri", "travel", "retail"]):
        # prefer month ranges for seasonal businesses
        # choose a contiguous 2-3 month window
        start_idx = random.randint(0, 11)
        span = random.choice([2, 3])
        idxs = [(start_idx + i) % 12 for i in range(span)]
        start = months[idxs[0]]
        end = months[idxs[-1]]
        return f"{start} - {end}"

    # Otherwise occasionally return a named season
    if random.random() < 0.6:
        season = random.choice(list(seasons.keys()))
        start, end = seasons[season]
        return f"{season} ({start} - {end})"

    # fallback: a shorter month window
    start_idx = random.randint(0, 11)
    span = random.choice([1, 2])
    idxs = [(start_idx + i) % 12 for i in range(span)]
    start = months[idxs[0]]
    end = months[idxs[-1]]
    if start == end:
        return f"{start}"
    return f"{start} - {end}"


# --- Sample idea creation for mini business plan and seeding favorites ---
def create_sample_idea(brand_name, tagline):
    domain = "Snack Boxes"
    idea_text = (
        f"{brand_name} offers curated boxes of 6-8 homemade snacks (granola bars, spiced nuts, sweet bites) "
        f"with seasonal themes and direct-to-consumer subscription options. Perfect for gifting and office snacks."
    )
    feature = "Curated themed boxes"
    audience = "Busy professionals & gift buyers"
    monetization = "One-time boxes + monthly subscriptions"

    ivalue = estimate_initial_investment(domain, feature)
    ivalue_display = f"${ivalue:,}"

    return {
        "startup_name": brand_name,
        "domain": domain,
        "idea": idea_text,
        "audience": audience,
        "feature": feature,
        "monetization": monetization,
        "tagline": tagline,
        "initial_investment_value": ivalue,
        "initial_investment": ivalue_display,
        "best_platform": pick_best_platform(feature),
        "projected_annual_revenue": estimate_annual_revenue(domain, feature),
        "peak_period": estimate_peak_period(domain),
    }


@app.route("/business_plan")
def business_plan():
    # One-page mini-business-plan for Cozy Snack Boxes with 5 brand options
    brands = [
        ("CozyCrate", "Warm bites, month after month."),
        ("NibbleNest", "Snack small. Delight often."),
        ("BoxedBites", "Handmade snacks for every moment."),
        ("HarvestHues", "Seasonal flavors, delivered."),
        ("TinyTreatCo", "Big flavor, small boxes.")
    ]

    # high-level plan content
    plan = {
        "title": "Cozy Snack Boxes — Mini Business Plan",
        "overview": "Curated boxes of homemade snacks sold as one-off gifts or subscription boxes. Low initial overhead, local ingredients, focus on seasonal themes and corporate gifting.",
        "pricing": "Single box: $18-$28 | Monthly subscription: $15-$22 per month",
        "initial_budget": "Ingredients, packaging, labels, basic website, 2 months marketing (~$1,200 - $3,000)",
        "three_month_budget": [
            ("Month 1: Setup", "$1,200 - $2,000 (website, supplies, photography)"),
            ("Month 2: Pilot & Markets", "$600 - $1,200 (local market fees, samples, ads)"),
            ("Month 3: Scale Prep", "$600 - $1,200 (inventory, packaging improvements)")
        ],
        "marketing_checklist": [
            "Instagram + Reels with unboxing and behind-the-scenes",
            "Local farmers market stall on weekends",
            "Partnerships with co-working spaces for sampling",
            "Referral discount for subscriptions",
            "Seasonal themed campaigns (holiday boxes)"
        ],
        "brands": brands
    }

    return render_template("business_plan.html", plan=plan)


@app.route("/seed_samples")
def seed_samples():
    if "user" not in session:
        return redirect(url_for("login"))

    brands = [
        ("CozyCrate", "Warm bites, month after month."),
        ("NibbleNest", "Snack small. Delight often."),
        ("BoxedBites", "Handmade snacks for every moment."),
        ("HarvestHues", "Seasonal flavors, delivered."),
        ("TinyTreatCo", "Big flavor, small boxes.")
    ]

    db = get_db()
    cur = db.cursor()
    user = session.get("user")
    # create sample ideas and insert into favorites table if not exists
    for name, tagline in brands:
        sample = create_sample_idea(name, tagline)
        idea_json = json.dumps(sample)
        # naive uniqueness: check if same idea_json exists for this user
        cur.execute("SELECT id FROM favorites WHERE user_email = ? AND idea_json = ?", (user, idea_json))
        if not cur.fetchone():
            cur.execute("INSERT INTO favorites (user_email, idea_json, created_at) VALUES (?,?,?)",
                        (user, idea_json, datetime.utcnow().isoformat()))

    # add to history table
    cur.execute("INSERT INTO history (user_email, domain, count, duration, investment, created_at) VALUES (?,?,?,?,?,?)",
                (user, "Snack Boxes (sample)", len(brands), None, None, datetime.utcnow().isoformat()))
    db.commit()

    return redirect(url_for("favorites_page"))


@app.route("/")
def home():
    if "user" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT password_hash FROM users WHERE email = ?", (email,))
        row = cur.fetchone()
        if row and check_password_hash(row[0], password):
            session["user"] = email
            return redirect(url_for("dashboard"))
        else:
            error = "Invalid email or password"

    return render_template("login.html", error=error)


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        domain = request.form.get("domain")
        if domain:
            # read duration (months to profit) and investment budget from form
            try:
                duration = int(request.form.get("duration", 3))
            except Exception:
                duration = 3
            duration = max(1, min(60, duration))

            # investment budget (USD) — allow numeric input
            try:
                investment = int(request.form.get("investment", 1000))
            except Exception:
                investment = 1000

            # number of ideas to generate (limit to reasonable range)
            try:
                count = int(request.form.get("count", 4))
            except Exception:
                count = 4
            count = max(1, min(8, count))
            strategy = request.form.get("strategy")
            results = generate_ideas(domain, count=count, strategy=strategy)
            # attach user requested duration and budget and compute fit
            for r in results:
                r["user_profit_duration_months"] = duration
                r["user_investment_budget"] = investment
                # compare budget with estimated required initial investment
                required = r.get("initial_investment_value", None)
                if required is None:
                    r["investment_fit"] = "Estimate unavailable"
                else:
                    if investment >= required:
                        r["investment_fit"] = "Your budget looks sufficient to start."
                    else:
                        diff = required - investment
                        r["investment_fit"] = f"You may need an additional ${diff:,} to meet the estimated initial investment."
            # store in session so details/favorites can reference them
            session["last_results"] = results
            # add to search history (keep recent 20)
            history = session.get("history", [])
            history.insert(0, {"domain": domain, "count": count, "duration_months": duration, "investment": investment})
            session["history"] = history[:20]
            return render_template("result.html", results=results, domain=domain)

    return render_template("index.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        if not email or not password:
            error = "Please provide email and password"
        else:
            db = get_db()
            cur = db.cursor()
            cur.execute("SELECT id FROM users WHERE email = ?", (email,))
            if cur.fetchone():
                error = "User already exists"
            else:
                pw_hash = generate_password_hash(password)
                cur.execute("INSERT INTO users (email, password_hash) VALUES (?,?)", (email, pw_hash))
                db.commit()
                session["user"] = email
                return redirect(url_for("dashboard"))
    return render_template("register.html", error=error)


@app.route("/forgot", methods=["GET", "POST"])
def forgot():
    msg = None
    if request.method == "POST":
        email = request.form.get("email")
        # In a real app we'd send an email. Here, just inform if user exists.
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cur.fetchone():
            msg = "We found that email. Since this demo has no email service, please contact admin or register a new account."
        else:
            msg = "No account found for that email. You can register a new user."
    return render_template("forgot.html", msg=msg)


@app.route("/idea/<int:idx>")
def idea_detail(idx):
    last = session.get("last_results", [])
    if idx < 0 or idx >= len(last):
        return redirect(url_for("dashboard"))
    idea = last[idx]
    # determine if favorited
    db = get_db()
    cur = db.cursor()
    user = session.get("user")
    is_fav = False
    fav_id = None
    if user:
        # find favorite by idea text for this user
        cur.execute("SELECT id, idea_json FROM favorites WHERE user_email = ?", (user,))
        for row in cur.fetchall():
            try:
                stored = json.loads(row[1])
                if stored.get("idea") == idea.get("idea"):
                    is_fav = True
                    fav_id = row[0]
                    break
            except Exception:
                continue
    return render_template("idea_detail.html", idea=idea, idx=idx, is_fav=is_fav, fav_id=fav_id)


@app.route("/favorite", methods=["POST"])
def favorite_toggle():
    # Toggle favorite by index (from results) or remove by fav_id (from favorites page)
    db = get_db()
    cur = db.cursor()
    user = session.get("user")
    if not user:
        return redirect(url_for("login"))

    fav_id = request.form.get("fav_id")
    idx_val = request.form.get("index")

    if fav_id:
        # remove favorite by id
        try:
            cur.execute("DELETE FROM favorites WHERE id = ? AND user_email = ?", (int(fav_id), user))
            db.commit()
        except Exception:
            pass
        return redirect(request.referrer or url_for("favorites_page"))

    if idx_val is not None:
        try:
            idx = int(idx_val)
        except Exception:
            return redirect(url_for("dashboard"))
        last = session.get("last_results", [])
        if idx < 0 or idx >= len(last):
            return redirect(url_for("dashboard"))
        item = last[idx]
        idea_json = json.dumps(item)
        # add to DB if not exists
        cur.execute("SELECT id FROM favorites WHERE user_email = ? AND idea_json = ?", (user, idea_json))
        if not cur.fetchone():
            cur.execute("INSERT INTO favorites (user_email, idea_json, created_at) VALUES (?,?,?)",
                        (user, idea_json, datetime.utcnow().isoformat()))
            db.commit()
        return redirect(request.referrer or url_for("dashboard"))

    return redirect(url_for("dashboard"))


@app.route("/favorites")
def favorites_page():
    if "user" not in session:
        return redirect(url_for("login"))
    db = get_db()
    cur = db.cursor()
    user = session.get("user")
    cur.execute("SELECT id, idea_json, created_at FROM favorites WHERE user_email = ? ORDER BY created_at DESC", (user,))
    rows = cur.fetchall()
    favorites = []
    for r in rows:
        try:
            idea = json.loads(r[1])
        except Exception:
            idea = {"idea": r[1]}
        idea["fav_id"] = r[0]
        idea["fav_created_at"] = r[2]
        favorites.append(idea)
    return render_template("favorites.html", favorites=favorites)


@app.route("/history")
def history_page():
    if "user" not in session:
        return redirect(url_for("login"))
    db = get_db()
    cur = db.cursor()
    user = session.get("user")
    cur.execute("SELECT domain, count, duration, investment, created_at FROM history WHERE user_email = ? ORDER BY created_at DESC", (user,))
    rows = cur.fetchall()
    history = []
    for r in rows:
        history.append({
            "domain": r[0],
            "count": r[1],
            "duration": r[2],
            "investment": r[3],
            "created_at": r[4]
        })
    return render_template("history.html", history=history)


if __name__ == "__main__":
    app.run(debug=True)
    if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)