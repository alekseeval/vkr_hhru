from data_parsers.hhVacancyParser import HhVacancyParser


def main():
    # Получение данных по всем вакансиям
    parser = HhVacancyParser()
    parser.get_all_vacancies_id_by_request()

    # Выведение кол-ва полученных данных в логи и запись их в файл
    # print('---> ' + str(len(vacancies_data)))
    # vacancies_data_file = open('data/vacancies.txt', 'w')
    # json.dump(vacancies_data, vacancies_data_file)
    # vacancies_data_file.close()


if __name__ == '__main__':
    main()
