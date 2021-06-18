from peewee import *

db_handle = PostgresqlDatabase(
            'hh_ru',
            user='admin',
            password='admin',
            host='localhost',
            port='5432'
        )


class BaseModel(Model):
    class Meta:
        database = db_handle


class Address(Model):
    city = TextField()
    street = TextField()
    building = TextField()
    description = TextField()
    lat = DecimalField()
    lng = DecimalField()

    class Meta:
        primary_key = False
        db_table = 'addresses'
        database = db_handle


class Currency(Model):
    code = CharField(max_length=3, primary_key=True)
    abbr = CharField(max_length=5)
    name = CharField(max_length=20)
    rate = DecimalField()
    default = BooleanField()

    class Meta:
        db_table = 'currencies'
        database = db_handle


class Area(Model):
    id = CharField(max_length=32, primary_key=True)
    name = TextField()

    class Meta:
        db_table = 'areas'
        database = db_handle


class Specialization(Model):
    id = CharField(max_length=10, primary_key=True)
    profarea_id = CharField(max_length=5)
    profarea_name = TextField()
    name = TextField()

    class Meta:
        db_table = 'specializations'
        database = db_handle


class Experience(Model):
    id = TextField(primary_key=True)
    name = TextField()

    class Meta:
        db_table = 'experiences'
        database = db_handle


class Schedule(Model):
    id = CharField(max_length=12, primary_key=True)
    name = CharField(max_length=16)

    class Meta:
        db_table = 'schedules'
        database = db_handle


class Employment(Model):
    id = CharField(max_length=10, primary_key=True)
    name = CharField(max_length=22)

    class Meta:
        db_table = 'employments'
        database = db_handle


class Vacancy(Model):
    id = CharField(max_length=32, primary_key=True)
    name = TextField()
    description = TextField(column_name='description')
    area_id = ForeignKeyField(Area, column_name='area_id')
    branded_description = TextField(column_name='branded_description')
    schedule = ForeignKeyField(Schedule, column_name='schedule')
    accept_handicapped = BooleanField()
    accept_kids = BooleanField()
    accept_incomplete_resumes = BooleanField()
    experience = ForeignKeyField(Experience, column_name='experience')
    address_lat = DecimalField()
    address_lng = DecimalField()
    employment_id = ForeignKeyField(Employment, column_name='employment_id')
    salary_from = DecimalField()
    salary_to = DecimalField()
    salary_currency_code = ForeignKeyField(Currency, column_name='salary_currency_code')
    salary_gross = BooleanField()
    archived = BooleanField()
    created_at = DateTimeField()
    published_at = DateTimeField()
    employer_id = CharField(max_length=32)
    has_test = BooleanField()
    premium = BooleanField()
    vacancy_type = CharField(max_length=10)
    vacancy_billing_type = CharField(max_length=15)

    class Meta:
        db_table = 'vacancies'
        database = db_handle


class VacancySpecialization(Model):
    vacancy_id = ForeignKeyField(Vacancy, column_name='vacancy_id')
    specialization_id = ForeignKeyField(Specialization, column_name='specialization_id')

    class Meta:
        primary_key = False
        db_table = 'vacancy_specialization'
        database = db_handle


class KeySkill(Model):
    id = BigIntegerField(primary_key=True)
    name = TextField()

    class Meta:
        db_table = 'key_skills'
        database = db_handle


class VacancySkill(Model):
    vacancy_id = ForeignKeyField(Vacancy, column_name='vacancy_id')
    skill_id = ForeignKeyField(KeySkill, column_name='skill_id')

    class Meta:
        primary_key = False
        db_table = 'vacancy_skill'
        database = db_handle


class EmployerType(Model):
    id = CharField(max_length=20, primary_key=True)
    name = CharField(max_length=22)

    class Meta:
        db_table = 'types_of_employers'
        database = db_handle


class Employer(Model):
    id = CharField(max_length=20, primary_key=True)
    name = TextField()
    trusted = BooleanField()
    type = ForeignKeyField(EmployerType, column_name='type')
    description = TextField()
    site_url = TextField()
    alternate_url = TextField()
    area_id = ForeignKeyField(Area, column_name='area_id')

    class Meta:
        db_table = 'employers'
        database = db_handle


# class EmployerIndustry(Model):
#     employer_id = ForeignKeyField(Employer, column_name='employer_id')
#     industry_id = ForeignKeyField(Industry, column_name='specialization_id')
#
#     class Meta:
#         primary_key = False
#         db_table = 'employer_industry'
#         database = db_handle
