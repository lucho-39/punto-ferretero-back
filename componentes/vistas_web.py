from flask import render_template
from flask import redirect
from flask import url_for
from flask import request, flash
import openpyxl
from werkzeug.utils import secure_filename
import os

from componentes.modelos import Categoria
from componentes.modelos import Imagen
from componentes.modelos import Proveedor
from componentes.modelos import Producto


def registrar_rutas_web(app):
    app.config['UPLOAD_FOLDER'] = '/'
    app.config['ALLOWED_EXTENSIONS'] = {'xlsx', 'xls'}

    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower(
               ) in app.config['ALLOWED_EXTENSIONS']

    @app.route('/subir', methods=['GET', 'POST'])
    def subir_productos():
        if request.method == 'POST':
            if 'file' not in request.files:
                flash('No se ha seleccionado ningún archivo')
                return redirect(request.url)
            file = request.files['file']
            if file.filename == '':
                flash('No se ha seleccionado ningún archivo')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                try:
                    workbook = openpyxl.load_workbook(filepath)
                    sheet = workbook.active

                    header = [cell.value for cell in sheet[1]]

                    # Mapeo de columnas a campos del modelo Producto
                    col_mapping = {
                        'proveedor': ['Proveedor', 'proveedor', 'prov'],
                        'art': ['Articulo', 'articulo', 'art'],
                        'cod': ['Codigo', 'codigo', 'cod'],
                        'desc': ['Descripcion', 'descripcion', 'desc'],
                    }

                    # Encontrar los índices de las columnas en el archivo Excel
                    col_indices = {}
                    for field, possible_names in col_mapping.items():
                        for name in possible_names:
                            if name in header:
                                col_indices[field] = header.index(name)
                                break

                    productos_importados = 0
                    productos_confirmados = []
                    for row in sheet.iter_rows(min_row=2, values_only=True):
                        data = dict(zip(header, row))

                        prov_name = data.get(col_mapping["proveedor"][0]) or \
                            data.get(col_mapping["proveedor"][1]) or \
                            data.get(col_mapping["proveedor"][2])

                        proveedor_obj = Proveedor.obtener("name", prov_name)
                        if not proveedor_obj:
                            nuevo_proveedor = Proveedor(
                                None, None, prov_name, None)
                            prov_id = nuevo_proveedor.guardar_db()
                            # validar retorno: puede ser id numérico o un mensaje de error
                            if isinstance(prov_id, str):
                                if prov_id.isdigit():
                                    prov_id = int(prov_id)
                                else:
                                    app.logger.error(
                                        f"Error al crear proveedor '{prov_name}': {prov_id}")
                                    continue
                            if not prov_id:
                                app.logger.error(
                                    f"No se pudo crear el proveedor: {prov_name}")
                                continue
                        else:
                            prov_id = proveedor_obj.id

                        art = data.get(col_mapping['art'][0]) or \
                            data.get(col_mapping['art'][1]) or \
                            data.get(col_mapping['art'][2])

                        cod = data.get(col_mapping['cod'][0]) or \
                            data.get(col_mapping['cod'][1]) or \
                            data.get(col_mapping['cod'][2])

                        desc = data.get(col_mapping['desc'][0]) or \
                            data.get(col_mapping['desc'][1]) or \
                            data.get(col_mapping['desc'][2])

                        tit = ' '.join(str(desc).split(
                            ' ')[:3]) if desc else None

                        # Crear un nuevo producto
                        nuevo_producto = Producto(
                            None, art, cod, tit, desc, None, None, prov_id, None)
                        producto_id = nuevo_producto.guardar_db()
                        app.logger.debug(
                            f"Intento guardar producto '{tit}' -> id retornado: {producto_id}")
                        # validar retorno: id numérico o mensaje de error
                        if isinstance(producto_id, str):
                            if producto_id.isdigit():
                                producto_id = int(producto_id)
                            else:
                                app.logger.error(
                                    f"Error al crear producto '{tit}' (cod:{cod}): {producto_id}")
                                continue
                        if not producto_id:
                            app.logger.error(
                                f"No se obtuvo ID al guardar producto: {tit} (cod: {cod})")
                            continue

                        # Verificar que el producto existe en la BD consultándolo
                        verificado = Producto.obtener('id', producto_id)
                        if not verificado:
                            app.logger.error(
                                f"Producto con id {producto_id} no encontrado tras guardar.")
                            continue

                        productos_importados += 1
                        productos_confirmados.append(producto_id)

                    app.logger.info(
                        f"Productos procesados: {len(productos_confirmados)} confirmados. IDs: {productos_confirmados}")
                    flash(
                        f'Se importaron {productos_importados} productos correctamente.')
                    return redirect(url_for('productos', mensaje=f'Se importaron {productos_importados} productos correctamente.'))
                except Exception as e:
                    flash(f'Error al procesar el archivo Excel: {e}')
                    return redirect(request.url)
            else:
                flash('Tipo de archivo no permitido')
                return redirect(request.url)
        return render_template('subir_productos.html')

    # ****** Inicio ******
    @app.route('/')
    def inicio():
        return render_template('inicio.html')

    # ****** Modelos ******
    @app.route('/categorias')
    @app.route('/categorias/<mensaje>')
    def categorias(mensaje=None):
        categorias = Categoria.obtener()
        return render_template('./modelos/categorias.html', categorias=categorias, mensaje=mensaje)
    
    @app.route('/imagenes')
    @app.route('/imagenes/<mensaje>')
    def imagenes(mensaje=None):
        imagenes = Imagen.obtener()
        return render_template('./modelos/imagenes.html', imagenes=imagenes, mensaje=mensaje)

    @app.route('/productos')
    @app.route('/productos/<mensaje>')
    def productos(mensaje=None):
        productos = Producto.obtener()
        for producto in productos:
            producto.cat_id = Categoria.obtener('id', producto.cat_id).name
        return render_template('./modelos/productos.html', productos=productos, mensaje=mensaje)
    
    @app.route('/proveedores')
    @app.route('/proveedores/<mensaje>')
    def proveedores(mensaje=None):
        proveedores = Proveedor.obtener()
        return render_template('./modelos/proveedores.html', proveedores=proveedores, mensaje=mensaje)

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
