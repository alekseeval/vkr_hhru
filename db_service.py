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
    def open_connection(self):
        self.connection = psycopg2.connect(
            dbname=self.db_name,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port
        )
        assert self.connection.closed == 0
        print(f'--> Connection to {self.db_name} database was opened')

    def close_connection(self):
        self.connection.close()
        self.connection = None
        print(f'--> Connection to {self.db_name} database was closed')

    # --------------------------------------------------------------------------------------
    # Сохраняет данные в таблицу schedule
    #
    # schedules     --  список словарей {'id':some_str, 'name':some_str}
    # --------------------------------------------------------------------------------------
    def add_to_schedule_table(self, schedules):
        with self.connection.cursor() as cursor:
            for schedule in schedules:
                cursor.execute('''
                    INSERT INTO schedule
                    VALUES (%(id)s, %(name)s) 
                    ON CONFLICT (id)
                    DO UPDATE SET name = %(name)s
                ''', schedule)
        self.connection.commit()
        print(f'----> Into table schedule was inserted {len(schedules)} values')

    # --------------------------------------------------------------------------------------
    # Сохраняет данные в таблицу experience
    #
    # experience_list     --  список словарей {'id':some_str, 'name':some_str}
    # --------------------------------------------------------------------------------------
    def add_to_experience_table(self, experience_list):
        with self.connection.cursor() as cursor:
            for experience in experience_list:
                cursor.execute('''
                    INSERT INTO experience
                    VALUES (%(id)s, %(name)s)
                    ON CONFLICT (id)
                    DO UPDATE SET name = %(name)s
                ''', experience)
        self.connection.commit()
        print(f'----> Into table experience was inserted {len(experience_list)} values')

    # --------------------------------------------------------------------------------------
    # Сохраняет данные в таблицу currency
    #
    # currencies        --  список словарей с данными в формате который предоставляет API
    # --------------------------------------------------------------------------------------
    def add_to_currency_table(self, currencies):
        with self.connection.cursor() as cursor:
            for currency in currencies:
                cursor.execute('''
                    INSERT INTO currency
                    VALUES (%(code)s, %(abbr)s, %(name)s, %(rate)s, %(default)s)
                    ON CONFLICT (code)
                    DO UPDATE SET (abbr, name, rate, is_default) = (%(abbr)s, %(name)s, %(rate)s, %(default)s)
                ''', currency)
        self.connection.commit()
        print(f'----> Into table currency was inserted {len(currencies)} values')

    # --------------------------------------------------------------------------------------
    # Сохраняет данные в таблицу employment
    #
    # employments       --  список словарей с данными в формате который предоставляет API
    # --------------------------------------------------------------------------------------
    def add_to_employment_table(self, employments):
        with self.connection.cursor() as cursor:
            for employment in employments:
                cursor.execute('''
                    INSERT INTO employment
                    VALUES (%(id)s, %(name)s)
                    ON CONFLICT (id)
                    DO UPDATE SET name = %(name)s
                ''', employment)
        self.connection.commit()
        print(f'----> Into table employment was inserted {len(employments)} values')

    # TODO: Удалить переменную для бедага debug_number_of_rows (в будущем)
    # --------------------------------------------------------------------------------------
    # Сохраняет данные в таблицу specialization
    #
    # specializations       --  список словарей с данными в формате который предоставляет API
    # --------------------------------------------------------------------------------------
    def add_to_specialization_table(self, specializations):
        cursor = self.connection.cursor()

        debug_number_of_rows = 0
        for super_specialization in specializations:
            profarea_name = super_specialization.get('name')
            profarea_id = super_specialization.get('id')
            for specialization in super_specialization.get('specializations'):
                debug_number_of_rows += 1
                specialization['profarea_id'] = profarea_id
                specialization['profarea_name'] = profarea_name
                cursor.execute('''
                    INSERT INTO specialization
                    VALUES (%(id)s, %(name)s, %(profarea_id)s, %(profarea_name)s)
                    ON CONFLICT (id)
                    DO UPDATE SET (name, profarea_id, profarea_name) = (%(name)s, %(profarea_id)s, %(profarea_name)s)
                ''', specialization)

        cursor.close()
        self.connection.commit()
        print(f'----> Into table specialization was inserted {debug_number_of_rows} values')

    # TODO: Переделать метод под запись полных данных о вакансиях
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

    # --------------------------------------------------------------------------------------
    # Инициализирует все необходимые для работы таблицы в базе данных
    # из скрипта data/hh_ru_backup
    # --------------------------------------------------------------------------------------
    def init_db(self):
        with self.connection.cursor() as cursor:
            cursor.execute(open('data/hh_ru_backup', 'r').read())
        self.connection.commit()
        print(f'----> 10 tables was recently created')
