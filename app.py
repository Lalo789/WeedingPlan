from flask import Flask, render_template, jsonify, url_for, redirect, request, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from functools import wraps
from datetime import datetime

from db import db  
from models import Usuario, Cliente, Servicio, Proveedor, Evento, EventoServicio
from forms import LoginForm, RegistroForm, EventoForm, ServicioForm, ProveedorForm, AgregarServicioEventoForm
app = Flask(__name__)
app.config.from_object('config')
db.init_app(app)

#Inicializar extensiones
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor inicia sesion para acceder'
login_manager.login_message_category = 'Aviso'

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

@app.route('/cliente/perfil')
def cliente_perfil():
    
    return render_template('cliente_perfil.htm')

@app.route('/servicios')
def servicios():
    return render_template('servicios.htm')

@app.route('/servicios_forms')
def servicios_forms():
    return render_template('servicios_forms.htm')

@app.route('/servicios/modificar')
def servicios_mod():
    return render_template('servicios_mod.htm')

@app.route('/perfil')
def perfil():
    return render_template('perfil.htm')

# CONFIGURACIÓN DE FLASK-LOGIN

@login_manager.user_loader
def load_user(user_id):
    "Carga al usuario por su id"
    return Usuario.query.get(int(user_id))

# DECORADORES PERSONALIZADOS PARA AUTORIZACIÓN

