import psycopg2


class DbService:

    connection = None

    def __init__(self, db_name, user, password, host='localhost', port='5433'):
        self.db_name = db_name
        self.user = user
        self.password = password
        self.host = host
        self.port = port

    # --------------------------------------------------------------------------------------
    # Создает соединение с базой данных
    # --------------------------------------------------------------------------------------
    def connect(self):
        self.connection = psycopg2.connect(
            dbname=self.db_name,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port
        )
        assert self.connection.closed == 0

    def close_connection(self):
        self.connection.close()
