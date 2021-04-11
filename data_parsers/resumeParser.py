from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class HhResumesParser:

    def __init__(self):
        self.driver = webdriver.Chrome('chromedriver.exe')
        self.driver.maximize_window()

    def get_resumes_info(self):
        self.driver.get('https://hh.ru/search/resume')
        self.driver.close()
