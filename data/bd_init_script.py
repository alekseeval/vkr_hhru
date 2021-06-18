from services.db_service import DbService

db_service = DbService()
with open('hh_ru_backup_current_schema') as file:
    db_service.execute_file_script(file)

# Удаление использованных данных
del db_service
del DbService
