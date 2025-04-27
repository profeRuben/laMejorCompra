from datetime import datetime
from flask_login import UserMixin
from extensions import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    
    orders = db.relationship('Order', backref='user', lazy=True)

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    model = db.Column(db.String(50), nullable=True)  # Modelo específico del teléfono
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)  # Stock disponible
    last_updated = db.Column(db.DateTime, default=datetime.now)  # Fecha de última actualización
    category = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    featured = db.Column(db.Boolean, default=False)
    
    order_items = db.relationship('OrderItem', backref='product', lazy=True)

class CartItem:
    """Clase para representar un elemento del carrito (no persistente)"""
    def __init__(self, product, quantity, total):
        self.product = product
        self.quantity = quantity
        self.total = total

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total = db.Column(db.Float, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    zip_code = db.Column(db.String(20), nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    date = db.Column(db.DateTime, default=datetime.now)
    
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade="all, delete-orphan")
    
    @property
    def order_number(self):
        return f"ORD-{self.id:06d}"
