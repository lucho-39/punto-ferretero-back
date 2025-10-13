from flask import jsonify
from flask import render_template
from flask import request


from componentes.modelos import Categoria
from componentes.modelos import Imagen
from componentes.modelos import Proveedor
from componentes.modelos import Producto


def registrar_rutas(app):
    @app.route("/api/productos", methods=['GET'])
    def api_productos():
        productos = Producto.obtener()
        datos = [producto.__dict__ for producto in productos]

        for dato in datos:
            c_id = dato['cat_id']
            dato['categoria'] = Categoria.obtener(
                'id', c_id).__dict__['name']
            dato['proveedor'] = Proveedor.obtener(
                'id', dato['prov_id']).__dict__
            dato['imagen'] = Imagen.obtener('id', dato['img_id']).__dict__

            del dato['cat_id']
            del dato['prov_id']
            del dato['img_id']

        return jsonify(datos)
