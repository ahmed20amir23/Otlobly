#FLASK Setup :)
from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

# Patterns 
from design_patterns.pricing_strategy import NormalPricing
from design_patterns.payment_factory import PaymentFactory
from design_patterns.observer import OrderSubject, UserNotifier, AdminNotifier
from design_patterns.decorators import logger
from design_patterns.adapter import PaymentAdapter, ExternalPaymentAPI
from design_patterns.singleton import Config

load_dotenv('secret.env')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

db = SQLAlchemy(app)

# Singleton usage
config = Config()

# ================= MODELS =================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    role = db.Column(db.String(20), default="user")

    orders = db.relationship(
        'Order',
        backref='user',
        cascade="all, delete-orphan"
    )


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    price = db.Column(db.Float)

    orders = db.relationship('Order', backref='product')


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer, default=1)
    status = db.Column(db.String(50), default="created")

    payment = db.relationship(
        'Payment',
        backref='order',
        uselist=False,
        cascade="all, delete-orphan"
    )


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    method = db.Column(db.String(50))
    amount = db.Column(db.Float)

# ================= ADMIN DECORATOR =================
def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/login')

        user = db.session.get(User, session['user_id'])

        if not user or user.role != "admin":
            return "Unauthorized", 403

        return f(*args, **kwargs)
    return wrapper


# ================= ROUTES =================
@app.route('/')
def index():
    return render_template('index.html')


# ---------- AUTH ----------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = User(
            name=request.form['name'],
            email=request.form['email'],
            password=generate_password_hash(request.form['password'])
        )
        db.session.add(user)
        db.session.commit()
        return redirect('/login')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if not user:
            flash("Register First!!")
            return redirect('/register')
        if user and check_password_hash(user.password, request.form['password']):
            session['user_id'] = user.id
            if user.role == "admin":
                return redirect('/admin')
            else:
                return redirect('/dashboard')
        else:
            flash("Invalid email or password")

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


# ---------- DASHBOARD ----------
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    user = db.session.get(User, session['user_id'])

    if user.role == "admin":
        return redirect('/admin')

    orders = db.session.query(Order, Product)\
        .join(Product)\
        .filter(Order.user_id == user.id).all()

    payments = Payment.query.join(Order)\
        .filter(Order.user_id == user.id).all()

    total = sum([p.amount for p in payments])

    products = Product.query.all()

    return render_template(
        'dashboard.html',
        user=user,
        orders=orders,
        payments=payments,
        total=total,
        products=products
    )


# ---------- ORDERS ----------
@logger  #Decorator
@app.route('/order', methods=['POST'])
def create_order():
    if 'user_id' not in session:
        return redirect('/login')

    product = db.session.get(Product, int(request.form['product_id']))
    quantity = int(request.form['quantity'])

    order = Order(
        user_id=session['user_id'],
        product_id=product.id,
        quantity=quantity,
        status="created"
    )

    db.session.add(order)
    db.session.commit()

    #Observer
    subject = OrderSubject()
    subject.add(UserNotifier())
    subject.add(AdminNotifier())
    subject.notify("New order created")

    return redirect('/dashboard')


@app.route('/order/<int:id>/update', methods=['POST'])
def update_order(id):
    if 'user_id' not in session:
        return redirect('/login')

    order = db.session.get(Order, id)

    if not order or order.user_id != session['user_id']:
        return "Unauthorized"

    order.product_id = request.form['product_id']
    order.quantity = int(request.form['quantity'])

    db.session.commit()

    return redirect('/dashboard')


@app.route('/order/<int:id>/delete')
def delete_order(id):
    if 'user_id' not in session:
        return redirect('/login')

    order = db.session.get(Order, id)

    if not order or order.user_id != session['user_id']:
        return "Unauthorized"

    payment = Payment.query.filter_by(order_id=id).first()

    if payment:
        flash("Cannot delete a paid order", "warning")
        return redirect('/dashboard')

    db.session.delete(order)
    db.session.commit()

    return redirect('/dashboard')


# ---------- PAYMENT ----------
@app.route('/payment/add', methods=['POST'])
def add_payment():
    if 'user_id' not in session:
        return redirect('/login')

    order = db.session.get(Order, int(request.form['order_id']))

    if not order or order.user_id != session['user_id']:
        return "Unauthorized"

    if order.payment:
        return redirect('/dashboard')

    #Strategy
    strategy = NormalPricing()
    total = strategy.calculate(order.product.price, order.quantity)

    #Factory
    payment_method = PaymentFactory.create("card")
    payment_method.pay(total)

    #Adapter
    api = ExternalPaymentAPI()
    adapter = PaymentAdapter(api)
    adapter.pay(total)

    payment = Payment(
        order=order,
        method="card",
        amount=total
    )

    order.status = "paid"

    db.session.add(payment)
    db.session.commit()

    return redirect('/dashboard')


@app.route('/payment/<int:id>/delete')
def delete_payment_user(id):
    if 'user_id' not in session:
        return redirect('/login')

    payment = db.session.get(Payment, id)

    if not payment:
        return redirect('/dashboard')

    if payment.order.user_id != session['user_id']:
        return "Unauthorized"

    order = payment.order
    if order:
        order.status = "created"

    db.session.delete(payment)
    db.session.commit()

    flash("💳 Payment deleted", "warning")

    return redirect('/dashboard')


# ================= ADMIN =================
@app.route('/admin')
@admin_required
def admin_dashboard():
    users = User.query.all()
    orders = Order.query.all()
    payments = Payment.query.all()

    return render_template("admin.html", users=users, orders=orders, payments=payments)

@app.route('/admin/product/add', methods=['POST'])
@admin_required
def add_product():
    name = request.form['name']
    price = float(request.form['price'])

    product = Product(
        name=name,
        price=price
    )
    if Product.query.filter_by(name=name).first():
        flash("Product already exists", "warning")
        return redirect('/admin')

    db.session.add(product)
    db.session.commit()

    flash("✅ Product added successfully", "success")

    return redirect('/admin')

@app.route('/admin/user/<int:id>/delete')
@admin_required
def delete_user(id):
    user = db.session.get(User, id)

    if not user:
        return redirect('/admin')

    if user.role == "admin":
        flash("Cannot delete admin", "danger")
        return redirect('/admin')

    if user.id == session['user_id']:
        flash("You cannot delete yourself", "danger")
        return redirect('/admin')

    db.session.delete(user)
    db.session.commit()

    return redirect('/admin')


@app.route('/admin/payment/<int:id>/delete')
@admin_required
def delete_payment_admin(id):
    payment = db.session.get(Payment, id)

    if not payment:
        return redirect('/admin')

    order = payment.order
    if order:
        order.status = "created"

    db.session.delete(payment)
    db.session.commit()

    flash("💳 Payment deleted", "warning")

    return redirect('/admin')


# ================= RUN =================
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        # admin = User.query.filter_by(email="admin@admin.com").first()
        # if not admin:
        #     admin = User(
        #         name="Admin",
        #         email="admin@admin.com",
        #         password=generate_password_hash("123"),
        #         role="admin"
        #     )
        #     db.session.add(admin)
        #     db.session.commit()

        if Product.query.count() == 0:
            db.session.add(Product(name="Burger", price=5))
            db.session.add(Product(name="Pizza", price=8))
            db.session.add(Product(name="Fries", price=3))
            db.session.commit()

    app.run(debug=True)