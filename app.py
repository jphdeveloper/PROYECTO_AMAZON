from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash

app = Flask(__name__, static_folder='static')
app.secret_key = '97110c78ae51a45af397be6534caef90ebb9b1dcb3380af008f90b23a5d1616bf19bc29098105da20fe'

# Configuración de SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://Root123:Root1102807012.@localhost/db_amazon'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "amazonincsoft@gmail.com" 
app.config["MAIL_PASSWORD"] = "npog egrq ndyv npbi"

mail = Mail(app)

# Definición del modelo de Usuario
class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(100), unique=True, nullable=False)
    contraseña = db.Column(db.String(100), nullable=False)
    rol = db.Column(db.String(30), nullable=False)

class Empleados(db.Model):
    __tablename__ = 'empleados'
    id_empleado = db.Column(db.String(30), primary_key=True)
    nombre_empleado = db.Column(db.String(50), nullable=False)
    nombre_categoria = db.Column(db.String(20), db.ForeignKey('categorias.nombre_categoria'))
    salario = db.Column(db.Numeric(10,2))
    categorias = db.relationship('Categorias', backref=db.backref('empleado', lazy=True))

class Clientes(db.Model):
    __tablename__ = 'clientes'
    id_cliente = db.Column(db.String(30), primary_key=True)
    nombre_cliente = db.Column(db.String(50), nullable=False)
    nombre_categoria = db.Column(db.String(20), db.ForeignKey('categorias.nombre_categoria'))
    correo = db.Column(db.String(100), unique=True, nullable=False)  # Nuevo campo
    contraseña = db.Column(db.String(255), nullable=False)  # Nuevo campo
    estado = db.Column(db.String(20), default="Activo")  # Corregido: debe ser String
    categorias = db.relationship('Categorias', backref=db.backref('cliente', lazy=True))
class Categorias(db.Model):
    __tablename__ = 'categorias'
    nombre_categoria = db.Column(db.String(50), primary_key=True)
    nombre_sucursal = db.Column(db.String(15))
    presupuesto = db.Column(db.Numeric(12,2))

class Productos(db.Model):
    __tablename__ = 'productos'
    id_producto = db.Column(db.String(30), primary_key=True)
    descripcion = db.Column(db.String(50))
    nombre_categoria = db.Column(db.String(20), db.ForeignKey('categorias.nombre_categoria'))
    precio = db.Column(db.Integer)
    categorias = db.relationship('Categorias', backref=db.backref('productos', lazy=True))

class Asesor(db.Model):
    __tablename__ = 'asesor'
    idf_cliente = db.Column(db.String(30), db.ForeignKey('clientes.id_cliente'), primary_key=True)
    idf_empleado = db.Column(db.String(30), db.ForeignKey('empleados.id_empleado'))
    clientes = db.relationship('Clientes', backref=db.backref('asesor', uselist=False))
    empleados = db.relationship('Empleados', backref=db.backref('asesorias', lazy=True))

class Sucursales(db.Model):
    __tablename__ = 'sucursales'
    nombre_sucursal = db.Column(db.String(15), primary_key=True)
    numero_sala = db.Column(db.String(7), primary_key=True)
    capacidad = db.Column(db.Integer)


@app.context_processor
def inject_user():
    return {'nombre_usuario': session.get('nombre', "Mi Cuenta")}


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    correo = request.form.get('correo')
    contraseña = request.form.get('contraseña')
    rol_seleccionado = request.form.get('rol')

    user = Usuario.query.filter_by(correo=correo, contraseña=contraseña).first()

    if user:
        if user.rol != rol_seleccionado:
            flash('No tienes permisos para iniciar sesión con este rol.', 'error')
            return redirect(url_for('login'))
        
        # Guardar datos en la sesión, asegurando que 'correo' esté presente
        session['usuario_id'] = user.id
        session['nombre'] = user.nombre
        session['correo'] = user.correo  # 🔹 Asegurar que 'correo' se guarde
        session['rol'] = user.rol

        flash('Inicio de sesión exitoso', 'success')

        if user.rol == "admin":
            return redirect(url_for('dashboard'))
        elif user.rol == "cliente":
            return redirect(url_for('clientes'))  # Redirigir a clientes.html

    flash('Correo o contraseña incorrectos', 'error')
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    flash('Cierre de sesión exitoso!', 'info')
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

import uuid  

@app.route('/register', methods=['POST'])
def register_post():
    nombre = request.form.get('nombre')
    correo = request.form.get('correo')
    contraseña = request.form.get('password')
    rol = request.form.get('rol')

    existe_usuario = Usuario.query.filter_by(correo=correo).first()
    if existe_usuario:
        flash("El correo electrónico ya está registrado. Usa otro.", "error")
        return redirect(url_for('register'))

    try:
        nuevo_usuario = Usuario(
            nombre=nombre, 
            correo=correo, 
            contraseña=contraseña,
            rol=rol
        )
        db.session.add(nuevo_usuario)

        if rol.lower() == "cliente":
            nuevo_cliente = Clientes(
                id_cliente=str(uuid.uuid4())[:8],
                nombre_cliente=nombre,
                nombre_categoria="Sin categoría",
                correo=correo,
                contraseña=contraseña,
                estado="Activo"
            )
            db.session.add(nuevo_cliente)

        db.session.commit()
        flash("Registro exitoso", "success")
        return redirect(url_for('login'))

    except Exception as e:
        db.session.rollback()
        flash(f"Se produjo un error al registrar el usuario: {str(e)}", "error")

    return redirect(url_for('register'))



@app.route('/recovery')
def recovery():
    return render_template('recovery.html')

@app.route('/recovery', methods=['POST'])
def recovery_post():
    correo = request.form.get('correo')

    user = Usuario.query.filter_by(correo=correo).first()

    if user:
        flash('Se ha enviado un correo para recuperar tu cuenta', 'success')
    else:
        flash('El correo no está registrado', 'error')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    nombre_usuario = session.get('nombre', "Mi Cuenta")
    return render_template("dashboard.html", nombre_usuario=nombre_usuario)

@app.route('/categorias')
def categorias():
    nombre_usuario = session.get('nombre', "Mi Cuenta")

    return render_template("categorias.html", nombre_usuario=nombre_usuario)

@app.route('/nosotros')
def nosotros():
    nombre_usuario = session.get('nombre', "Mi Cuenta")
    return render_template("nosotros.html", nombre_usuario=nombre_usuario)

@app.route('/clientes')
def clientes():
    if 'correo' not in session: 
        flash("Debes iniciar sesión primero.", "error")
        return redirect(url_for('login'))


    cliente_actual = Clientes.query.filter_by(correo=session['correo']).first()

    if not cliente_actual:
        flash("No se encontró información de cliente para este usuario.", "error")
        return redirect(url_for('login'))

    
    productos = Productos.query.all()

    return render_template('clientes.html', cliente=cliente_actual, productos=productos)

@app.route('/sucursal')
def sucursal():
    sucursal=Sucursales.query.all()
    return render_template("sucursal.html",sucursal=sucursal)

@app.route('/perfil_admin')
def perfil_admin():
    # Verificar si el usuario está autenticado y es admin
    if 'usuario_id' not in session or session.get('rol') != 'admin':
        flash('Acceso denegado. Debes ser administrador.', 'error')
        return redirect(url_for('login'))  # Redirige a login si no es admin

    # Obtener datos del usuario desde la base de datos
    usuario = Usuario.query.get(session['usuario_id'])

    if not usuario:
        flash('Usuario no encontrado.', 'error')
        return redirect(url_for('dashboard'))  # Si no existe, redirige al dashboard

    return render_template('perfil_admin.html', usuario=usuario)

@app.route('/perfil_cliente')
def perfil_cliente():
    # Verificar si el usuario está autenticado y es cliente
    if 'usuario_id' not in session or session.get('rol') != 'cliente':
        flash('Acceso denegado. Debes ser cliente.', 'error')
        return redirect(url_for('login'))  # Redirige a login si no es cliente

    # Obtener datos del usuario desde la base de datos
    usuario = Usuario.query.get(session['usuario_id'])

    if not usuario:
        flash('Usuario no encontrado.', 'error')
        return redirect(url_for('dashboard'))  # Si no existe, redirige al dashboard

    return render_template('perfil_cliente.html', usuario=usuario)

@app.route('/editar_admin')
def editar_admin():
    # Verificar si el usuario está autenticado y es admin
    if 'usuario_id' not in session or session.get('rol') != 'admin':
        flash('Acceso denegado. Debes ser administrador.', 'error')
        return redirect(url_for('login'))  # Redirige a login si no es admin

    # Obtener datos del usuario desde la base de datos
    usuario = Usuario.query.get(session['usuario_id'])

    if not usuario:
        flash('Usuario no encontrado.', 'error')
        return redirect(url_for('perfil_admin'))  # Si no existe, redirige al dashboard
    return render_template('editar_admin.html', usuario=usuario)

@app.route('/editar_cliente')
def editar_cliente():
    # Verificar si el usuario está autenticado y es admin
    if 'usuario_id' not in session or session.get('rol') != 'cliente':
        flash('Acceso denegado. Debes ser cliente.', 'error')
        return redirect(url_for('login'))  # Redirige a login si no es cliente

    # Obtener datos del usuario desde la base de datos
    usuario = Usuario.query.get(session['usuario_id'])

    if not usuario:
        flash('Usuario no encontrado.', 'error')
        return redirect(url_for('perfil_cliente'))  # Si no existe, redirige al dashboard
    return render_template('editar_cliente.html', usuario=usuario)

@app.route('/editar_datos')
def editar_datos():
    # Verificar si el usuario está autenticado y es admin
    if 'usuario_id' not in session or session.get('rol') != 'admin':
        flash('Acceso denegado. Debes ser administrador.', 'error')
        return redirect(url_for('login'))

    # Obtener los datos del usuario desde la base de datos
    usuario = Usuario.query.get(session['usuario_id'])

    if not usuario:
        flash('Usuario no encontrado.', 'error')
        return redirect(url_for('perfil_admin'))

    return render_template('editar_datos.html', usuario=usuario)

@app.route('/datos_clientes')
def datos_clientes():
    # Verificar si el usuario está autenticado y es cliente
    if 'usuario_id' not in session or session.get('rol') != 'cliente':
        flash('Acceso denegado. Debes ser cliente.', 'error')
        return redirect(url_for('login'))

    # Obtener los datos del usuario desde la base de datos
    usuario = Usuario.query.get(session['usuario_id'])

    if not usuario:
        flash('Usuario no encontrado.', 'error')
        return redirect(url_for('perfil_cliente'))

    return render_template('editar_datos_cliente.html', usuario=usuario)


@app.route('/correo_elegido', methods=['GET', 'POST'])
def correo_elegido():
    if 'usuario_id' not in session or session.get('rol') != 'admin':
        flash('Acceso denegado. Debes ser administrador.', 'error')
        return redirect(url_for('login'))

    # Obtener los datos del usuario
    usuario = Usuario.query.get(session['usuario_id'])

    if not usuario:
        flash('Usuario no encontrado.', 'error')
        return redirect(url_for('perfil_admin'))

    if request.method == 'POST':
        nuevo_correo = request.form.get('correo')
        nueva_contraseña = request.form.get('contraseña')

        if nuevo_correo:
            usuario.correo = nuevo_correo
        
        # Si el usuario no cambia la contraseña, se mantiene la anterior
        if nueva_contraseña and nueva_contraseña != usuario.contraseña:
            usuario.contraseña = nueva_contraseña  

        db.session.commit()  # Guardar cambios en la BD
        flash('Correo y/o contraseña actualizados correctamente.', 'success')
        return redirect(url_for('perfil_admin'))

    return render_template('correo_elegido.html', usuario=usuario)

@app.route('/correo_elegido_cliente', methods=['GET', 'POST'])
def correo_elegido_cliente():
    if 'usuario_id' not in session or session.get('rol') != 'cliente':
        flash('Acceso denegado. Debes ser cliente.', 'error')
        return redirect(url_for('login'))

    # Obtener los datos del usuario
    usuario = Usuario.query.get(session['usuario_id'])

    if not usuario:
        flash('Usuario no encontrado.', 'error')
        return redirect(url_for('perfil_cliente'))

    if request.method == 'POST':
        nuevo_correo = request.form.get('correo')
        nueva_contraseña = request.form.get('contraseña')

        if nuevo_correo:
            usuario.correo = nuevo_correo
        
        # Si el usuario no cambia la contraseña, se mantiene la anterior
        if nueva_contraseña and nueva_contraseña != usuario.contraseña:
            usuario.contraseña = nueva_contraseña  

        db.session.commit()  # Guardar cambios en la BD
        flash('Correo y/o contraseña actualizados correctamente.', 'success')
        return redirect(url_for('perfil_cliente'))

    return render_template('correo_elegido_cliente.html', usuario=usuario)

