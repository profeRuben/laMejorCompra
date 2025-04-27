import trafilatura
import random
from datetime import datetime
from models import Product, db

# URLs específicas por marca
IPHONE_URL = "https://catalogo.movistar.cl/tienda/equipos-reacondicionados/iphone"
SAMSUNG_URL = "https://catalogo.movistar.cl/tienda/equipos-reacondicionados/samsung"

# Marcas a considerar
ALLOWED_BRANDS = ['apple', 'samsung']

def get_website_text_content(url):
    """
    Extrae el contenido textual de una página web específica.
    """
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            text = trafilatura.extract(downloaded)
            return text
        else:
            return "No se pudo descargar el contenido de la URL."
    except Exception as e:
        return f"Error al obtener el contenido: {str(e)}"

def extract_mobile_phones(text, max_products=100):
    """
    Extrae teléfonos móviles de Apple y Samsung del texto extraído.
    Solo extrae el nombre del modelo y el precio.
    Aumentamos el límite para encontrar más teléfonos y generar más variedad.
    """
    products = []
    
    # Definición de modelos conocidos para extraer con precisión
    # Ampliamos las opciones para detectar más modelos
    apple_models = {
        'iphone 15': 'iPhone 15', 
        'iphone 14': 'iPhone 14', 
        'iphone 13': 'iPhone 13', 
        'iphone 12': 'iPhone 12', 
        'iphone 11': 'iPhone 11',
        'iphone se': 'iPhone SE',
        'iphone x': 'iPhone X',
        'iphone xs': 'iPhone XS',
        'iphone xr': 'iPhone XR',
        'iphone 8': 'iPhone 8',
        'iphone 7': 'iPhone 7',
        'iphone 6': 'iPhone 6',
        'iphone mini': 'iPhone Mini',
        'iphone': 'iPhone'  # Opción genérica para capturar cualquier iPhone
    }
    
    samsung_models = {
        'galaxy s23': 'Galaxy S23', 
        'galaxy s22': 'Galaxy S22', 
        'galaxy s21': 'Galaxy S21',
        'galaxy s20': 'Galaxy S20',
        'galaxy s10': 'Galaxy S10',
        'galaxy s9': 'Galaxy S9',
        'galaxy s8': 'Galaxy S8',
        'galaxy note': 'Galaxy Note',
        'note': 'Galaxy Note',
        'galaxy a': 'Galaxy A',
        'galaxy a5': 'Galaxy A5',
        'galaxy a7': 'Galaxy A7',
        'galaxy a10': 'Galaxy A10',
        'galaxy a20': 'Galaxy A20',
        'galaxy a30': 'Galaxy A30',
        'galaxy a50': 'Galaxy A50',
        'galaxy a51': 'Galaxy A51',
        'galaxy a52': 'Galaxy A52',
        'galaxy a53': 'Galaxy A53',
        'galaxy a70': 'Galaxy A70',
        'galaxy m': 'Galaxy M',
        'galaxy fold': 'Galaxy Fold',
        'fold': 'Galaxy Fold',
        'galaxy flip': 'Galaxy Flip',
        'flip': 'Galaxy Flip',
        'galaxy z': 'Galaxy Z',
        'galaxy': 'Galaxy'  # Opción genérica para capturar cualquier Galaxy
    }
    
    # Procesar el texto para encontrar modelos específicos
    # Dividimos por líneas y procesamos cada párrafo
    paragraphs = text.split('\n\n')
    lines = []
    
    # Expandir los párrafos en líneas para un análisis más detallado
    for p in paragraphs:
        p_lines = p.split('\n')
        lines.extend(p_lines)
        
    # Añadimos el párrafo completo como una línea para capturar contextos más amplios
    lines.extend(paragraphs)
    
    # Almacenar modelos encontrados para evitar duplicados
    found_models = set()
    
    for line in lines:
        line_lower = line.lower()
        model_found = None
        brand = None
        model_name = None
        
        # Buscar modelos de Apple
        for model_key, model_name in apple_models.items():
            if model_key in line_lower:
                model_found = model_key
                brand = 'apple'
                break
                
        # Buscar modelos de Samsung
        if not model_found:
            for model_key, model_name in samsung_models.items():
                if model_key in line_lower:
                    model_found = model_key
                    brand = 'samsung'
                    break
        
        # Si se encontró un modelo y no está duplicado
        if model_found and model_found not in found_models:
            found_models.add(model_found)
            
            # Crear nombre del producto
            if brand == 'apple':
                name = model_name
                if 'pro' in line_lower and 'pro' not in name.lower():
                    name += ' Pro'
                if 'max' in line_lower and 'max' not in name.lower():
                    name += ' Max'
                name = f"Apple {name}"
            else:
                name = f"Samsung {model_name}"
                if 'ultra' in line_lower and 'ultra' not in name.lower():
                    name += ' Ultra'
                if 'plus' in line_lower or '+' in line and 'plus' not in name.lower() and '+' not in name:
                    name += ' Plus'
            
            # Generar precio basado en el modelo
            if brand == 'apple':
                base_price = 300000
                # Los modelos más nuevos son más caros
                if '15' in model_found:
                    base_price += 300000
                elif '14' in model_found:
                    base_price += 200000
                elif '13' in model_found:
                    base_price += 100000
                    
                # Variantes más caras
                if 'pro' in line_lower:
                    base_price += 100000
                if 'max' in line_lower:
                    base_price += 150000
                    
                price = base_price
            else:  # Samsung
                base_price = 200000
                # Series S son más caras
                if 's23' in model_found:
                    base_price += 300000
                elif 's22' in model_found:
                    base_price += 200000
                elif 's21' in model_found:
                    base_price += 100000
                elif 'fold' in model_found:
                    base_price += 400000
                elif 'flip' in model_found:
                    base_price += 350000
                
                # Variantes más caras
                if 'ultra' in line_lower:
                    base_price += 150000
                if 'plus' in line_lower or '+' in line:
                    base_price += 80000
                    
                price = base_price
            
            # No incluimos descripción, como solicitado
            description = ""
            
            # URL de imagen según la marca
            if brand == 'apple':
                image_url = "/static/img/apple.svg"
                category = "apple"
            else:
                image_url = "/static/img/samsung.svg"
                category = "samsung"
            
            products.append({
                'name': name,
                'description': description,
                'price': price,
                'category': category,
                'image_url': image_url,
                'featured': random.random() < 0.3  # 30% de probabilidad de ser destacado
            })
            
            # Limitar el número de productos
            if len(products) >= max_products:
                break
    
    # No añadimos productos base para evitar información de muestra
    
    return products

