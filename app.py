import os, json
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mail import Mail, Message
from urllib.parse import quote_plus
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
# --- Wyroby piekarnicze (Chleby) ---
BAKERY_ITEMS = [
    {
        "id": "chleb-maslo-orzechowe",
        "name": "Chleb z masła orzechowego",
        "desc": "Przechowywać w chłodnym i suchym miejscu; można mrozić.",
        "price": "19 zł",
        "image": "/static/img/bakery/chleb-maslo-orzechowe.jpg",
        "badge": "Keto",
        "macros": {"kcal": 1267, "B": 71, "W": 22, "T": 102},
    },
    {
        "id": "chleb-siemie-lniane",
        "name": "Chleb z siemienia lnianego",
        "desc": "Przechowywać w chłodnym i suchym miejscu; można mrozić.",
        "price": "13 zł",
        "image": "/static/img/bakery/chleb-siemie-lniane.jpg",
        "badge": "Keto",
        "macros": {"kcal": 2357, "B": 99, "W": 67, "T": 162},
    },
    {
        "id": "chleb-cebulka-czosnek-niedzwiedzi",
        "name": "Chleb z suszoną cebulką i czosnkiem niedźwiedzim",
        "desc": "Przechowywać w chłodnym i suchym miejscu; można mrozić.",
        "price": "22 zł",
        "image": "/static/img/bakery/chleb-cebulka-czosnek-niedzwiedzi.jpg",
        "badge": "Aromatyczny",
        "macros": {"kcal": 2273, "B": 114.8, "W": 25.5, "T": 190.2},
    },
    {
        "id": "chleb-mascarpone",
        "name": "Chleb na bazie serka mascarpone",
        "desc": "Przechowywać w chłodnym i suchym miejscu; można mrozić.",
        "price": "20 zł",
        "image": "/static/img/bakery/chleb-mascarpone.jpg",
        "badge": "Keto",
        "macros": {"kcal": 2816, "B": 97.6, "W": 29.4, "T": 248.2},
    },
    {
        "id": "chleb-majonez",
        "name": "Chleb na bazie majonezu",
        "desc": "Przechowywać w chłodnym i suchym miejscu; można mrozić.",
        "price": "20 zł",
        "image": "/static/img/bakery/chleb-majonez.jpg",
        "badge": "Keto",
        "macros": {"kcal": 2768, "B": 57.3, "W": 35.7, "T": 261.7},
    },
    {
        "id": "bulki-lnianie-3",
        "name": "Bułki z siemienia lnianego (3 szt.)",
        "desc": "Przechowywać w chłodnym i suchym miejscu; można mrozić.",
        "price": "10 zł / 3 szt",
        "image": "/static/img/bakery/bulki-lniane.jpg",
        "badge": "Pakiet",
        "macros": {"kcal": None, "B": None, "W": None, "T": None},
    },
    {
        "id": "bulki-migdalowe-3",
        "name": "Bułki migdałowe (3 szt.)",
        "desc": "Przechowywać w chłodnym i suchym miejscu; można mrozić.",
        "price": "10 zł / 3 szt",
        "image": "/static/img/bakery/bulki-migdalowe.jpg",
        "badge": "Pakiet",
        "macros": {"kcal": None, "B": None, "W": None, "T": None},
    },
]

