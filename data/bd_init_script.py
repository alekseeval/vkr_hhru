from data_parsers.hhParser import HhParser
from services.db_service import DbService

# TODO: Дописать инициализацию БД, если ее не существует

# Вгрузка статичных словарей в БД
parser = HhParser()
db_service = DbService()

# Получение данных справочника dictionaries и занесение их в
data = parser.get_dictionaries()
db_service.add_to_schedule_table(data.get('schedule'))
db_service.add_to_experience_table(data.get('experience'))
db_service.add_to_currency_table(data.get('currency'))
db_service.add_to_employment_table(data.get('employment'))

# Получние данных из справочника specializations и занесение их в БД
data = parser.get_specializations_dict()
db_service.add_to_specialization_table(data)
