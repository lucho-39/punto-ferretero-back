from flask import render_template
from flask import redirect
from flask import url_for
from flask import request

from componentes.modelos import Categoria
from componentes.modelos import Imagen
from componentes.modelos import Proveedor
from componentes.modelos import Producto


def registrar_rutas_web(app):
    # ****** Inicio ******
    @app.route('/')
    def inicio():
        return render_template('inicio.html')

    # ****** Modelos ******
    @app.route('/productos')
    @app.route('/productos/<mensaje>')
    def productos(mensaje=None):
        productos = Producto.obtener()
        for producto in productos:
            producto.cat_id = Categoria.obtener('id', producto.cat_id)
            proveedor = Proveedor.obtener('id', producto.prov_id)
            p_nom = proveedor.name
            producto.proveedor = f"{p_nom}"
        return render_template('./modelos/productos.html', productos=productos, mensaje=mensaje)

    # ****** Detalle de registros y CRUD ******
    tablas = {
        "producto": Producto,
        "categoria": Categoria,
        "proveedor": Proveedor,
        "imagen": Imagen
    }

    @app.route('/<id>/<tipo>/detalle')
    def ver_detalle(id, tipo):
        return render_template("./modelos/crud/detalle.html",
                               datos=tablas[tipo].obtener('id', id),
                               tipo=tipo)

    @app.route('/<id>/<tipo>/eliminar')
    def eliminar(id, tipo):
        respuesta = tablas[tipo].eliminar(id)
        return redirect(url_for(tipo + "s", mensaje=respuesta))

    @app.route('/<id>/<tipo>/modificar', methods=['POST'])
    def modificar(id, tipo):
        if request.method == 'POST':
            datos = dict(request.form)
            datos['id'] = id
            respuesta = tablas[tipo].modificar(datos)
        return redirect(url_for(tipo + "s", mensaje=respuesta))

    @app.route('/<tipo>/crear', methods=['GET', 'POST'])
    def crear(tipo):
        if request.method == 'POST':
            datos = dict(request.form).values()
            nvo_registro = tablas[tipo](*list(datos))
            respuesta = nvo_registro.guardar_db()
            return redirect(url_for(tipo + "s", mensaje=respuesta))
        modelo = tablas[tipo].campos[1:]
        return render_template('./modelos/crud/crear.html', tipo=tipo, modelo=modelo)

    # ****** API ******
    @app.route('/api')
    def api_docu():
        return render_template('./api/docu.html')

    # ****** Manejo de URL incorrecta ******
    @app.errorhandler(404)
    def lanzar_error(error):
        return render_template("./404.html", ctx=error)