# --- Wyroby cukiernicze (Ciasta) ---
PASTRY_ITEMS = [
    {
        "id": "keto-brownie",
        "name": "Keto brownie",
        "price": "120 zł",
        "image": "/static/img/pastry/keto-brownie.jpg",
        "badge": "Keto",
        "macros": {"kcal": None, "B": None, "W": None, "T": None},
    },
    {
        "id": "keto-brownie-orzech",
        "name": "Keto brownie z masłem orzechowym i orzechami",
        "price": "140 zł",
        "image": "/static/img/pastry/keto-brownie-orzech.jpg",
        "badge": "Keto",
        "macros": {"kcal": None, "B": None, "W": None, "T": None},
    },
    {
        "id": "keto-tarta-jagodowa",
        "name": "Keto tarta z owocami jagodowymi i kremem mascarpone-śmietana",
        "price": "80 zł",
        "image": "/static/img/pastry/keto-tarta-jagodowa.jpg",
        "badge": "Keto",
        "macros": {"kcal": None, "B": None, "W": None, "T": None},
    },
    {
        "id": "babeczki-tluszczowe",
        "name": "Babeczki tłuszczowe",
        "desc": "Min. 3 szt.",
        "price": "7 zł / szt",
        "image": "/static/img/pastry/babeczki-tluszczowe.jpg",
        "badge": "Min. 3",
        "macros": {"kcal": 194, "B": 7, "W": 3, "T": 17},
    },
    {
        "id": "ciastka-maslo-orzechowe-slonecznik",
        "name": "Ciastka z masła orzechowego ze słonecznikiem",
        "price": "10 zł / 2 szt",
        "image": "/static/img/pastry/ciastka-orzech-slonecznik.jpg",
        "macros": {"kcal": None, "B": None, "W": None, "T": None},
    },
    {
        "id": "ciastka-orzech-czekolada",
        "name": "Ciastka orzechowe z kawałkami czekolady",
        "price": "14 zł / 2 szt",
        "image": "/static/img/pastry/ciastka-orzech-czekolada.jpg",
        "macros": {"kcal": None, "B": None, "W": None, "T": None},
    },
    {
        "id": "ciastka-pistacjowe",
        "name": "Ciastka pistacjowe",
        "price": "15 zł / 2 szt",
        "image": "/static/img/pastry/ciastka-pistacjowe.jpg",
        "macros": {"kcal": None, "B": None, "W": None, "T": None},
    },
    {
        "id": "ciastka-tahini-czekolada",
        "name": "Ciastka tahini z kawałkami czekolady",
        "price": "15 zł / 2 szt",
        "image": "/static/img/pastry/ciastka-tahini-czekolada.jpg",
        "macros": {"kcal": None, "B": None, "W": None, "T": None},
    },
    {
        "id": "kokosanki",
        "name": "Kokosanki",
        "price": "12 zł / 10 szt",
        "image": "/static/img/pastry/kokosanki.jpg",
        "macros": {"kcal": None, "B": None, "W": None, "T": None},
    },
    {
        "id": "muffinki-brownie-krem",
        "name": "Muffinki Brownie z kremem czekoladowym",
        "desc": "Min. 3 szt.",
        "price": "8 zł / szt",
        "image": "/static/img/pastry/muffinki-brownie-krem.jpg",
        "badge": "Min. 3",
        "macros": {"kcal": None, "B": None, "W": None, "T": None},
    },
    {
        "id": "deser-smietankowy-orzech",
        "name": "Orzechowy deser śmietankowy",
        "price": "12 zł / szt",
        "image": "/static/img/pastry/deser-orzech.jpg",
        "macros": {"kcal": None, "B": None, "W": None, "T": None},
    },
    {
        "id": "deser-smietankowy-pistacja",
        "name": "Pistacjowy deser śmietankowy",
        "price": "15 zł / szt",
        "image": "/static/img/pastry/deser-pistacja.jpg",
        "macros": {"kcal": None, "B": None, "W": None, "T": None},
    },
    {
        "id": "keto-tartaletki-rozne",
        "name": "Keto-tartaletki na bazie kremu mascarpone (różne smaki)",
        "desc": "Z owocami, pistacjowe, orzechowe, czekoladowe. Min. 2 szt.",
        "price": "13 zł / szt",
        "image": "/static/img/pastry/tartaletki-rozne.jpg",
        "badge": "Min. 2",
        "macros": {"kcal": None, "B": None, "W": None, "T": None},
    },
    {
        "id": "keto-cynamonki",
        "name": "Keto cynamonki",
        "desc": "Zapytaj o cenę i dostępność.",
        "price": "—",
        "image": "/static/img/pastry/keto-cynamonki.jpg",
        "badge": "Zapytaj",
        "macros": {"kcal": None, "B": None, "W": None, "T": None},
    },

    # --- Serniki (warianty 12/6 porcji) ---
    {
        "id": "sernik-pistacjowy",
        "name": "Sernik pistacjowy",
        "desc": "Śr. 26 cm przy całym.",
        "image": "/static/img/pastry/sernik-pistacjowy.jpg",
        "badge": "Sernik",
        "variants": [
            {"id": "12", "label": "12 porcji", "price": "180 zł"},
            {"id": "6",  "label": "6 porcji",  "price": "90 zł"},
        ],
        "macros": {"kcal": None, "B": None, "W": None, "T": None},
    },
    {
        "id": "sernik-migdalowy-spod",
        "name": "Sernik na migdałowym spodzie",
        "desc": "Śr. 26 cm przy całym.",
        "image": "/static/img/pastry/sernik-migdalowy-spod.jpg",
        "badge": "Sernik",
        "variants": [
            {"id": "12", "label": "12 porcji", "price": "120 zł"},
            {"id": "6",  "label": "6 porcji",  "price": "60 zł"},
        ],
        "macros": {"kcal": None, "B": None, "W": None, "T": None},
    },
    {
        "id": "sernik-borowki-kruszonka",
        "name": "Sernik z borówkami i kruszonką",
        "desc": "Śr. 26 cm przy całym.",
        "image": "/static/img/pastry/sernik-borowki-kruszonka.jpg",
        "badge": "Sernik",
        "variants": [
            {"id": "12", "label": "12 porcji", "price": "180 zł"},
            {"id": "6",  "label": "6 porcji",  "price": "90 zł"},
        ],
        "macros": {"kcal": None, "B": None, "W": None, "T": None},
    },
    {
        "id": "sernik-kokosowy",
        "name": "Sernik kokosowy",
        "desc": "Śr. 26 cm przy całym.",
        "image": "/static/img/pastry/sernik-kokosowy.jpg",
        "badge": "Sernik",
        "variants": [
            {"id": "12", "label": "12 porcji", "price": "120 zł"},
            {"id": "6",  "label": "6 porcji",  "price": "60 zł"},
        ],
        "macros": {"kcal": None, "B": None, "W": None, "T": None},
    },
    {
        "id": "sernik-kawowy",
        "name": "Sernik kawowy",
        "desc": "Śr. 26 cm przy całym.",
        "image": "/static/img/pastry/sernik-kawowy.jpg",
        "badge": "Sernik",
        "variants": [
            {"id": "12", "label": "12 porcji", "price": "100 zł"},
            {"id": "6",  "label": "6 porcji",  "price": "50 zł"},
        ],
        "macros": {"kcal": None, "B": None, "W": None, "T": None},
    },
    {
        "id": "sernik-zebra",
        "name": "Sernik „zebra”",
        "desc": "Śr. 26 cm przy całym.",
        "image": "/static/img/pastry/sernik-zebra.jpg",
        "badge": "Sernik",
        "variants": [
            {"id": "12", "label": "12 porcji", "price": "120 zł"},
            {"id": "6",  "label": "6 porcji",  "price": "60 zł"},
        ],
        "macros": {"kcal": None, "B": None, "W": None, "T": None},
    },
]

