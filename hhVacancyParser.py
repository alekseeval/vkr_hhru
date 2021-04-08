import requests
import json
import time

from pprint import pprint


class HhVacancyParser:
    api_url = 'https://api.hh.ru'

    # --------------------------------------------------------------------------------------
    # Получение данных о всех вакансиях на одной странице запроса
    #
    # extra_req_params  -- dict, который должен содержать параметры запроса к API
    #                      дефолтное значение {'page': 0, 'per_page': 100}
    # page              -- номер страницы запроса к API
    # @return           -- возвращает данные о вакансиях как массив словарей
    # --------------------------------------------------------------------------------------
    def __get_vacancies(self, page=0, extra_req_params=None):
        vacancies_url = self.api_url + '/vacancies'
        req_params = {
            'page': page,
            'per_page': 100
        }
        if extra_req_params is not None:
            req_params.update(extra_req_params)
        request = requests.get(vacancies_url, req_params)
        data = json.loads(request.content.decode())
        request.close()
        return data

    # --------------------------------------------------------------------------------------
    # Возвращает данные о всех вакансиях по запросу, с учетом пагинации
    #
    # @return   -- инофрмация о всех вакансиях по запросу в формате массива словарей
    # --------------------------------------------------------------------------------------
    def get_all_vacancies(self):
        data = self.__get_vacancies()
        data_book = data.get('items')
        while data.get('page') < data.get('pages')-1:
            data = self.__get_vacancies(data.get('page') + 1)
            data_book += data.get('items')
        return data_book

    # --------------------------------------------------------------------------------------
    # Получние полной информации о вакансии посредством запроса к hh.ru API
    #
    # vacancy_id    -- id вакансии на сайте
    # @return       -- возвращает данные о вакансии как dict
    # --------------------------------------------------------------------------------------
    def get_vacancy_info_by_id(self, vacancy_id):
        vacancy_url = self.api_url + f'/vacancies/{vacancy_id}'
        request = requests.get(vacancy_url)
        data = json.loads(request.content.decode())
        return data
