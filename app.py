import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mail import Mail, Message

app = Flask(__name__)

# Config
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret')
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', app.config['MAIL_USERNAME'])

mail = Mail(app)

# Sample products (placeholder images via picsum)
BREADS = [
    {"id": 1, "name": "Chleb Wiejski", "image": "https://picsum.photos/seed/chleb1/800/600"},
    {"id": 2, "name": "Chleb Orkiszowy", "image": "https://picsum.photos/seed/chleb2/800/600"},
    {"id": 3, "name": "Bagietka Tradycyjna", "image": "https://picsum.photos/seed/chleb3/800/600"},
    {"id": 4, "name": "Chleb Żytni", "image": "https://picsum.photos/seed/chleb4/800/600"},
]

CAKES = [
    {"id": 101, "name": "Sernik Klasyczny", "image": "https://picsum.photos/seed/ciasto1/800/600"},
    {"id": 102, "name": "Szarlotka Domowa", "image": "https://picsum.photos/seed/ciasto2/800/600"},
    {"id": 103, "name": "Brownie Czekoladowe", "image": "https://picsum.photos/seed/ciasto3/800/600"},
    {"id": 104, "name": "Tarta Cytrynowa", "image": "https://picsum.photos/seed/ciasto4/800/600"},
]

def all_products():
    return BREADS + CAKES

@app.context_processor
def inject_nav():
    return {
        "NAV": [
            {"href": url_for('home'), "label": "Strona główna"},
            {"href": url_for('menu'), "label": "Menu"},
            {"href": url_for('keto'), "label": "Keto"},
            {"href": url_for('ciasta_i_chleby'), "label": "Ciasta i Chleby"},
        ]
    }

@app.route("/")
def home():
    gallery_images = [
        "https://picsum.photos/seed/gal1/800/600",
        "https://picsum.photos/seed/gal2/800/600",
        "https://picsum.photos/seed/gal3/800/600",
        "https://picsum.photos/seed/gal4/800/600",
        "https://picsum.photos/seed/gal5/800/600",
        "https://picsum.photos/seed/gal6/800/600",
    ]
    carousel_images = [
        "https://picsum.photos/seed/car1/1280/640",
        "https://picsum.photos/seed/car2/1280/640",
        "https://picsum.photos/seed/car3/1280/640",
        "https://picsum.photos/seed/car4/1280/640",
        "https://picsum.photos/seed/car5/1280/640",
    ]
    return render_template("home.html", gallery_images=gallery_images, carousel_images=carousel_images)

@app.route("/menu")
def menu():
    sample_menu = [
        {"name": "Espresso", "desc": "Podwójny shot, 60 ml", "price": "9 PLN"},
        {"name": "Latte", "desc": "Kawa mleczna, różne mleka", "price": "14 PLN"},
        {"name": "Cappuccino", "desc": "Spienione mleko i espresso", "price": "13 PLN"},
        {"name": "Herbata Zielona", "desc": "Liściasta, 400 ml", "price": "10 PLN"},
    ]
    return render_template("menu.html", items=sample_menu)

@app.route("/keto")
def keto():
    return render_template("keto.html")

@app.route("/ciasta-i-chleby")
def ciasta_i_chleby():
    return render_template("ciasta_i_chleby.html")

@app.route("/chleby")
def chleby():
    return render_template("products.html", products=BREADS, category="Chleby")

@app.route("/ciasta")
def ciasta():
    return render_template("products.html", products=CAKES, category="Ciasta")

@app.post("/add-to-cart/<int:product_id>")
def add_to_cart(product_id: int):
    product = next((p for p in all_products() if p["id"] == product_id), None)
    if product is None:
        flash("Produkt nie został znaleziony.", "error")
    else:
        cart = session.get("cart", [])
        cart.append(product_id)
        session["cart"] = cart
        flash(f"Dodano „{product['name']}” do zamówienia.", "success")
    return redirect(request.referrer or url_for("ciasta_i_chleby"))

@app.route("/zamowienie", methods=["GET", "POST"])
def zamowienie():
    if request.method == "GET":
        # Just render the form page
        return render_template("order_from.html")

    # POST: read user fields
    first_name = request.form.get("first_name") or request.form.get("imie") or ""
    last_name  = request.form.get("last_name")  or request.form.get("nazwisko") or ""
    phone      = request.form.get("phone")      or request.form.get("numer_telefonu") or ""
    email      = request.form.get("email")      or request.form.get("e_mail") or ""

    # Cart JSON from hidden field
    cart_json  = request.form.get("cart_json") or "[]"
    try:
        cart = json.loads(cart_json)
    except Exception:
        cart = []

    # Build a readable order summary
    def pln(v): 
        try: 
            return f"{float(v):.2f} zł"
        except: 
            return f"{v} zł"

    lines = []
    total = 0.0
    for item in cart:
        name = item.get("name", "Produkt")
        qty  = int(item.get("qty", 1) or 1)
        price = float(item.get("price", 0) or 0)
        line_total = qty * price
        total += line_total
        lines.append(f"- {qty} × {name}: {pln(line_total)}")

    order_summary = "\n".join(lines) if lines else "(Koszyk pusty)"
    total_line = f"Suma: {pln(total)}"

    # Email content
    subject = f"Nowe zamówienie — {first_name} {last_name}"
    body = f"""Nowe zamówienie z formularza:

Dane klienta:
- Imię: {first_name}
- Nazwisko: {last_name}
- Telefon: {phone}
- E-mail: {email}

Pozycje:
{order_summary}

{total_line}
"""

    # Send the email (uses your Flask-Mail configuration)
    try:
        msg = Message(
            subject=subject,
            recipients=["kacper.rabeda6@gmail.com"],  # <-- change if needed
            body=body,
        )
        # optional: set reply-to to customer email
        if email:
            msg.reply_to = email
        mail.send(msg)
        flash("Dziękujemy! Zamówienie zostało wysłane.", "success")
        # Optionally redirect to a thank-you page or back to home
        return redirect(url_for("home"))
    except Exception as e:
        # Log/flash the error
        print("MAIL ERROR:", e)
        flash("Wystąpił problem z wysłaniem zamówienia. Spróbuj ponownie.", "error")
        return render_template("order_from.html"), 500

@app.get("/thank-you")
def thank_you():
    return render_template("thank_you.html")

if __name__ == "__main__":
    app.run(debug=True)