@app.route('/nombre_elegido', methods=['GET', 'POST'])
def nombre_elegido():
    # Verificar si el usuario está autenticado y es admin
    if 'usuario_id' not in session or session.get('rol') != 'admin':
        flash('Acceso denegado. Debes ser administrador.', 'error')
        return redirect(url_for('login'))

    usuario = Usuario.query.get(session['usuario_id'])

    if not usuario:
        flash('Usuario no encontrado.', 'error')
        return redirect(url_for('perfil_admin'))

    if request.method == 'POST':
        nuevo_nombre = request.form['nombre']
        if nuevo_nombre:
            usuario.nombre = nuevo_nombre
            db.session.commit()  # Guardar cambios en la BD
            
            session['nombre'] = nuevo_nombre

            flash('Nombre actualizado correctamente.', 'success')
            return redirect(url_for('perfil_admin'))

    return render_template('nombre_elegido.html', usuario=usuario)

@app.route('/nombre_elegido_cliente', methods=['GET', 'POST'])
def nombre_elegido_cliente():
    # Verificar si el usuario está autenticado y es cliente
    if 'usuario_id' not in session or session.get('rol') != 'cliente':
        flash('Acceso denegado. Debes ser cliente.', 'error')
        return redirect(url_for('login'))

    usuario = Usuario.query.get(session['usuario_id'])

    if not usuario:
        flash('Usuario no encontrado.', 'error')
        return redirect(url_for('perfil_cliente'))

    if request.method == 'POST':
        nuevo_nombre = request.form['nombre']
        if nuevo_nombre:
            usuario.nombre = nuevo_nombre
            db.session.commit()  # Guardar cambios en la BD
            
            session['nombre'] = nuevo_nombre

            flash('Nombre actualizado correctamente.', 'success')
            return redirect(url_for('perfil_cliente'))

    return render_template('nombre_elegido_cliente.html', usuario=usuario)

@app.route('/empleado')
def empleado():
    page = request.args.get('page', 1, type=int)
    per_page = 7
    search = request.args.get('search', '').strip()

    # Comenzamos con la consulta base
    consulta = Empleados.query

    # Si hay un término de búsqueda, filtramos
    if search:
        consulta = consulta.filter(
            (Empleados.id_empleado.like(f"%{search}%")) | 
            (Empleados.nombre_empleado.ilike(f"%{search}%")) | 
            (Empleados.nombre_categoria.ilike(f"%{search}%"))
        )

    # Obtener el total de empleados que cumplen con la consulta
    total_empleados = consulta.count()

    # Aplicamos paginación
    empleados = consulta.offset((page - 1) * per_page).limit(per_page).all()
    
    # Calculamos el número total de páginas
    total_pages = (total_empleados + per_page - 1) // per_page

    return render_template('empleado.html', empleado=empleados, page=page, total_pages=total_pages, search=search)


@app.route('/nuevo_empleado', methods=['GET', 'POST'])
def nuevo_empleado():
    nombre_categoria = Categorias.query.distinct(Categorias.nombre_categoria).all()

    if request.method == "POST":
        id_empleado = request.form['id_empleado']
        nombre_empleado = request.form['nombre_empleado']
        nombre_categoria = request.form['nombre_categoria']
        salario = request.form['salario']  # empleado

        try:
            existe_producto = Empleados.query.filter_by(id_empleado=id_empleado).first()
            if existe_producto:
                flash("El ID del empleado ya existe. Elija uno diferente.", "danger")
                return redirect(url_for('nuevo_empleado'))

            crea_empleado = Empleados(
                id_empleado=id_empleado,
                nombre_empleado=nombre_empleado,
                nombre_categoria=nombre_categoria,
                salario=salario
            )  # empleado
            db.session.add(crea_empleado)
            db.session.commit()
            flash("Empleado añadido con éxito!", "success")
            return redirect('/empleado')

        except Exception as e:
            db.session.rollback()  # Revertir cambios si hay un error
            flash(f"Error al añadir el empleado: {str(e)}", "danger")
            return redirect(url_for('nuevo_empleado'))

    return render_template('nuevo_empleado.html', categorias=nombre_categoria)

@app.route('/actualizar_empleado/<string:id_empleado>', methods=['GET', 'POST'])
def actualizar_empleado(id_empleado):
    empleados = Empleados.query.get(id_empleado)
    nombre_categoria = Categorias.query.distinct(Categorias.nombre_categoria).all()

    if request.method == "POST":
        empleados.nombre_empleado = request.form['nombre_empleado']
        empleados.nombre_categoria = request.form['nombre_categoria']
        empleados.salario = request.form['salario']  # empleado
        try:
            db.session.commit()
            flash("¡Perfil actualizado exitosamente!", "success")
            return redirect('/empleado')
        except Exception as e:
            db.session.rollback()  # Revierte cambios si hay un error
            flash(f"Error al actualizar el empleado: {str(e)}", "danger")
            return redirect(url_for('actualizar_empleado', id_empleado=id_empleado))

    return render_template('actualizar_empleado.html', empleados=empleados, categorias=nombre_categoria)


@app.route('/eliminar_empleado/<string:id_empleado>', methods=['GET', 'POST'])
def eliminar_empleado(id_empleado):
    empleados = Empleados.query.get(id_empleado)

    if empleados:
        db.session.delete(empleados)
        db.session.commit()
        flash("Empleado eliminado !", "warning")
        return redirect('/empleado')

    return redirect('/empleados')

from sqlalchemy.sql.expression import func  # Para seleccionar un empleado aleatorio

@app.route('/cliente')
def cliente():
    page = request.args.get('page', 1, type=int)
    per_page = 7
    search = request.args.get('search', '').strip()

    # Consulta base
    consulta = Clientes.query

    # Si hay búsqueda, filtrar resultados
    if search:
        consulta = consulta.filter(
            (Clientes.id_cliente.like(f"%{search}%")) | 
            (Clientes.nombre_cliente.ilike(f"%{search}%")) | 
            (Clientes.nombre_categoria.ilike(f"%{search}%"))
        )

    # Obtener clientes
    clientes = consulta.offset((page - 1) * per_page).limit(per_page).all()

    # Asignar un empleado aleatorio a cada cliente según su categoría
    for cliente in clientes:
        empleado_aleatorio = Empleados.query.filter_by(nombre_categoria=cliente.nombre_categoria).order_by(func.rand()).first()
        cliente.empleado_asignado = empleado_aleatorio.nombre_empleado if empleado_aleatorio else "N/A"

    # Contar clientes filtrados o todos
    total_clientes = consulta.count()
    total_pages = (total_clientes + per_page - 1) // per_page  # ✅ Corregido

    return render_template("cliente.html", clientes=clientes, page=page, total_pages=total_pages, search=search)


@app.route('/nuevo_cliente', methods=['GET', 'POST'])
def nuevo_cliente():
    categorias = Categorias.query.distinct(Categorias.nombre_categoria).all()

    if request.method == "POST":
        id_cliente = request.form['id']
        nombre_cliente = request.form['nombre_cliente']
        categoria_seleccionada = request.form['nombre_categoria']
        correo = request.form['correo']
        contraseña = request.form['contraseña']  # 🔹 Se guarda sin encriptar

        try:
            # Verificar si el ID ya existe en clientes
            existe_cliente = Clientes.query.filter_by(id_cliente=id_cliente).first()
            if existe_cliente:
                flash("El ID del cliente ya existe. Elija uno diferente.", "danger")
                return redirect(url_for('nuevo_cliente'))

            # Verificar si el correo ya está en uso en Usuarios
            existe_correo = Usuario.query.filter_by(correo=correo).first()
            if existe_correo:
                flash("El correo ya está registrado. Usa otro.", "danger")
                return redirect(url_for('nuevo_cliente'))

            # Crear nuevo cliente sin encriptar la contraseña
            nuevo_cliente = Clientes(
                id_cliente=id_cliente, 
                nombre_cliente=nombre_cliente, 
                nombre_categoria=categoria_seleccionada, 
                correo=correo,
                contraseña=contraseña,  # 🔹 Se guarda en texto plano
                estado="Activo"
            )
            db.session.add(nuevo_cliente)

            # Crear nuevo usuario con rol "cliente"
            nuevo_usuario = Usuario(
                nombre=nombre_cliente,  
                correo=correo,
                contraseña=contraseña,  # 🔹 Se guarda en texto plano
                rol="cliente"
            )
            db.session.add(nuevo_usuario)

            db.session.commit()
            flash("Cliente agregado con éxito!", "success")
            return redirect('/cliente')

        except Exception as e:
            db.session.rollback()
            flash(f"Se produjo un error al agregar: {str(e)}", "danger")
            return render_template('nuevo_cliente.html', categorias=categorias)

    return render_template('nuevo_cliente.html', categorias=categorias)

@app.route('/actualizar_cliente/<string:id_cliente>', methods=['GET', 'POST'])
def actualizar_cliente(id_cliente):
    cliente = Clientes.query.get(id_cliente)
    categorias = Categorias.query.distinct(Categorias.nombre_categoria).all()
    usuario = Usuario.query.filter_by(correo=cliente.correo).first()  # Buscar el usuario asociado

    if request.method == "POST":
        nuevo_nombre = request.form['nombre_cliente']
        nueva_categoria = request.form['nombre_categoria']
        nuevo_estado = request.form['estado']
        nuevo_correo = request.form['correo']  # Ahora el correo se puede actualizar
        
        try:
            # Verificar si el correo ha cambiado y si el nuevo correo ya está en uso
            if nuevo_correo != cliente.correo:
                existe_correo = Usuario.query.filter_by(correo=nuevo_correo).first()
                if existe_correo:
                    flash("El correo ya está en uso. Usa otro diferente.", "danger")
                    return redirect(url_for('actualizar_cliente', id_cliente=id_cliente))

            # Actualizar cliente
            cliente.nombre_cliente = nuevo_nombre
            cliente.nombre_categoria = nueva_categoria
            cliente.estado = nuevo_estado
            cliente.correo = nuevo_correo  # Se actualiza el correo del cliente

            # Si existe el usuario asociado, también se actualiza el correo y el nombre
            if usuario:
                usuario.nombre = nuevo_nombre
                usuario.correo = nuevo_correo  # Se actualiza el correo del usuario

            db.session.commit()
            flash("Perfil actualizado exitosamente!", "success")
            return redirect('/cliente')

        except Exception as e:
            db.session.rollback()  
            flash(f"Se produjo un error durante la actualización: {str(e)}", "danger")

    return render_template('actualizar_cliente.html', clientes=cliente, categorias=categorias)

@app.route('/eliminar_cliente/<string:id_cliente>', methods=['GET', 'POST'])
def eliminar_cliente(id_cliente):
    cliente = Clientes.query.get(id_cliente)
    
    if cliente:
        usuario = Usuario.query.filter_by(correo=cliente.correo).first()  # Buscar el usuario asociado

        try:
            db.session.delete(cliente)
            if usuario:
                db.session.delete(usuario)  # Solo eliminar si existe

            db.session.commit()
            flash("Cliente eliminado con éxito!", "warning")

        except Exception as e:
            db.session.rollback()
            flash(f"Error al eliminar el cliente: {str(e)}", "danger")

    return redirect('/cliente')

