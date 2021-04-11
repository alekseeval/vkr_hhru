# TODO: Додумать работу с req_param в методе get_all_vacancies (какие параметры стоит добавлять в словарь и стоит ли)
#       Может не стоит вообще задавать дефолтное значение

import requests
import json

from db_service import DbService
from typing import Final


class HhVacancyParser:

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
    def __get_vacancies_by_request(self, req_params):
        request = requests.get(self.API_VACANCIES_URL, req_params)
        data = json.loads(request.content.decode())
        request.close()
        assert 'errors' not in data
        return data

    # --------------------------------------------------------------------------------------
    # Возвращает данные о всех вакансиях по запросу, с учетом пагинации
    #
    # req_params    --  dict, который должен содержать параметры запроса к API,
    #                   дефолтное значение - req_params = {'page': 0, 'perPage': 100}
    # @return       --  инофрмация о вакансиях в виде массива словарей, где каждый словарь
    #                   отвечает за отдельную вакансию
    # --------------------------------------------------------------------------------------
    def get_all_vacancies_id_by_request(self, req_params=None):
        # Проверка наличая параметров запроса
        if req_params is None:
            req_params = {}
        if 'page' not in req_params:
            req_params['page'] = 0
        if 'per_page' not in req_params:
            req_params['per_page'] = 100

        # Подключение к базе данных
        self.db_service.connect()

        # Заполнение данными о вакансиях с первой страницы запроса
        data = self.__get_vacancies_by_request(req_params)
        data_book = data.get('items')

        # Получние данных с оставшихся страниц
        while data.get('page') < data.get('pages')-1:
            req_params['page'] += 1
            data = self.__get_vacancies_by_request(req_params)
            data_book += data.get('items')

        # Запись полученных данных в бд для дальнейшей работы
        self.db_service.save_vacancies_id(data_book)

        # Разрыв соединения с базой данных
        self.db_service.close_connection()

        return data_book

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
