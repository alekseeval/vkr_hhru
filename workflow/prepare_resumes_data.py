import json
from services.db_service import DbService
import re

with open('..//data/resume_data.json', 'r') as file:
    resume_list = json.load(file)

db_service = DbService()

db_specializations = db_service.execute_script("SELECT id, name FROM specialization")

bd_schedules_orig = db_service.execute_script("SELECT id, name FROM schedule")
bd_schedules = {}
for sch in bd_schedules_orig:
    bd_schedules[sch[1].lower()] = sch[0]
del bd_schedules_orig

bd_employment_orig = db_service.execute_script("SELECT id, name FROM employment")
bd_employment = {}
for emp in bd_employment_orig:
    bd_employment[emp[1].lower()] = emp[0]
del bd_employment_orig

id_regex = re.compile(r'e/(.+?)\?')
resume_copy = [resume for resume in resume_list]
for resume in resume_copy:

    # Резюме без ссылки и названия не рассматриваем
    if (resume['href'] is None) or (resume['title'] is None):
        resume_list.remove(resume)
        continue
    resume['id'] = re.search(id_regex, resume['href']).group(1)
    del resume['href']

    # Сопоставление региона поиска с данными справочника
    address_id = db_service.execute_script(f"SELECT id FROM area WHERE name like '{resume['address']}'")
    if len(address_id) == 0:
        resume_list.remove(resume)
        continue
    del resume['address']
    resume['area_id'] = address_id[0][0]

    # Зарплата приводится к числовому значению в рублях
    if resume['salary'] is not None:
        currency_rate = db_service.execute_script(
            f"SELECT rate FROM currency WHERE abbr like '{resume['salary']['currency']}'"
        )
        if len(currency_rate) == 0:
            resume_list.remove(resume)
            continue
        salary_value = resume['salary']['value'] * (1/currency_rate[0][0])  # перевод в рубли
        salary_value = int(salary_value)  # округление до целого
        salary_value = salary_value - salary_value % -500  # округление до ближайшего кратного 500 значения
        resume['salary'] = salary_value

    # Сопоставление специализации резюме со справочником
    for spec in resume['specializations']:
        spec_id = [spec_result[0] for spec_result in db_specializations if spec_result[1] == spec]
        if len(spec_id) != 1:
            resume['specializations'].remove(spec)
            continue
        resume['specializations'][resume['specializations'].index(spec)] = spec_id[0]

    # Перевод опыта работы в число
    for experience in resume['experience']:
        exp_splitted_string = experience['time'].split(' ')
        res = 0
        for i in range(0, len(exp_splitted_string), 2):
            if 'лет' in exp_splitted_string[i+1]\
                    or 'год' in exp_splitted_string[i+1]\
                    or 'ye' in exp_splitted_string[i+1]:
                res += int(exp_splitted_string[i])*12
            else:
                res += int(exp_splitted_string[i])
        experience['time'] = res

    # Сопоставление графиков работы со справочником API
    for i in range(len(resume['schedule'])):
        resume['schedule'][i] = bd_schedules.get(resume['schedule'][i])

    # Сопоставление занятости со справочником API
    for i in range(len(resume['employment'])):
        resume['employment'][i] = bd_employment.get(resume['employment'][i])

with open('..//data/resume_data_prepared.json', 'w') as file:
    json.dump(resume_list, file)