@app.route('/nuevo_producto', methods=['GET', 'POST'])
def nuevo_producto():
    categorias = Categorias.query.distinct(Categorias.nombre_categoria).all()  # Fetch categorias

    if request.method == 'POST':
        id_producto = request.form['id_producto']
        descripcion = request.form['descripcion']
        nombre_categoria = request.form['nombre_categoria']
        precio = request.form['precio']

        try:
            # Asegura que el ID del producto sea único
            existe_producto = Productos.query.filter_by(id_producto=id_producto).first()
            if existe_producto:
                flash("El ID del producto ya existe. Elija uno diferente..", "danger")
                return redirect(url_for('nuevo_producto'))

            # Crea y agrega el nuevo producto a la base de datos
            crea_producto = Productos(id_producto=id_producto, descripcion=descripcion, nombre_categoria=nombre_categoria, precio=precio)
            db.session.add(crea_producto)
            db.session.commit()
            flash("Producto añadido con éxito!", "success")
            return redirect(url_for('categorias'))

        except Exception as e:
            db.session.rollback()
            flash("Se produjo un error al agregar el producto: " + str(e), "danger")
            return redirect(url_for('nuevo_producto'))  # Redireccionar de nuevo a la página de agregar producto con el parámetro nombre_categoria

    return render_template('nuevo_producto.html', categorias=categorias)

@app.route('/arte')
def arte():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 7
        search_productos = request.args.get('search_productos', '').strip()
        search_empleados = request.args.get('search_empleados', '').strip()
        search_clientes = request.args.get('search_clientes', '').strip()

        # Consultar productos, empleados y clientes de la categoría "Arte y artesanías"
        consulta_productos = Productos.query.filter(Productos.nombre_categoria == 'Arte y artesanías')
        consulta_empleados = Empleados.query.filter(Empleados.nombre_categoria == 'Arte y artesanías')
        consulta_clientes = Clientes.query.filter(Clientes.nombre_categoria == 'Arte y artesanías')

        # Si hay búsqueda en productos, filtrar por referencia o descripción
        if search_productos:
            consulta_productos = consulta_productos.filter(
                (Productos.id_producto.like(f"%{search_productos}%")) |
                (Productos.descripcion.ilike(f"%{search_productos}%"))
            )

        # Si hay búsqueda en empleados, filtrar por número de identificación o nombre
        if search_empleados:
            consulta_empleados = consulta_empleados.filter(
                (Empleados.id_empleado.like(f"%{search_empleados}%")) |
                (Empleados.nombre_empleado.ilike(f"%{search_empleados}%"))
            )

        # Si hay búsqueda en clientes, filtrar por número de identificación o nombre
        if search_clientes:
            consulta_clientes = consulta_clientes.filter(
                (Clientes.id_cliente.like(f"%{search_clientes}%")) |
                (Clientes.nombre_cliente.ilike(f"%{search_clientes}%"))
            )

        # Contar total de registros
        total_productos = consulta_productos.count()
        total_empleados = consulta_empleados.count()
        total_clientes = consulta_clientes.count()

        # Aplicar paginación
        productos = consulta_productos.offset((page - 1) * per_page).limit(per_page).all()
        empleados = consulta_empleados.offset((page - 1) * per_page).limit(per_page).all()
        clientes = consulta_clientes.offset((page - 1) * per_page).limit(per_page).all()

        # Determinar el total de páginas basado en el conjunto más grande
        total_registros = max(total_productos, total_empleados, total_clientes)
        total_pages = (total_registros + per_page - 1) // per_page

        return render_template(
            "arte.html",
            productos=productos,
            empleados=empleados,
            clientes=clientes,
            page=page,
            total_pages=total_pages,
            search_productos=search_productos,
            search_empleados=search_empleados,
            search_clientes=search_clientes
        )

    except Exception as e:
        print("Error en la consulta SQL:", str(e))
        flash("Se produjo un error al obtener los datos", "danger")
        return render_template("arte.html", productos=[], empleados=[], clientes=[], page=1, total_pages=1, search_productos="", search_empleados="", search_clientes="")

@app.route('/automotriz')
def automotriz():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 7
        search_productos = request.args.get('search_productos', '').strip()
        search_empleados = request.args.get('search_empleados', '').strip()
        search_clientes = request.args.get('search_clientes', '').strip()

        # Consultar productos, empleados y clientes de la categoría "Automotriz"
        consulta_productos = Productos.query.filter(Productos.nombre_categoria == 'Automotriz')
        consulta_empleados = Empleados.query.filter(Empleados.nombre_categoria == 'Automotriz')
        consulta_clientes = Clientes.query.filter(Clientes.nombre_categoria == 'Automotriz')

        # Si hay búsqueda en productos, filtrar por referencia o descripción
        if search_productos:
            consulta_productos = consulta_productos.filter(
                (Productos.id_producto.like(f"%{search_productos}%")) |
                (Productos.descripcion.ilike(f"%{search_productos}%"))
            )

        # Si hay búsqueda en empleados, filtrar por número de identificación o nombre
        if search_empleados:
            consulta_empleados = consulta_empleados.filter(
                (Empleados.id_empleado.like(f"%{search_empleados}%")) |
                (Empleados.nombre_empleado.ilike(f"%{search_empleados}%"))
            )

        # Si hay búsqueda en clientes, filtrar por número de identificación o nombre
        if search_clientes:
            consulta_clientes = consulta_clientes.filter(
                (Clientes.id_cliente.like(f"%{search_clientes}%")) |
                (Clientes.nombre_cliente.ilike(f"%{search_clientes}%"))
            )

        # Contar total de registros
        total_productos = consulta_productos.count()
        total_empleados = consulta_empleados.count()
        total_clientes = consulta_clientes.count()

        # Aplicar paginación
        productos = consulta_productos.offset((page - 1) * per_page).limit(per_page).all()
        empleados = consulta_empleados.offset((page - 1) * per_page).limit(per_page).all()
        clientes = consulta_clientes.offset((page - 1) * per_page).limit(per_page).all()

        # Determinar el total de páginas basado en el conjunto más grande
        total_registros = max(total_productos, total_empleados, total_clientes)
        total_pages = (total_registros + per_page - 1) // per_page

        return render_template(
            "automotriz.html",
            productos=productos,
            empleados=empleados,
            clientes=clientes,
            page=page,
            total_pages=total_pages,
            search_productos=search_productos,
            search_empleados=search_empleados,
            search_clientes=search_clientes
        )

    except Exception as e:
        print("Error en la consulta SQL:", str(e))
        flash("Se produjo un error al obtener los datos", "danger")
        return render_template("automotriz.html", productos=[], empleados=[], clientes=[], page=1, total_pages=1, search_productos="", search_empleados="", search_clientes="")

@app.route('/computadoras')
def computadoras():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 7
        search_productos = request.args.get('search_productos', '').strip()
        search_empleados = request.args.get('search_empleados', '').strip()
        search_clientes = request.args.get('search_clientes', '').strip()

        # Consultar productos, empleados y clientes de la categoría "Computadoras"
        consulta_productos = Productos.query.filter(Productos.nombre_categoria == 'Computadoras')
        consulta_empleados = Empleados.query.filter(Empleados.nombre_categoria == 'Computadoras')
        consulta_clientes = Clientes.query.filter(Clientes.nombre_categoria == 'Computadoras')

        # Si hay búsqueda en productos, filtrar por referencia o descripción
        if search_productos:
            consulta_productos = consulta_productos.filter(
                (Productos.id_producto.like(f"%{search_productos}%")) |
                (Productos.descripcion.ilike(f"%{search_productos}%"))
            )

        # Si hay búsqueda en empleados, filtrar por número de identificación o nombre
        if search_empleados:
            consulta_empleados = consulta_empleados.filter(
                (Empleados.id_empleado.like(f"%{search_empleados}%")) |
                (Empleados.nombre_empleado.ilike(f"%{search_empleados}%"))
            )

        # Si hay búsqueda en clientes, filtrar por número de identificación o nombre
        if search_clientes:
            consulta_clientes = consulta_clientes.filter(
                (Clientes.id_cliente.like(f"%{search_clientes}%")) |
                (Clientes.nombre_cliente.ilike(f"%{search_clientes}%"))
            )

        # Contar total de registros
        total_productos = consulta_productos.count()
        total_empleados = consulta_empleados.count()
        total_clientes = consulta_clientes.count()

        # Aplicar paginación
        productos = consulta_productos.offset((page - 1) * per_page).limit(per_page).all()
        empleados = consulta_empleados.offset((page - 1) * per_page).limit(per_page).all()
        clientes = consulta_clientes.offset((page - 1) * per_page).limit(per_page).all()

        # Determinar el total de páginas basado en el conjunto más grande
        total_registros = max(total_productos, total_empleados, total_clientes)
        total_pages = (total_registros + per_page - 1) // per_page

        return render_template(
            "computadoras.html",
            productos=productos,
            empleados=empleados,
            clientes=clientes,
            page=page,
            total_pages=total_pages,
            search_productos=search_productos,
            search_empleados=search_empleados,
            search_clientes=search_clientes
        )

    except Exception as e:
        print("Error en la consulta SQL:", str(e))
        flash("Se produjo un error al obtener los datos", "danger")
        return render_template("computadoras.html", productos=[], empleados=[], clientes=[], page=1, total_pages=1, search_productos="", search_empleados="", search_clientes="")


@app.route('/bebes')
def bebes():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 7
        search_productos = request.args.get('search_productos', '').strip()
        search_empleados = request.args.get('search_empleados', '').strip()
        search_clientes = request.args.get('search_clientes', '').strip()

        # Consultar productos, empleados y clientes de la categoría "Computadoras"
        consulta_productos = Productos.query.filter(Productos.nombre_categoria == 'Bebés')
        consulta_empleados = Empleados.query.filter(Empleados.nombre_categoria == 'Bebés')
        consulta_clientes = Clientes.query.filter(Clientes.nombre_categoria == 'Bebés')

        # Si hay búsqueda en productos, filtrar por referencia o descripción
        if search_productos:
            consulta_productos = consulta_productos.filter(
                (Productos.id_producto.like(f"%{search_productos}%")) |
                (Productos.descripcion.ilike(f"%{search_productos}%"))
            )

        # Si hay búsqueda en empleados, filtrar por número de identificación o nombre
        if search_empleados:
            consulta_empleados = consulta_empleados.filter(
                (Empleados.id_empleado.like(f"%{search_empleados}%")) |
                (Empleados.nombre_empleado.ilike(f"%{search_empleados}%"))
            )

        # Si hay búsqueda en clientes, filtrar por número de identificación o nombre
        if search_clientes:
            consulta_clientes = consulta_clientes.filter(
                (Clientes.id_cliente.like(f"%{search_clientes}%")) |
                (Clientes.nombre_cliente.ilike(f"%{search_clientes}%"))
            )

        # Contar total de registros
        total_productos = consulta_productos.count()
        total_empleados = consulta_empleados.count()
        total_clientes = consulta_clientes.count()

        # Aplicar paginación
        productos = consulta_productos.offset((page - 1) * per_page).limit(per_page).all()
        empleados = consulta_empleados.offset((page - 1) * per_page).limit(per_page).all()
        clientes = consulta_clientes.offset((page - 1) * per_page).limit(per_page).all()

        # Determinar el total de páginas basado en el conjunto más grande
        total_registros = max(total_productos, total_empleados, total_clientes)
        total_pages = (total_registros + per_page - 1) // per_page

        return render_template(
            "bebes.html",
            productos=productos,
            empleados=empleados,
            clientes=clientes,
            page=page,
            total_pages=total_pages,
            search_productos=search_productos,
            search_empleados=search_empleados,
            search_clientes=search_clientes
        )

    except Exception as e:
        print("Error en la consulta SQL:", str(e))
        flash("Se produjo un error al obtener los datos", "danger")
        return render_template("bebes.html", productos=[], empleados=[], clientes=[], page=1, total_pages=1, search_productos="", search_empleados="", search_clientes="")
    
