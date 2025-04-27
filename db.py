from models import User, Product
from werkzeug.security import generate_password_hash

# In-memory data storage
_users = []
_products = []

# Initialize with some sample users and products
def init_db():
    global _users, _products
    
    # Initialize sample users if empty
    if not _users:
        _users = [
            User(
                id=1,
                name="Admin User",
                email="admin@example.com",
                password_hash=generate_password_hash("admin123"),
                is_admin=True
            ),
            User(
                id=2,
                name="Regular User",
                email="user@example.com",
                password_hash=generate_password_hash("user123"),
                is_admin=False
            )
        ]
    
    # Initialize sample products if empty
    if not _products:
        _products = [
            Product(
                id=1,
                name="Mechanical Keyboard",
                description="A high-quality mechanical keyboard with RGB lighting and tactile switches for an enhanced typing experience.",
                price=89.99,
                category="Keyboards",
                image_url="https://cdn-icons-png.flaticon.com/512/2553/2553589.png",
                stock=50
            ),
            Product(
                id=2,
                name="27-inch 4K Monitor",
                description="Ultra HD 4K monitor with IPS panel for incredible color accuracy and wide viewing angles.",
                price=299.99,
                category="Monitors",
                image_url="https://cdn-icons-png.flaticon.com/512/900/900334.png",
                stock=25
            ),
            Product(
                id=3,
                name="Wireless Gaming Mouse",
                description="High-precision wireless mouse with adjustable DPI settings and programmable buttons for gamers.",
                price=59.99,
                category="Mice",
                image_url="https://cdn-icons-png.flaticon.com/512/2267/2267642.png",
                stock=75
            ),
            Product(
                id=4,
                name="Noise-Cancelling Headphones",
                description="Premium wireless headphones with active noise cancellation and long battery life.",
                price=149.99,
                category="Headphones",
                image_url="https://cdn-icons-png.flaticon.com/512/716/716405.png",
                stock=40
            ),
            Product(
                id=5,
                name="Ergonomic Keyboard",
                description="Split design ergonomic keyboard for comfortable typing and reduced strain.",
                price=119.99,
                category="Keyboards",
                image_url="https://cdn-icons-png.flaticon.com/512/2553/2553590.png",
                stock=30
            ),
            Product(
                id=6,
                name="24-inch Gaming Monitor",
                description="144Hz gaming monitor with 1ms response time for smooth gameplay.",
                price=249.99,
                category="Monitors",
                image_url="https://cdn-icons-png.flaticon.com/512/900/900335.png",
                stock=20
            ),
            Product(
                id=7,
                name="Ergonomic Mouse",
                description="Vertical ergonomic mouse designed to reduce wrist strain during long computing sessions.",
                price=39.99,
                category="Mice",
                image_url="https://cdn-icons-png.flaticon.com/512/2267/2267645.png",
                stock=60
            ),
            Product(
                id=8,
                name="Gaming Headset",
                description="Surround sound gaming headset with detachable microphone for immersive gaming experience.",
                price=89.99,
                category="Headphones",
                image_url="https://cdn-icons-png.flaticon.com/512/716/716407.png",
                stock=35
            )
        ]

# Initialize the database with sample data
init_db()

# User-related functions
def get_users():
    return _users

def get_user_by_id(user_id):
    return next((user for user in _users if user.id == user_id), None)

def get_user_by_email(email):
    return next((user for user in _users if user.email == email), None)

def add_user(user):
    _users.append(user)

# Product-related functions
def get_products():
    return _products

def get_product_by_id(product_id):
    return next((product for product in _products if product.id == product_id), None)

def add_product(product):
    _products.append(product)

def update_product(updated_product):
    for index, product in enumerate(_products):
        if product.id == updated_product.id:
            _products[index] = updated_product
            break

def delete_product(product_id):
    global _products
    _products = [product for product in _products if product.id != product_id]
