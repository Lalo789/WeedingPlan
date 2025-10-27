from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, DecimalField, IntegerField, SelectField, DateField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, NumberRange, Optional
from models import Usuario
from datetime import datetime


class LoginForm(FlaskForm):

    "Formulario de inicio de sesion "

    username = StringField('Usuario',
        validators = [
            DataRequired(message="El nombre de usuario es obligatorio"),
            Length(min =3 , max = 80, message = 'El usuario debe tener entre 3 y 80 caracteres')
        ],
        render_kw={"placeholder": "Ingrese su usuario"}
        )
    
    password = PasswordField('Contraseña',
        validators = [
            DataRequired(message="La contraseña es obligatoria"),
        ], 
        render_kw={"placeholder": "Ingrese su contraseña"}
        )
    
    remember = BooleanField('Recordarme')


class RegistroForm(FlaskForm):

    "Formulario de registro de usuario "

    username = StringField('Nombre de Usuario',
        validators = [
            DataRequired(message="El nombre de usuario es obligatorio"),
            Length(min = 3, max = 80, message = 'El usuario debe tener entre 3 y 80 caracteres')
        ],
        render_kw={"placeholder": "Elige un nombre de usuario"}
        )
    
    nombre_completo = StringField('Nombre Completo',
            validators = [
                DataRequired(message="El nombre completo es obligatorio"),
                Length(min = 3, max = 120, message = 'El nombre completo debe tener entre 3 y 120 caracteres')
            ],
            render_kw={"placeholder": "Tu nombre completo"}
            )

    email = StringField('Correo Electrónico',
            validators = [
                DataRequired(message="El correo electrónico es obligatorio"),
                Email(message="Ingrese un correo electrónico válido")
            ],
            render_kw={"placeholder": "tu@email.com"}
            )
        
    telefono = StringField('Teléfono',
            validators = [
                Optional(),
                Length(min=10, max=15, message='El telefono debe teener entre 10 y 15 caracteres')
            ],
            render_kw={"placeholder":"10 digitos"}
            )

    password = PasswordField('Contraseña',
            validators = [
                DataRequired(message="La contraseña es obligatoria"),
                Length(min = 6, message = 'La contraseña debe tener al menos 6 caracteres'),
                EqualTo('confirm_password', message='Las contraseñas deben coincidir')
            ],
            render_kw={"placeholder": "Ingrese su contraseña"}
            )
        
    confirmar_password = PasswordField('Confirmar Contraseña',
            validators = [
                DataRequired(message="Por favor confirme su contraseña")
            ],
            render_kw={"placeholder": "Confirme su contraseña"}
            )

    def validate_username(self, username):
            "Validacion personalizada para nombre de usuario único"
            usuario = Usuario.query.filter_by(username=username.data).first()
            if usuario:
                raise ValidationError('El nombre de usuario ya está en uso. Por favor elija otro.')

    def validate_email(self, email):
            usuario = Usuario.query.filter_by(email=email.data).first()
            if usuario:
                raise ValidationError('El correo electrónico ya está registrado. Por favor utilice otro.')
            

class EventoForm(FlaskForm):
    "Formulario para crear o modificar eventos"

    titulo = StringField('Título del Evento',
        validators = [
            DataRequired(message="El título es obligatorio"),
            Length(min=3, max=100, message='El título debe tener entre 3 y 100 caracteres')
        ],
        render_kw={"placeholder": "Ingrese el título del evento"}
        )

    descripcion = TextAreaField('Descripción',
        validators = [
            Optional(),
            Length(max=500, message='La descripción no puede exceder los 500 caracteres')
            ],
        render_kw={"placeholder": "Describe el evento",
        "rows": 4
            }
        )

    fecha_evento = DateField('Fecha del Evento',
        validators = [
            DataRequired(message="La fecha es obligatoria")
        ],
        render_kw= {
        "type": "datetime-local",
        "Placeholder": "dd/mm/aaaa hh:mm"
        }
        )

    Lugar = StringField('Lugar',
        validators = [
            Optional(),
            Length(max=150, message='La ubicación no puede exceder los 150 caracteres')
        ],
        render_kw={"placeholder": "Direccion o nombre del lugar"}
        )
    
    num_invitados = IntegerField('Número de Invitados',
        validators = [
             Optional(),
             NumberRange(min=1, max=10000, message='ingresa un numero valido de invitados')
        ],
        render_kw={"placeholder": "Cantidad estimada de invitados"}
        )
    
    presupuesto_estimado = DecimalField('Presupuesto Estimado',
        validators = [
             Optional(),
             NumberRange(min=0, message='El presupuesto debe ser un número positivo')
        ],
        render_kw={
             "placeholder": "Presupuesto en pesos",
             "step": "0.01"
             }
        )
    
    estado = SelectField('Estado', 
        choices =[
            ('pendiente', 'Pendiente'),
            ('confirmado', 'Confirmado'),
            ('cancelado', 'Cancelado'),
            ('completado', 'Completado')
        ],
        validators=[DataRequired()]
    )
    

