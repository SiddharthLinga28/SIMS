from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from pymongo import MongoClient
import random
import string
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Used for session handling

# MongoDB Connection
client = MongoClient("mongodb+srv://rathiabay:EglKSx21Hu5WUXO4@main.bapge.mongodb.net/?retryWrites=true&w=majority&appName=Main")
db = client["Inventory-management"]

# Function to generate unique business code
def generate_business_code():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=7))

@app.route("/")
def login():
    """Render the login page."""
    return render_template("login.html", error=False)

@app.route("/login", methods=["POST"])
def handle_login():
    """Handle login logic."""
    store_id = request.form["storeID"]
    password = request.form["password"]
    
    # Check database for credentials
    user = db.logins.find_one({"storeID": store_id})
    if user and check_password_hash(user["password"], password):
        session['store_id'] = store_id  # Store session data
        print(f"DEBUG: Login successful for {store_id}, session set.")
        return redirect(url_for("business_details", store_id=store_id))
    else:
        print(f"DEBUG: Login failed for {store_id}. Incorrect password or store ID.")
        return render_template("login.html", error=True)

@app.route("/register")
def registration():
    """Render the registration page."""
    return render_template("registration.html")

@app.route("/register", methods=["POST"])
def handle_registration():
    """Handle registration logic."""
    owner_name = request.form["ownerName"]
    business_name = request.form["businessName"]
    business_type = request.form["businessType"]
    password = request.form["password"]
    location = request.form["location"]
    items = request.form.getlist("item_name")
    variations = request.form.getlist("item_variation")
    costs = request.form.getlist("item_cost")
    
    store_id = generate_business_code()  # Generate unique business ID
    hashed_password = generate_password_hash(password)  # Hash password
    
    # Ensure items are stored as a proper list of dictionaries
    items_list = [{"name": items[i], "variation": variations[i], "cost": costs[i]} for i in range(len(items))]
    
    # Save registration details in the database
    db.registration.insert_one({
        "storeID": store_id,
        "ownerName": owner_name,
        "businessName": business_name,
        "businessType": business_type,
        "location": location,
        "password": hashed_password,
        "items": items_list  # Ensure this is stored as a list
    })
    
    db.logins.insert_one({
        "storeID": store_id,
        "password": hashed_password  # Store hashed password
    })
    
    return jsonify({"success": True, "store_id": store_id})

@app.route("/business/<store_id>")
def business_details(store_id):
    """Display business details after login."""
    if 'store_id' not in session:
        print("DEBUG: Session store_id is missing")
        return redirect(url_for("login"))

    # Fetch business details
    business = db.registration.find_one({"storeID": store_id})
    
    if not business:
        print(f"DEBUG: No business found for storeID: {store_id}")
        print(list(db.registration.find()))  # Debug print all businesses
        return "Business not found!", 404
    
    print(f"DEBUG: Business data retrieved for {store_id}: {business}")
    
    return render_template("business_details.html", business=business)

@app.route("/logout")
def logout():
    """Handle user logout."""
    session.pop('store_id', None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
