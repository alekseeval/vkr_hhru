from peewee import *

user = 'admin'
password = 'admin'
db_name = 'hh_ru'

db_handle = PostgresqlDatabase(
    db_name,
    user=user,
    password=password,
    host='localhost'
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
        primary_key = CompositeKey('lat', 'lng')
        db_table = 'address'
        database = db_handle


class MetroStation(Model):
    station_id = TextField()
    station_name = TextField()
    line_id = TextField()
    line_name = TextField()
    lat = DecimalField()
    lng = DecimalField()

    class Meta:
        primary_key = CompositeKey('lat', 'lng')
        db_table = 'metro_station'
        database = db_handle


class AddressMetro(Model):
    address_lat = DecimalField()
    address_lng = DecimalField()
    metro_station_lat = DecimalField()
    metro_station_lng = DecimalField()

    class Meta:
        primary_key = False
        db_table = 'address_metro'
        database = db_handle


class Currency(Model):
    code = CharField(max_length=3, primary_key=True)
    abbr = CharField(max_length=5)
    name = CharField(max_length=20)
    rate = DecimalField()
    default = BooleanField()

    class Meta:
        db_table = 'currency'
        database = db_handle


class Area(Model):
    id = CharField(max_length=32, primary_key=True)
    name = TextField()

    class Meta:
        db_table = 'area'
        database = db_handle


class Specialization(Model):
    id = CharField(max_length=10, primary_key=True)
    profarea_id = CharField(max_length=5)
    profarea_name = TextField()
    name = TextField()

    class Meta:
        db_table = 'specialization'
        database = db_handle


class Experience(Model):
    id = TextField(primary_key=True)
    name = TextField()

    class Meta:
        db_table = 'experience'
        database = db_handle


class Schedule(Model):
    id = CharField(max_length=12, primary_key=True)
    name = CharField(max_length=16)

    class Meta:
        db_table = 'schedule'
        database = db_handle


class Employment(Model):
    id = CharField(max_length=10, primary_key=True)
    name = CharField(max_length=22)

    class Meta:
        db_table = 'employment'
        database = db_handle


class Vacancy(Model):
    id = CharField(max_length=32, primary_key=True)
    name = TextField()
    description = TextField()
    area_id = ForeignKeyField(Area)
    branded_description = TextField()
    schedule = ForeignKeyField(Schedule)
    accept_handicapped = BooleanField()
    accept_kids = BooleanField()
    accept_incomplete_resumes = BooleanField()
    experience = ForeignKeyField(Experience)
    address_lat = DecimalField()
    address_lng = DecimalField()
    employment_id = ForeignKeyField(Employment)
    salary_from = DecimalField()
    salary_to = DecimalField()
    salary_currency_code = ForeignKeyField(Currency)
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


class SpecializationVacancy(Model):
    vacancy_id = ForeignKeyField(Vacancy)
    specialization_id = ForeignKeyField(Specialization)

    class Meta:
        db_table = 'specialization_vacancy'
        database = db_handle


class VacancySkill(Model):
    vacancy_id = ForeignKeyField(Vacancy)
    skill_name = TextField()

    class Meta:
        db_table = 'vacancy_skill'
        database = db_handle
