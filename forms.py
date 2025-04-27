from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FloatField, TextAreaField, SelectField, HiddenField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, URL, Optional

class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember = BooleanField('Recordarme')
    submit = SubmitField('Iniciar Sesión')

class RegisterForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired(), Length(min=4, max=25)])
    email = StringField('Correo Electrónico', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[
        DataRequired(),
        Length(min=6, message='La contraseña debe tener al menos 6 caracteres')
    ])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[
        DataRequired(),
        EqualTo('password', message='Las contraseñas deben coincidir')
    ])
    submit = SubmitField('Registrarse')

class ProductForm(FlaskForm):
    name = StringField('Nombre del Producto', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Descripción', validators=[DataRequired(), Length(max=500)])
    model = StringField('Modelo', validators=[Length(max=50)], default='')
    price = FloatField('Precio ($)', validators=[DataRequired(), NumberRange(min=0.01)])
    stock = IntegerField('Stock', validators=[NumberRange(min=0)], default=0)
    category = SelectField('Categoría', 
                          choices=[
                              ('apple', 'Apple'),
                              ('samsung', 'Samsung')
                          ],
                          validators=[DataRequired()])
    image_url = StringField('URL de Imagen', validators=[DataRequired(), URL()], 
                           default='/static/img/apple.svg',
                           description='URL de imagen SVG (puede usar /static/img/apple.svg o /static/img/samsung.svg)')
    featured = BooleanField('Producto Destacado')
    submit = SubmitField('Guardar Producto')

class CheckoutForm(FlaskForm):
    full_name = StringField('Nombre Completo', validators=[DataRequired(), Length(max=100)])
    email = StringField('Correo Electrónico', validators=[DataRequired(), Email()])
    address = StringField('Dirección', validators=[DataRequired(), Length(max=200)])
    city = StringField('Ciudad', validators=[DataRequired(), Length(max=100)])
    state = StringField('Región/Provincia', validators=[DataRequired(), Length(max=100)])
    zip_code = StringField('Código Postal', validators=[DataRequired(), Length(max=20)])
    payment_method = SelectField('Método de Pago', 
                                choices=[
                                    ('credit_card', 'Tarjeta de Crédito'),
                                    ('paypal', 'PayPal'),
                                    ('bitcoin', 'Bitcoin')
                                ],
                                validators=[DataRequired()])
    card_number = StringField('Número de Tarjeta', validators=[Optional(), Length(min=16, max=16)])
    card_expiry = StringField('Fecha de Vencimiento (MM/AA)', validators=[Optional(), Length(min=5, max=5)])
    card_cvv = StringField('CVV', validators=[Optional(), Length(min=3, max=4)])
    submit = SubmitField('Realizar Pedido')
