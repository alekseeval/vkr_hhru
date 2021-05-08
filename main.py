from data_parsers.hhParser import HhParser


def main():
    # Получение данных по всем вакансиям
    parser = HhParser()
    parser.get_vacancies()

    # Выведение кол-ва полученных данных в логи и запись их в файл
    # print('---> ' + str(len(vacancies_data)))
    # vacancies_data_file = open('data/vacancies.txt', 'w')
    # json.dump(vacancies_data, vacancies_data_file)
    # vacancies_data_file.close()


if __name__ == '__main__':
    main()
