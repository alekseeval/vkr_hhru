# TODO: Додумать работу с req_param в методе get_all_vacancies (какие параметры стоит добавлять в словарь и стоит ли)
#       Может не стоит вообще задавать дефолтное значение
# TODO: Заменить assert для ошибок в запросах, на соответствующие обработки
# TODO: Убрать работу с БД из этого класса полностью

import requests
import json

from tqdm.notebook import tqdm
from typing import Final


class HhParser:

    API_URL: Final = 'https://api.hh.ru'
    API_VACANCIES_URL: Final = API_URL + '/vacancies'

    # --------------------------------------------------------------------------------------
    # req_params        --  dict, который должен содержать параметры запроса к API
    # @return           --  возвращает данные о вакансиях по указанной странице запроса
    #                       как массив словарей
    # --------------------------------------------------------------------------------------
    def __get_vacancies_by_request(self, req_params):
        request = requests.get(self.API_VACANCIES_URL, req_params)
        data = json.loads(request.content.decode())
        request.close()
        assert 'errors' not in data  # Note: Обработать исключение
        return data

    # --------------------------------------------------------------------------------------
    # Возвращает данные о всех вакансиях по запросу, с учетом пагинации (с учетом
    # стандартного ограничения API на глубину запроса не более чем в 2000 записей)
    # Если в параметрах запроса указана страница page, то пагинация не учитывается
    #
    # req_params    --  dict, который должен содержать параметры запроса к API,
    #                   дефолтное значение - req_params = {'page': 0, 'perPage': 100}
    # @return       --  инофрмация о вакансиях в виде массива словарей
    # --------------------------------------------------------------------------------------
    def get_vacancies(self, req_params=None):

        # Проверка наличая параметров запроса
        if req_params is None:
            req_params = {}

        # Если в параметрах запроса нет указания страницы, то выполняем запрос по всем страницам запроса,
        # иначе только по указанной
        if 'page' not in req_params:
            req_params['page'] = 0
            req_params['per_page'] = 100
        else:
            return self.__get_vacancies_by_request(req_params)

        # Заполнение данными о вакансиях с первой страницы запроса
        data = self.__get_vacancies_by_request(req_params)
        data_book = data.get('items')

        # Получние данных с оставшихся страниц NOTE: WITH PROGRESS BAR
        for i in tqdm(range(1, data.get('pages')), desc='Получение id вакансий'):
            req_params['page'] = i
            data = self.__get_vacancies_by_request(req_params)
            data_book += data.get('items')

        # Получение полных данных о вакансиях NOTE: WITH PROGRESS BAR
        vacancies_info = []
        for data in tqdm(data_book, desc='Выгрузка вакансий'):
            vacancies_info.append(self.get_vacancy_by_id(data.get('id')))

        return vacancies_info

    # --------------------------------------------------------------------------------------
    # vacancy_id    --  id вакансии на сайте
    # @return       --  возвращает полные данные о вакансии как dict
    # --------------------------------------------------------------------------------------
    def get_vacancy_by_id(self, vacancy_id):
        request = requests.get(self.API_VACANCIES_URL + f'/{vacancy_id}')
        data = json.loads(request.content.decode())
        request.close()
        assert 'errors' not in data  # Note: Обработать исключение
        return data

    # --------------------------------------------------------------------------------------
    # Метод выгружает базу словарей API
    # --------------------------------------------------------------------------------------
    def get_dictionaries(self):
        request = requests.get(f'{self.API_URL}/dictionaries')
        data = json.loads(request.content.decode())
        request.close()
        return data

    # --------------------------------------------------------------------------------------
    # Метод выгружает базу существующих специализаций
    # --------------------------------------------------------------------------------------
    def get_specializations_dict(self):
        request = requests.get(f'{self.API_URL}/specializations')
        data = json.loads(request.content.decode())
        request.close()
        return data
