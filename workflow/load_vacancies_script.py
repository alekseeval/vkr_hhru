from datetime import datetime, timedelta
from tqdm import tqdm
import threading
import gc

from data_parsers.hhApiParser import HhApiParser
from services.db_service import DbService

parser = HhApiParser()
cur_date = {
    'from': (datetime.now() - timedelta(days=1)),
    'to': datetime.now()
}
req_param = {
        'specialization': 1,
        'per_page': 0,
        'date_from': cur_date['from'].strftime('%Y-%m-%dT%H:%M:%S'),
        'date_to': cur_date['to'].strftime('%Y-%m-%dT%H:%M:%S')
    }
data = parser.execute_request(req_param=req_param)
dates = []
total_vacancies_number = 0
while data['found'] != 0:
    while data['found'] > 2000:
        cur_date['from'] += timedelta(hours=1)
        req_param['date_from'] = cur_date['from'].strftime('%Y-%m-%dT%H:%M:%S')
        data = parser.execute_request(req_param=req_param)

    total_vacancies_number += data['found']
    dates.append([cur_date['from'].strftime('%Y-%m-%dT%H:%M:%S'), cur_date['to'].strftime('%Y-%m-%dT%H:%M:%S')])

    cur_date['to'] = cur_date['from']
    cur_date['from'] -= timedelta(hours=12)
    req_param['date_from'] = cur_date['from'].strftime('%Y-%m-%dT%H:%M:%S')
    req_param['date_to'] = cur_date['to'].strftime('%Y-%m-%dT%H:%M:%S')
    data = parser.execute_request(req_param=req_param)
print(f'За последний месяц имеется {total_vacancies_number} вакансий')


def load_vacancies(d_range):
    params = {
        'page': 0,
        'per_page': 100,
        'date_from': d_range[0],
        'date_to': d_range[1],
        'specialization': 1
    }
    vac = parser.get_vacancies(req_params=params)
    db_service.save_vacancies(vac)
    vac.clear()


db_service = DbService()
THREADS_NUMBER = 6
for i in tqdm(range(0, len(dates), THREADS_NUMBER)):

    threads = []
    upper_i = i + THREADS_NUMBER
    if upper_i > len(dates):
        upper_i = len(dates)

    for j in range(i, upper_i):
        threads.append(threading.Thread(target=load_vacancies, args=(dates[j],)))

    for t in threads:
        t.start()

    for t in threads:
        t.join()
    threads.clear()
    gc.collect()

employers = db_service.execute_script('SELECT DISTINCT employer_id FROM vacancies WHERE employer_id is not NULL')


def load_employers(employer):
    employer_info = parser.get_employers_info(employer)
    db_service.save_employers(employer_info)


threads = []
size = int(len(employers)/4)
threads.append(threading.Thread(target=load_employers, args=(employers[:size*1],)))
threads.append(threading.Thread(target=load_employers, args=(employers[size*1:size*2],)))
threads.append(threading.Thread(target=load_employers, args=(employers[size*2:size*3],)))
threads.append(threading.Thread(target=load_employers, args=(employers[size*3:],)))

for thread in threads:
    thread.start()

for thread in threads:
    thread.join()
