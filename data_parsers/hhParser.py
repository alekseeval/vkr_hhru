import requests
import json

from tqdm.notebook import tqdm
from typing import Final
from time import sleep


class HhParser:
    API_URL: Final = 'https://api.hh.ru'
    API_VACANCIES_URL: Final = API_URL + '/vacancies'
    api_access_token = None

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
    # Возвращает API access_token, при необходимости генерируя его по новой
    # --------------------------------------------------------------------------------------
    def get_api_token(self):

        if self.api_access_token is not None:
            return self.api_access_token

        with open('com.alekseev.workflow/oauth_data/api_token', 'r') as file:
            file_data = json.load(file)
            self.api_access_token = file_data['access_token']

        # Если токен еще валиден
        if self.__test_access_key(self.api_access_token):
            return self.api_access_token

        with open('com.alekseev.workflow/oauth_data/api_credentials', 'r') as file:
            file_data = json.load(file)
            client_id = file_data['client_id']
            client_secret = file_data['client_secret']
        req_params = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret
        }
        request = requests.post('https://hh.ru/oauth/token', req_params)
        data = request.json()
        request.close()

        assert 'error' not in data

        self.api_access_token = data['access_token']
        with open('com.alekseev.workflow/oauth_data/api_token', 'w') as file:
            json.dump(data, file)
        return self.api_access_token

    # --------------------------------------------------------------------------------------
    # @return       --  True, если токен валиден, иначе False
    # --------------------------------------------------------------------------------------
    @staticmethod
    def __test_access_key(access_token):
        request = requests.get('https://api.hh.ru/me', headers={'Authorization': f'Bearer {access_token}'})
        return request.status_code == 200

    # --------------------------------------------------------------------------------------
    # Возвращает данные о всех вакансиях по запросу, с учетом пагинации (с учетом
    # стандартного ограничения API на глубину запроса не более чем в 2000 записей)
    #
    # req_params    --  dict, который должен содержать параметры запроса к API,
    #                   дефолтное значение - req_params = {'page': 0, 'perPage': 100}
    # single_page   --  флаг, если True, то выводится результат только переданной стрницы запроса
    # @return       --  инофрмация о вакансиях в виде массива словарей
    # --------------------------------------------------------------------------------------
    def get_vacancies(self, req_params=None, single_page=False):

        # Проверка наличая параметров запроса
        if req_params is None:
            req_params = {
                'page': 0,
                'per_page': 100
            }

        if single_page:
            return self.__get_vacancies_by_request(req_params)['items']

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
            try:
                vacancies_info.append(self.get_vacancy_by_id(data.get('id')))
            except:
                sleep(1)
                vacancies_info.append(self.get_vacancy_by_id(data.get('id')))

        return vacancies_info

    # --------------------------------------------------------------------------------------
    # vacancy_id    --  id вакансии на сайте
    # @return       --  возвращает полные данные о вакансии как dict
    # --------------------------------------------------------------------------------------
    def get_vacancy_by_id(self, vacancy_id):
        request = requests.get(self.API_VACANCIES_URL + f'/{vacancy_id}', timeout=50)
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

    # --------------------------------------------------------------------------------------
    # Метод выполняет запрос к API с переданными параметрами
    #
    # req_param     -- словарь параметров запроса к API
    # sub_href      -- раздел API, к которому осуществляется доступ (пример: .../vacancies)
    # @return       -- dict объкт с данными по запросу
    # --------------------------------------------------------------------------------------
    def execute_request(self, req_param, sub_href='vacancies'):
        request = requests.get(f'{self.API_URL}/{sub_href}', req_param, timeout=50)
        data = json.loads(request.content.decode())
        request.close()
        return data
