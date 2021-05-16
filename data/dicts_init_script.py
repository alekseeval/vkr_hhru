from data_parsers.hhVacancyParser import HhVacancyParser
from services.db_service import DbService

# Получение данных справочника dictionaries и занесение их в
parser = HhVacancyParser()
db_service = DbService()

data = parser.get_dictionaries()
db_service.add_to_schedule_table(data.get('schedule'))
db_service.add_to_experience_table(data.get('experience'))
db_service.add_to_currency_table(data.get('currency'))
db_service.add_to_employment_table(data.get('employment'))
db_service.add_to_employer_type_table(data.get('employer_type'))

# Получение данных из справочника specializations и занесение их в БД
data = parser.get_specializations_dict()
db_service.add_to_specialization_table(data)

# Удаление использованных данных
del parser
del db_service
del data
