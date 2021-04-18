# TODO: Додумать работу с req_param в методе get_all_vacancies (какие параметры стоит добавлять в словарь и стоит ли)
#       Может не стоит вообще задавать дефолтное значение

import requests
import json

from db_service import DbService
from typing import Final


class HhParser:

    API_URL: Final = 'https://api.hh.ru'
    API_VACANCIES_URL: Final = API_URL + '/vacancies'

    # --------------------------------------------------------------------------------------
    # db_service    --  сервис для свизи с БД, необязательный параметр, если не указывать,
    #                   то запись идет в базу данных с именем 'hh_ru' под пользовалетем
    #                   'admin' c паролем 'admin'
    # --------------------------------------------------------------------------------------
    def __init__(self, db_service=DbService('hh_ru', 'admin', 'admin')):
        self.db_service = db_service

    # --------------------------------------------------------------------------------------
    # Метод private, так как используется только для выполнения запроса без учета пагинации
    #
    # req_params        --  dict, который должен содержать параметры запроса к API
    # @return           --  возвращает данные о вакансиях по указанной странице запроса
    #                       как массив словарей
    # --------------------------------------------------------------------------------------
    def get_vacancies_by_request(self, req_params):
        request = requests.get(self.API_VACANCIES_URL, req_params)
        data = json.loads(request.content.decode())
        request.close()
        assert 'errors' not in data
        return data

    # --------------------------------------------------------------------------------------
    # Возвращает данные о всех вакансиях по запросу, с учетом пагинации, начиная со страницы
    # page, указанной в req_params, заканчивая последней доступной страницей по запросу
    # (с учетом стандартного ограничения API на глубину запроса не более чем в 2000 записей)
    #
    # req_params    --  dict, который должен содержать параметры запроса к API,
    #                   дефолтное значение - req_params = {'page': 0, 'perPage': 100}
    # @return       --  инофрмация о вакансиях в виде массива словарей, где каждый словарь
    #                   отвечает за отдельную вакансию
    # --------------------------------------------------------------------------------------
    def get_vacancies_from_all_pages(self, req_params=None):
        # Проверка наличая параметров запроса
        if req_params is None:
            req_params = {}
        if 'page' not in req_params:
            req_params['page'] = 0
        if 'per_page' not in req_params:
            req_params['per_page'] = 100

        # Заполнение данными о вакансиях с первой страницы запроса
        data = self.get_vacancies_by_request(req_params)
        data_book = data.get('items')

        # Получние данных с оставшихся страниц
        while data.get('page') < data.get('pages')-1:
            req_params['page'] += 1
            data = self.get_vacancies_by_request(req_params)
            data_book += data.get('items')

        # Получение полных данных о вакансиях
        vacancies_info = []
        for data in data_book:
            vacancies_info.append(self.get_vacancy_info_by_id(data.get('id')))

        # Запись полученных данных в бд для дальнейшей работы
        self.db_service.save_vacancies(vacancies_info)

        return vacancies_info

    # --------------------------------------------------------------------------------------
    # vacancy_id    --  id вакансии на сайте
    # @return       --  возвращает полные данные о вакансии как dict
    # --------------------------------------------------------------------------------------
    def get_vacancy_info_by_id(self, vacancy_id):
        request = requests.get(self.API_VACANCIES_URL + f'/{vacancy_id}')
        data = json.loads(request.content.decode())
        request.close()
        assert 'errors' not in data
        return data

    # --------------------------------------------------------------------------------------
    # Метод выгружает в базу данных словари предоставляемые API
    # --------------------------------------------------------------------------------------
    def load_to_db_dictionaries(self):

        # Получение данных справочника dictionaries и занесение их в БД
        request = requests.get(f'{self.API_URL}/dictionaries')
        data = json.loads(request.content.decode())
        request.close()
        self.db_service.add_to_schedule_table(data.get('schedule'))
        self.db_service.add_to_experience_table(data.get('experience'))
        self.db_service.add_to_currency_table(data.get('currency'))
        self.db_service.add_to_employment_table(data.get('employment'))

        # Получние данных из справочника specializations и занесение их в БД
        request = requests.get(f'{self.API_URL}/specializations')
        data = json.loads(request.content.decode())
        request.close()
        self.db_service.add_to_specialization_table(data)
