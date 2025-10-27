from db import db
from flask_login import UserMixin
from datetime import datetime

class Cliente(db.Model):
    __tablename__ = 'clientes'  
    id_cliente = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(100), unique=True, nullable=False)
    telefono = db.Column(db.String(15))
    direccion = db.Column(db.String(200))

    def __repr__(self):
        return f'<Cliente {self.nombre}>'
    
class Usuario(UserMixin, db.Model):
    "Autenticación de usuarios"

    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(90), unique=True, nullable=False, index=True)
    password = db.Column(db.String(200), nullable=False)

    "Role de administrador o cliente"
    rol = db.Column(db.String(20), nullable=False, default='cliente')

    "Informacion"
    nombre_completo = db.Column(db.String(100))
    telefono = db.Column(db.String(15))
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    activo = db.Column(db.Boolean, default=True)

    "Relaciones"
    eventos = db.relationship('Evento', backref='usuario', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Usuario {self.username}> - {self.rol}'
    
    "Metodo para saber si es admin"
    def es_admin(self):
        return self.rol == 'admin'
    
class Servicio(db.Model):
        "Servicios que ofrece"
        __tablename__ = 'servicios'

        id_servicio = db.Column(db.Integer, primary_key=True)
        nombre = db.Column(db.String(100), nullable=False)
        descripcion = db.Column(db.String(255))
        precio_base = db.Column(db.Float, nullable=False)
        categoria = db.Column(db.String(50))
        disponible = db.Column(db.Boolean, default=True)
        imagen_url = db.Column(db.String(255))
        fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

        "Relacion de muchos a muchos"
        eventos = db.relationship('EventoServicio', backref='servicio', lazy=True)

        def __repr__(self):
            return f'<Servicio {self.nombre}'
        
class Proveedor(db.Model):
     
     "Proveedores que ayudaran a relizar los servicios"

     __tablename__ = 'proveedores'

     id = db.Column(db.Integer, primary_key=True)
     nombre = db.Column(db.String(100), nullable=False)
     tipo_servicio = db.Column(db.String(100), nullable=False)
     contacto = db.Column(db.String(100))
     telefono = db.Column(db.String(15))
     email = db.Column(db.String(100))
     calificacion = db.Column(db.Numeric(3, 2))
     notas = db.Column(db.Text)
     activo = db.Column(db.Boolean, default = True)

     def __repr__(self):
          return f'<Proveedor {self.nombre}>'
     

class Evento(db.Model):
     
     "Evento principal que pueden reservar"

     __tablename__ ='eventos'

     id = db.Column(db.Integer, primary_key=True)
     usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
     titulo = db.Column(db.String(100), nullable=False)
     descripcion = db.Column(db.Text)
     fecha_evento = db.Column(db.DateTime, nullable=False)
     lugar = db.Column(db.String(200))
     num_invitados = db.Column(db.Integer)
     presupuesto_estimado = db.Column(db.Numeric(10, 2))
     "Pendente, Confirmado, Cancelado, Completado"
     estado = db.Column(db.String(20), default='pendiente')

     fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
     fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
     servicios_contratados = db.relationship('EventoServicio', backref='evento', lazy=True, cascade="all, delete-orphan")

     def __repr__(self):
          return f"<Evento {self.titulo} - {self.fecha_evento}>"
     
     def calcular_total(self):
        "Calcula el costo total del evento y los servicios"
        total = sum([es.precio_acordado for es in self.servicios_contratados])
        return total
     
class EventoServicio(db.Model):
     "Relacion muchos a muchos entre Evento y Servicio"

     __tablename__ = 'evento_servicio'

     id = db.Column(db.Integer, primary_key=True)
     evento_id = db.Column(db.Integer, db.ForeignKey('eventos.id'), nullable=False)
     servicio_id = db.Column(db.Integer, db.ForeignKey('servicios.id_servicio'), nullable=False)
     precio_acordado = db.Column(db.Numeric(10, 2), nullable=False)
     notas = db.Column(db.Text)
     fecha_agregado = db.Column(db.DateTime, default=datetime.utcnow)

     def __repr__(self):
            return f"<EventoServicio {self.evento_id} - {self.servicio_id}>"