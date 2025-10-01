from db import db

class Cliente(db.Model):
    __tablename__ = 'clientes'  
    id_cliente = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(100), unique=True, nullable=False)
    telefono = db.Column(db.String(15))
    direccion = db.Column(db.String(200))

    def __repr__(self):
        return f'<Cliente {self.nombre}>'
    
