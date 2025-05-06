import pytest
from models import Product
from extensions import db

@pytest.fixture
def test_product(app):
    """Fixture para crear un producto de prueba."""
    with app.app_context():
        product = Product(
            name='Test Product',
            model='Test Model',
            description='Test Description',
            price=10000,
            stock=10,
            category='test',
            image_url='/static/img/test.svg',
            featured=True
        )
        db.session.add(product)
        db.session.commit()
        
        yield product
        
        # Limpiar después de la prueba
        db.session.delete(product)
        db.session.commit()

def test_add_to_cart(client, test_product):
    """Prueba añadir un producto al carrito."""
    response = client.post(f'/add_to_cart/{test_product.id}', data={
        'quantity': 2
    }, follow_redirects=True)
    
    assert response.status_code == 200
    
    # Verificar mensaje de éxito
    assert b'Agregaste Test Product a tu carrito' in response.data
    
    # Verificar que el producto está en el carrito
    response = client.get('/cart')
    assert b'Test Product' in response.data
    assert b'20.000' in response.data  # Precio total (10000 * 2)

def test_update_cart(client, test_product):
    """Prueba actualizar la cantidad de un producto en el carrito."""
    # Primero agregamos un producto al carrito
    client.post(f'/add_to_cart/{test_product.id}', data={'quantity': 1})
    
    # Luego actualizamos la cantidad
    response = client.post('/update_cart', data={
        'product_id': test_product.id,
        'quantity': 3
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Carrito actualizado' in response.data
    
    # Verificar que la cantidad se actualizó
    response = client.get('/cart')
    assert b'30.000' in response.data  # Precio total (10000 * 3)

def test_remove_from_cart(client, test_product):
    """Prueba eliminar un producto del carrito."""
    # Primero agregamos un producto al carrito
    client.post(f'/add_to_cart/{test_product.id}', data={'quantity': 1})
    
    # Luego lo eliminamos (cantidad 0)
    response = client.post('/update_cart', data={
        'product_id': test_product.id,
        'quantity': 0
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Producto eliminado del carrito' in response.data
    
    # Verificar que el carrito está vacío
    response = client.get('/cart')
    assert b'Tu carrito est' in response.data