def admin_required(f):
    "Decorator para rutas que requieren permisos de administrador"
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Debes iniciar sesión para acceder a esta página.', 'warning')
            return redirect(url_for('login'))
        if not current_user.es_admin():
            flash('No tienes permisos para acceder a esta página.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# AUTENTICACIÓN: LOGIN, REGISTRO, LOGOUT

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Ruta de inicio de sesión.
    Si el usuario ya está autenticado, redirige al dashboard correspondiente.
    """
    if current_user.is_authenticated:
        if current_user.es_admin():
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('cliente_dashboard'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(username=form.username.data).first()
        
        if usuario and bcrypt.check_password_hash(usuario.password_hash, form.password.data):
            if not usuario.activo:
                flash('Tu cuenta está desactivada. Contacta al administrador.', 'danger')
                return redirect(url_for('login'))
            
            login_user(usuario, remember=form.remember.data)
            flash(f'¡Bienvenido {usuario.nombre_completo}!', 'success')
            
            # Redirigir a la página que intentaba acceder, o al dashboard
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            
            if usuario.es_admin():
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('cliente_dashboard'))
        else:
            flash('Usuario o contraseña incorrectos.', 'danger')
    
    return render_template('login.htm', form=form)


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    """
    Ruta de registro para nuevos usuarios.
    Por defecto, los nuevos usuarios se registran como 'cliente'.
    """
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistroForm()
    
    if form.validate_on_submit():
        # Encriptar la contraseña
        password_hash = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        
        # Crear nuevo usuario
        nuevo_usuario = Usuario(
            username=form.username.data,
            nombre_completo=form.nombre_completo.data,
            email=form.email.data,
            telefono=form.telefono.data,
            password_hash=password_hash,
            rol='cliente'  # Los nuevos registros son clientes por defecto
        )
        
        db.session.add(nuevo_usuario)
        db.session.commit()
        
        flash('¡Cuenta creada exitosamente! Ya puedes iniciar sesión.', 'success')
        return redirect(url_for('login'))
    
    return render_template('registro.htm', form=form)


@app.route('/logout')
@login_required
def logout():
    """Cierra la sesión del usuario actual"""
    logout_user()
    flash('Has cerrado sesión exitosamente.', 'info')
    return redirect(url_for('index'))


# DASHBOARD DE CLIENTES

@app.route('/cliente/dashboard')
@login_required
def cliente_dashboard():
    """
    Dashboard principal para clientes.
    Muestra todos los eventos del cliente actual.
    """
    if current_user.es_admin():
        return redirect(url_for('admin_dashboard'))
    
    eventos = Evento.query.filter_by(usuario_id=current_user.id).order_by(Evento.fecha_evento.desc()).all()
    return render_template('cliente/dashboard.htm', eventos=eventos)


@app.route('/cliente/evento/nuevo', methods=['GET', 'POST'])
@login_required
def cliente_nuevo_evento():
    """
    Permite a un cliente crear un nuevo evento.
    """
    form = EventoForm()
    
    if form.validate_on_submit():
        # Convertir string de fecha a datetime
        try:
            fecha_evento = datetime.strptime(form.fecha_evento.data, '%Y-%m-%dT%H:%M')
        except ValueError:
            flash('Formato de fecha inválido.', 'danger')
            return render_template('cliente/evento_form.htm', form=form)
        
        nuevo_evento = Evento(
            usuario_id=current_user.id,
            titulo=form.titulo.data,
            descripcion=form.descripcion.data,
            fecha_evento=fecha_evento,
            lugar=form.lugar.data,
            num_invitados=form.num_invitados.data,
            presupuesto_estimado=form.presupuesto_estimado.data,
            estado='pendiente'  # Estado inicial
        )
        
        db.session.add(nuevo_evento)
        db.session.commit()
        
        flash('¡Evento creado exitosamente!', 'success')
        return redirect(url_for('cliente_ver_evento', evento_id=nuevo_evento.id))
    
    return render_template('cliente/evento_form.htm', form=form, accion='Crear')


@app.route('/cliente/evento/<int:evento_id>')
@login_required
def cliente_ver_evento(evento_id):
    """
    Vista detallada de un evento específico del cliente.
    """
    evento = Evento.query.get_or_404(evento_id)
    
    # Verificar que el evento pertenezca al usuario actual
    if evento.usuario_id != current_user.id and not current_user.es_admin():
        flash('No tienes permiso para ver este evento.', 'danger')
        return redirect(url_for('cliente_dashboard'))
    
    servicios_disponibles = Servicio.query.filter_by(disponible=True).all()
    return render_template('cliente/evento_detalle.htm', evento=evento, servicios_disponibles=servicios_disponibles)


@app.route('/cliente/evento/<int:evento_id>/editar', methods=['GET', 'POST'])
@login_required
def cliente_editar_evento(evento_id):
    """
    Permite al cliente editar su evento.
    """
    evento = Evento.query.get_or_404(evento_id)
    
    # Verificar permisos
    if evento.usuario_id != current_user.id and not current_user.es_admin():
        flash('No tienes permiso para editar este evento.', 'danger')
        return redirect(url_for('cliente_dashboard'))
    
    form = EventoForm(obj=evento)
    
    # Pre-llenar el campo de fecha en formato correcto
    if request.method == 'GET':
        form.fecha_evento.data = evento.fecha_evento.strftime('%Y-%m-%dT%H:%M')
    
    if form.validate_on_submit():
        try:
            fecha_evento = datetime.strptime(form.fecha_evento.data, '%Y-%m-%dT%H:%M')
        except ValueError:
            flash('Formato de fecha inválido.', 'danger')
            return render_template('cliente/evento_form.htm', form=form, accion='Editar')
        
        evento.titulo = form.titulo.data
        evento.descripcion = form.descripcion.data
        evento.fecha_evento = fecha_evento
        evento.lugar = form.lugar.data
        evento.num_invitados = form.num_invitados.data
        evento.presupuesto_estimado = form.presupuesto_estimado.data
        
        # Solo los admins pueden cambiar el estado
        if current_user.es_admin():
            evento.estado = form.estado.data
        
        db.session.commit()
        flash('Evento actualizado exitosamente.', 'success')
        return redirect(url_for('cliente_ver_evento', evento_id=evento.id))
    
    return render_template('cliente/evento_form.htm', form=form, accion='Editar', evento=evento)


@app.route('/cliente/evento/<int:evento_id>/cancelar', methods=['POST'])
@login_required
def cliente_cancelar_evento(evento_id):
    """
    Permite al cliente cancelar su evento.
    """
    evento = Evento.query.get_or_404(evento_id)
    
    if evento.usuario_id != current_user.id and not current_user.es_admin():
        flash('No tienes permiso para cancelar este evento.', 'danger')
        return redirect(url_for('cliente_dashboard'))
    
    evento.estado = 'cancelado'
    db.session.commit()
    
    flash('Evento cancelado exitosamente.', 'info')
    return redirect(url_for('cliente_dashboard'))


@app.route('/cliente/evento/<int:evento_id>/servicio/agregar', methods=['POST'])
@login_required
def cliente_agregar_servicio(evento_id):
    """
    Agrega un servicio al evento del cliente.
    """
    evento = Evento.query.get_or_404(evento_id)
    
    if evento.usuario_id != current_user.id and not current_user.es_admin():
        flash('No tienes permiso para modificar este evento.', 'danger')
        return redirect(url_for('cliente_dashboard'))
    
    servicio_id = request.form.get('servicio_id', type=int)
    precio_acordado = request.form.get('precio_acordado', type=float)
    
    if not servicio_id or not precio_acordado:
        flash('Datos incompletos.', 'danger')
        return redirect(url_for('cliente_ver_evento', evento_id=evento_id))
    
    servicio = Servicio.query.get_or_404(servicio_id)
    
    # Verificar que no esté ya agregado
    existe = EventoServicio.query.filter_by(evento_id=evento_id, servicio_id=servicio_id).first()
    if existe:
        flash('Este servicio ya está agregado al evento.', 'warning')
        return redirect(url_for('cliente_ver_evento', evento_id=evento_id))
    
    evento_servicio = EventoServicio(
        evento_id=evento_id,
        servicio_id=servicio_id,
        precio_acordado=precio_acordado
    )
    
    db.session.add(evento_servicio)
    db.session.commit()
    
    flash(f'Servicio "{servicio.nombre}" agregado exitosamente.', 'success')
    return redirect(url_for('cliente_ver_evento', evento_id=evento_id))


@app.route('/cliente/evento/<int:evento_id>/servicio/<int:servicio_id>/eliminar', methods=['POST'])
@login_required
def cliente_eliminar_servicio(evento_id, servicio_id):
    """
    Elimina un servicio del evento del cliente.
    """
    evento = Evento.query.get_or_404(evento_id)
    
    if evento.usuario_id != current_user.id and not current_user.es_admin():
        flash('No tienes permiso para modificar este evento.', 'danger')
        return redirect(url_for('cliente_dashboard'))
    
    evento_servicio = EventoServicio.query.filter_by(evento_id=evento_id, servicio_id=servicio_id).first_or_404()
    
    db.session.delete(evento_servicio)
    db.session.commit()
    
    flash('Servicio eliminado del evento.', 'info')
    return redirect(url_for('cliente_ver_evento', evento_id=evento_id))


# DASHBOARD DE ADMINISTRADORES

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """
    Dashboard principal para administradores.
    Muestra estadísticas y resumen del sistema.
    """
    total_usuarios = Usuario.query.count()
    total_eventos = Evento.query.count()
    total_servicios = Servicio.query.count()
    eventos_pendientes = Evento.query.filter_by(estado='pendiente').count()
    
    eventos_recientes = Evento.query.order_by(Evento.fecha_creacion.desc()).limit(5).all()
    
    return render_template('admin/dashboard.htm', 
                         total_usuarios=total_usuarios,
                         total_eventos=total_eventos,
                         total_servicios=total_servicios,
                         eventos_pendientes=eventos_pendientes,
                         eventos_recientes=eventos_recientes)


# CRUD DE SERVICIOS (SOLO ADMIN)

@app.route('/admin/servicios')
@admin_required
def admin_servicios():
    """Lista todos los servicios del sistema"""
    servicios_lista = Servicio.query.all()
    return render_template('admin/servicios.htm', servicios=servicios_lista)


@app.route('/admin/servicio/nuevo', methods=['GET', 'POST'])
@admin_required
def admin_nuevo_servicio():
    """Crear un nuevo servicio"""
    form = ServicioForm()
    
    if form.validate_on_submit():
        nuevo_servicio = Servicio(
            nombre=form.nombre.data,
            descripcion=form.descripcion.data,
            precio_base=form.precio_base.data,
            categoria=form.categoria.data,
            imagen_url=form.imagen_url.data,
            disponible=form.disponible.data
        )
        
        db.session.add(nuevo_servicio)
        db.session.commit()
        
        flash(f'Servicio "{nuevo_servicio.nombre}" creado exitosamente.', 'success')
        return redirect(url_for('admin_servicios'))
    
    return render_template('admin/servicio_form.htm', form=form, accion='Crear')


@app.route('/admin/servicio/<int:servicio_id>/editar', methods=['GET', 'POST'])
@admin_required
def admin_editar_servicio(servicio_id):
    """Editar un servicio existente"""
    servicio = Servicio.query.get_or_404(servicio_id)
    form = ServicioForm(obj=servicio)
    
    if form.validate_on_submit():
        servicio.nombre = form.nombre.data
        servicio.descripcion = form.descripcion.data
        servicio.precio_base = form.precio_base.data
        servicio.categoria = form.categoria.data
        servicio.imagen_url = form.imagen_url.data
        servicio.disponible = form.disponible.data
        
        db.session.commit()
        flash(f'Servicio "{servicio.nombre}" actualizado exitosamente.', 'success')
        return redirect(url_for('admin_servicios'))
    
    return render_template('admin/servicio_form.htm', form=form, accion='Editar', servicio=servicio)


@app.route('/admin/servicio/<int:servicio_id>/eliminar', methods=['POST'])
@admin_required
def admin_eliminar_servicio(servicio_id):
    """Eliminar un servicio"""
    servicio = Servicio.query.get_or_404(servicio_id)
    
    # Verificar si el servicio está en uso
    en_uso = EventoServicio.query.filter_by(servicio_id=servicio_id).count()
    if en_uso > 0:
        flash(f'No se puede eliminar el servicio "{servicio.nombre}" porque está en uso en {en_uso} evento(s).', 'danger')
        return redirect(url_for('admin_servicios'))
    
    db.session.delete(servicio)
    db.session.commit()
    
    flash(f'Servicio "{servicio.nombre}" eliminado exitosamente.', 'success')
    return redirect(url_for('admin_servicios'))


# GESTIÓN DE EVENTOS (ADMIN)

@app.route('/admin/eventos')
@admin_required
def admin_eventos():
    """Lista todos los eventos del sistema"""
    eventos = Evento.query.order_by(Evento.fecha_evento.desc()).all()
    return render_template('admin/eventos.htm', eventos=eventos)


@app.route('/admin/evento/<int:evento_id>')
@admin_required
def admin_ver_evento(evento_id):
    """Ver detalle de cualquier evento"""
    evento = Evento.query.get_or_404(evento_id)
    return render_template('admin/evento_detalle.htm', evento=evento)


# GESTIÓN DE USUARIOS (ADMIN)

@app.route('/admin/usuarios')
@admin_required
def admin_usuarios():
    """Lista todos los usuarios del sistema"""
    usuarios = Usuario.query.all()
    return render_template('admin/usuarios.htm', usuarios=usuarios)


@app.route('/admin/usuario/<int:usuario_id>/toggle-activo', methods=['POST'])
@admin_required
def admin_toggle_usuario_activo(usuario_id):
    """Activa o desactiva un usuario"""
    usuario = Usuario.query.get_or_404(usuario_id)
    
    if usuario.id == current_user.id:
        flash('No puedes desactivar tu propia cuenta.', 'danger')
        return redirect(url_for('admin_usuarios'))
    
    usuario.activo = not usuario.activo
    db.session.commit()
    
    estado = 'activado' if usuario.activo else 'desactivado'
    flash(f'Usuario "{usuario.username}" {estado} exitosamente.', 'success')
    return redirect(url_for('admin_usuarios'))


# GESTIÓN DE PROVEEDORES (ADMIN)

@app.route('/admin/proveedores')
@admin_required
def admin_proveedores():
    """Lista todos los proveedores"""
    proveedores = Proveedor.query.all()
    return render_template('admin/proveedores.htm', proveedores=proveedores)


@app.route('/admin/proveedor/nuevo', methods=['GET', 'POST'])
@admin_required
def admin_nuevo_proveedor():
    """Crear un nuevo proveedor"""
    form = ProveedorForm()
    
    if form.validate_on_submit():
        nuevo_proveedor = Proveedor(
            nombre=form.nombre.data,
            tipo_servicio=form.tipo_servicio.data,
            contacto=form.contacto.data,
            telefono=form.telefono.data,
            email=form.email.data,
            calificacion=form.calificacion.data,
            notas=form.notas.data,
            activo=form.activo.data
        )
        
        db.session.add(nuevo_proveedor)
        db.session.commit()
        
        flash(f'Proveedor "{nuevo_proveedor.nombre}" creado exitosamente.', 'success')
        return redirect(url_for('admin_proveedores'))
    
    return render_template('admin/proveedor_form.htm', form=form, accion='Crear')


@app.route('/admin/proveedor/<int:proveedor_id>/editar', methods=['GET', 'POST'])
@admin_required
def admin_editar_proveedor(proveedor_id):
    """Editar un proveedor existente"""
    proveedor = Proveedor.query.get_or_404(proveedor_id)
    form = ProveedorForm(obj=proveedor)
    
    if form.validate_on_submit():
        proveedor.nombre = form.nombre.data
        proveedor.tipo_servicio = form.tipo_servicio.data
        proveedor.contacto = form.contacto.data
        proveedor.telefono = form.telefono.data
        proveedor.email = form.email.data
        proveedor.calificacion = form.calificacion.data
        proveedor.notas = form.notas.data
        proveedor.activo = form.activo.data
        
        db.session.commit()
        flash(f'Proveedor "{proveedor.nombre}" actualizado exitosamente.', 'success')
        return redirect(url_for('admin_proveedores'))
    
    return render_template('admin/proveedor_form.htm', form=form, accion='Editar', proveedor=proveedor)


@app.route('/admin/proveedor/<int:proveedor_id>/eliminar', methods=['POST'])
@admin_required
def admin_eliminar_proveedor(proveedor_id):
    """Eliminar un proveedor"""
    proveedor = Proveedor.query.get_or_404(proveedor_id)
    
    db.session.delete(proveedor)
    db.session.commit()
    
    flash(f'Proveedor "{proveedor.nombre}" eliminado exitosamente.', 'success')
    return redirect(url_for('admin_proveedores'))


# MANEJO DE ERRORES

@app.errorhandler(404)
def page_not_found(e):
    """Página de error 404"""
    return render_template('404.htm', error=str(e)), 404


@app.errorhandler(403)
def forbidden(e):
    """Página de error 403 - Acceso prohibido"""
    return render_template('403.htm', error=str(e)), 403


@app.errorhandler(500)
def internal_server_error(e):
    """Página de error 500 - Error del servidor"""
    return render_template('500.htm', error=str(e)), 500


# FILTROS JINJA PERSONALIZADOS

@app.template_filter('currency')
def currency_filter(value):
    "Formatea números como moneda"
    if value is None:
        return "$0.00"
    return f"${value:,.2f}"


@app.template_filter('datetime_format')
def datetime_format_filter(value, format='%d/%m/%Y %H:%M'):
    "Formatea objetos datetime"
    if value is None:
        return ""
    return value.strftime(format)


# CONTEXTO GLOBAL PARA TEMPLATES

@app.context_processor
def utility_processor():
    '"Hace que ciertas funciones estén disponibles en todos los templates."'
    return dict(
        now=datetime.utcnow,
        enumerate=enumerate
    )


if __name__ == '__main__':
    app.run(debug=True)