CATEGORY_MAP = {
    "piekarnicze": {
        "title": "Wyroby piekarnicze",
        "items": BAKERY_ITEMS
    },
    "cukiernicze": {
        "title": "Wyroby cukiernicze",
        "items": PASTRY_ITEMS
    },
}
# --- MENU (from menupdf.pdf) ---
MENU_SECTIONS = [
    {
        "title": "Kawy",
        "items": [
            {"name": "Espresso",                      "price": "9 zł"},
            {"name": "Podwójne espresso",            "price": "14 zł"},
            {"name": "Espresso macchiato",           "price": "11 zł"},
            {"name": "Macchiato",                    "price": "15 zł"},
            {"name": "Flat white",                   "price": "13 zł"},
            {"name": "Cappuccino (małe)",            "price": "13 zł"},
            {"name": "Cappuccino (duże)",            "price": "16 zł"},
            {"name": "Latte",                        "price": "15 zł"},
            {"name": "Latte smakowe",                "price": "18 zł"},
            {"name": "Americano",                    "price": "13 zł"},
            {"name": "Kawa z dolewką – przelew",     "price": "10 zł"},
            {"name": "Kawa bezkofeinowa",            "price": "13 zł"},
            {"name": "Kawa rozpuszczalna",           "price": "10 zł"},
            {"name": "Keto kawa – „kuloodporna”",    "price": "19 zł"},
        ],
    },
    {
        "title": "Kawy na zimno",
        "items": [
            {"name": "Iced latte",                  "price": "13 zł"},
            {"name": "Kawa z lodami",               "price": "18 zł"},
            {"name": "Kawa z „Coffee Ice Cubes”",   "price": "14 zł"},
            {"name": "Caffè affogato",              "price": "13 zł"},
            {"name": "Espresso tonic",              "price": "16 zł"},
        ],
    },
    # Dodasz tu kolejne sekcje, gdy otrzymamy więcej pozycji (np. Herbaty, Lemoniady, Przekąski...).
]

