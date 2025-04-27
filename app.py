import os
import logging
import locale
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash, request, session, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix
from forms import LoginForm, RegisterForm, ProductForm, CheckoutForm
from config import Config
from extensions import db, login_manager

# Función para formatear precios en formato chileno
def format_cl_currency(value):
    return f"${int(value):,}".replace(",", ".")

# Setup logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure database - SQLite es más ligero para este proyecto
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///lamejorcompra.db"
# initialize the app with the extension
db.init_app(app)

# Register filters
app.jinja_env.filters['cl_currency'] = format_cl_currency

# Configure Chilean locale for currency formatting
try:
    locale.setlocale(locale.LC_ALL, 'es_CL.UTF-8')
except:
    # Fallback to generic Spanish locale if Chilean not available
    try:
        locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
    except:
        pass

# Inicializar login manager desde extensions.py
login_manager.init_app(app)

# Importamos los modelos después de inicializar la aplicación y la base de datos
from models import User, Product, Order, OrderItem, CartItem

# Creamos las tablas en la base de datos
with app.app_context():
    # Utilizamos una migración para aplicar los cambios al esquema
    # sin perder datos existentes
    # Creamos todas las tablas desde cero ya que SQLite tiene limitaciones para ALTER TABLE
    db.create_all()
    
    # Verificamos si el usuario admin ya existe y lo creamos si no
    if not User.query.filter_by(username='admin').first():
        admin_user = User(
            username='admin',
            email='admin@example.com',
            password_hash=generate_password_hash('admin123'),
            is_admin=True
        )
        db.session.add(admin_user)
        db.session.commit()
        
    # Verificamos si el usuario normal ya existe y lo creamos si no
    if not User.query.filter_by(username='user').first():
        regular_user = User(
            username='user',
            email='user@example.com',
            password_hash=generate_password_hash('user123'),
            is_admin=False
        )
        db.session.add(regular_user)
        db.session.commit()
        
    # Aseguramos que la base de datos tenga al menos una referencia a cada modelo de teléfono
    # Solo ejecutamos esto si no hay productos en la base de datos
    if Product.query.count() == 0:
        # Modelos básicos de iPhone
        iphone_models = [
            {'name': 'Apple iPhone 15', 'model': 'iPhone 15', 'category': 'apple', 'price': 489990},
            {'name': 'Apple iPhone 14', 'model': 'iPhone 14', 'category': 'apple', 'price': 399990},
            {'name': 'Apple iPhone 13', 'model': 'iPhone 13', 'category': 'apple', 'price': 359990},
            {'name': 'Apple iPhone SE', 'model': 'iPhone SE', 'category': 'apple', 'price': 229990}
        ]
        
        # Modelos básicos de Samsung
        samsung_models = [
            {'name': 'Samsung Galaxy S23', 'model': 'Galaxy S23', 'category': 'samsung', 'price': 399990},
            {'name': 'Samsung Galaxy A54', 'model': 'Galaxy A54', 'category': 'samsung', 'price': 199990},
            {'name': 'Samsung Galaxy Z Flip', 'model': 'Galaxy Z Flip', 'category': 'samsung', 'price': 499990}
        ]
        
        # Añadir modelos a la base de datos
        for phone in iphone_models + samsung_models:
            product = Product(
                name=phone['name'],
                model=phone['model'],
                description=f"Teléfono {phone['name']} recondicionado",
                price=phone['price'],
                stock=0,
                category=phone['category'],
                image_url=f"/static/img/{phone['category']}.svg",
                featured=False
            )
            db.session.add(product)
        
        db.session.commit()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    featured_products = Product.query.filter_by(featured=True).all()
    return render_template('home.html', featured_products=featured_products)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('home'))
        else:
            flash('Usuario o contraseña inválidos', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        
        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash('Nombre de usuario ya está en uso', 'danger')
            return render_template('register.html', form=form)
        
        if User.query.filter_by(email=email).first():
            flash('Correo electrónico ya está registrado', 'danger')
            return render_template('register.html', form=form)
        
        # Create new user
        new_user = User(
            username=username, 
            email=email, 
            password_hash=generate_password_hash(password), 
            is_admin=False
        )
        db.session.add(new_user)
        db.session.commit()
        
        flash('¡Registro exitoso! Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión.', 'info')
    return redirect(url_for('home'))

@app.route('/catalog')
def catalog():
    category = request.args.get('category', None)
    search = request.args.get('search', '').lower()
    
    # Consulta base
    query = Product.query
    
    # Filtrar por categoría si se especifica
    if category:
        query = query.filter_by(category=category)
    
    # Filtrar por término de búsqueda si se proporciona
    if search:
        query = query.filter(
            db.or_(
                db.func.lower(Product.name).contains(search),
                db.func.lower(Product.description).contains(search)
            )
        )
    
    # Obtener productos filtrados
    filtered_products = query.all()
    
    # Obtener categorías únicas para la barra lateral
    categories = db.session.query(Product.category).distinct().all()
    categories = sorted([c[0] for c in categories])
    
    return render_template('catalog.html', products=filtered_products, categories=categories, 
                          current_category=category, search_term=search)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    
    # Buscar productos relacionados en la misma categoría
    related_products = Product.query.filter(
        Product.category == product.category,
        Product.id != product.id
    ).limit(4).all()
    
    return render_template('product_detail.html', product=product, related_products=related_products)

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    quantity = int(request.form.get('quantity', 1))
    
    if quantity <= 0:
        flash('La cantidad debe ser positiva', 'danger')
        return redirect(url_for('product_detail', product_id=product_id))
    
    product = Product.query.get_or_404(product_id)
    
    # Initialize cart if it doesn't exist
    if 'cart' not in session:
        session['cart'] = []
    
    # Check if product is already in cart
    for item in session['cart']:
        if item['product_id'] == product_id:
            item['quantity'] += quantity
            flash(f'Agregaste {quantity} más de {product.name} a tu carrito', 'success')
            session.modified = True
            return redirect(url_for('cart'))
    
    # Add new item to cart
    session['cart'].append({
        'product_id': product_id,
        'quantity': quantity
    })
    session.modified = True
    
    flash(f'Agregaste {product.name} a tu carrito', 'success')
    return redirect(url_for('cart'))

@app.route('/cart')
def cart():
    if 'cart' not in session or not session['cart']:
        return render_template('cart.html', cart_items=[], total=0)
    
    cart_items = []
    total = 0
    
    for item in session['cart']:
        product = Product.query.get(item['product_id'])
        if product:
            item_total = product.price * item['quantity']
            total += item_total
            cart_items.append(CartItem(product, item['quantity'], item_total))
    
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/update_cart', methods=['POST'])
def update_cart():
    product_id = int(request.form.get('product_id'))
    quantity = int(request.form.get('quantity'))
    
    if 'cart' not in session:
        flash('Tu carrito está vacío', 'warning')
        return redirect(url_for('cart'))
    
    # Verificar que el producto existe en la base de datos
    product = Product.query.get(product_id)
    if not product:
        flash('Producto no encontrado', 'danger')
        return redirect(url_for('cart'))
    
    if quantity <= 0:
        # Eliminar el producto del carrito
        session['cart'] = [item for item in session['cart'] if item['product_id'] != product_id]
        flash('Producto eliminado del carrito', 'info')
    else:
        # Actualizar cantidad
        for item in session['cart']:
            if item['product_id'] == product_id:
                item['quantity'] = quantity
                flash('Carrito actualizado', 'success')
                break
    
    session.modified = True
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if 'cart' not in session or not session['cart']:
        flash('Tu carrito está vacío', 'warning')
        return redirect(url_for('cart'))
    
    # Calculate order total
    cart_items = []
    total = 0
    
    for item in session['cart']:
        product = Product.query.get(item['product_id'])
        if product:
            item_total = product.price * item['quantity']
            total += item_total
            cart_items.append(CartItem(product, item['quantity'], item_total))
    
    form = CheckoutForm()
    
    if form.validate_on_submit():
        # Create new order
        order = Order(
            user_id=current_user.id,
            total=total,
            full_name=form.full_name.data,
            email=form.email.data,
            address=form.address.data,
            city=form.city.data,
            state=form.state.data,
            zip_code=form.zip_code.data,
            payment_method=form.payment_method.data,
            date=datetime.now()
        )
        
        db.session.add(order)
        db.session.flush()  # Para obtener el ID generado
        
        # Crear items del pedido
        for item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product.id,
                quantity=item.quantity,
                price=item.product.price
            )
            db.session.add(order_item)
        
        db.session.commit()
        
        # Clear cart
        session.pop('cart', None)
        
        # Store order ID in session for confirmation page
        session['last_order_id'] = order.id
        
        flash('¡Pedido realizado con éxito!', 'success')
        return redirect(url_for('confirmation'))
    
    return render_template('checkout.html', form=form, cart_items=cart_items, total=total)