@app.route('/cuidado_personal')
def cuidado_personal():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 7
        search_productos = request.args.get('search_productos', '').strip()
        search_empleados = request.args.get('search_empleados', '').strip()
        search_clientes = request.args.get('search_clientes', '').strip()

        # Consultar productos, empleados y clientes de la categoría "Computadoras"
        consulta_productos = Productos.query.filter(Productos.nombre_categoria == 'Belleza y cuidado personal')
        consulta_empleados = Empleados.query.filter(Empleados.nombre_categoria == 'Belleza y cuidado personal')
        consulta_clientes = Clientes.query.filter(Clientes.nombre_categoria == 'Belleza y cuidado personal')

        # Si hay búsqueda en productos, filtrar por referencia o descripción
        if search_productos:
            consulta_productos = consulta_productos.filter(
                (Productos.id_producto.like(f"%{search_productos}%")) |
                (Productos.descripcion.ilike(f"%{search_productos}%"))
            )

        # Si hay búsqueda en empleados, filtrar por número de identificación o nombre
        if search_empleados:
            consulta_empleados = consulta_empleados.filter(
                (Empleados.id_empleado.like(f"%{search_empleados}%")) |
                (Empleados.nombre_empleado.ilike(f"%{search_empleados}%"))
            )

        # Si hay búsqueda en clientes, filtrar por número de identificación o nombre
        if search_clientes:
            consulta_clientes = consulta_clientes.filter(
                (Clientes.id_cliente.like(f"%{search_clientes}%")) |
                (Clientes.nombre_cliente.ilike(f"%{search_clientes}%"))
            )

        # Contar total de registros
        total_productos = consulta_productos.count()
        total_empleados = consulta_empleados.count()
        total_clientes = consulta_clientes.count()

        # Aplicar paginación
        productos = consulta_productos.offset((page - 1) * per_page).limit(per_page).all()
        empleados = consulta_empleados.offset((page - 1) * per_page).limit(per_page).all()
        clientes = consulta_clientes.offset((page - 1) * per_page).limit(per_page).all()

        # Determinar el total de páginas basado en el conjunto más grande
        total_registros = max(total_productos, total_empleados, total_clientes)
        total_pages = (total_registros + per_page - 1) // per_page

        return render_template(
            "cuidado_personal.html",
            productos=productos,
            empleados=empleados,
            clientes=clientes,
            page=page,
            total_pages=total_pages,
            search_productos=search_productos,
            search_empleados=search_empleados,
            search_clientes=search_clientes
        )

    except Exception as e:
        print("Error en la consulta SQL:", str(e))
        flash("Se produjo un error al obtener los datos", "danger")
        return render_template("cuidado_personal.html", productos=[], empleados=[], clientes=[], page=1, total_pages=1, search_productos="", search_empleados="", search_clientes="")

@app.route('/cine')
def cine():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 7
        search_productos = request.args.get('search_productos', '').strip()
        search_empleados = request.args.get('search_empleados', '').strip()
        search_clientes = request.args.get('search_clientes', '').strip()

        # Consultar productos, empleados y clientes de la categoría "Computadoras"
        consulta_productos = Productos.query.filter(Productos.nombre_categoria == 'Cine y TV')
        consulta_empleados = Empleados.query.filter(Empleados.nombre_categoria == 'Cine y TV')
        consulta_clientes = Clientes.query.filter(Clientes.nombre_categoria == 'Cine y TV')

        # Si hay búsqueda en productos, filtrar por referencia o descripción
        if search_productos:
            consulta_productos = consulta_productos.filter(
                (Productos.id_producto.like(f"%{search_productos}%")) |
                (Productos.descripcion.ilike(f"%{search_productos}%"))
            )

        # Si hay búsqueda en empleados, filtrar por número de identificación o nombre
        if search_empleados:
            consulta_empleados = consulta_empleados.filter(
                (Empleados.id_empleado.like(f"%{search_empleados}%")) |
                (Empleados.nombre_empleado.ilike(f"%{search_empleados}%"))
            )

        # Si hay búsqueda en clientes, filtrar por número de identificación o nombre
        if search_clientes:
            consulta_clientes = consulta_clientes.filter(
                (Clientes.id_cliente.like(f"%{search_clientes}%")) |
                (Clientes.nombre_cliente.ilike(f"%{search_clientes}%"))
            )

        # Contar total de registros
        total_productos = consulta_productos.count()
        total_empleados = consulta_empleados.count()
        total_clientes = consulta_clientes.count()

        # Aplicar paginación
        productos = consulta_productos.offset((page - 1) * per_page).limit(per_page).all()
        empleados = consulta_empleados.offset((page - 1) * per_page).limit(per_page).all()
        clientes = consulta_clientes.offset((page - 1) * per_page).limit(per_page).all()

        # Determinar el total de páginas basado en el conjunto más grande
        total_registros = max(total_productos, total_empleados, total_clientes)
        total_pages = (total_registros + per_page - 1) // per_page

        return render_template(
            "cine.html",
            productos=productos,
            empleados=empleados,
            clientes=clientes,
            page=page,
            total_pages=total_pages,
            search_productos=search_productos,
            search_empleados=search_empleados,
            search_clientes=search_clientes
        )

    except Exception as e:
        print("Error en la consulta SQL:", str(e))
        flash("Se produjo un error al obtener los datos", "danger")
        return render_template("cine.html", productos=[], empleados=[], clientes=[], page=1, total_pages=1, search_productos="", search_empleados="", search_clientes="")

@app.route('/deportes')
def deportes():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 7
        search_productos = request.args.get('search_productos', '').strip()
        search_empleados = request.args.get('search_empleados', '').strip()
        search_clientes = request.args.get('search_clientes', '').strip()

        # Consultar productos, empleados y clientes de la categoría "Computadoras"
        consulta_productos = Productos.query.filter(Productos.nombre_categoria == 'Deportes y actividades al aire libre')
        consulta_empleados = Empleados.query.filter(Empleados.nombre_categoria == 'Deportes y actividades al aire libre')
        consulta_clientes = Clientes.query.filter(Clientes.nombre_categoria == 'Deportes y actividades al aire libre')

        # Si hay búsqueda en productos, filtrar por referencia o descripción
        if search_productos:
            consulta_productos = consulta_productos.filter(
                (Productos.id_producto.like(f"%{search_productos}%")) |
                (Productos.descripcion.ilike(f"%{search_productos}%"))
            )

        # Si hay búsqueda en empleados, filtrar por número de identificación o nombre
        if search_empleados:
            consulta_empleados = consulta_empleados.filter(
                (Empleados.id_empleado.like(f"%{search_empleados}%")) |
                (Empleados.nombre_empleado.ilike(f"%{search_empleados}%"))
            )

        # Si hay búsqueda en clientes, filtrar por número de identificación o nombre
        if search_clientes:
            consulta_clientes = consulta_clientes.filter(
                (Clientes.id_cliente.like(f"%{search_clientes}%")) |
                (Clientes.nombre_cliente.ilike(f"%{search_clientes}%"))
            )

        # Contar total de registros
        total_productos = consulta_productos.count()
        total_empleados = consulta_empleados.count()
        total_clientes = consulta_clientes.count()

        # Aplicar paginación
        productos = consulta_productos.offset((page - 1) * per_page).limit(per_page).all()
        empleados = consulta_empleados.offset((page - 1) * per_page).limit(per_page).all()
        clientes = consulta_clientes.offset((page - 1) * per_page).limit(per_page).all()

        # Determinar el total de páginas basado en el conjunto más grande
        total_registros = max(total_productos, total_empleados, total_clientes)
        total_pages = (total_registros + per_page - 1) // per_page

        return render_template(
            "deportes.html",
            productos=productos,
            empleados=empleados,
            clientes=clientes,
            page=page,
            total_pages=total_pages,
            search_productos=search_productos,
            search_empleados=search_empleados,
            search_clientes=search_clientes
        )

    except Exception as e:
        print("Error en la consulta SQL:", str(e))
        flash("Se produjo un error al obtener los datos", "danger")
        return render_template("deportes.html", productos=[], empleados=[], clientes=[], page=1, total_pages=1, search_productos="", search_empleados="", search_clientes="")
    
@app.route('/electronicos')
def electronicos():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 7
        search_productos = request.args.get('search_productos', '').strip()
        search_empleados = request.args.get('search_empleados', '').strip()
        search_clientes = request.args.get('search_clientes', '').strip()

        # Consultar productos, empleados y clientes de la categoría "Computadoras"
        consulta_productos = Productos.query.filter(Productos.nombre_categoria == 'Electrónicos')
        consulta_empleados = Empleados.query.filter(Empleados.nombre_categoria == 'Electrónicos')
        consulta_clientes = Clientes.query.filter(Clientes.nombre_categoria == 'Electrónicos')

        # Si hay búsqueda en productos, filtrar por referencia o descripción
        if search_productos:
            consulta_productos = consulta_productos.filter(
                (Productos.id_producto.like(f"%{search_productos}%")) |
                (Productos.descripcion.ilike(f"%{search_productos}%"))
            )

        # Si hay búsqueda en empleados, filtrar por número de identificación o nombre
        if search_empleados:
            consulta_empleados = consulta_empleados.filter(
                (Empleados.id_empleado.like(f"%{search_empleados}%")) |
                (Empleados.nombre_empleado.ilike(f"%{search_empleados}%"))
            )

        # Si hay búsqueda en clientes, filtrar por número de identificación o nombre
        if search_clientes:
            consulta_clientes = consulta_clientes.filter(
                (Clientes.id_cliente.like(f"%{search_clientes}%")) |
                (Clientes.nombre_cliente.ilike(f"%{search_clientes}%"))
            )

        # Contar total de registros
        total_productos = consulta_productos.count()
        total_empleados = consulta_empleados.count()
        total_clientes = consulta_clientes.count()

        # Aplicar paginación
        productos = consulta_productos.offset((page - 1) * per_page).limit(per_page).all()
        empleados = consulta_empleados.offset((page - 1) * per_page).limit(per_page).all()
        clientes = consulta_clientes.offset((page - 1) * per_page).limit(per_page).all()

        # Determinar el total de páginas basado en el conjunto más grande
        total_registros = max(total_productos, total_empleados, total_clientes)
        total_pages = (total_registros + per_page - 1) // per_page

        return render_template(
            "electronicos.html",
            productos=productos,
            empleados=empleados,
            clientes=clientes,
            page=page,
            total_pages=total_pages,
            search_productos=search_productos,
            search_empleados=search_empleados,
            search_clientes=search_clientes
        )

    except Exception as e:
        print("Error en la consulta SQL:", str(e))
        flash("Se produjo un error al obtener los datos", "danger")
        return render_template("electronicos.html", productos=[], empleados=[], clientes=[], page=1, total_pages=1, search_productos="", search_empleados="", search_clientes="")
    
@app.route('/equipaje')
def equipaje():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 7
        search_productos = request.args.get('search_productos', '').strip()
        search_empleados = request.args.get('search_empleados', '').strip()
        search_clientes = request.args.get('search_clientes', '').strip()

        # Consultar productos, empleados y clientes de la categoría "Computadoras"
        consulta_productos = Productos.query.filter(Productos.nombre_categoria == 'Equipaje')
        consulta_empleados = Empleados.query.filter(Empleados.nombre_categoria == 'Equipaje')
        consulta_clientes = Clientes.query.filter(Clientes.nombre_categoria == 'Equipaje')

        # Si hay búsqueda en productos, filtrar por referencia o descripción
        if search_productos:
            consulta_productos = consulta_productos.filter(
                (Productos.id_producto.like(f"%{search_productos}%")) |
                (Productos.descripcion.ilike(f"%{search_productos}%"))
            )

        # Si hay búsqueda en empleados, filtrar por número de identificación o nombre
        if search_empleados:
            consulta_empleados = consulta_empleados.filter(
                (Empleados.id_empleado.like(f"%{search_empleados}%")) |
                (Empleados.nombre_empleado.ilike(f"%{search_empleados}%"))
            )

        # Si hay búsqueda en clientes, filtrar por número de identificación o nombre
        if search_clientes:
            consulta_clientes = consulta_clientes.filter(
                (Clientes.id_cliente.like(f"%{search_clientes}%")) |
                (Clientes.nombre_cliente.ilike(f"%{search_clientes}%"))
            )

        # Contar total de registros
        total_productos = consulta_productos.count()
        total_empleados = consulta_empleados.count()
        total_clientes = consulta_clientes.count()

        # Aplicar paginación
        productos = consulta_productos.offset((page - 1) * per_page).limit(per_page).all()
        empleados = consulta_empleados.offset((page - 1) * per_page).limit(per_page).all()
        clientes = consulta_clientes.offset((page - 1) * per_page).limit(per_page).all()

        # Determinar el total de páginas basado en el conjunto más grande
        total_registros = max(total_productos, total_empleados, total_clientes)
        total_pages = (total_registros + per_page - 1) // per_page

        return render_template(
            "equipaje.html",
            productos=productos,
            empleados=empleados,
            clientes=clientes,
            page=page,
            total_pages=total_pages,
            search_productos=search_productos,
            search_empleados=search_empleados,
            search_clientes=search_clientes
        )

    except Exception as e:
        print("Error en la consulta SQL:", str(e))
        flash("Se produjo un error al obtener los datos", "danger")
        return render_template("equipaje.html", productos=[], empleados=[], clientes=[], page=1, total_pages=1, search_productos="", search_empleados="", search_clientes="")


