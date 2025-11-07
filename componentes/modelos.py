from base_db.conexion_db import conexion
from base_db.tabla_db import Tabla
from auxiliares.cifrado import encriptar


class Categoria(Tabla):

    tabla = 'category'
    conexion = conexion
    campos = ('id', 'name', 'unit')

    def __init__(self, *args, de_bbdd=False):
        super().crear(args, de_bbdd)


class Imagen(Tabla):

    tabla = 'image'
    conexion = conexion
    campos = ('id', 'url_img', 'txt_alt')

    def __init__(self, *args, de_bbdd=False):
        super().crear(args, de_bbdd)


class Proveedor(Tabla):

    tabla = 'prov'
    conexion = conexion
    campos = ('id', 'cod', 'name', 'obs')

    def __init__(self, *args, de_bbdd=False):
        super().crear(args, de_bbdd)


class Producto(Tabla):

    tabla = 'product'
    conexion = conexion
    campos = ('id', 'art', 'cod', 'tit', 'desc',
              'cat_id', 'img_id', 'prov_id', 'rating')

    def __init__(self, *args, de_bbdd=False):
        super().crear(args, de_bbdd)