@app.route('/confirmation')
@login_required
def confirmation():
    order_id = session.get('last_order_id')
    if not order_id:
        flash('No se encontró un pedido reciente', 'warning')
        return redirect(url_for('home'))
    
    order = Order.query.get(order_id)
    if not order:
        flash('Pedido no encontrado', 'danger')
        return redirect(url_for('home'))
    
    return render_template('confirmation.html', order=order)

# Admin routes
@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        abort(403)
    
    # Obtener todos los productos de la base de datos
    products = Product.query.all()
    
    return render_template('admin/index.html', products=products)

@app.route('/admin/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    if not current_user.is_admin:
        abort(403)
    
    form = ProductForm()
    
    if form.validate_on_submit():
        new_product = Product(
            name=form.name.data,
            description=form.description.data,
            model=form.model.data,
            price=form.price.data,
            stock=form.stock.data,
            category=form.category.data,
            image_url=form.image_url.data,
            featured=form.featured.data,
            last_updated=datetime.now()
        )
        
        db.session.add(new_product)
        db.session.commit()
        
        flash('Producto añadido exitosamente', 'success')
        return redirect(url_for('admin'))
    
    return render_template('admin/add_product.html', form=form)

@app.route('/admin/edit_product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    if not current_user.is_admin:
        abort(403)
    
    product = Product.query.get_or_404(product_id)
    
    form = ProductForm(obj=product)
    
    if form.validate_on_submit():
        product.name = form.name.data
        product.description = form.description.data
        product.model = form.model.data
        product.price = form.price.data
        product.stock = form.stock.data
        product.category = form.category.data
        product.image_url = form.image_url.data
        product.featured = form.featured.data
        product.last_updated = datetime.now()
        
        db.session.commit()
        
        flash('Producto actualizado exitosamente', 'success')
        return redirect(url_for('admin'))
    
    return render_template('admin/edit_product.html', form=form, product=product)

@app.route('/admin/delete_product/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    if not current_user.is_admin:
        abort(403)
    
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    
    flash('Producto eliminado exitosamente', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/reports')
@login_required
def admin_reports():
    if not current_user.is_admin:
        abort(403)
    
    # Consultar datos reales de ventas desde la base de datos
    orders = Order.query.all()
    
    # Si no hay pedidos, mostrar mensaje de que no hay datos
    if not orders:
        return render_template('admin/reports.html', 
                             no_data=True,
                             version='1.2')
    
    # Calcular estadísticas de ventas
    total_sales = sum(order.total for order in orders)
    avg_order_value = total_sales / len(orders) if orders else 0
    
    # Obtener productos más vendidos
    most_sold_products = db.session.query(
        Product.name,
        db.func.sum(OrderItem.quantity).label('total_qty')
    ).join(OrderItem).group_by(Product.id).order_by(db.desc('total_qty')).limit(5).all()
    
    # Obtener datos para gráfico de ventas por categoría
    sales_by_category = db.session.query(
        Product.category,
        db.func.sum(OrderItem.quantity * OrderItem.price).label('total')
    ).join(OrderItem).group_by(Product.category).all()
    
    return render_template('admin/reports.html', 
                          orders=orders,
                          total_sales=total_sales,
                          avg_order_value=avg_order_value,
                          most_sold_products=most_sold_products,
                          sales_by_category=sales_by_category,
                          no_data=False,
                          version='1.2')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

@app.route('/admin/update-catalog', methods=['POST'])
@login_required
def update_catalog():
    if not current_user.is_admin:
        abort(403)
    
    try:
        # Importamos la función de web_scraper.py
        from web_scraper import update_product_prices_and_stock
        
        # Actualizar precios y stock de los productos existentes
        updated_count = update_product_prices_and_stock()
        
        if updated_count > 0:
            flash(f'Se actualizaron {updated_count} productos del catálogo con éxito', 'success')
        else:
            flash('No se encontraron productos para actualizar en el catálogo', 'info')
            
        return redirect(url_for('admin'))
        
    except Exception as e:
        app.logger.error(f"Error actualizando catálogo: {str(e)}")
        flash(f'Error al actualizar el catálogo: {str(e)}', 'danger')
        return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
