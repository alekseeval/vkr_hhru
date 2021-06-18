import json
import re
from services.db_service import DbService


with open('..//data/resume_data_prepared.json', 'r') as file:
    resumes = json.load(file)

resumes_id = []
for resume in resumes:
    if resume['id'] in resumes_id:
        resume['broken'] = True
        resumes.remove(resume)
        continue
    resumes_id.append(resume['id'])

    del resume['additional_education']

    resume['total_experience'] = 0
    for exp in resume['experience']:
        resume['total_experience'] += exp['time']
    del resume['experience']

    old_specs = resume['specializations']
    resume['specializations'] = []
    for spec in old_specs:
        if '.' in spec:
            resume['specializations'].append(spec)

normal_resumes = []
for r in resumes:
    if len(r) == 12:
        normal_resumes.append(r)

print('---> Запись')
db_service = DbService()
db_service.load_resumes(normal_resumes)
