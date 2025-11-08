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
    app.config['UPLOAD_FOLDER'] = './uploads'
    app.config['ALLOWED_EXTENSIONS'] = {'xlsx', 'xls'}

    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower(
               ) in app.config['ALLOWED_EXTENSIONS']

    def pluralizar(tipo):
        """
        Convierte el nombre del tipo singular al plural correcto para las rutas
        """
        plurales = {
            "producto": "productos",
            "categoria": "categorias",
            "proveedor": "proveedores",
            "imagen": "imagenes"
        }
        return plurales.get(tipo, tipo + "s")

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
                
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                try:
                    workbook = openpyxl.load_workbook(filepath)
                    sheet = workbook.active

                    header = [cell.value for cell in sheet[1]]

                    # Mapeo de columnas a campos del modelo Producto
                    col_mapping = {
                        'proveedor': ['Proveedor', 'proveedor', 'prov', 'Prov'],
                        'art': ['Artículo', 'Articulo', 'artículo', 'articulo', 'art', 'Art'],
                        'cod': ['Código', 'Codigo', 'código', 'codigo', 'cod', 'Cod'],
                        'desc': ['Descripción', 'Descripcion', 'descripción', 'descripcion', 'desc', 'Desc'],
                        'cat': ['Categoría', 'Categoria', 'categoría', 'categoria', 'cat', 'Cat'],
                        'img': ['Imagen', 'imagen', 'img', 'Img']
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
                    errores = []
                    
                    # Buscar o crear categoría por defecto "Sin categoría"
                    categoria_default = Categoria.obtener("name", "Sin categoría")
                    if not categoria_default:
                        # Constructor Categoria SIN id: (name, unit)
                        nueva_categoria = Categoria(
                            "Sin categoría",  # name
                            None              # unit
                        )
                        cat_default_id = nueva_categoria.guardar_db()
                        if not cat_default_id or not isinstance(cat_default_id, int):
                            flash('Error: No se pudo crear la categoría por defecto', 'error')
                            return redirect(request.url)
                    else:
                        cat_default_id = categoria_default.id
                    
                    for row_num, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
                        try:
                            data = dict(zip(header, row))

                            # ========== PROVEEDOR (buscar por código) ==========
                            prov_codigo = None
                            for col_name in col_mapping["proveedor"]:
                                if col_name in data and data[col_name] is not None and str(data[col_name]).strip():
                                    prov_codigo = str(data[col_name]).strip()
                                    break

                            # Validar que haya proveedor
                            if not prov_codigo:
                                errores.append(f"Fila {row_num}: Falta el código del proveedor")
                                continue

                            # Buscar proveedor por código (campo 'cod')
                            proveedor_obj = Proveedor.obtener("cod", prov_codigo)
                            if not proveedor_obj:
                                # Si no existe, crear nuevo proveedor con ese código
                                nuevo_proveedor = Proveedor(
                                    prov_codigo,  # cod
                                    f"Proveedor {prov_codigo}",  # name (generado automáticamente)
                                    None          # obs
                                )
                                prov_id = nuevo_proveedor.guardar_db()
                                
                                if not prov_id or not isinstance(prov_id, int):
                                    errores.append(f"Fila {row_num}: No se pudo crear el proveedor con código '{prov_codigo}'")
                                    continue
                                
                                app.logger.info(f"Proveedor creado: código={prov_codigo}, id={prov_id}")
                            else:
                                prov_id = proveedor_obj.id

                            # ========== ARTÍCULO (opcional) ==========
                            art = None
                            for col_name in col_mapping['art']:
                                if col_name in data and data[col_name] is not None and str(data[col_name]).strip():
                                    art = str(data[col_name]).strip()
                                    break

                            # ========== CÓDIGO (opcional) ==========
                            cod = None
                            for col_name in col_mapping['cod']:
                                if col_name in data and data[col_name] is not None and str(data[col_name]).strip():
                                    cod = str(data[col_name]).strip()
                                    break

                            # ========== DESCRIPCIÓN (OBLIGATORIO) ==========
                            desc = None
                            for col_name in col_mapping['desc']:
                                if col_name in data and data[col_name] is not None:
                                    desc = str(data[col_name]).strip()
                                    if desc:  # Solo si no está vacío después del strip
                                        break
                                    desc = None  # Resetear si estaba vacío

                            # Validar que haya descripción (campo obligatorio)
                            if not desc:
                                errores.append(f"Fila {row_num}: Falta la descripción del producto (campo obligatorio)")
                                continue

                            # Generar título automáticamente: primeras 3 palabras de la descripción
                            tit = ' '.join(desc.split()[:3])

                            # ========== CATEGORÍA (buscar por nombre) ==========
                            cat_id = cat_default_id  # Por defecto usar "Sin categoría"
                            cat_nombre = None
                            for col_name in col_mapping['cat']:
                                if col_name in data and data[col_name] is not None and str(data[col_name]).strip():
                                    cat_nombre = str(data[col_name]).strip()
                                    break
                            
                            if cat_nombre:
                                # Buscar categoría por nombre
                                categoria_obj = Categoria.obtener("name", cat_nombre)
                                if categoria_obj:
                                    cat_id = categoria_obj.id
                                else:
                                    # Si no existe, crear nueva categoría
                                    nueva_cat = Categoria(
                                        cat_nombre,  # name
                                        None         # unit
                                    )
                                    cat_id = nueva_cat.guardar_db()
                                    if cat_id and isinstance(cat_id, int):
                                        app.logger.info(f"Categoría creada: nombre={cat_nombre}, id={cat_id}")
                                    else:
                                        errores.append(f"Fila {row_num}: No se pudo crear la categoría '{cat_nombre}', usando categoría por defecto")
                                        cat_id = cat_default_id

                            # ========== IMAGEN (buscar por URL) ==========
                            img_id = None
                            img_url = None
                            for col_name in col_mapping['img']:
                                if col_name in data and data[col_name] is not None and str(data[col_name]).strip():
                                    img_url = str(data[col_name]).strip()
                                    break
                            
                            if img_url:
                                # Buscar imagen por URL
                                imagen_obj = Imagen.obtener("url_img", img_url)
                                if imagen_obj:
                                    img_id = imagen_obj.id
                                else:
                                    # Si no existe, crear nueva imagen
                                    nueva_img = Imagen(
                                        img_url,  # url_img
                                        None      # txt_alt
                                    )
                                    img_id = nueva_img.guardar_db()
                                    if img_id and isinstance(img_id, int):
                                        app.logger.info(f"Imagen creada: url={img_url}, id={img_id}")
                                    else:
                                        errores.append(f"Fila {row_num}: No se pudo crear la imagen '{img_url}'")
                                        img_id = None

                            # DEBUG: Verificar valores antes de crear el producto
                            app.logger.debug(f"Fila {row_num} - Creando producto: art={art}, cod={cod}, tit={tit}, cat_id={cat_id}, img_id={img_id}, prov_id={prov_id}")
                            
                            # CORRECCIÓN: Crear producto SIN el id (el método crear() lo omite automáticamente)
                            # Constructor: Producto(art, cod, tit, desc, cat_id, img_id, prov_id, rating)
                            # NO incluir 'id' como primer parámetro cuando de_bbdd=False
                            nuevo_producto = Producto(
                                art,      # art
                                cod,      # cod
                                tit,      # tit (título)
                                desc,     # desc (descripción)
                                cat_id,   # cat_id (categoría)
                                img_id,   # img_id (imagen)
                                prov_id,  # prov_id (proveedor)
                                0         # rating (valor inicial)
                            )
                            
                            # DEBUG: Verificar atributos del objeto creado
                            app.logger.debug(f"Fila {row_num} - Objeto producto creado correctamente")
                            
                            producto_id = nuevo_producto.guardar_db()
                            
                            if not producto_id or not isinstance(producto_id, int):
                                errores.append(f"Fila {row_num}: No se obtuvo ID al guardar producto '{tit}'")
                                continue

                            # Verificar que el producto existe en la BD
                            verificado = Producto.obtener('id', producto_id)
                            if not verificado:
                                errores.append(f"Fila {row_num}: Producto con ID {producto_id} no encontrado tras guardar")
                                continue

                            productos_importados += 1
                            productos_confirmados.append(producto_id)
                            
                        except Exception as e:
                            errores.append(f"Fila {row_num}: Error inesperado - {str(e)}")
                            continue

                    # Mostrar resultados
                    app.logger.info(
                        f"Productos procesados: {len(productos_confirmados)} confirmados. IDs: {productos_confirmados}")
                    
                    if errores:
                        # Mostrar solo los primeros 5 errores
                        for error in errores[:5]:
                            flash(error, 'warning')
                        if len(errores) > 5:
                            flash(f'... y {len(errores) - 5} errores más', 'warning')
                    
                    if productos_importados > 0:
                        flash(f'Se importaron {productos_importados} productos correctamente.', 'success')
                        return redirect(url_for('productos', mensaje=f'Se importaron {productos_importados} productos correctamente.'))
                    else:
                        flash('No se pudo importar ningún producto. Revisa los errores.', 'error')
                        return redirect(request.url)
                        
                except Exception as e:
                    app.logger.error(f'Error al procesar archivo Excel: {str(e)}')
                    flash(f'Error al procesar el archivo Excel: {e}', 'error')
                    return redirect(request.url)
            else:
                flash('Tipo de archivo no permitido. Use .xlsx o .xls', 'error')
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
            categoria = Categoria.obtener('id', producto.cat_id)
            producto.cat_id = categoria.name if categoria else None
            # Obtener el código del proveedor en lugar del ID
            proveedor = Proveedor.obtener('id', producto.prov_id)
            producto.prov_id = proveedor.cod if proveedor else None
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
        datos = tablas[tipo].obtener('id', id)
        
        contexto = {'datos': datos, 'tipo': tipo}
        
        if tipo == 'producto':
            contexto['categorias'] = Categoria.obtener()
            contexto['proveedores'] = Proveedor.obtener()
            contexto['imagenes'] = Imagen.obtener()
        
        return render_template("./modelos/crud/detalle.html", **contexto)

    @app.route('/<id>/<tipo>/eliminar')
    def eliminar(id, tipo):
        respuesta = tablas[tipo].eliminar(id)
        return redirect(url_for(pluralizar(tipo), mensaje=respuesta))

    @app.route('/<id>/<tipo>/modificar', methods=['POST'])
    def modificar(id, tipo):
        if request.method == 'POST':
            datos = dict(request.form)
            datos['id'] = id
            
            if tipo == 'producto':
                # Validar categoría
                if 'cat_id' in datos and datos['cat_id']:
                    categoria = Categoria.obtener('id', datos['cat_id'])
                    if not categoria:
                        mensaje = f'Error: La categoría con ID {datos["cat_id"]} no existe.'
                        return redirect(url_for(pluralizar(tipo), mensaje=mensaje))
                
                # Validar proveedor
                if 'prov_id' in datos and datos['prov_id']:
                    proveedor = Proveedor.obtener('id', datos['prov_id'])
                    if not proveedor:
                        mensaje = f'Error: El proveedor con ID {datos["prov_id"]} no existe.'
                        return redirect(url_for(pluralizar(tipo), mensaje=mensaje))
                
                # Validar imagen
                if 'img_id' in datos and datos['img_id']:
                    imagen = Imagen.obtener('id', datos['img_id'])
                    if not imagen:
                        mensaje = f'Error: La imagen con ID {datos["img_id"]} no existe.'
                        return redirect(url_for(pluralizar(tipo), mensaje=mensaje))
            
            resultado = tablas[tipo].modificar(datos)
            
            if resultado and resultado != 'No se pudo modificar el registro.':
                mensaje = 'Modificación exitosa.'
            else:
                mensaje = 'No se pudo modificar el registro.'
                
        return redirect(url_for(pluralizar(tipo), mensaje=mensaje))

    @app.route('/<tipo>/crear', methods=['GET', 'POST'])
    def crear(tipo):
        if request.method == 'POST':
            datos = dict(request.form).values()
            nvo_registro = tablas[tipo](*list(datos))
            resultado = nvo_registro.guardar_db()
            
            if resultado and isinstance(resultado, int):
                mensaje = f'Creación exitosa. ID: {resultado}'
            elif resultado is False:
                mensaje = 'No se pudo crear el registro.'
            else:
                mensaje = str(resultado)
                
            return redirect(url_for(pluralizar(tipo), mensaje=mensaje))
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