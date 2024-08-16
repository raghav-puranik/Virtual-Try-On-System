# app.py
import os
import sqlite3
from flask import Flask, render_template, redirect, url_for, request,session,flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_migrate import Migrate
from sqlalchemy import inspect
import subprocess
from sqlalchemy.orm import validates

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = 'your_secret_key'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# # Use a connection pool
# db.engine.pool.use_threadlocal = True

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    @validates('password')
    def validate_password(self, key, password):
        assert len(password) >= 6, "Password must be at least 6 characters long."
        return password

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    last_login_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    phone_number = db.Column(db.String(20))
    email = db.Column(db.String(100))

class RegistrationData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20))
    email = db.Column(db.String(100))
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Integer, default=1)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    total_cost = db.Column(db.Float, nullable=False)

@app.route('/')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                user.last_login_timestamp = datetime.now()
                session['user_id'] = user.id  # Store user ID in session
                db.session.commit()
                return redirect(url_for('index'))
            else:
                flash('Invalid username or password!', 'error')
        else:
            flash('User not found!', 'error')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        name = request.form['name']
        phone_number = request.form['phone_number']
        email = request.form['email']
        password = request.form['password']

        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different username.', 'error')
            return redirect(url_for('register'))

        # Create new user
        new_user = User(username=username, phone_number=phone_number, email=email,
                        password=generate_password_hash(password))
        db.session.add(new_user)

        # Save registration data in separate table
        registration_data = RegistrationData(username=username, phone_number=phone_number, email=email,
                                             password=generate_password_hash(password))
        db.session.add(registration_data)

        db.session.commit()

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Clear the user's session
    return redirect(url_for('login'))  # Redirect to the login page

# Add admin login and registration routes
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin = Admin.query.filter_by(username=username).first()
        if admin and check_password_hash(admin.password, password):
            # Redirect admin to admin_dashboard.html upon successful login
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password!', 'error')
    else:
        flash('User not found!', 'error')
    return render_template('adminLogin.html')

@app.route('/admin_register', methods=['POST'])
def admin_register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        existing_admin = Admin.query.filter_by(username=username).first()
        if existing_admin:
            flash('Admin username already exists. Please choose a different username.', 'error')
            return redirect(url_for('admin_login'))

        new_admin = Admin(username=username, password=generate_password_hash(password))
        db.session.add(new_admin)
        db.session.commit()

        flash('Admin registration successful!', 'success')
        return redirect(url_for('admin_login'))

    return redirect(url_for('admin_login'))

def initialize_database():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Create products table if not exists
    cursor.execute('''CREATE TABLE IF NOT EXISTS products (
                        id INTEGER PRIMARY KEY,
                        image TEXT,
                        name TEXT,
                        price REAL,
                        description TEXT,
                        brand TEXT,
                        try_image TEXT
                    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS glass_products (
                            id INTEGER PRIMARY KEY,
                            image TEXT,
                            name TEXT,
                            price REAL,
                            description TEXT,
                            brand TEXT,
                            try_image TEXT
                        )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS earrings_products (
                                id INTEGER PRIMARY KEY,
                                image TEXT,
                                name TEXT,
                                price REAL,
                                description TEXT,
                                brand TEXT,
                                try_image TEXT
                            )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS neaklace_products (
                                    id INTEGER PRIMARY KEY,
                                    image TEXT,
                                    name TEXT,
                                    price REAL,
                                    description TEXT,
                                    brand TEXT,
                                    try_image TEXT
                                )''')

    # Commit changes and close connection
    conn.commit()
    conn.close()



# Function to fetch product details from SQLite database
def get_products():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    conn.close()
    return products

def get_necklace_products():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM neacklace_products")
    products = cursor.fetchall()
    conn.close()
    return products

def get_glass_products():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM glass_products")
    products = cursor.fetchall()
    conn.close()
    return products

def get_earrings_products():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM earrings_products")
    products = cursor.fetchall()
    conn.close()
    return products


# @app.route('/admin_dashboard')
# def admin_dashboard():
#     # Fetch products from the database using get_products function
#     products = get_products()
#     return render_template('admin_dashboard.html', products=products)

@app.route('/admin_dashboard')
def admin_dashboard():
    # Fetch products from different tables
    products = get_products()
    glass_products = get_glass_products()
    neacklace_products = get_necklace_products()
    earrings_products = get_earrings_products()

    return render_template('admin_dashboard.html', products=products, glass_products=glass_products,
                           neacklace_products=neacklace_products, earrings_products=earrings_products)

@app.route('/config.php')
def config():
    return  render_template('config.php')

@app.route('/index.html')
def index():
    return render_template('index.html')
                
@app.route('/necklaces.html')
def necklaces():
    products = get_necklace_products()
    return render_template('necklaces.html',products=products)

@app.route('/glass.html')
def glass():
    products = get_glass_products()
    return render_template('glass.html',products=products)

@app.route('/earrings.html')
def earrings():
    products = get_earrings_products()
    return render_template('earrings.html',products=products)

