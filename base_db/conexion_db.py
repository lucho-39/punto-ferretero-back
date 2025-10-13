import mysql.connector

config_dev = {
    'user': 'root',
    'password': '',
    'host': '127.0.0.1',
    'database': 'puntoferretero',
}

config_prod = {
    'user': 'luciano',
    'password': 'PuntoFerretero',
    'host': 'luciano.mysql.pythonanywhere-services.com',
    'database': 'luciano$puntoferretero',
}

conexion = mysql.connector.connect(**config_dev)
