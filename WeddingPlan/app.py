from flask import Flask, render_template, jsonify, url_for, redirect, request
from db import db  
from models import Cliente

app = Flask(__name__)
app.config.from_object('config')
db.init_app(app)

#rutas
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/base')
def base():
    return render_template('base.htm')

@app.route('/test-db')
def test_db():
    try:
        db.session.execute(db.text('SELECT 1'))
        return jsonify({'status': 'success', 'message': 'Conexión a la base de datos exitosa.'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error en la conexión: {e}'})

@app.route('/cliente')
def mostrar_cliente():
    clientes = Cliente.query.all()
    return render_template('clientes.htm', clientes=clientes)

@app.route('/cliente/nuevo', methods=['GET', 'POST'])
def nuevo_cliente():
    if request.method == 'POST':
        # recibe los datos del formulario
        nombre = request.form['nombre']
        email = request.form['email']
        telefono = request.form['telefono']
        
        nuevo = Cliente(nombre=nombre, email=email, telefono=telefono)
        
        db.session.add(nuevo)
        db.session.commit()
        
        return redirect(url_for('mostrar_cliente'))
        
    return render_template('cliente_forms.htm')

@app.route('/servicios')
def servicios():
    return render_template('servicios.htm')

@app.route('/servicios_forms')
def servicios_forms():
    return render_template('servicios_forms.htm')

@app.route('/servicios/modificar')
def servicios_mod():
    return render_template('servicios_mod.htm')