@app.route('/herramientas')
def herramientas():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 7
        search_productos = request.args.get('search_productos', '').strip()
        search_empleados = request.args.get('search_empleados', '').strip()
        search_clientes = request.args.get('search_clientes', '').strip()

        # Consultar productos, empleados y clientes de la categoría "Computadoras"
        consulta_productos = Productos.query.filter(Productos.nombre_categoria == 'Herramientas y mejoramiento del hogar')
        consulta_empleados = Empleados.query.filter(Empleados.nombre_categoria == 'Herramientas y mejoramiento del hogar')
        consulta_clientes = Clientes.query.filter(Clientes.nombre_categoria == 'Herramientas y mejoramiento del hogar')

        # Si hay búsqueda en productos, filtrar por referencia o descripción
        if search_productos:
            consulta_productos = consulta_productos.filter(
                (Productos.id_producto.like(f"%{search_productos}%")) |
                (Productos.descripcion.ilike(f"%{search_productos}%"))
            )

        # Si hay búsqueda en empleados, filtrar por número de identificación o nombre
        if search_empleados:
            consulta_empleados = consulta_empleados.filter(
                (Empleados.id_empleado.like(f"%{search_empleados}%")) |
                (Empleados.nombre_empleado.ilike(f"%{search_empleados}%"))
            )

        # Si hay búsqueda en clientes, filtrar por número de identificación o nombre
        if search_clientes:
            consulta_clientes = consulta_clientes.filter(
                (Clientes.id_cliente.like(f"%{search_clientes}%")) |
                (Clientes.nombre_cliente.ilike(f"%{search_clientes}%"))
            )

        # Contar total de registros
        total_productos = consulta_productos.count()
        total_empleados = consulta_empleados.count()
        total_clientes = consulta_clientes.count()

        # Aplicar paginación
        productos = consulta_productos.offset((page - 1) * per_page).limit(per_page).all()
        empleados = consulta_empleados.offset((page - 1) * per_page).limit(per_page).all()
        clientes = consulta_clientes.offset((page - 1) * per_page).limit(per_page).all()

        # Determinar el total de páginas basado en el conjunto más grande
        total_registros = max(total_productos, total_empleados, total_clientes)
        total_pages = (total_registros + per_page - 1) // per_page

        return render_template(
            "herramientas.html",
            productos=productos,
            empleados=empleados,
            clientes=clientes,
            page=page,
            total_pages=total_pages,
            search_productos=search_productos,
            search_empleados=search_empleados,
            search_clientes=search_clientes
        )

    except Exception as e:
        print("Error en la consulta SQL:", str(e))
        flash("Se produjo un error al obtener los datos", "danger")
        return render_template("herramientas.html", productos=[], empleados=[], clientes=[], page=1, total_pages=1, search_productos="", search_empleados="", search_clientes="")

@app.route('/cocina')
def cocina():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 7
        search_productos = request.args.get('search_productos', '').strip()
        search_empleados = request.args.get('search_empleados', '').strip()
        search_clientes = request.args.get('search_clientes', '').strip()

        # Consultar productos, empleados y clientes de la categoría "Computadoras"
        consulta_productos = Productos.query.filter(Productos.nombre_categoria == 'Hogar y cocina')
        consulta_empleados = Empleados.query.filter(Empleados.nombre_categoria == 'Hogar y cocina')
        consulta_clientes = Clientes.query.filter(Clientes.nombre_categoria == 'Hogar y cocina')

        # Si hay búsqueda en productos, filtrar por referencia o descripción
        if search_productos:
            consulta_productos = consulta_productos.filter(
                (Productos.id_producto.like(f"%{search_productos}%")) |
                (Productos.descripcion.ilike(f"%{search_productos}%"))
            )

        # Si hay búsqueda en empleados, filtrar por número de identificación o nombre
        if search_empleados:
            consulta_empleados = consulta_empleados.filter(
                (Empleados.id_empleado.like(f"%{search_empleados}%")) |
                (Empleados.nombre_empleado.ilike(f"%{search_empleados}%"))
            )

        # Si hay búsqueda en clientes, filtrar por número de identificación o nombre
        if search_clientes:
            consulta_clientes = consulta_clientes.filter(
                (Clientes.id_cliente.like(f"%{search_clientes}%")) |
                (Clientes.nombre_cliente.ilike(f"%{search_clientes}%"))
            )

        # Contar total de registros
        total_productos = consulta_productos.count()
        total_empleados = consulta_empleados.count()
        total_clientes = consulta_clientes.count()

        # Aplicar paginación
        productos = consulta_productos.offset((page - 1) * per_page).limit(per_page).all()
        empleados = consulta_empleados.offset((page - 1) * per_page).limit(per_page).all()
        clientes = consulta_clientes.offset((page - 1) * per_page).limit(per_page).all()

        # Determinar el total de páginas basado en el conjunto más grande
        total_registros = max(total_productos, total_empleados, total_clientes)
        total_pages = (total_registros + per_page - 1) // per_page

        return render_template(
            "cocina.html",
            productos=productos,
            empleados=empleados,
            clientes=clientes,
            page=page,
            total_pages=total_pages,
            search_productos=search_productos,
            search_empleados=search_empleados,
            search_clientes=search_clientes
        )

    except Exception as e:
        print("Error en la consulta SQL:", str(e))
        flash("Se produjo un error al obtener los datos", "danger")
        return render_template("cocina.html", productos=[], empleados=[], clientes=[], page=1, total_pages=1, search_productos="", search_empleados="", search_clientes="")

@app.route('/industrial')
def industrial():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 7
        search_productos = request.args.get('search_productos', '').strip()
        search_empleados = request.args.get('search_empleados', '').strip()
        search_clientes = request.args.get('search_clientes', '').strip()

        # Consultar productos, empleados y clientes de la categoría "Computadoras"
        consulta_productos = Productos.query.filter(Productos.nombre_categoria == 'Industrial y científico')
        consulta_empleados = Empleados.query.filter(Empleados.nombre_categoria == 'Industrial y científico')
        consulta_clientes = Clientes.query.filter(Clientes.nombre_categoria == 'Industrial y científico')

        # Si hay búsqueda en productos, filtrar por referencia o descripción
        if search_productos:
            consulta_productos = consulta_productos.filter(
                (Productos.id_producto.like(f"%{search_productos}%")) |
                (Productos.descripcion.ilike(f"%{search_productos}%"))
            )

        # Si hay búsqueda en empleados, filtrar por número de identificación o nombre
        if search_empleados:
            consulta_empleados = consulta_empleados.filter(
                (Empleados.id_empleado.like(f"%{search_empleados}%")) |
                (Empleados.nombre_empleado.ilike(f"%{search_empleados}%"))
            )

        # Si hay búsqueda en clientes, filtrar por número de identificación o nombre
        if search_clientes:
            consulta_clientes = consulta_clientes.filter(
                (Clientes.id_cliente.like(f"%{search_clientes}%")) |
                (Clientes.nombre_cliente.ilike(f"%{search_clientes}%"))
            )

        # Contar total de registros
        total_productos = consulta_productos.count()
        total_empleados = consulta_empleados.count()
        total_clientes = consulta_clientes.count()

        # Aplicar paginación
        productos = consulta_productos.offset((page - 1) * per_page).limit(per_page).all()
        empleados = consulta_empleados.offset((page - 1) * per_page).limit(per_page).all()
        clientes = consulta_clientes.offset((page - 1) * per_page).limit(per_page).all()

        # Determinar el total de páginas basado en el conjunto más grande
        total_registros = max(total_productos, total_empleados, total_clientes)
        total_pages = (total_registros + per_page - 1) // per_page

        return render_template(
            "industrial.html",
            productos=productos,
            empleados=empleados,
            clientes=clientes,
            page=page,
            total_pages=total_pages,
            search_productos=search_productos,
            search_empleados=search_empleados,
            search_clientes=search_clientes
        )

    except Exception as e:
        print("Error en la consulta SQL:", str(e))
        flash("Se produjo un error al obtener los datos", "danger")
        return render_template("industrial.html", productos=[], empleados=[], clientes=[], page=1, total_pages=1, search_productos="", search_empleados="", search_clientes="")

@app.route('/mascotas')
def mascotas():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 7
        search_productos = request.args.get('search_productos', '').strip()
        search_empleados = request.args.get('search_empleados', '').strip()
        search_clientes = request.args.get('search_clientes', '').strip()

        # Consultar productos, empleados y clientes de la categoría "Computadoras"
        consulta_productos = Productos.query.filter(Productos.nombre_categoria == 'Insumos para mascotas')
        consulta_empleados = Empleados.query.filter(Empleados.nombre_categoria == 'Insumos para mascotas')
        consulta_clientes = Clientes.query.filter(Clientes.nombre_categoria == 'Insumos para mascotas')

        # Si hay búsqueda en productos, filtrar por referencia o descripción
        if search_productos:
            consulta_productos = consulta_productos.filter(
                (Productos.id_producto.like(f"%{search_productos}%")) |
                (Productos.descripcion.ilike(f"%{search_productos}%"))
            )

        # Si hay búsqueda en empleados, filtrar por número de identificación o nombre
        if search_empleados:
            consulta_empleados = consulta_empleados.filter(
                (Empleados.id_empleado.like(f"%{search_empleados}%")) |
                (Empleados.nombre_empleado.ilike(f"%{search_empleados}%"))
            )

        # Si hay búsqueda en clientes, filtrar por número de identificación o nombre
        if search_clientes:
            consulta_clientes = consulta_clientes.filter(
                (Clientes.id_cliente.like(f"%{search_clientes}%")) |
                (Clientes.nombre_cliente.ilike(f"%{search_clientes}%"))
            )

        # Contar total de registros
        total_productos = consulta_productos.count()
        total_empleados = consulta_empleados.count()
        total_clientes = consulta_clientes.count()

        # Aplicar paginación
        productos = consulta_productos.offset((page - 1) * per_page).limit(per_page).all()
        empleados = consulta_empleados.offset((page - 1) * per_page).limit(per_page).all()
        clientes = consulta_clientes.offset((page - 1) * per_page).limit(per_page).all()

        # Determinar el total de páginas basado en el conjunto más grande
        total_registros = max(total_productos, total_empleados, total_clientes)
        total_pages = (total_registros + per_page - 1) // per_page

        return render_template(
            "mascotas.html",
            productos=productos,
            empleados=empleados,
            clientes=clientes,
            page=page,
            total_pages=total_pages,
            search_productos=search_productos,
            search_empleados=search_empleados,
            search_clientes=search_clientes
        )

    except Exception as e:
        print("Error en la consulta SQL:", str(e))
        flash("Se produjo un error al obtener los datos", "danger")
        return render_template("mascotas.html", productos=[], empleados=[], clientes=[], page=1, total_pages=1, search_productos="", search_empleados="", search_clientes="")

@app.route('/juguetes')
def juguetes():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 7
        search_productos = request.args.get('search_productos', '').strip()
        search_empleados = request.args.get('search_empleados', '').strip()
        search_clientes = request.args.get('search_clientes', '').strip()

        # Consultar productos, empleados y clientes de la categoría "Computadoras"
        consulta_productos = Productos.query.filter(Productos.nombre_categoria == 'Juguetes y juegos')
        consulta_empleados = Empleados.query.filter(Empleados.nombre_categoria == 'Juguetes y juegos')
        consulta_clientes = Clientes.query.filter(Clientes.nombre_categoria == 'Juguetes y juegos')

        # Si hay búsqueda en productos, filtrar por referencia o descripción
        if search_productos:
            consulta_productos = consulta_productos.filter(
                (Productos.id_producto.like(f"%{search_productos}%")) |
                (Productos.descripcion.ilike(f"%{search_productos}%"))
            )

        # Si hay búsqueda en empleados, filtrar por número de identificación o nombre
        if search_empleados:
            consulta_empleados = consulta_empleados.filter(
                (Empleados.id_empleado.like(f"%{search_empleados}%")) |
                (Empleados.nombre_empleado.ilike(f"%{search_empleados}%"))
            )

        # Si hay búsqueda en clientes, filtrar por número de identificación o nombre
        if search_clientes:
            consulta_clientes = consulta_clientes.filter(
                (Clientes.id_cliente.like(f"%{search_clientes}%")) |
                (Clientes.nombre_cliente.ilike(f"%{search_clientes}%"))
            )

        # Contar total de registros
        total_productos = consulta_productos.count()
        total_empleados = consulta_empleados.count()
        total_clientes = consulta_clientes.count()

        # Aplicar paginación
        productos = consulta_productos.offset((page - 1) * per_page).limit(per_page).all()
        empleados = consulta_empleados.offset((page - 1) * per_page).limit(per_page).all()
        clientes = consulta_clientes.offset((page - 1) * per_page).limit(per_page).all()

        # Determinar el total de páginas basado en el conjunto más grande
        total_registros = max(total_productos, total_empleados, total_clientes)
        total_pages = (total_registros + per_page - 1) // per_page

        return render_template(
            "juguetes.html",
            productos=productos,
            empleados=empleados,
            clientes=clientes,
            page=page,
            total_pages=total_pages,
            search_productos=search_productos,
            search_empleados=search_empleados,
            search_clientes=search_clientes
        )

    except Exception as e:
        print("Error en la consulta SQL:", str(e))
        flash("Se produjo un error al obtener los datos", "danger")
        return render_template("juguetes.html", productos=[], empleados=[], clientes=[], page=1, total_pages=1, search_productos="", search_empleados="", search_clientes="")


