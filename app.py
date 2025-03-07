from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, static_folder='static')
app.secret_key = '97110c78ae51a45af397be6534caef90ebb9b1dcb3380af008f90b23a5d1616bf19bc29098105da20fe'

# Configuración de SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://Root123:Root1102807012.@localhost/db_amazon'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

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
    estado = db.Column(db.Integer)
    categorias = db.relationship('Categorias', backref=db.backref('cliente', lazy=True))

class Categorias(db.Model):
    __tablename__ = 'categorias'
    nombre_categoria = db.Column(db.String(20), primary_key=True)
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
    rol_seleccionado = request.form.get('rol')  # Obtener el rol seleccionado en el formulario

    user = Usuario.query.filter_by(correo=correo, contraseña=contraseña).first()

    if user:
        if user.rol != rol_seleccionado:  # Verificar que el rol seleccionado coincida con el de la BD
            flash('No tienes permisos para iniciar sesión con este rol.', 'error')
            return redirect(url_for('login'))
        
        session['usuario_id'] = user.id
        session['nombre'] = user.nombre
        flash('Inicio de sesión exitoso', 'success')
        return redirect(url_for('dashboard'))
    
    flash('Correo o contraseña incorrectos', 'error')
    return redirect(url_for('login'))


@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register_post():
    nombre = request.form.get('nombre')
    correo = request.form.get('correo')
    contraseña = request.form.get('password')  # Aquí cambia de 'contraseña' a 'password'
    rol = request.form.get('rol')

    # Verificar si el usuario ya existe
    existe_usuario = Usuario.query.filter_by(correo=correo).first()
    if existe_usuario:
        flash("El correo electrónico ya está registrado. Usa otro.", "error")
        return redirect(url_for('register'))

    try:
        nuevo_usuario = Usuario(nombre=nombre, correo=correo, contraseña=contraseña, rol=rol)
        db.session.add(nuevo_usuario)
        db.session.commit()
        flash("Registro exitoso", "success")
        return redirect(url_for('login'))
    except Exception as e:
        db.session.rollback()
        flash("Se produjo un error al registrar el usuario", "error")

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
    return render_template('dashboard.html')

@app.route('/categorias')
def categorias():
    return render_template('categorias.html')

@app.route('/nosotros')
def nosotros():
    return render_template('nosotros.html')

@app.route('/sucursal')
def sucursal():
    sucursal=Sucursales.query.all()
    return render_template("sucursal.html",sucursal=sucursal)

@app.route('/empleado')
def empleado():
    empleados = Empleados.query.all()
    return render_template('empleado.html', empleado=empleados)

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

@app.route('/cliente')
def  cliente():
    clientes=Clientes.query.all()
    return render_template("cliente.html", clientes = clientes)


from werkzeug.security import generate_password_hash

