from services.db_service import DbService
from data_parsers.hhResumeParser import HhResumeParser
from data_parsers.hhApiParser import HhApiParser

import re
import threading
from tqdm import tqdm

# TODO: получить ссылки на все доступные резюме
# NOTE: Разделить процесс получения на 2-3 потока
id_regex = re.compile(r'e/(.+?)\?')
ids = []


def parse(spec_id):
    parser = HhResumeParser()
    hrefs = parser.get_resume_href_list(spec_id, number_of_pages=50)
    ids.extend([re.search(id_regex, href).group(1) for href in hrefs])
    parser.driver.quit()
    del parser


service = DbService()
data = service.execute_script("SELECT id FROM specializations WHERE profarea_id = '1'")
specs = [item[0] for item in data]
threads = []
for i in tqdm(range(0, len(specs), 3)):
    threads.append(threading.Thread(target=parse, args=(specs[i],)))
    threads.append(threading.Thread(target=parse, args=(specs[i+1],)))
    threads.append(threading.Thread(target=parse, args=(specs[i+2],)))

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    threads.clear()
    print(len(ids))


ids = list(set(ids))
print(len(ids))


# TODO: получить информацию из списка предыдущего шага и записать в БД
# NOTE: Разделить процесс получения на 4-6 потоков

parser = HhApiParser()
db_service = DbService()


def load_resumes(resume_ids):
    cur_resumes = []
    for resume_id in resume_ids:
        cur_resumes.append(parser.get_resume_data(resume_id=resume_id, access_token='H2R24B3O475ALK45NVDTHQ6U8LTKO9IPLS4RBU17SD0LOO1MMTPPKN9VO3CFVACC'))
    # db_service.load_resumes(cur_resumes) # TODO


load_resumes(ids)







# from services.db_service import DbService
# from data_parsers.hhResumeParser import HhResumeParser
#
# import threading
# from tqdm import tqdm
# import json
#
# service = DbService()
# data = service.execute_script("SELECT id FROM specializations WHERE profarea_id = '1'")
# specs = [item[0] for item in data]
# del data
#
# parser_1 = HhResumeParser()
# parser_2 = HhResumeParser()
# resumes_data = [[], []]
# for i in tqdm(range(0, len(specs)-1, 2)):
#     thread_1 = threading.Thread(target=lambda s: resumes_data[0].extend(parser_1.get_resumes(s)), args=(specs[i],))
#     thread_2 = threading.Thread(target=lambda s: resumes_data[1].extend(parser_2.get_resumes(s)), args=(specs[i+1],))
#
#     threads = [thread_1, thread_2]
#     for t in threads:
#         t.start()
#
#     for t in threads:
#         t.join()
#
#     threads.clear()
#     # resumes_data += parser.get_resumes(spec_id)
# parser_1.driver.quit()
# parser_2.driver.quit()
#
# resumes_data = resumes_data[0] + resumes_data[1]
# with open('..//data/resume_data.json', 'w') as file:
#     json.dump(resumes_data, file)
# del resumes_data
#
# with open('..//data/resume_data.json', 'r') as file:
#     data = json.load(file)
# print(len(data))
