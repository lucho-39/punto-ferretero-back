from flask import jsonify, request
from componentes.modelos import Categoria, Imagen, Proveedor, Producto


def registrar_rutas(app):
    
    # ========== PRODUCTOS ==========
    
    @app.route("/api/productos", methods=['GET'])
    def api_productos():
        """Obtener todos los productos con sus relaciones"""
        try:
            productos = Producto.obtener()
            datos = []
            
            for producto in productos:
                producto_dict = producto.__dict__.copy()
                
                # Obtener relaciones
                categoria = Categoria.obtener('id', producto_dict.get('cat_id'))
                proveedor = Proveedor.obtener('id', producto_dict.get('prov_id'))
                imagen = Imagen.obtener('id', producto_dict.get('img_id'))
                
                # Agregar relaciones al diccionario
                producto_dict['categoria'] = categoria.__dict__ if categoria else None
                producto_dict['proveedor'] = proveedor.__dict__ if proveedor else None
                producto_dict['imagen'] = imagen.__dict__ if imagen else None
                
                # Eliminar IDs de relaciones
                del producto_dict['cat_id']
                del producto_dict['prov_id']
                del producto_dict['img_id']
                
                datos.append(producto_dict)
            
            return jsonify(datos), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route("/api/productos/<int:id>", methods=['GET'])
    def api_producto_detalle(id):
        """Obtener un producto específico"""
        try:
            producto = Producto.obtener('id', id)
            if not producto:
                return jsonify({"error": "Producto no encontrado"}), 404
            
            producto_dict = producto.__dict__.copy()
            
            # Obtener relaciones
            categoria = Categoria.obtener('id', producto_dict.get('cat_id'))
            proveedor = Proveedor.obtener('id', producto_dict.get('prov_id'))
            imagen = Imagen.obtener('id', producto_dict.get('img_id'))
            
            producto_dict['categoria'] = categoria.__dict__ if categoria else None
            producto_dict['proveedor'] = proveedor.__dict__ if proveedor else None
            producto_dict['imagen'] = imagen.__dict__ if imagen else None
            
            del producto_dict['cat_id']
            del producto_dict['prov_id']
            del producto_dict['img_id']
            
            return jsonify(producto_dict), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route("/api/productos", methods=['POST'])
    def api_producto_crear():
        """Crear un nuevo producto"""
        try:
            datos = request.get_json()
            
            # Validar campos requeridos
            if not datos:
                return jsonify({"error": "No se enviaron datos"}), 400
            
            nuevo_producto = Producto(
                None,  # id
                datos.get('art'),
                datos.get('cod'),
                datos.get('tit'),
                datos.get('desc'),
                datos.get('cat_id'),
                datos.get('img_id'),
                datos.get('prov_id'),
                datos.get('rating')
            )
            
            resultado = nuevo_producto.guardar_db()
            
            # Validar resultado
            if isinstance(resultado, str) and not resultado.isdigit():
                return jsonify({"error": resultado}), 400
            
            producto_id = int(resultado) if isinstance(resultado, str) else resultado
            
            return jsonify({
                "mensaje": "Producto creado exitosamente",
                "id": producto_id
            }), 201
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route("/api/productos/<int:id>", methods=['PUT'])
    def api_producto_modificar(id):
        """Modificar un producto existente"""
        try:
            producto = Producto.obtener('id', id)
            if not producto:
                return jsonify({"error": "Producto no encontrado"}), 404
            
            datos = request.get_json()
            if not datos:
                return jsonify({"error": "No se enviaron datos"}), 400
            
            datos['id'] = id
            resultado = Producto.modificar(datos)
            
            return jsonify({"mensaje": resultado}), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route("/api/productos/<int:id>", methods=['DELETE'])
    def api_producto_eliminar(id):
        """Eliminar un producto"""
        try:
            producto = Producto.obtener('id', id)
            if not producto:
                return jsonify({"error": "Producto no encontrado"}), 404
            
            resultado = Producto.eliminar(id)
            
            return jsonify({"mensaje": resultado}), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    
    # ========== CATEGORÍAS ==========
    
    @app.route("/api/categorias", methods=['GET'])
    def api_categorias():
        """Obtener todas las categorías"""
        try:
            categorias = Categoria.obtener()
            datos = [categoria.__dict__ for categoria in categorias]
            return jsonify(datos), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route("/api/categorias/<int:id>", methods=['GET'])
    def api_categoria_detalle(id):
        """Obtener una categoría específica"""
        try:
            categoria = Categoria.obtener('id', id)
            if not categoria:
                return jsonify({"error": "Categoría no encontrada"}), 404
            
            return jsonify(categoria.__dict__), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route("/api/categorias", methods=['POST'])
    def api_categoria_crear():
        """Crear una nueva categoría"""
        try:
            datos = request.get_json()
            
            if not datos:
                return jsonify({"error": "No se enviaron datos"}), 400
            
            nueva_categoria = Categoria(
                None,  # id
                datos.get('name'),
                datos.get('unit')
            )
            
            resultado = nueva_categoria.guardar_db()
            
            if isinstance(resultado, str) and not resultado.isdigit():
                return jsonify({"error": resultado}), 400
            
            categoria_id = int(resultado) if isinstance(resultado, str) else resultado
            
            return jsonify({
                "mensaje": "Categoría creada exitosamente",
                "id": categoria_id
            }), 201
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route("/api/categorias/<int:id>", methods=['PUT'])
    def api_categoria_modificar(id):
        """Modificar una categoría existente"""
        try:
            categoria = Categoria.obtener('id', id)
            if not categoria:
                return jsonify({"error": "Categoría no encontrada"}), 404
            
            datos = request.get_json()
            if not datos:
                return jsonify({"error": "No se enviaron datos"}), 400
            
            datos['id'] = id
            resultado = Categoria.modificar(datos)
            
            return jsonify({"mensaje": resultado}), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route("/api/categorias/<int:id>", methods=['DELETE'])
    def api_categoria_eliminar(id):
        """Eliminar una categoría"""
        try:
            categoria = Categoria.obtener('id', id)
            if not categoria:
                return jsonify({"error": "Categoría no encontrada"}), 404
            
            resultado = Categoria.eliminar(id)
            
            return jsonify({"mensaje": resultado}), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    
    # ========== PROVEEDORES ==========
    
    @app.route("/api/proveedores", methods=['GET'])
    def api_proveedores():
        """Obtener todos los proveedores"""
        try:
            proveedores = Proveedor.obtener()
            datos = [proveedor.__dict__ for proveedor in proveedores]
            return jsonify(datos), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route("/api/proveedores/<int:id>", methods=['GET'])
    def api_proveedor_detalle(id):
        """Obtener un proveedor específico"""
        try:
            proveedor = Proveedor.obtener('id', id)
            if not proveedor:
                return jsonify({"error": "Proveedor no encontrado"}), 404
            
            return jsonify(proveedor.__dict__), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route("/api/proveedores", methods=['POST'])
    def api_proveedor_crear():
        """Crear un nuevo proveedor"""
        try:
            datos = request.get_json()
            
            if not datos:
                return jsonify({"error": "No se enviaron datos"}), 400
            
            nuevo_proveedor = Proveedor(
                None,  # id
                datos.get('cod'),
                datos.get('name'),
                datos.get('obs')
            )
            
            resultado = nuevo_proveedor.guardar_db()
            
            if isinstance(resultado, str) and not resultado.isdigit():
                return jsonify({"error": resultado}), 400
            
            proveedor_id = int(resultado) if isinstance(resultado, str) else resultado
            
            return jsonify({
                "mensaje": "Proveedor creado exitosamente",
                "id": proveedor_id
            }), 201
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route("/api/proveedores/<int:id>", methods=['PUT'])
    def api_proveedor_modificar(id):
        """Modificar un proveedor existente"""
        try:
            proveedor = Proveedor.obtener('id', id)
            if not proveedor:
                return jsonify({"error": "Proveedor no encontrado"}), 404
            
            datos = request.get_json()
            if not datos:
                return jsonify({"error": "No se enviaron datos"}), 400
            
            datos['id'] = id
            resultado = Proveedor.modificar(datos)
            
            return jsonify({"mensaje": resultado}), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route("/api/proveedores/<int:id>", methods=['DELETE'])
    def api_proveedor_eliminar(id):
        """Eliminar un proveedor"""
        try:
            proveedor = Proveedor.obtener('id', id)
            if not proveedor:
                return jsonify({"error": "Proveedor no encontrado"}), 404
            
            resultado = Proveedor.eliminar(id)
            
            return jsonify({"mensaje": resultado}), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    
    # ========== IMÁGENES ==========
    
    @app.route("/api/imagenes", methods=['GET'])
    def api_imagenes():
        """Obtener todas las imágenes"""
        try:
            imagenes = Imagen.obtener()
            datos = [imagen.__dict__ for imagen in imagenes]
            return jsonify(datos), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route("/api/imagenes/<int:id>", methods=['GET'])
    def api_imagen_detalle(id):
        """Obtener una imagen específica"""
        try:
            imagen = Imagen.obtener('id', id)
            if not imagen:
                return jsonify({"error": "Imagen no encontrada"}), 404
            
            return jsonify(imagen.__dict__), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route("/api/imagenes", methods=['POST'])
    def api_imagen_crear():
        """Crear una nueva imagen"""
        try:
            datos = request.get_json()
            
            if not datos:
                return jsonify({"error": "No se enviaron datos"}), 400
            
            nueva_imagen = Imagen(
                None,  # id
                datos.get('url_img'),
                datos.get('txt_alt')
            )
            
            resultado = nueva_imagen.guardar_db()
            
            if isinstance(resultado, str) and not resultado.isdigit():
                return jsonify({"error": resultado}), 400
            
            imagen_id = int(resultado) if isinstance(resultado, str) else resultado
            
            return jsonify({
                "mensaje": "Imagen creada exitosamente",
                "id": imagen_id
            }), 201
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route("/api/imagenes/<int:id>", methods=['PUT'])
    def api_imagen_modificar(id):
        """Modificar una imagen existente"""
        try:
            imagen = Imagen.obtener('id', id)
            if not imagen:
                return jsonify({"error": "Imagen no encontrada"}), 404
            
            datos = request.get_json()
            if not datos:
                return jsonify({"error": "No se enviaron datos"}), 400
            
            datos['id'] = id
            resultado = Imagen.modificar(datos)
            
            return jsonify({"mensaje": resultado}), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route("/api/imagenes/<int:id>", methods=['DELETE'])
    def api_imagen_eliminar(id):
        """Eliminar una imagen"""
        try:
            imagen = Imagen.obtener('id', id)
            if not imagen:
                return jsonify({"error": "Imagen no encontrada"}), 404
            
            resultado = Imagen.eliminar(id)
            
            return jsonify({"mensaje": resultado}), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500