@app.route('/libros')
def libros():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 7
        search_productos = request.args.get('search_productos', '').strip()
        search_empleados = request.args.get('search_empleados', '').strip()
        search_clientes = request.args.get('search_clientes', '').strip()

        # Consultar productos, empleados y clientes de la categoría "Computadoras"
        consulta_productos = Productos.query.filter(Productos.nombre_categoria == 'Libros')
        consulta_empleados = Empleados.query.filter(Empleados.nombre_categoria == 'Libros')
        consulta_clientes = Clientes.query.filter(Clientes.nombre_categoria == 'Libros')

        # Si hay búsqueda en productos, filtrar por referencia o descripción
        if search_productos:
            consulta_productos = consulta_productos.filter(
                (Productos.id_producto.like(f"%{search_productos}%")) |
                (Productos.descripcion.ilike(f"%{search_productos}%"))
            )

        # Si hay búsqueda en empleados, filtrar por número de identificación o nombre
        if search_empleados:
            consulta_empleados = consulta_empleados.filter(
                (Empleados.id_empleado.like(f"%{search_empleados}%")) |
                (Empleados.nombre_empleado.ilike(f"%{search_empleados}%"))
            )

        # Si hay búsqueda en clientes, filtrar por número de identificación o nombre
        if search_clientes:
            consulta_clientes = consulta_clientes.filter(
                (Clientes.id_cliente.like(f"%{search_clientes}%")) |
                (Clientes.nombre_cliente.ilike(f"%{search_clientes}%"))
            )

        # Contar total de registros
        total_productos = consulta_productos.count()
        total_empleados = consulta_empleados.count()
        total_clientes = consulta_clientes.count()

        # Aplicar paginación
        productos = consulta_productos.offset((page - 1) * per_page).limit(per_page).all()
        empleados = consulta_empleados.offset((page - 1) * per_page).limit(per_page).all()
        clientes = consulta_clientes.offset((page - 1) * per_page).limit(per_page).all()

        # Determinar el total de páginas basado en el conjunto más grande
        total_registros = max(total_productos, total_empleados, total_clientes)
        total_pages = (total_registros + per_page - 1) // per_page

        return render_template(
            "libros.html",
            productos=productos,
            empleados=empleados,
            clientes=clientes,
            page=page,
            total_pages=total_pages,
            search_productos=search_productos,
            search_empleados=search_empleados,
            search_clientes=search_clientes
        )

    except Exception as e:
        print("Error en la consulta SQL:", str(e))
        flash("Se produjo un error al obtener los datos", "danger")
        return render_template("libros.html", productos=[], empleados=[], clientes=[], page=1, total_pages=1, search_productos="", search_empleados="", search_clientes="")


@app.route('/moda_niñas')
def moda_niñas():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 7
        search_productos = request.args.get('search_productos', '').strip()
        search_empleados = request.args.get('search_empleados', '').strip()
        search_clientes = request.args.get('search_clientes', '').strip()

        # Consultar productos, empleados y clientes de la categoría "Computadoras"
        consulta_productos = Productos.query.filter(Productos.nombre_categoria == 'Moda de niñas')
        consulta_empleados = Empleados.query.filter(Empleados.nombre_categoria == 'Moda de niñas')
        consulta_clientes = Clientes.query.filter(Clientes.nombre_categoria == 'Moda de niñas')

        # Si hay búsqueda en productos, filtrar por referencia o descripción
        if search_productos:
            consulta_productos = consulta_productos.filter(
                (Productos.id_producto.like(f"%{search_productos}%")) |
                (Productos.descripcion.ilike(f"%{search_productos}%"))
            )

        # Si hay búsqueda en empleados, filtrar por número de identificación o nombre
        if search_empleados:
            consulta_empleados = consulta_empleados.filter(
                (Empleados.id_empleado.like(f"%{search_empleados}%")) |
                (Empleados.nombre_empleado.ilike(f"%{search_empleados}%"))
            )

        # Si hay búsqueda en clientes, filtrar por número de identificación o nombre
        if search_clientes:
            consulta_clientes = consulta_clientes.filter(
                (Clientes.id_cliente.like(f"%{search_clientes}%")) |
                (Clientes.nombre_cliente.ilike(f"%{search_clientes}%"))
            )

        # Contar total de registros
        total_productos = consulta_productos.count()
        total_empleados = consulta_empleados.count()
        total_clientes = consulta_clientes.count()

        # Aplicar paginación
        productos = consulta_productos.offset((page - 1) * per_page).limit(per_page).all()
        empleados = consulta_empleados.offset((page - 1) * per_page).limit(per_page).all()
        clientes = consulta_clientes.offset((page - 1) * per_page).limit(per_page).all()

        # Determinar el total de páginas basado en el conjunto más grande
        total_registros = max(total_productos, total_empleados, total_clientes)
        total_pages = (total_registros + per_page - 1) // per_page

        return render_template(
            "moda_niñas.html",
            productos=productos,
            empleados=empleados,
            clientes=clientes,
            page=page,
            total_pages=total_pages,
            search_productos=search_productos,
            search_empleados=search_empleados,
            search_clientes=search_clientes
        )

    except Exception as e:
        print("Error en la consulta SQL:", str(e))
        flash("Se produjo un error al obtener los datos", "danger")
        return render_template("moda_niñas.html", productos=[], empleados=[], clientes=[], page=1, total_pages=1, search_productos="", search_empleados="", search_clientes="")

@app.route('/moda_niños')
def moda_niños():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 7
        search_productos = request.args.get('search_productos', '').strip()
        search_empleados = request.args.get('search_empleados', '').strip()
        search_clientes = request.args.get('search_clientes', '').strip()

        # Consultar productos, empleados y clientes de la categoría "Computadoras"
        consulta_productos = Productos.query.filter(Productos.nombre_categoria == 'Moda de niños')
        consulta_empleados = Empleados.query.filter(Empleados.nombre_categoria == 'Moda de niños')
        consulta_clientes = Clientes.query.filter(Clientes.nombre_categoria == 'Moda de niños')

        # Si hay búsqueda en productos, filtrar por referencia o descripción
        if search_productos:
            consulta_productos = consulta_productos.filter(
                (Productos.id_producto.like(f"%{search_productos}%")) |
                (Productos.descripcion.ilike(f"%{search_productos}%"))
            )

        # Si hay búsqueda en empleados, filtrar por número de identificación o nombre
        if search_empleados:
            consulta_empleados = consulta_empleados.filter(
                (Empleados.id_empleado.like(f"%{search_empleados}%")) |
                (Empleados.nombre_empleado.ilike(f"%{search_empleados}%"))
            )

        # Si hay búsqueda en clientes, filtrar por número de identificación o nombre
        if search_clientes:
            consulta_clientes = consulta_clientes.filter(
                (Clientes.id_cliente.like(f"%{search_clientes}%")) |
                (Clientes.nombre_cliente.ilike(f"%{search_clientes}%"))
            )

        # Contar total de registros
        total_productos = consulta_productos.count()
        total_empleados = consulta_empleados.count()
        total_clientes = consulta_clientes.count()

        # Aplicar paginación
        productos = consulta_productos.offset((page - 1) * per_page).limit(per_page).all()
        empleados = consulta_empleados.offset((page - 1) * per_page).limit(per_page).all()
        clientes = consulta_clientes.offset((page - 1) * per_page).limit(per_page).all()

        # Determinar el total de páginas basado en el conjunto más grande
        total_registros = max(total_productos, total_empleados, total_clientes)
        total_pages = (total_registros + per_page - 1) // per_page

        return render_template(
            "moda_niños.html",
            productos=productos,
            empleados=empleados,
            clientes=clientes,
            page=page,
            total_pages=total_pages,
            search_productos=search_productos,
            search_empleados=search_empleados,
            search_clientes=search_clientes
        )

    except Exception as e:
        print("Error en la consulta SQL:", str(e))
        flash("Se produjo un error al obtener los datos", "danger")
        return render_template("moda_niños.html", productos=[], empleados=[], clientes=[], page=1, total_pages=1, search_productos="", search_empleados="", search_clientes="")

@app.route('/moda_hombre')
def moda_hombre():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 7
        search_productos = request.args.get('search_productos', '').strip()
        search_empleados = request.args.get('search_empleados', '').strip()
        search_clientes = request.args.get('search_clientes', '').strip()

        # Consultar productos, empleados y clientes de la categoría "Computadoras"
        consulta_productos = Productos.query.filter(Productos.nombre_categoria == 'Moda para Hombre')
        consulta_empleados = Empleados.query.filter(Empleados.nombre_categoria == 'Moda para Hombre')
        consulta_clientes = Clientes.query.filter(Clientes.nombre_categoria == 'Moda para Hombre')

        # Si hay búsqueda en productos, filtrar por referencia o descripción
        if search_productos:
            consulta_productos = consulta_productos.filter(
                (Productos.id_producto.like(f"%{search_productos}%")) |
                (Productos.descripcion.ilike(f"%{search_productos}%"))
            )

        # Si hay búsqueda en empleados, filtrar por número de identificación o nombre
        if search_empleados:
            consulta_empleados = consulta_empleados.filter(
                (Empleados.id_empleado.like(f"%{search_empleados}%")) |
                (Empleados.nombre_empleado.ilike(f"%{search_empleados}%"))
            )

        # Si hay búsqueda en clientes, filtrar por número de identificación o nombre
        if search_clientes:
            consulta_clientes = consulta_clientes.filter(
                (Clientes.id_cliente.like(f"%{search_clientes}%")) |
                (Clientes.nombre_cliente.ilike(f"%{search_clientes}%"))
            )

        # Contar total de registros
        total_productos = consulta_productos.count()
        total_empleados = consulta_empleados.count()
        total_clientes = consulta_clientes.count()

        # Aplicar paginación
        productos = consulta_productos.offset((page - 1) * per_page).limit(per_page).all()
        empleados = consulta_empleados.offset((page - 1) * per_page).limit(per_page).all()
        clientes = consulta_clientes.offset((page - 1) * per_page).limit(per_page).all()

        # Determinar el total de páginas basado en el conjunto más grande
        total_registros = max(total_productos, total_empleados, total_clientes)
        total_pages = (total_registros + per_page - 1) // per_page

        return render_template(
            "moda_hombre.html",
            productos=productos,
            empleados=empleados,
            clientes=clientes,
            page=page,
            total_pages=total_pages,
            search_productos=search_productos,
            search_empleados=search_empleados,
            search_clientes=search_clientes
        )

    except Exception as e:
        print("Error en la consulta SQL:", str(e))
        flash("Se produjo un error al obtener los datos", "danger")
        return render_template("moda_hombre.html", productos=[], empleados=[], clientes=[], page=1, total_pages=1, search_productos="", search_empleados="", search_clientes="")

