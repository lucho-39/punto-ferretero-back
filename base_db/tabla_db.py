import logging


class Tabla:

    # Creación de la tabla
    def __init__(self, nombre, conexion, campos):
        self.tabla = nombre
        self.conexion = conexion
        self.campos = campos

    # CRUD
    def crear(self, valores, de_bbdd=False):
        """
        Si de_bbdd=True, 'valores' viene como (registro_tuple,)
        Si de_bbdd=False, 'valores' viene como tuple de valores (sin id)
        """
        if de_bbdd:
            registros = valores[0]
            for campo, valor in zip(self.campos, registros):
                setattr(self, campo, valor)
        else:
            for campo, valor in zip(self.campos[1:], valores):
                setattr(self, campo, valor)

    def guardar_db(self):
        """
        Inserta el registro y devuelve el id (int) si fue posible,
        o False en caso de error.
        """
        cols = list(self.campos[1:])
        cols_sql = ", ".join(f"`{c}`" for c in cols)
        placeholders = ", ".join(["%s"] * len(cols))
        consulta = f"INSERT INTO {self.tabla} ({cols_sql}) VALUES ({placeholders});"
        datos = tuple(getattr(self, c) for c in cols)

        rta_db = self.__conectar(consulta, datos)

        # __conectar devuelve el last_id (int) o False; si devuelve True lo consideramos fallo aquí
        if rta_db is False or isinstance(rta_db, bool):
            return False

        try:
            return int(rta_db)
        except Exception:
            return False

    @classmethod
    def obtener(cls, campo=None, valor=None):

        if campo is None or valor is None:
            consulta = f"SELECT * FROM {cls.tabla};"
            rta_db = cls.__conectar(consulta)
            if rta_db is not False and rta_db:
                return [cls(registro, de_bbdd=True) for registro in rta_db]
            else:
                return []
        else:
            consulta = f"SELECT * FROM {cls.tabla} WHERE {campo} = %s;"
            rta_db = cls.__conectar(consulta, (valor,))
            if rta_db is not False and rta_db:
                return cls(rta_db[0], de_bbdd=True)
            else:
                return None

    @classmethod
    def eliminar(cls, id):
        consulta = f"DELETE FROM {cls.tabla} WHERE id = %s ;"
        rta_db = cls.__conectar(consulta, (id,))

        if rta_db:
            return 'Eliminación exitosa.'

        return 'No se pudo eliminar el registro.'

    @classmethod
    def modificar(cls, registro):
        update_q = f"UPDATE {cls.tabla} "
        set_q = 'SET '

        id_val = registro.pop('id')
        id_val = int(id_val) if type(id_val) != int else id_val

        campos = list(registro.keys())
        set_q += ", ".join(f"{c} = %s" for c in campos)
        where_q = f" WHERE id = %s;"
        consulta = update_q + set_q + where_q
        nvos_datos = tuple(list(registro.values()) + [id_val])
        rta_db = cls.__conectar(consulta, nvos_datos)

        if rta_db:
            return 'Modificación exitosa.'

        return 'No se pudo modificar el registro.'

    @classmethod
    def __conectar(cls, consulta, datos=None):
        """
        Ejecuta la consulta y devuelve:
         - Para SELECT: lista de tuplas o False si no hay resultado
         - Para INSERT: last_insert_id (int) o False en error
         - Para UPDATE/DELETE: True si ejecutó correctamente o False en error
        No cierra la conexión global; solo cierra cursores.
        """
        try:
            cursor = cls.conexion.cursor()
        except Exception:
            # intentar reconectar si el objeto ofrece connect()
            try:
                cls.conexion.connect()
                cursor = cls.conexion.cursor()
            except Exception as e:
                logging.exception("")
                return False

        try:
            sql_upper = consulta.strip().upper()
            if sql_upper.startswith('SELECT'):
                if datos is not None:
                    cursor.execute(consulta, datos)
                else:
                    cursor.execute(consulta)
                rows = cursor.fetchall()
                cursor.close()
                return rows if rows else False
            else:
                if datos is not None:
                    cursor.execute(consulta, datos)
                else:
                    cursor.execute(consulta)

                # INSERT -> intentar obtener lastrowid
                if sql_upper.startswith('INSERT'):
                    last_id = None
                    try:
                        last_id = getattr(cursor, 'lastrowid', None)
                        if not last_id:
                            cursor.execute("SELECT LAST_INSERT_ID();")
                            res = cursor.fetchone()
                            if res:
                                last_id = res[0]
                    except Exception:
                        last_id = None

                    try:
                        cls.conexion.commit()
                    except Exception:
                        logging.exception("Error en commit después de INSERT")

                    cursor.close()
                    return last_id if last_id is not None else True

                # UPDATE/DELETE -> commit y devolver True si no hubo error
                else:
                    try:
                        cls.conexion.commit()
                    except Exception:
                        logging.exception(
                            "Error en commit después de UPDATE/DELETE")
                    cursor.close()
                    return True

        except Exception:
            logging.exception("Error ejecutando consulta SQL")
            try:
                cls.conexion.rollback()
            except Exception:
                pass
            try:
                cursor.close()
            except Exception:
                pass
            return False