@app.route('/thank.html')
def thank():
    return render_template('thank.html')

@app.route('/cart.html')
def cart():
    # Query cart items from the database
    items = CartItem.query.all()

    # Calculate total cost
    total_cost = sum(item.price for item in items)

    # Render the cart.html template with the cart items and total cost
    return render_template('cart.html', items=items, total_cost=total_cost)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    data = request.json
    if data:
        price = float(data['price'].replace('₹', ''))
        cart_item = CartItem(name=data['name'], price=data['price'], image=data['image'])
        db.session.add(cart_item)
        db.session.commit()
        return jsonify(message="Product added to cart"), 200
    return jsonify(error="Invalid request"), 400

@app.route('/remove_item', methods=['POST'])
def remove_item():
    data = request.json
    if data and 'itemId' in data:
        item_id = data['itemId']
        item = CartItem.query.get(item_id)
        if item:
            db.session.delete(item)
            db.session.commit()
            return jsonify(message="Item removed successfully"), 200
    return jsonify(error="Failed to remove item"), 400


@app.route('/add_product', methods=['POST'])
def add_product():
    if request.method == 'POST':
        # Get form data
        table_name = request.form['tableName']
        image = request.form['image']
        name = request.form['name']
        price = request.form['price']
        description = request.form['description']
        brand = request.form['brand']
        try_image = request.form['tryImage']

        # Connect to the SQLite database
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Insert the product into the selected table
        cursor.execute(f'''
            INSERT INTO {table_name} (image, name, price, description, brand, try_image)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (image, name, price, description, brand, try_image))

        # Commit the transaction
        conn.commit()

        # Close the connection
        conn.close()

        flash('Product added successfully!', 'success')

        # Redirect back to the admin dashboard
        return redirect(url_for('admin_dashboard'))

@app.route('/delete_product', methods=['POST'])
def delete_product():
    if request.method == 'POST':
        table_name = request.form['deleteTableName']
        try_image = request.form['tryImageToDelete']

        # Connect to the SQLite database
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Delete the product from the selected table
        cursor.execute(f'''
            DELETE FROM {table_name} WHERE try_image = ?
        ''', (try_image,))

        # Commit the transaction
        conn.commit()

        # Close the connection
        conn.close()

        flash('Product deleted successfully!', 'success')

        # Redirect back to the admin dashboard
        return redirect(url_for('admin_dashboard'))


@app.route('/confirm_order', methods=['POST'])
def confirm_order():
    if request.method == 'POST':
        # Get form data
        username = request.form['username']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        total_cost = request.form['total_cost']

        # Insert order into database or perform any other necessary action
        # For example:
        new_order = Order(username=username, email=email, phone=phone, address=address, total_cost=total_cost)
        db.session.add(new_order)
        db.session.commit()

        # Optionally, you can redirect to a thank you page or another page
        return redirect(url_for('thank'))

@app.route('/shirts.html')
def shirts():
    products = get_products()
    return render_template('shirts.html', products=products)

@app.route('/try_shirt_image/<image_name>')
def try_shirt_image(image_name):
    # image_name = request.args.get('image_name', '')
    shirt_path = f"static/shirt_images/{image_name}"

    # Write the path to a file
    with open("shirt_path.txt", "w") as file:
        file.write(shirt_path)

    # Run the shirt.py script
    os.system("python shirt.py")

    # return redirect(url_for('sproduct', product_id='pro1'))
    # return redirect(url_for('shirt', product_id=image_name))
    return redirect(url_for('shirts'))

@app.route('/try_glass_image/<image_name>')
def try_glass_image(image_name):
    # image_name = request.args.get('image_name', '')
    glass_path = f"static/glass_images/{image_name}"

    # Write the path to a file
    with open("glass_path.txt", "w") as file:
        file.write(glass_path)

    # Run the shirt.py script
    os.system("python glass.py")

    # return redirect(url_for('sproduct', product_id='pro1'))
    # return redirect(url_for('shirt', product_id=image_name))
    return redirect(url_for('glass'))

@app.route('/try_earring_image/<image_name>')
def try_earring_image(image_name):
    # image_name = request.args.get('image_name', '')
    earrings_path = f"static/earring_images/{image_name}"

    # Write the path to a file
    with open("earrings_path.txt", "w") as file:
        file.write(earrings_path)

    # Run the shirt.py script
    os.system("python earrings.py")

    # return redirect(url_for('sproduct', product_id='pro1'))
    # return redirect(url_for('shirt', product_id=image_name))
    return redirect(url_for('earrings'))

@app.route('/try_necklace_image/<image_name>')
def try_necklace_image(image_name):
    # Construct the path to the necklace image
    necklace_path = f"static/necklace_images/{image_name}"

    # Write the path to a file
    with open("necklace_path.txt", "w") as file:
        file.write(necklace_path)

    # Run the necklace.py script
    os.system("python necklace.py")

    return redirect(url_for('necklaces'))


if __name__ == '__main__':
    initialize_database()
    with app.app_context():
        db.create_all()
    app.run(debug=True)