@app.route('/moda_mujer')
def moda_mujer():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 7
        search_productos = request.args.get('search_productos', '').strip()
        search_empleados = request.args.get('search_empleados', '').strip()
        search_clientes = request.args.get('search_clientes', '').strip()

        # Consultar productos, empleados y clientes de la categoría "Computadoras"
        consulta_productos = Productos.query.filter(Productos.nombre_categoria == 'Moda para mujer')
        consulta_empleados = Empleados.query.filter(Empleados.nombre_categoria == 'Moda para mujer')
        consulta_clientes = Clientes.query.filter(Clientes.nombre_categoria == 'Moda para mujer')

        # Si hay búsqueda en productos, filtrar por referencia o descripción
        if search_productos:
            consulta_productos = consulta_productos.filter(
                (Productos.id_producto.like(f"%{search_productos}%")) |
                (Productos.descripcion.ilike(f"%{search_productos}%"))
            )

        # Si hay búsqueda en empleados, filtrar por número de identificación o nombre
        if search_empleados:
            consulta_empleados = consulta_empleados.filter(
                (Empleados.id_empleado.like(f"%{search_empleados}%")) |
                (Empleados.nombre_empleado.ilike(f"%{search_empleados}%"))
            )

        # Si hay búsqueda en clientes, filtrar por número de identificación o nombre
        if search_clientes:
            consulta_clientes = consulta_clientes.filter(
                (Clientes.id_cliente.like(f"%{search_clientes}%")) |
                (Clientes.nombre_cliente.ilike(f"%{search_clientes}%"))
            )

        # Contar total de registros
        total_productos = consulta_productos.count()
        total_empleados = consulta_empleados.count()
        total_clientes = consulta_clientes.count()

        # Aplicar paginación
        productos = consulta_productos.offset((page - 1) * per_page).limit(per_page).all()
        empleados = consulta_empleados.offset((page - 1) * per_page).limit(per_page).all()
        clientes = consulta_clientes.offset((page - 1) * per_page).limit(per_page).all()

        # Determinar el total de páginas basado en el conjunto más grande
        total_registros = max(total_productos, total_empleados, total_clientes)
        total_pages = (total_registros + per_page - 1) // per_page

        return render_template(
            "moda_mujer.html",
            productos=productos,
            empleados=empleados,
            clientes=clientes,
            page=page,
            total_pages=total_pages,
            search_productos=search_productos,
            search_empleados=search_empleados,
            search_clientes=search_clientes
        )

    except Exception as e:
        print("Error en la consulta SQL:", str(e))
        flash("Se produjo un error al obtener los datos", "danger")
        return render_template("moda_mujer.html", productos=[], empleados=[], clientes=[], page=1, total_pages=1, search_productos="", search_empleados="", search_clientes="")

@app.route('/musica_mp3')
def musica_mp3():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 7
        search_productos = request.args.get('search_productos', '').strip()
        search_empleados = request.args.get('search_empleados', '').strip()
        search_clientes = request.args.get('search_clientes', '').strip()

        # Consultar productos, empleados y clientes de la categoría "Computadoras"
        consulta_productos = Productos.query.filter(Productos.nombre_categoria == 'Música MP3')
        consulta_empleados = Empleados.query.filter(Empleados.nombre_categoria == 'Música MP3')
        consulta_clientes = Clientes.query.filter(Clientes.nombre_categoria == 'Música MP3')

        # Si hay búsqueda en productos, filtrar por referencia o descripción
        if search_productos:
            consulta_productos = consulta_productos.filter(
                (Productos.id_producto.like(f"%{search_productos}%")) |
                (Productos.descripcion.ilike(f"%{search_productos}%"))
            )

        # Si hay búsqueda en empleados, filtrar por número de identificación o nombre
        if search_empleados:
            consulta_empleados = consulta_empleados.filter(
                (Empleados.id_empleado.like(f"%{search_empleados}%")) |
                (Empleados.nombre_empleado.ilike(f"%{search_empleados}%"))
            )

        # Si hay búsqueda en clientes, filtrar por número de identificación o nombre
        if search_clientes:
            consulta_clientes = consulta_clientes.filter(
                (Clientes.id_cliente.like(f"%{search_clientes}%")) |
                (Clientes.nombre_cliente.ilike(f"%{search_clientes}%"))
            )

        # Contar total de registros
        total_productos = consulta_productos.count()
        total_empleados = consulta_empleados.count()
        total_clientes = consulta_clientes.count()

        # Aplicar paginación
        productos = consulta_productos.offset((page - 1) * per_page).limit(per_page).all()
        empleados = consulta_empleados.offset((page - 1) * per_page).limit(per_page).all()
        clientes = consulta_clientes.offset((page - 1) * per_page).limit(per_page).all()

        # Determinar el total de páginas basado en el conjunto más grande
        total_registros = max(total_productos, total_empleados, total_clientes)
        total_pages = (total_registros + per_page - 1) // per_page

        return render_template(
            "musica_mp3.html",
            productos=productos,
            empleados=empleados,
            clientes=clientes,
            page=page,
            total_pages=total_pages,
            search_productos=search_productos,
            search_empleados=search_empleados,
            search_clientes=search_clientes
        )

    except Exception as e:
        print("Error en la consulta SQL:", str(e))
        flash("Se produjo un error al obtener los datos", "danger")
        return render_template("musica_mp3.html", productos=[], empleados=[], clientes=[], page=1, total_pages=1, search_productos="", search_empleados="", search_clientes="")

@app.route('/musica_cd')
def musica_cd():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 7
        search_productos = request.args.get('search_productos', '').strip()
        search_empleados = request.args.get('search_empleados', '').strip()
        search_clientes = request.args.get('search_clientes', '').strip()

        # Consultar productos, empleados y clientes de la categoría "Computadoras"
        consulta_productos = Productos.query.filter(Productos.nombre_categoria == 'Música, CD y vinilos')
        consulta_empleados = Empleados.query.filter(Empleados.nombre_categoria == 'Música, CD y vinilos')
        consulta_clientes = Clientes.query.filter(Clientes.nombre_categoria == 'Música, CD y vinilos')

        # Si hay búsqueda en productos, filtrar por referencia o descripción
        if search_productos:
            consulta_productos = consulta_productos.filter(
                (Productos.id_producto.like(f"%{search_productos}%")) |
                (Productos.descripcion.ilike(f"%{search_productos}%"))
            )

        # Si hay búsqueda en empleados, filtrar por número de identificación o nombre
        if search_empleados:
            consulta_empleados = consulta_empleados.filter(
                (Empleados.id_empleado.like(f"%{search_empleados}%")) |
                (Empleados.nombre_empleado.ilike(f"%{search_empleados}%"))
            )

        # Si hay búsqueda en clientes, filtrar por número de identificación o nombre
        if search_clientes:
            consulta_clientes = consulta_clientes.filter(
                (Clientes.id_cliente.like(f"%{search_clientes}%")) |
                (Clientes.nombre_cliente.ilike(f"%{search_clientes}%"))
            )

        # Contar total de registros
        total_productos = consulta_productos.count()
        total_empleados = consulta_empleados.count()
        total_clientes = consulta_clientes.count()

        # Aplicar paginación
        productos = consulta_productos.offset((page - 1) * per_page).limit(per_page).all()
        empleados = consulta_empleados.offset((page - 1) * per_page).limit(per_page).all()
        clientes = consulta_clientes.offset((page - 1) * per_page).limit(per_page).all()

        # Determinar el total de páginas basado en el conjunto más grande
        total_registros = max(total_productos, total_empleados, total_clientes)
        total_pages = (total_registros + per_page - 1) // per_page

        return render_template(
            "musica_cd.html",
            productos=productos,
            empleados=empleados,
            clientes=clientes,
            page=page,
            total_pages=total_pages,
            search_productos=search_productos,
            search_empleados=search_empleados,
            search_clientes=search_clientes
        )

    except Exception as e:
        print("Error en la consulta SQL:", str(e))
        flash("Se produjo un error al obtener los datos", "danger")
        return render_template("musica_cd.html", productos=[], empleados=[], clientes=[], page=1, total_pages=1, search_productos="", search_empleados="", search_clientes="")

@app.route('/ofertas')
def ofertas():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 7
        search_productos = request.args.get('search_productos', '').strip()
        search_empleados = request.args.get('search_empleados', '').strip()
        search_clientes = request.args.get('search_clientes', '').strip()

        # Consultar productos, empleados y clientes de la categoría "Computadoras"
        consulta_productos = Productos.query.filter(Productos.nombre_categoria == 'Ofertas')
        consulta_empleados = Empleados.query.filter(Empleados.nombre_categoria == 'Ofertas')
        consulta_clientes = Clientes.query.filter(Clientes.nombre_categoria == 'Ofertas')

        # Si hay búsqueda en productos, filtrar por referencia o descripción
        if search_productos:
            consulta_productos = consulta_productos.filter(
                (Productos.id_producto.like(f"%{search_productos}%")) |
                (Productos.descripcion.ilike(f"%{search_productos}%"))
            )

        # Si hay búsqueda en empleados, filtrar por número de identificación o nombre
        if search_empleados:
            consulta_empleados = consulta_empleados.filter(
                (Empleados.id_empleado.like(f"%{search_empleados}%")) |
                (Empleados.nombre_empleado.ilike(f"%{search_empleados}%"))
            )

        # Si hay búsqueda en clientes, filtrar por número de identificación o nombre
        if search_clientes:
            consulta_clientes = consulta_clientes.filter(
                (Clientes.id_cliente.like(f"%{search_clientes}%")) |
                (Clientes.nombre_cliente.ilike(f"%{search_clientes}%"))
            )

        # Contar total de registros
        total_productos = consulta_productos.count()
        total_empleados = consulta_empleados.count()
        total_clientes = consulta_clientes.count()

        # Aplicar paginación
        productos = consulta_productos.offset((page - 1) * per_page).limit(per_page).all()
        empleados = consulta_empleados.offset((page - 1) * per_page).limit(per_page).all()
        clientes = consulta_clientes.offset((page - 1) * per_page).limit(per_page).all()

        # Determinar el total de páginas basado en el conjunto más grande
        total_registros = max(total_productos, total_empleados, total_clientes)
        total_pages = (total_registros + per_page - 1) // per_page

        return render_template(
            "ofertas.html",
            productos=productos,
            empleados=empleados,
            clientes=clientes,
            page=page,
            total_pages=total_pages,
            search_productos=search_productos,
            search_empleados=search_empleados,
            search_clientes=search_clientes
        )

    except Exception as e:
        print("Error en la consulta SQL:", str(e))
        flash("Se produjo un error al obtener los datos", "danger")
        return render_template("ofertas.html", productos=[], empleados=[], clientes=[], page=1, total_pages=1, search_productos="", search_empleados="", search_clientes="")

@app.route('/primevideo')
def primevideo():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 7
        search_productos = request.args.get('search_productos', '').strip()
        search_empleados = request.args.get('search_empleados', '').strip()
        search_clientes = request.args.get('search_clientes', '').strip()

        # Consultar productos, empleados y clientes de la categoría "Computadoras"
        consulta_productos = Productos.query.filter(Productos.nombre_categoria == 'Prime Video')
        consulta_empleados = Empleados.query.filter(Empleados.nombre_categoria == 'Prime Video')
        consulta_clientes = Clientes.query.filter(Clientes.nombre_categoria == 'Prime Video')

        # Si hay búsqueda en productos, filtrar por referencia o descripción
        if search_productos:
            consulta_productos = consulta_productos.filter(
                (Productos.id_producto.like(f"%{search_productos}%")) |
                (Productos.descripcion.ilike(f"%{search_productos}%"))
            )

        # Si hay búsqueda en empleados, filtrar por número de identificación o nombre
        if search_empleados:
            consulta_empleados = consulta_empleados.filter(
                (Empleados.id_empleado.like(f"%{search_empleados}%")) |
                (Empleados.nombre_empleado.ilike(f"%{search_empleados}%"))
            )

        # Si hay búsqueda en clientes, filtrar por número de identificación o nombre
        if search_clientes:
            consulta_clientes = consulta_clientes.filter(
                (Clientes.id_cliente.like(f"%{search_clientes}%")) |
                (Clientes.nombre_cliente.ilike(f"%{search_clientes}%"))
            )

        # Contar total de registros
        total_productos = consulta_productos.count()
        total_empleados = consulta_empleados.count()
        total_clientes = consulta_clientes.count()

        # Aplicar paginación
        productos = consulta_productos.offset((page - 1) * per_page).limit(per_page).all()
        empleados = consulta_empleados.offset((page - 1) * per_page).limit(per_page).all()
        clientes = consulta_clientes.offset((page - 1) * per_page).limit(per_page).all()

        # Determinar el total de páginas basado en el conjunto más grande
        total_registros = max(total_productos, total_empleados, total_clientes)
        total_pages = (total_registros + per_page - 1) // per_page

        return render_template(
            "primevideo.html",
            productos=productos,
            empleados=empleados,
            clientes=clientes,
            page=page,
            total_pages=total_pages,
            search_productos=search_productos,
            search_empleados=search_empleados,
            search_clientes=search_clientes
        )

    except Exception as e:
        print("Error en la consulta SQL:", str(e))
        flash("Se produjo un error al obtener los datos", "danger")
        return render_template("primevideo.html", productos=[], empleados=[], clientes=[], page=1, total_pages=1, search_productos="", search_empleados="", search_clientes="")

