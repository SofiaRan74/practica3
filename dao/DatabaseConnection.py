import mysql.connector
class DatabaseConnection:
    _instance = None
    _connection = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance._connect()
        return cls._instance

    def _connect(self):
        try:
            self._connection = mysql.connector.connect(
                host="185.232.14.52",
                database="u760464709_23005116_bd",
                user="u760464709_23005116_usr",
                password="z8[T&05u"
            )
            print("✅ Conexión Singleton MySQL establecida")
        except mysql.connector.Error as err:
            print(f"❌ Error al conectar con MySQL: {err}")

    def get_connection(self):
        if not self._connection.is_connected():
            self._connect()
        return self._connection
        

