from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from tqdm.notebook import tqdm

from time import sleep
from typing import Final


class HhResumeParser:

    MAIN_URL: Final = 'https://irkutsk.hh.ru/'

    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        # self.driver.maximize_window()

    def go_to_page(self, page_number):
        self.driver.get(f'https://irkutsk.hh.ru/search/resume?'
                        f'clusters=true&'
                        f'exp_period=all_time&'
                        f'logic=normal&'
                        f'no_magic=true&'
                        f'order_by=relevance&'
                        f'ored_clusters=true&'
                        f'pos=full_text&text=&'
                        f'items_on_page=100&'
                        f'st=resumeSearch&'
                        f'relocation=living_or_relocation&'
                        f'specialization=1&'
                        f'gender=unknown&'
                        f'page={page_number}')

    def get_resumes(self):

        # Обход всех страниц запроса
        resume_hrefs = []
        for i in tqdm(range(10), desc='Обход страниц'):                                     # NOTE: WITH PROGRESS BAR
            self.go_to_page(i)
            self.driver.execute_script('window.scrollBy(0, 80000);')
            page_hrefs = self.driver.find_elements_by_css_selector('.resume-search-item__name')
            for href in page_hrefs:
                resume_hrefs.append(href.get_attribute('href'))

        # Обход всех полученных ссылок на резюме
        resumes_data = []
        for resume_href in tqdm(resume_hrefs, desc='Обход вакансий'):                       # NOTE: WITH PROGRESS BAR
            self.driver.get(resume_href)
            resumes_data.append(self.parse_resume_info())

        self.driver.close()
        return resumes_data

    def parse_resume_info(self):
        # Создание объекта данных резюме
        resume = {}

        # Получение данных о запрашиваемой ЗП
        salary_element = self.driver.find_elements_by_css_selector('.resume-block__title-text_salary')
        if len(salary_element) == 1:
            salary_split = salary_element[0].text.split(' ')
            salary = {
                'value':        int(salary_split[0].replace('\u2009', '')),
                'currency':     salary_split[1].replace('.', '')
            }
            resume['salary'] = salary
        else:
            resume['salary'] = None

        return resume
