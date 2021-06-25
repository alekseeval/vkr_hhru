from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

from typing import Final

import sys
if hasattr(sys.modules["__main__"], "get_ipython"):
    from tqdm import notebook as tqdm
else:
    from tqdm import tqdm


class HhResumeParser:

    MAIN_URL: Final = 'https://irkutsk.hh.ru/'

    def __init__(self):
        self.driver = None
        self.init_driver()

    def init_driver(self):
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless')
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        self.driver.maximize_window()
        self.driver.set_page_load_timeout(20)

    def go_to_page(self, href):
        try:
            self.driver.get(href)
        except:
            self.driver.quit()
            self.init_driver()
            self.driver.get(href)

    def get_resumes(self, spec_id, number_of_pages=10):

        # Обход всех страниц запроса
        resume_hrefs = self.get_resume_href_list(spec_id, number_of_pages)

        # Обход всех полученных ссылок на резюме
        resumes_data = []
        for resume_href in tqdm(resume_hrefs, desc='Обход вакансий'):                       # NOTE: WITH PROGRESS BAR
            # self.driver.get(resume_href)
            self.go_to_page(resume_href)
            # Обработка недоступного резюме
            if len(self.driver.find_elements_by_css_selector('.attention_bad')) != 0:
                continue
            resumes_data.append(self.parse_resume_info())

        # self.driver.close()
        return resumes_data

    def get_resume_href_list(self, spec_id, number_of_pages):
        resume_hrefs = []
        for i in tqdm(range(number_of_pages), desc='Обход страниц'):  # NOTE: WITH PROGRESS BAR
            self.go_to_page(
                f'https://irkutsk.hh.ru/search/resume?'
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
                f'specialization={spec_id}&'
                f'gender=unknown&'
                f'page={i}'
            )
            # self.driver.execute_script('window.scrollBy(0, 80000);')
            page_hrefs = self.driver.find_elements_by_css_selector('.resume-search-item__name')
            for href in page_hrefs:
                resume_hrefs.append(href.get_attribute('href'))
        return resume_hrefs

    def parse_resume_info(self):

        # Создание объекта данных резюме
        resume = {
            'href': self.driver.current_url
        }

        # Раскрытие всех дополнительных элементов страницы
        for el in self.driver.find_elements_by_css_selector('.resume-industries__open'):
            el.click()

        # Получение названия резюме
        resume['title'] = self.driver.find_element_by_css_selector('.resume-block__title-text').text

        # Определение наличия фото
        resume['have_photo'] = len(self.driver.find_elements_by_css_selector('.resume-photo')) != 0

        # Получение данных о запрашиваемой ЗП
        salary_element = self.driver.find_elements_by_css_selector('.resume-block__title-text_salary')
        if len(salary_element) == 1:
            salary_split = salary_element[0].text.split(' ')
            salary = {
                'value':        int(salary_split[0].replace('\u2009', '')),
                'currency':     salary_split[1]
            }
            resume['salary'] = salary
        else:
            resume['salary'] = None

        # Получение данных о адресе соискателя
        address = self.driver.find_elements_by_css_selector("span[data-qa='resume-personal-address']")
        if len(address) != 0:
            resume['address'] = address[0].text
        else:
            resume['address'] = None

        # Получение данных поля "Обо мне"
        about_field_element = self.driver.find_elements_by_css_selector("div[data-qa='resume-block-skills-content']")
        if len(about_field_element) != 0:
            resume['about'] = about_field_element[0].text
        else:
            resume['about'] = None

        # Получение специализаций резюме
        resume['specializations'] = []
        specs_el = self.driver.find_elements_by_css_selector(".resume-block__specialization")
        for spec in specs_el:
            resume['specializations'].append(spec.text)

        # Получение кол-ва высших образований
        higher_education_block = self.driver.find_elements_by_css_selector("div[data-qa='resume-block-education']")
        if len(higher_education_block) != 0:
            resume['higher_educations_number'] = len(
                higher_education_block[0].find_elements_by_css_selector("div[data-qa='resume-block-education-item']")
            )
        else:
            resume['higher_educations_number'] = 0

        # Получение списка повышений квалификаций/курсов
        resume['additional_education'] = []
        additional_education_block = self.driver.find_elements_by_css_selector(
            "div[data-qa='resume-block-additional-education']"
        )
        if len(additional_education_block) != 0:
            names = additional_education_block[0].find_elements_by_css_selector(
                "div[data-qa='resume-block-education-name']"
            )
            organizations = additional_education_block[0].find_elements_by_css_selector(
                "div[data-qa='resume-block-education-organization']"
            )
            for name, org in zip(names, organizations):
                resume['additional_education'].append(
                    {
                        'name': name.text,
                        'organization': org.text
                    }
                )

        # Получение опыта работы соискателя
        exp_time = self.driver.find_elements_by_css_selector('.bloko-text-tertiary')[:-1]
        exp_industries = self.driver.find_elements_by_css_selector('.resume-block__experience-industries')
        exp_positions = self.driver.find_elements_by_css_selector("div[data-qa='resume-block-experience-position']")
        resume_experience = []
        for time, industries_block, pos in zip(exp_time, exp_industries, exp_positions):
            industries = []
            industries_list = industries_block.find_elements_by_css_selector('.profareatree__subitem-experience')
            for el in industries_list:
                industries.append(el.text)
            resume_experience.append({'time': time.text, 'industries': industries, 'position': pos.text})
        resume['experience'] = resume_experience

        # Получение желаемого графика работы
        schedule_parent_block = self.driver.find_elements_by_css_selector("div[data-qa='resume-block-position']")
        if len(schedule_parent_block) != 0:
            paragraphs = schedule_parent_block[0].find_elements_by_css_selector('p')

            employment_text = paragraphs[0].text.replace('Employment: ', '').replace('Занятость: ', '')
            schedule_text = paragraphs[1].text.replace('Work schedule: ', '').replace('График работы: ', '')

            resume['schedule'] = schedule_text.split(', ')
            resume['employment'] = employment_text.split(', ')
        else:
            resume['schedule'] = []
            resume['employment'] = []

        # Получение списка ключевых навыков соискателя
        resume['key_skills'] = []
        key_skill_elements = self.driver.find_elements_by_css_selector('.bloko-tag__section_text')
        if len(key_skill_elements) != 0:
            for el in key_skill_elements:
                resume['key_skills'].append(el.text)

        return resume