class ServicioForm(FlaskForm):
     "Formulario para que los administradores getionen los servicios"

     nombre = StringField('Nombre del Servicio',
        validators = [
            DataRequired(message="El nombre del servicio es obligatorio"),
            Length(min=3, max=100, message='El nombre debe tener entre 3 y 100 caracteres')
        ],
        render_kw={"placeholder": "Ingrese el nombre del servicio"}
    )
     
     descripcion = TextAreaField('Descripción',
        validators = [
            Optional(),
            Length(max=500, message='La descripción no puede exceder los 500 caracteres')
        ],
        render_kw={"placeholder": "Describe el servicio",
                   "rows": 4
        }
    )
     
     precio_base = DecimalField('Precio Base',
        validators = [
             DataRequired(message="El precio base es obligatorio"),
             NumberRange(min=0, message='El precio debe ser un número positivo')
        ],
        render_kw={
             "placeholder": "Precio en pesos",
             "step": "0.01"
             }
     )

     categoria = SelectField('Categoría',
        choices=[
            ('fotografia', 'Fotografía'),
            ('catering', 'Catering'),
            ('decoracion', 'Decoración'),
            ('musica', 'Música'),
            ('transporte', 'Transporte'),
            ('otros', 'Otros')
        ],
        validators=[DataRequired(message='selecciona una categoría')]
     )

     imagen_url = StringField('URL de la Imagen',
        validators = [
            Optional(),
            Length(max=255, message='La URL no puede exceder los 255 caracteres')
        ],
        render_kw={"placeholder": "https://ejemplo.com/imagen.jpg"}

     )

     disponible = BooleanField('Disponible')

class ProveedorForm(FlaskForm):
    "Formulario para gestionar proveedores solo para administradores."

    nombre = StringField('Nombre del Proveedor', 
        validators=[
            DataRequired(message='El nombre del proveedor es obligatorio'),
            Length(min=3, max=150, message='El nombre debe tener entre 3 y 150 caracteres')
        ],
        render_kw={"placeholder": "Nombre de la empresa o persona"}
    )
    
    tipo_servicio = StringField('Tipo de Servicio', 
        validators=[
            Optional(),
            Length(max=100, message='El tipo de servicio no puede exceder 100 caracteres')
        ],
        render_kw={"placeholder": "Fotógrafo, Florista, DJ"}
    )
    
    contacto = StringField('Nombre de Contacto', 
        validators=[
            Optional(),
            Length(max=100, message='El nombre de contacto no puede exceder 100 caracteres')
        ],
        render_kw={"placeholder": "Persona de contacto"}
    )
    
    telefono = StringField('Teléfono', 
        validators=[
            Optional(),
            Length(min=10, max=15, message='El teléfono debe tener entre 10 y 15 caracteres')
        ],
        render_kw={"placeholder": "10 dígitos"}
    )
    
    email = StringField('Correo Electrónico', 
        validators=[
            Optional(),
            Email(message='Ingresa un correo electrónico válido')
        ],
        render_kw={"placeholder": "email@proveedor.com"}
    )
    
    calificacion = DecimalField('Calificación', 
        validators=[
            Optional(),
            NumberRange(min=0, max=5, message='La calificación debe estar entre 0 y 5')
        ],
        render_kw={
            "placeholder": "De 0.00 a 5.00",
            "step": "0.01"
        }
    )
    
    notas = TextAreaField('Notas', 
        validators=[
            Optional()
        ],
        render_kw={
            "placeholder": "Información adicional sobre el proveedor",
            "rows": 3
        }
    )
    
    activo = BooleanField('Activo')


class AgregarServicioEventoForm(FlaskForm):
    "Formulario para agregar servicios a un evento"
    servicio_id = SelectField('Servicio', 
        coerce=int,
        validators=[DataRequired(message='Debes seleccionar un servicio')]
    )
    
    precio_acordado = DecimalField('Precio Acordado', 
        validators=[
            DataRequired(message='El precio acordado es obligatorio'),
            NumberRange(min=0.01, message='El precio debe ser mayor a cero')
        ],
        render_kw={
            "placeholder": "Precio para este evento",
            "step": "0.01"
        }
    )
    
    notas = TextAreaField('Notas', 
        validators=[Optional()],
        render_kw={
            "placeholder": "Detalles específicos de este servicio para el evento",
            "rows": 2
        }
    )