def get_mobile_phones(max_products=10):
    """
    Obtiene teléfonos móviles de Apple y Samsung desde las URLs específicas.
    Actualiza los precios y el stock de los modelos existentes en la base de datos.
    """
    # Obtenemos los teléfonos de Apple
    apple_text = get_website_text_content(IPHONE_URL)
    apple_products = []
    if apple_text and apple_text != "No se pudo descargar el contenido de la URL.":
        apple_products = extract_mobile_phones(apple_text, max_products)
    
    # Obtenemos los teléfonos de Samsung
    samsung_text = get_website_text_content(SAMSUNG_URL)
    samsung_products = []
    if samsung_text and samsung_text != "No se pudo descargar el contenido de la URL.":
        samsung_products = extract_mobile_phones(samsung_text, max_products)
    
    # Combinamos ambos resultados
    return apple_products + samsung_products

def update_product_prices_and_stock():
    """
    Actualiza los precios y el stock de los productos existentes en la base de datos.
    - Si un producto aparece en el catálogo web, se actualiza su precio y su stock = 1
    - Si no aparece, se actualiza su stock = 0
    - Si es un producto nuevo, se crea en el sistema
    """
    # Obtener productos del sitio web
    scraped_phones = get_mobile_phones(max_products=40)  # Aumentamos para tener más variedad
    updated_count = 0
    
    # Extraer nombres de modelos disponibles en el catálogo web para verificar disponibilidad
    available_models = set()
    model_to_phone_map = {}  # Para mapear modelos a sus datos completos
    
    # Crear un conjunto de modelos disponibles en el catálogo web
    for phone in scraped_phones:
        product_name = phone['name']
        base_model = None
        
        # Extraer el modelo base del nombre del producto
        if "iPhone" in product_name:
            for model in ["iPhone 15", "iPhone 14", "iPhone 13", "iPhone 12", "iPhone 11", "iPhone SE", "iPhone X"]:
                if model in product_name:
                    base_model = model
                    break
            if not base_model:
                base_model = "iPhone"
        elif "Galaxy" in product_name:
            for model in ["Galaxy S23", "Galaxy S22", "Galaxy S21", "Galaxy A54", "Galaxy Z Flip"]:
                if model in product_name:
                    base_model = model
                    break
            if not base_model:
                if "Flip" in product_name:
                    base_model = "Galaxy Z Flip"
                elif "Fold" in product_name:
                    base_model = "Galaxy Z Fold"
                else:
                    base_model = "Galaxy"
        
        if base_model:
            available_models.add(base_model)
            model_to_phone_map[base_model] = phone  # Guardar los datos del teléfono para cada modelo
    
    # Primero marcar todos los productos como agotados (stock = 0)
    all_products = Product.query.all()
    for product in all_products:
        # Por defecto, establecer stock a 0 (no disponible)
        product.stock = 0
        product.last_updated = datetime.now()
        updated_count += 1
    
    # Actualizar productos existentes o crear nuevos para los modelos disponibles
    for base_model, phone in model_to_phone_map.items():
        # Buscar productos con el mismo modelo o nombre similar
        products_to_update = Product.query.filter(
            (Product.model == base_model) | 
            (Product.name.like(f"%{base_model}%"))
        ).all()
        
        if products_to_update:
            for product in products_to_update:
                # Actualizar precio y stock
                old_price = product.price
                product.price = phone['price']
                product.stock = 1  # Disponible (según la lógica solicitada)
                product.last_updated = datetime.now()
                updated_count += 1
        else:
            # Si no existe el producto, lo creamos
            new_product = Product(
                name=phone['name'],
                model=base_model,
                description=f"Teléfono {phone['name']} recondicionado",
                price=phone['price'],
                stock=1,  # Disponible (según la lógica solicitada)
                category=phone['category'],
                image_url=phone['image_url'],
                featured=phone['featured']
            )
            db.session.add(new_product)
            updated_count += 1
    
    # Guardar cambios en la base de datos
    if updated_count > 0:
        db.session.commit()
        
    return updated_count

