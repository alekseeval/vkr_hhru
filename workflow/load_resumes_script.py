from services.db_service import DbService
from data_parsers.hhResumeParser import HhResumeParser

import threading
from tqdm import tqdm
import json

service = DbService()
data = service.execute_script("SELECT id FROM specialization WHERE profarea_id = '1'")
specs = [item[0] for item in data]
del data

parser_1 = HhResumeParser()
parser_2 = HhResumeParser()
resumes_data = [[], []]
for i in tqdm(range(0, len(specs)-1, 2)):
    thread_1 = threading.Thread(target=lambda s: resumes_data[0].extend(parser_1.get_resumes(s)), args=(specs[i],))
    thread_2 = threading.Thread(target=lambda s: resumes_data[1].extend(parser_2.get_resumes(s)), args=(specs[i+1],))

    threads = [thread_1, thread_2]
    for t in threads:
        t.start()

    for t in threads:
        t.join()

    threads.clear()
    # resumes_data += parser.get_resumes(spec_id)
parser_1.driver.quit()
parser_2.driver.quit()

resumes_data = resumes_data[0] + resumes_data[1]
with open('..//data/resume_data.json', 'w') as file:
    json.dump(resumes_data, file)
del resumes_data

with open('..//data/resume_data.json', 'r') as file:
    data = json.load(file)
print(len(data))