# Ensure your /menu view sends MENU_SECTIONS to the template



def all_products():
    return BAKERY_ITEMS + PASTRY_ITEMS

@app.context_processor
def inject_nav():
    return {
        "NAV": [
            {"href": url_for('home'), "label": "Strona główna"},
            {"href": url_for('menu'), "label": "Menu"},
            {"href": url_for('keto'), "label": "Keto"},
            {"href": url_for('ciasta_i_chleby'), "label": "Zamów"},
            {"href": url_for('kontakt'),"label": "Kontakt", "href": "/kontakt"},
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
    return render_template("menu.html", sections=MENU_SECTIONS)

@app.route("/keto")
def keto():
    return render_template("keto.html")

@app.route("/ciasta-i-chleby")
def ciasta_i_chleby():
    return render_template("ciasta_i_chleby.html")
@app.route("/produkty")
def products():
    key = (request.args.get("category") or "").lower()
    ctx = CATEGORY_MAP.get(key)
    if not ctx:
        # domyślnie pokaż wybór albo przekieruj do jednej z kategorii
        # return render_template("products_chooser.html")
        # albo:
        return render_template("products.html", category="Wyroby piekarnicze", products=BAKERY_ITEMS)

    return render_template(
        "products.html",
        category=ctx["title"],
        products=ctx["items"]
    )

#@app.route("/chleby")
#def chleby():
#    return render_template("products.html", products=BREADS, category="Chleby")

#@app.route("/ciasta")
#def ciasta():
#    return render_template("products.html", products=CAKES, category="Ciasta")

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

@app.route("/kontakt")
def kontakt():
    contact = {
        "name": "Kawiarnia TEJ",
        "phone": "792 527 154",
        "address": "Święty Marcin 63, 61-806 Poznań",
        "email": "kawiarniatej@gmail.com",
        "hours": [
            "Poniedziałek – Piątek: 09:00–19:00",
            "Sobota: 10:00–19:00",
            "Niedziela: 11:00–19:00",
        ],
    }
    address_q = quote_plus(contact["address"])
    return render_template("kontakt.html", contact=contact, address_q=address_q)

@app.route("/zamowienie", methods=["GET", "POST"])
def zamowienie():
    if request.method == "GET":
        # Just render the form page
        return render_template("order_form.html")

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
        variant_label = item.get("variantLabel")
        if variant_label:
            name = f"{name} ({variant_label})"
        qty  = int(item.get("qty", 1) or 1)
        price = float(str(item.get("price", 0)).replace(",", ".").split()[0] or 0)
        line_total = qty * price
        total += line_total
        lines.append(f"- {qty} × {name}: {line_total:.2f} zł")

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
        return redirect(url_for("home", order="ok"))
    except Exception as e:
        # Log/flash the error
        print("MAIL ERROR:", e)
        flash("Wystąpił problem z wysłaniem zamówienia. Spróbuj ponownie.", "error")
        return render_template("order_form.html"), 500

@app.get("/thank-you")
def thank_you():
    return render_template("thank_you.html")

if __name__ == "__main__":
    app.run(debug=True)
