from services.db_service import DbService

db_service = DbService()
with open('..//data/hh_ru_backup_14052021_schema') as file:
    db_service.execute_file_script(file)

# Удаление использованных данных
del db_service
del DbService