@app.route('/nuevo_cliente', methods=['GET', 'POST'])
def nuevo_cliente():
    categorias = Categorias.query.distinct(Categorias.nombre_categoria).all()

    if request.method == "POST":
        id_cliente = request.form['id']
        nombre_cliente = request.form['nombre_cliente']
        categoria_seleccionada = request.form['nombre_categoria']

        try:
            # Verificar si el ID ya existe en la tabla de clientes
            existe_cliente = Clientes.query.filter_by(id_cliente=id_cliente).first()
            if existe_cliente:
                flash("El ID del cliente ya existe. Elija uno diferente.", "danger")
                return redirect(url_for('nuevo_cliente'))
            
            # Crear nuevo cliente
            nuevo_cliente = Clientes(
                id_cliente=id_cliente, 
                nombre_cliente=nombre_cliente, 
                nombre_categoria=categoria_seleccionada, 
                estado="Activo"
            )
            db.session.add(nuevo_cliente)

            # Solo crear usuario si el cliente debe tener acceso al sistema
            if categoria_seleccionada.lower() == "cliente":  
                nuevo_usuario = Usuario(
                    nombre=nombre_cliente,  # Se asigna el nombre correctamente
                    correo=f"{id_cliente}@correo.com",
                    contraseña=generate_password_hash(id_cliente),  # Contraseña encriptada
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
    clientes=Clientes.query.get(id_cliente)
    nombre_categoria = Categorias.query.distinct(Categorias.nombre_categoria).all()

    if request.method == "POST":
        clientes.nombre_cliente = request.form['nombre_cliente']
        clientes.nombre_categoria = request.form['nombre_categoria']
        clientes.estado = request.form['estado'] #---
        try:
            db.session.commit()
            flash("Perfil actualizado exitosamente!", "success")
            return redirect('/cliente')
        except Exception as e:
            db.session.rollback()  
            flash("Se produjo un error durante la actualización", "danger")

    return render_template('actualizar_cliente.html',clientes=clientes, categorias=nombre_categoria)

@app.route('/eliminar_cliente/<string:id_cliente>', methods=['GET', 'POST'])
def eliminar_cliente(id_cliente):
    clientes = Clientes.query.get(id_cliente)
    usuarios = Usuario.query.filter_by(correo=id_cliente).first() 
    if clientes:
        db.session.delete(clientes)
        db.session.delete(usuarios)
        db.session.commit()
        flash("Cliente eliminado !", "warning")
        return redirect('/cliente')

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
        # Consultar clientes de la categoría "Arte y artesanías"
        clientes = db.session.query(Clientes.id_cliente, Clientes.nombre_cliente).filter(
            Clientes.nombre_categoria == 'Arte y artesanías'
        ).all()

        # Consultar productos de la categoría "Arte y artesanías"
        productos = db.session.query(Productos.id_producto, Productos.descripcion, Productos.precio).filter(
            Productos.nombre_categoria == 'Arte y artesanías'
        ).all()

        # Consultar empleados de la categoría "Arte y artesanías"
        empleados = db.session.query(Empleados.id_empleado, Empleados.nombre_empleado).filter(
            Empleados.nombre_categoria == 'Arte y artesanías'
        ).all()

        print("Clientes encontrados:", clientes)  # Depuración en consola

    except Exception as e:
        print("Error en la consulta SQL:", str(e))  # Depuración en consola
        flash("Se produjo un error al obtener los datos", "danger")
        clientes, productos, empleados = [], [], []

    return render_template("arte.html", cliente=clientes, producto=productos, empleado=empleados)

@app.route('/automotriz')
def automotriz():
    try:
        # Consultar clientes de la categoría "Arte y artesanías"
        clientes = db.session.query(Clientes.id_cliente, Clientes.nombre_cliente).filter(
            Clientes.nombre_categoria == 'Automotriz'
        ).all()

        # Consultar productos de la categoría "Arte y artesanías"
        productos = db.session.query(Productos.id_producto, Productos.descripcion, Productos.precio).filter(
            Productos.nombre_categoria == 'Automotriz'
        ).all()

        # Consultar empleados de la categoría "Arte y artesanías"
        empleados = db.session.query(Empleados.id_empleado, Empleados.nombre_empleado).filter(
            Empleados.nombre_categoria == 'Automotriz'
        ).all()

        print("Clientes encontrados:", clientes)  # Depuración en consola

    except Exception as e:
        print("Error en la consulta SQL:", str(e))  # Depuración en consola
        flash("Se produjo un error al obtener los datos", "danger")
        clientes, productos, empleados = [], [], []

    return render_template("automotriz.html", cliente=clientes, producto=productos, empleado=empleados)

@app.route('/computadoras')
def computadoras():
    try:
        # Consultar clientes de la categoría "Arte y artesanías"
        clientes = db.session.query(Clientes.id_cliente, Clientes.nombre_cliente).filter(
            Clientes.nombre_categoria == 'Computadoras'
        ).all()

        # Consultar productos de la categoría "Arte y artesanías"
        productos = db.session.query(Productos.id_producto, Productos.descripcion, Productos.precio).filter(
            Productos.nombre_categoria == 'Computadoras'
        ).all()

        # Consultar empleados de la categoría "Arte y artesanías"
        empleados = db.session.query(Empleados.id_empleado, Empleados.nombre_empleado).filter(
            Empleados.nombre_categoria == 'Computadoras'
        ).all()

        print("Clientes encontrados:", clientes)  # Depuración en consola

    except Exception as e:
        print("Error en la consulta SQL:", str(e))  # Depuración en consola
        flash("Se produjo un error al obtener los datos", "danger")
        clientes, productos, empleados = [], [], []

    return render_template("computadoras.html", cliente=clientes, producto=productos, empleado=empleados)

@app.route('/oficinas')
def oficinas():
    return render_template('oficinas.html')

if __name__ == '__main__':
    app.run(debug=True)