import psycopg2
from data.data_model import *


class DbService:

    connection = None

    def __init__(self, db_name, user, password, host='localhost', port='5432'):
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

    def close_connection(self):
        self.connection.close()
        self.connection = None

    # --------------------------------------------------------------------------------------
    # Сохраняет данные в таблицу schedule
    #
    # schedules     --  список словарей {'id':some_str, 'name':some_str}
    # --------------------------------------------------------------------------------------
    def add_to_schedule_table(self, schedules):
        self.open_connection()
        with self.connection.cursor() as cursor:
            for schedule in schedules:
                cursor.execute('''
                    INSERT INTO schedule
                    VALUES (%(id)s, %(name)s) 
                    ON CONFLICT (id)
                    DO UPDATE SET name = %(name)s
                ''', schedule)
        self.connection.commit()
        self.close_connection()
        print(f'----> Into table schedule was inserted {len(schedules)} values')

    # --------------------------------------------------------------------------------------
    # Сохраняет данные в таблицу experience
    #
    # experience_list     --  список словарей {'id':some_str, 'name':some_str}
    # --------------------------------------------------------------------------------------
    def add_to_experience_table(self, experience_list):
        self.open_connection()
        with self.connection.cursor() as cursor:
            for experience in experience_list:
                cursor.execute('''
                    INSERT INTO experience
                    VALUES (%(id)s, %(name)s)
                    ON CONFLICT (id)
                    DO UPDATE SET name = %(name)s
                ''', experience)
        self.connection.commit()
        self.close_connection()
        print(f'----> Into table experience was inserted {len(experience_list)} values')

    # --------------------------------------------------------------------------------------
    # Сохраняет данные в таблицу currency
    #
    # currencies        --  список словарей с данными в формате который предоставляет API
    # --------------------------------------------------------------------------------------
    def add_to_currency_table(self, currencies):
        self.open_connection()
        with self.connection.cursor() as cursor:
            for currency in currencies:
                cursor.execute('''
                    INSERT INTO currency
                    VALUES (%(code)s, %(abbr)s, %(name)s, %(rate)s, %(default)s)
                    ON CONFLICT (code)
                    DO UPDATE SET (abbr, name, rate, is_default) = (%(abbr)s, %(name)s, %(rate)s, %(default)s)
                ''', currency)
        self.connection.commit()
        self.close_connection()
        print(f'----> Into table currency was inserted {len(currencies)} values')

    # --------------------------------------------------------------------------------------
    # Сохраняет данные в таблицу employment
    #
    # employments       --  список словарей с данными в формате который предоставляет API
    # --------------------------------------------------------------------------------------
    def add_to_employment_table(self, employments):
        self.open_connection()
        with self.connection.cursor() as cursor:
            for employment in employments:
                cursor.execute('''
                    INSERT INTO employment
                    VALUES (%(id)s, %(name)s)
                    ON CONFLICT (id)
                    DO UPDATE SET name = %(name)s
                ''', employment)
        self.connection.commit()
        self.close_connection()
        print(f'----> Into table employment was inserted {len(employments)} values')

    # TODO: Удалить переменную для бедага debug_number_of_rows (в будущем)
    # --------------------------------------------------------------------------------------
    # Сохраняет данные в таблицу specialization
    #
    # specializations       --  список словарей с данными в формате который предоставляет API
    # --------------------------------------------------------------------------------------
    def add_to_specialization_table(self, specializations):
        self.open_connection()
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
                    DO UPDATE SET 
                        (name, profarea_id, profarea_name) = (%(name)s, %(profarea_id)s, %(profarea_name)s)
                ''', specialization)

        cursor.close()
        self.connection.commit()
        self.close_connection()
        print(f'----> Into table specialization was inserted {debug_number_of_rows} values')

    # TODO: Переделать метод под запись полных данных о вакансиях
    # --------------------------------------------------------------------------------------
    # Сохраняет в таблицу vacancies_id данные о id вакансий
    #
    # id_list   --  list of vacancies as dictionaries or data with 'id' field
    # --------------------------------------------------------------------------------------
    def save_vacancies(self, vacancies_list):

        for vacancy in vacancies_list:

            area = vacancy.get('area')
            if area is not None:
                Area.get_or_create(id=area.get('id'), name=area.get('name'))
            else:
                area = {}

            schedule = vacancy.get('schedule')
            if schedule is not None:
                Schedule.get_or_create(id=schedule.get('id'), name=schedule.get('name'))
            else:
                schedule = {}

            experience = vacancy.get('experience')
            if experience is not None:
                Experience.get_or_create(id=experience.get('id'), name=experience.get('name'))
            else:
                experience = {}

            address = vacancy.get('address')
            if address is not None:
                Address.get_or_create(lat=address.get('lat'), lng=address.get('lng'), street=address.get('street'),
                                      building=address.get('building'), description=address.get('description'),
                                      city=address.get('city'))
                metros = vacancy.get('metro_stations')
                if metros is not None:
                    for metro in metros:
                        MetroStation.get_or_create(lat=metro.get('lat'), lng=metro.get('lng'),
                                                   station_id=metro.get('station_id'),
                                                   station_name=metro.get('station_name'),
                                                   line_id=metro.get('line_id'), line_name=metro.get('line_name'))
                        AddressMetro.get_or_create(address_lat=address.get('lat'), address_lng=address.get('lng'),
                                                   metro_station_lat=metro.get('lat'),
                                                   metro_station_lng=metro.get('lng'))
            else:
                address = {}

            employment = vacancy.get('employment')
            if employment is not None:
                Employment.get_or_create(id=employment.get('id'), name=employment.get('name'))
            else:
                employment = {'id': None}

            salary = vacancy.get('salary')
            if salary is None:
                salary = {}

            b_type = vacancy.get('billing_type')
            if b_type is None:
                b_type = {}

            Vacancy.get_or_create(
                id=vacancy.get('id'),
                name=vacancy.get('name'),
                description=vacancy.get('description'),
                premium=vacancy.get('premium'),
                branded_description=vacancy.get('branded_description'),
                accept_handicapped=vacancy.get('accept_handicapped'),
                accept_kids=vacancy.get('accept_kids'),
                accept_incomplete_resumes=vacancy.get('accept_incomplete_resumes'),
                salary_from=salary.get('from'),
                salary_to=salary.get('to'),
                salary_gross=salary.get('gross'),
                archived=vacancy.get('archived'),
                created_at=vacancy.get('created_at'),
                published_at=vacancy.get('published_at'),
                employer_id=vacancy.get('employer').get('id'),
                has_test=vacancy.get('has_test'),
                vacancy_type=vacancy.get('type').get('id'),
                vacancy_billing_type=b_type.get('id'),

                area_id=area.get('id'),
                schedule=schedule.get('id'),
                experience=experience.get('id'),
                address_lat=address.get('lat'),
                address_lng=address.get('lng'),
                employment_id=employment.get('id'),
                salary_currency_code=salary.get('currency')
            )

            skills = vacancy.get('key_skills')
            if skills is not None:
                for skill in skills:
                    VacancySkill.get_or_create(vacancy_id=vacancy.get('id'), skill_name=skill.get('name'))

            specializations = vacancy.get('specializations')
            if specializations is not None:
                for spec in specializations:
                    Specialization.get_or_create(id=spec.get('id'), name=spec.get('name'),
                                                 profarea_id=spec.get('profarea_id'),
                                                 profarea_name=spec.get('profarea_name'))
                    SpecializationVacancy.get_or_create(vacancy_id=vacancy.get('id'), specialization_id=spec.get('id'))

        print(f'----> Into table vacancies_id was inserted {len(vacancies_list)} vacancies')

    # --------------------------------------------------------------------------------------
    # Выполняет скрипт из файла
    #
    # file      --  файл в котором записан скрипт
    # --------------------------------------------------------------------------------------
    def execute_script(self, file):
        self.open_connection()
        with self.connection.cursor() as cursor:
            cursor.execute(file.read())
        self.connection.commit()
        self.close_connection()
        print(f'----> Script was successfully executed')
