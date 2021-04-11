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
        print(f'----> Connection to {self.db_name} database was opened')

    def close_connection(self):
        self.connection.close()
        self.connection = None
        print(f'----> Connection to {self.db_name} database was closed')

    # --------------------------------------------------------------------------------------
    # Сохраняет в таблицу vacancies_id данные о id вакансий
    #
    # id_list   --  list of vacancies as dictionaries od data with 'id' field
    # --------------------------------------------------------------------------------------
    def save_vacancies_id(self, vacancies_list):
        assert self.connection is not None
        with self.connection.cursor() as cursor:
            for vac in vacancies_list:
                cursor.execute('INSERT INTO vacancies_id (id) VALUES (%s) ON CONFLICT DO NOTHING;', (vac.get('id'), ))
        self.connection.commit()
        print(f'----> Into table vacancies_id was inserted {len(vacancies_list)} values')
