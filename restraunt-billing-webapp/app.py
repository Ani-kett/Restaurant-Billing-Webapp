from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"

# initializes the mongo db database
client = MongoClient("mongodb://localhost:27017/")
db = client["restaurantdb"]
menu_col = db["menu"]
orders_col = db["orders"]

# add menu items to database
if menu_col.count_documents({}) == 0:
    default_items = [
        {'_id': 1, 'name': "Paneer Butter Masala", 'price': 180},
        {'_id': 2, 'name': "Butter Naan", 'price': 40},
        {'_id': 3, 'name': "Veg Biryani", 'price': 160},
        {'_id': 4, 'name': "Masala Dosa", 'price': 100},
        {'_id': 5, 'name': "Spicy Paneer Wrap", 'price': 140},
        {'_id': 6, 'name': "Grilled Chicken Sandwich", 'price': 160},
        {'_id': 7, 'name': "Chicken Biryani", 'price': 190},
        {'_id': 8, 'name': "Butter Chicken", 'price': 200},
        {'_id': 9, 'name': "Egg Curry", 'price': 150},
        {'_id': 10, 'name': "Chicken Tikka Roll", 'price': 170},
        {'_id': 11, 'name': "Cold Drink", 'price': 30},
        {'_id': 12, 'name': "Fresh Lime Soda", 'price': 35},
        {'_id': 13, 'name': "Cold Coffee", 'price': 90},
        {'_id': 14, 'name': "Lemon Iced Tea", 'price': 70},
        {'_id': 15, 'name': "Gulab Jamun", 'price': 25}
    ]
    menu_col.insert_many(default_items)

@app.route("/")
def landing():
    return render_template("landing.html")

# requests the details from the landing page
@app.route("/start_order", methods=["POST"])
def start_order():
    session["customer"] = {
        "name": request.form["name"],
        "phone": request.form["phone"],
        "order_type": request.form["order_type"],
        "payment": request.form["payment"]
    }
    return redirect(url_for("menu"))

# directs the user to menu page
@app.route("/menu")
def menu():
    if "customer" not in session:
        return redirect(url_for("landing"))

    customer = session["customer"]
    menu = list(menu_col.find().sort("_id"))

    # Step 2: Most Popular sorted by most ordered globaly
    pipeline = [
        {"$unwind": "$items"},
        {"$group": {
            "_id": "$items.name",
            "count": {"$sum": "$items.qty"}
        }},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]
    popular_items_raw = list(orders_col.aggregate(pipeline))

    # Map item names to their full info from the menu
    name_to_item = {item["name"]: item for item in menu}
    most_popular = []
    for entry in popular_items_raw:
        name = entry["_id"]
        if name in name_to_item:
            most_popular.append({
                "name": name,
                "count": entry["count"]
            })

    # return most popular item to the side section
    return render_template("index.html",
                           menu=menu,
                           customer=customer,
                           most_popular=most_popular)


@app.route("/place_order", methods=["POST"])
def place_order():
    if "customer" not in session:
        return redirect(url_for("landing"))

    order_items = []
    subtotal = 0

    # adds item to the order section
    for item_id in request.form:
        try:
            qty = int(request.form[item_id])
            if qty > 0:
                item = menu_col.find_one({"_id": int(item_id)})
                if item:
                    line_total = qty * item['price']
                    subtotal += line_total
                    order_items.append({
                        "name": item['name'],
                        "qty": qty,
                        "unit_price": item['price'],
                        "total": line_total
                    })
        except ValueError:
            continue

    if not order_items:
        return redirect(url_for("menu"))

    gst = round(subtotal * 0.05, 2)
    total = round(subtotal + gst, 2)
    now = datetime.now()

    customer_info = session["customer"]

    bill = {
        "items": order_items,
        "subtotal": round(subtotal, 2),
        "gst": gst,
        "total": total,
        "timestamp": now,
        "customer": customer_info
    }

    order_id = orders_col.insert_one(bill).inserted_id

    # shows bill details on bill.html
    return render_template("bill.html",
                           items=order_items,
                           subtotal=subtotal,
                           gst=gst,
                           total=total,
                           time=now.strftime('%d-%m-%Y %H:%M:%S'),
                           order_id=order_id,
                           customer=customer_info)

if __name__ == "__main__":
    app.run(debug=True)