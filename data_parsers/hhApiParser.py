import requests
import json

from tqdm import tqdm
from typing import Final
from time import sleep


class HhApiParser:
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
        assert 'errors' not in data
        return data

    # --------------------------------------------------------------------------------------
    # Возвращает данные о всех вакансиях по запросу, с учетом пагинации (с учетом
    # стандартного ограничения API на глубину запроса не более чем в 2000 записей)
    #
    # req_params    --  dict, который должен содержать параметры запроса к API,
    #                   дефолтное значение - req_params = {'page': 0, 'perPage': 100}
    # single_page   --  флаг, если True, то выводится результат только переданной страницы запроса
    # @return       --  информация о вакансиях в виде массива словарей
    # --------------------------------------------------------------------------------------
    def get_vacancies(self, req_params=None, single_page=False):

        # Проверка наличия параметров запроса
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

        # Получение данных с оставшихся страниц
        for i in range(1, data.get('pages')):
            req_params['page'] = i
            data = self.__get_vacancies_by_request(req_params)
            data_book += data.get('items')

        # Получение полных данных о вакансиях
        vacancies_info = []
        for data in tqdm(data_book):                                                        # NOTE: WITH PROGRESS BAR
            try:
                vacancy = self.get_vacancy_by_id(data.get('id'))
            except:
                sleep(1)
                vacancy = self.get_vacancy_by_id(data.get('id'))
            if 'errors' in vacancy:
                continue
            vacancies_info.append(vacancy)

        return vacancies_info

    # --------------------------------------------------------------------------------------
    # vacancy_id    --  id вакансии на сайте
    # @return       --  возвращает полные данные о вакансии как dict
    # --------------------------------------------------------------------------------------
    def get_vacancy_by_id(self, vacancy_id):
        request = requests.get(self.API_VACANCIES_URL + f'/{vacancy_id}', timeout=50)
        data = json.loads(request.content.decode())
        request.close()
        # assert 'errors' not in data
        return data

    # --------------------------------------------------------------------------------------
    # emp_id        --  id нанимателя на сайте
    # @return       --  возвращает полные данные о нанимателе
    # --------------------------------------------------------------------------------------
    def get_employer_info(self, emp_id):
        request = requests.get(f'{self.API_URL}/employers/{emp_id}')
        data = request.json()
        request.close()
        return data

    # --------------------------------------------------------------------------------------
    # emp_id_list   --  список id нанимателей, завернутых в tuple
    # @return       --  возвращает полные данные о переданных нанимателях
    # --------------------------------------------------------------------------------------
    def get_employers_info(self, emp_id_list):
        data = []
        for emp_id_tuple in tqdm(emp_id_list, desc='Выгрузка нанимателей'):                 # NOTE: WITH PROGRESS BAR
            try:
                cur_emp = self.get_employer_info(emp_id_tuple[0])
            except:
                sleep(1)
                cur_emp = self.get_employer_info(emp_id_tuple[0])
            if cur_emp.get('errors') is not None:
                continue
            data.append(cur_emp)
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
    # @return       -- dict объект с данными по запросу
    # --------------------------------------------------------------------------------------
    def execute_request(self, req_param, sub_href='vacancies'):
        request = requests.get(f'{self.API_URL}/{sub_href}', req_param, timeout=50)
        data = json.loads(request.content.decode())
        request.close()
        return data

    def get_auth_info(self, access_token):
        response = requests.get(f'{self.API_URL}/me', headers={'Authorization': f'Bearer {access_token}'})
        data = response.json()
        response.close()
        return data

    def get_applicant_resumes(self, access_token):
        response = requests.get(f'{self.API_URL}/resumes/mine', headers={'Authorization': f'Bearer {access_token}'})
        data = response.json()
        response.close()
        return data

    def get_applicant_resume_data(self, resume_id, access_token):
        response = requests.get(f'{self.API_URL}/resumes/{resume_id}', headers={'Authorization': f'Bearer {access_token}'})
        data = response.json()
        response.close()
        return data

    def change_user_resume_data(self, resume_id, change_params, access_token):

        response = requests.put(f'{self.API_URL}/resumes/{resume_id}', json=change_params,
                                headers={'Authorization': f'Bearer {access_token}'})
        response.close()

        return True

    def get_vacancies_similar_to_resume(self, resume_id, access_token):
        response = requests.get(f'{self.API_URL}/resumes/{resume_id}/similar_vacancies', params={'per_page': 50},
                                headers={'Authorization': f'Bearer {access_token}'})
        data = response.json()
        response.close()
        return data['items']