@app.route('/salud')
def salud():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 7
        search_productos = request.args.get('search_productos', '').strip()
        search_empleados = request.args.get('search_empleados', '').strip()
        search_clientes = request.args.get('search_clientes', '').strip()

        # Consultar productos, empleados y clientes de la categoría "Computadoras"
        consulta_productos = Productos.query.filter(Productos.nombre_categoria == 'Salud y productos para el hogar')
        consulta_empleados = Empleados.query.filter(Empleados.nombre_categoria == 'Salud y productos para el hogar')
        consulta_clientes = Clientes.query.filter(Clientes.nombre_categoria == 'Salud y productos para el hogar')

        # Si hay búsqueda en productos, filtrar por referencia o descripción
        if search_productos:
            consulta_productos = consulta_productos.filter(
                (Productos.id_producto.like(f"%{search_productos}%")) |
                (Productos.descripcion.ilike(f"%{search_productos}%"))
            )

        # Si hay búsqueda en empleados, filtrar por número de identificación o nombre
        if search_empleados:
            consulta_empleados = consulta_empleados.filter(
                (Empleados.id_empleado.like(f"%{search_empleados}%")) |
                (Empleados.nombre_empleado.ilike(f"%{search_empleados}%"))
            )

        # Si hay búsqueda en clientes, filtrar por número de identificación o nombre
        if search_clientes:
            consulta_clientes = consulta_clientes.filter(
                (Clientes.id_cliente.like(f"%{search_clientes}%")) |
                (Clientes.nombre_cliente.ilike(f"%{search_clientes}%"))
            )

        # Contar total de registros
        total_productos = consulta_productos.count()
        total_empleados = consulta_empleados.count()
        total_clientes = consulta_clientes.count()

        # Aplicar paginación
        productos = consulta_productos.offset((page - 1) * per_page).limit(per_page).all()
        empleados = consulta_empleados.offset((page - 1) * per_page).limit(per_page).all()
        clientes = consulta_clientes.offset((page - 1) * per_page).limit(per_page).all()

        # Determinar el total de páginas basado en el conjunto más grande
        total_registros = max(total_productos, total_empleados, total_clientes)
        total_pages = (total_registros + per_page - 1) // per_page

        return render_template(
            "salud.html",
            productos=productos,
            empleados=empleados,
            clientes=clientes,
            page=page,
            total_pages=total_pages,
            search_productos=search_productos,
            search_empleados=search_empleados,
            search_clientes=search_clientes
        )

    except Exception as e:
        print("Error en la consulta SQL:", str(e))
        flash("Se produjo un error al obtener los datos", "danger")
        return render_template("salud.html", productos=[], empleados=[], clientes=[], page=1, total_pages=1, search_productos="", search_empleados="", search_clientes="")

@app.route('/software')
def software():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 7
        search_productos = request.args.get('search_productos', '').strip()
        search_empleados = request.args.get('search_empleados', '').strip()
        search_clientes = request.args.get('search_clientes', '').strip()

        # Consultar productos, empleados y clientes de la categoría "Computadoras"
        consulta_productos = Productos.query.filter(Productos.nombre_categoria == 'Software')
        consulta_empleados = Empleados.query.filter(Empleados.nombre_categoria == 'Software')
        consulta_clientes = Clientes.query.filter(Clientes.nombre_categoria == 'Software')

        # Si hay búsqueda en productos, filtrar por referencia o descripción
        if search_productos:
            consulta_productos = consulta_productos.filter(
                (Productos.id_producto.like(f"%{search_productos}%")) |
                (Productos.descripcion.ilike(f"%{search_productos}%"))
            )

        # Si hay búsqueda en empleados, filtrar por número de identificación o nombre
        if search_empleados:
            consulta_empleados = consulta_empleados.filter(
                (Empleados.id_empleado.like(f"%{search_empleados}%")) |
                (Empleados.nombre_empleado.ilike(f"%{search_empleados}%"))
            )

        # Si hay búsqueda en clientes, filtrar por número de identificación o nombre
        if search_clientes:
            consulta_clientes = consulta_clientes.filter(
                (Clientes.id_cliente.like(f"%{search_clientes}%")) |
                (Clientes.nombre_cliente.ilike(f"%{search_clientes}%"))
            )

        # Contar total de registros
        total_productos = consulta_productos.count()
        total_empleados = consulta_empleados.count()
        total_clientes = consulta_clientes.count()

        # Aplicar paginación
        productos = consulta_productos.offset((page - 1) * per_page).limit(per_page).all()
        empleados = consulta_empleados.offset((page - 1) * per_page).limit(per_page).all()
        clientes = consulta_clientes.offset((page - 1) * per_page).limit(per_page).all()

        # Determinar el total de páginas basado en el conjunto más grande
        total_registros = max(total_productos, total_empleados, total_clientes)
        total_pages = (total_registros + per_page - 1) // per_page

        return render_template(
            "software.html",
            productos=productos,
            empleados=empleados,
            clientes=clientes,
            page=page,
            total_pages=total_pages,
            search_productos=search_productos,
            search_empleados=search_empleados,
            search_clientes=search_clientes
        )

    except Exception as e:
        print("Error en la consulta SQL:", str(e))
        flash("Se produjo un error al obtener los datos", "danger")
        return render_template("software.html", productos=[], empleados=[], clientes=[], page=1, total_pages=1, search_productos="", search_empleados="", search_clientes="")

@app.route('/kindle')
def kindle():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 7
        search_productos = request.args.get('search_productos', '').strip()
        search_empleados = request.args.get('search_empleados', '').strip()
        search_clientes = request.args.get('search_clientes', '').strip()

        # Consultar productos, empleados y clientes de la categoría "Computadoras"
        consulta_productos = Productos.query.filter(Productos.nombre_categoria == 'Tienda Kindle')
        consulta_empleados = Empleados.query.filter(Empleados.nombre_categoria == 'Tienda Kindle')
        consulta_clientes = Clientes.query.filter(Clientes.nombre_categoria == 'Tienda Kindle')

        # Si hay búsqueda en productos, filtrar por referencia o descripción
        if search_productos:
            consulta_productos = consulta_productos.filter(
                (Productos.id_producto.like(f"%{search_productos}%")) |
                (Productos.descripcion.ilike(f"%{search_productos}%"))
            )

        # Si hay búsqueda en empleados, filtrar por número de identificación o nombre
        if search_empleados:
            consulta_empleados = consulta_empleados.filter(
                (Empleados.id_empleado.like(f"%{search_empleados}%")) |
                (Empleados.nombre_empleado.ilike(f"%{search_empleados}%"))
            )

        # Si hay búsqueda en clientes, filtrar por número de identificación o nombre
        if search_clientes:
            consulta_clientes = consulta_clientes.filter(
                (Clientes.id_cliente.like(f"%{search_clientes}%")) |
                (Clientes.nombre_cliente.ilike(f"%{search_clientes}%"))
            )

        # Contar total de registros
        total_productos = consulta_productos.count()
        total_empleados = consulta_empleados.count()
        total_clientes = consulta_clientes.count()

        # Aplicar paginación
        productos = consulta_productos.offset((page - 1) * per_page).limit(per_page).all()
        empleados = consulta_empleados.offset((page - 1) * per_page).limit(per_page).all()
        clientes = consulta_clientes.offset((page - 1) * per_page).limit(per_page).all()

        # Determinar el total de páginas basado en el conjunto más grande
        total_registros = max(total_productos, total_empleados, total_clientes)
        total_pages = (total_registros + per_page - 1) // per_page

        return render_template(
            "kindle.html",
            productos=productos,
            empleados=empleados,
            clientes=clientes,
            page=page,
            total_pages=total_pages,
            search_productos=search_productos,
            search_empleados=search_empleados,
            search_clientes=search_clientes
        )

    except Exception as e:
        print("Error en la consulta SQL:", str(e))
        flash("Se produjo un error al obtener los datos", "danger")
        return render_template("kindle.html", productos=[], empleados=[], clientes=[], page=1, total_pages=1, search_productos="", search_empleados="", search_clientes="")

@app.route('/videojuegos')
def videojuegos():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 7
        search_productos = request.args.get('search_productos', '').strip()
        search_empleados = request.args.get('search_empleados', '').strip()
        search_clientes = request.args.get('search_clientes', '').strip()

        # Consultar productos, empleados y clientes de la categoría "Computadoras"
        consulta_productos = Productos.query.filter(Productos.nombre_categoria == 'Videojuegos')
        consulta_empleados = Empleados.query.filter(Empleados.nombre_categoria == 'Videojuegos')
        consulta_clientes = Clientes.query.filter(Clientes.nombre_categoria == 'Videojuegos')

        # Si hay búsqueda en productos, filtrar por referencia o descripción
        if search_productos:
            consulta_productos = consulta_productos.filter(
                (Productos.id_producto.like(f"%{search_productos}%")) |
                (Productos.descripcion.ilike(f"%{search_productos}%"))
            )

        # Si hay búsqueda en empleados, filtrar por número de identificación o nombre
        if search_empleados:
            consulta_empleados = consulta_empleados.filter(
                (Empleados.id_empleado.like(f"%{search_empleados}%")) |
                (Empleados.nombre_empleado.ilike(f"%{search_empleados}%"))
            )

        # Si hay búsqueda en clientes, filtrar por número de identificación o nombre
        if search_clientes:
            consulta_clientes = consulta_clientes.filter(
                (Clientes.id_cliente.like(f"%{search_clientes}%")) |
                (Clientes.nombre_cliente.ilike(f"%{search_clientes}%"))
            )

        # Contar total de registros
        total_productos = consulta_productos.count()
        total_empleados = consulta_empleados.count()
        total_clientes = consulta_clientes.count()

        # Aplicar paginación
        productos = consulta_productos.offset((page - 1) * per_page).limit(per_page).all()
        empleados = consulta_empleados.offset((page - 1) * per_page).limit(per_page).all()
        clientes = consulta_clientes.offset((page - 1) * per_page).limit(per_page).all()

        # Determinar el total de páginas basado en el conjunto más grande
        total_registros = max(total_productos, total_empleados, total_clientes)
        total_pages = (total_registros + per_page - 1) // per_page

        return render_template(
            "videojuegos.html",
            productos=productos,
            empleados=empleados,
            clientes=clientes,
            page=page,
            total_pages=total_pages,
            search_productos=search_productos,
            search_empleados=search_empleados,
            search_clientes=search_clientes
        )

    except Exception as e:
        print("Error en la consulta SQL:", str(e))
        flash("Se produjo un error al obtener los datos", "danger")
        return render_template("videojuegos.html", productos=[], empleados=[], clientes=[], page=1, total_pages=1, search_productos="", search_empleados="", search_clientes="")



@app.route('/oficinas')
def oficinas():
    return render_template('oficinas.html')

@app.route("/send_email", methods=["POST"])
def send_email():
    # Obtener los datos del formulario
    name = request.form["name"]
    email = request.form["email"]
    message = request.form["message"]

    msg = Message(
        subject=f"Nuevo mensaje de {name}",
        sender="amazonincsoft@gmail.com@gmail.com",    # Correo de donde se envía el mensaje
        recipients=["juanhernandezsilva25@gmail.com"],  # Correo de destino
        reply_to=email  # Para responder al usuario
    )
    msg.body = f"Nombre: {name}\nCorreo: {email}\n\nMensaje:\n{message}"

    try:
        mail.send(msg)
        flash("Correo enviado correctamente.", "success")
    except Exception as e:
        flash(f"Error al enviar el correo: {str(e)}", "danger")

    return redirect("/")

if __name__ == '__main__':
    app.run(debug=True)