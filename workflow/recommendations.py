import cv2
import requests
import numpy as np
import datetime
import re

from services.db_service import DbService
from data_parsers.hhApiParser import HhApiParser
import workflow.skills_recomendations as skill_rec


def check_photo(photo_info):

    db_service = DbService()
    all = db_service.execute_script('SELECT count(have_photo) FROM resume')
    have_photo = db_service.execute_script('SELECT count(have_photo) FROM resume WHERE have_photo = TRUE ')

    percentage = int(have_photo[0][0]/all[0][0] * 100)-1

    if photo_info is None:
        return {
            'title': 'Отсутствует фотография',
            'text': 'Фотография в резюме всегда будет плюсом, даже если должность не предполагает общения с людьми.'
                    ' Фото сделает резюме персонализированным: ее легче заметить, а отклик с фото сложнее пропустить'
                    ' или удалить. Но выбирать портрет для резюме нужно критически: неудачное фото может все испортить.'
                    ' Лучше всего подойдет профессиональное портретное фото, деловое и нейтральное.',
            'sub_text': f'На данный момент около {percentage}% всех резюме публикуются с фотографией!',
            'type': 'warning'
        }
    face_cascade = cv2.CascadeClassifier('..//workflow/haarcascade_frontalface_default.xml')

    req = requests.get(photo_info['medium'])
    arr = np.asarray(bytearray(req.content), dtype=np.uint8)
    img = cv2.imdecode(arr, -1)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, 1.1, 4)

    if len(faces) == 0:
        return {
            'title': 'Не найдено лицо на фотографии',
            'text': 'Мы не смогли распознать вас на фотографии. Убедитесь, что ваше лицо хорошо'
                    ' различимо и не закрыто элементами одежды.',
            'type': 'warning'
        }

    if len(faces) > 1:
        return {
            'title': 'Более одного лица на фотографии',
            'text': 'Нам удалось распознать несколько лиц на вашей фотографии. Групповые фото не подходят для '
                    'резюме, убедитесь, что на фото изображены только вы.',
            'type': 'danger'
        }

    return False


# TODO: Рекомендации на основе опыта других соискателей
def check_experience(experience):
    if not experience:
        return {
            'title': 'Отсутствует опыт работы',
            'text': 'Работодателю нужно понимать с какими задачами вы сталкивались в своей профессиональной'
                    ' деятельности, поэтому важно указывать ваш опыт работы. Если вы только начинающий специалист'
                    ' и опыта работы у вас ещё нет, то вам следует дополнить поле "Обо мне" задачами, которые вы'
                    ' решали в ходе обучения в учебном заведении и рассказать о своих личных проектах, над которыми'
                    ' вы работали. Так же важно, чтобы решаемые вами задачи демонстрировали ваш уровень навыков,'
                    ' необходимых для требуемой должности. ',
            'type': 'info'
        }

    for i in range(len(experience) - 1):
        position_start_date = datetime.datetime.fromisoformat(experience[i]['start'])
        last_position_end_date = datetime.datetime.fromisoformat(experience[i + 1]['end'])
        duration = position_start_date - last_position_end_date
        if duration.days > 93:
            return {
                'title': 'Существует длительный перерыв в карьере',
                'text': 'Опыт работы должен выглядеть цельным, без длительных перерывов. Если перерывы были,'
                        ' то они должны иметь объяснения: декретный отпуск, занятие бизнесом, фриланс и так далее. Эти'
                        ' рекомендуется раскрыть в разделе "Обо мне". Будьте готовы, что работодатель поинтересуется'
                        ' причинами перерывов в карьере на собеседовании.',
                'type': 'info'
            }

    return False


# TODO: Рекомендации на основе опыта других соискателей
def check_key_skills(skill_set):
    if not skill_set:
        return {
            'title': 'Не указаны ключевые навыки',
            'text': 'Многие соискатели полностью игнорируют этот раздел, а зря: часто именно сюда смотрит рекрутер'
                    ' после знакомства с опытом и образованием кандидата. Ключевые навыки — это специфические знания'
                    ' и умения, относящиеся непосредственно к рабочим процессам.',
            'type': 'danger'
        }
    skills_recommendations = skill_rec.recommendate(skill_set)
    skills_recommendations = [sr['skill'] for sr in skills_recommendations]
    if skill_set:
        return {
            'title': 'Информация о ключевых навыках',
            'text': 'С указанными вами навыками, работодатели часто требуют:',
            'sub_list': skills_recommendations,
            'type': 'info'
        }

    return False


# TODO: Рекомендации на основе опыта других соискателей
def check_salary(salary, resume_id, access_token):

    parser = HhApiParser()
    vacancies = parser.get_vacancies_similar_to_resume(resume_id, access_token)
    salaries = [vacancy['salary']['from'] for vacancy in vacancies if vacancy['salary'] is not None and vacancy['salary']['currency'] == 'RUR']
    salaries = np.array(list(filter(lambda x: x is not None, salaries)))
    salary_median = int(np.median(salaries))

    if len(salaries) < 20:
        if salary is None:
            return {
                'title': 'Не указана желаемая зарплата',
                'text': 'Статистика HeadHunter показывает, что если в резюме отсутствуют зарплатные ожидания, то количество'
                        ' приглашений снижается. Это связано с тем, что работодатель склонен минимизировать время на'
                        ' подбор:он в первую очередь приглашает тех, чье резюме дает исчерпывающую информацию — как о'
                        ' профессиональном уровне, так и о зарплатных ожиданиях. И только потом приступает к рассмотрению'
                        ' других кандидатов.',
                'type': 'danger'
            }
        else:
            return False
    if salary is None:
        return {
            'title': 'Не указана желаемая зарплата',
            'text': 'Статистика HeadHunter показывает, что если в резюме отсутствуют зарплатные ожидания, то количество'
                    ' приглашений снижается. Это связано с тем, что работодатель склонен минимизировать время на'
                    ' подбор:он в первую очередь приглашает тех, чье резюме дает исчерпывающую информацию — как о'
                    ' профессиональном уровне, так и о зарплатных ожиданиях. И только потом приступает к рассмотрению'
                    ' других кандидатов.',
            'sub_text': f'Наиболее распространенное значение заработной платы, среди опубликованных вакансий,'
                        f' похожих на ваше резюме:',
            'sub_list': [f'{salary_median} руб'],
            'type': 'danger'
        }

    return {
            'title': 'Информация о среднем значении ЗП',
            'sub_text': f'Наиболее распространенное значение заработной платы, среди опубликованных вакансий,'
                        f' похожих на ваше резюме:',
            'sub_list': [f'{salary_median} руб'],
            'type': 'info'
        }


def check_skills(about):
    if about is None:
        return {
            'title': 'Не заполнено поле "Обо мне"',
            'text': 'Данное поле дает вам возможность описать ваши личностные качества, которые характеризуют вас '
                    'как хорошего специалиста. В нем вы можете описать не только ваши личностные качества, но и ваши '
                    'увлечения, связанные с желаемой работой. Заполняйте это поле дынными, которые помогут вам получить'
                    ' работу.',
            'type': 'danger'
        }


def check_work_recommendations(recs):
    if not recs:
        return {
            'title': 'Нет рекомендаций с прошлых мест работы',
            'text': 'Укажите людей, которые могут дать вам рекомендацию. Желательно, чтобы как минимум один из них имел'
                    ' отношение к вашему предыдущему месту работы. Таким образом вы будете выглядеть более'
                    ' востребованным в глазах работодателя.',
            'type': 'info'
        }

    return False


# TODO: сделать подбор еще и по методу API
def get_vacancy_title_recommendation(title):

    title_tokens = re.sub('[^a-zа-я]', ' ', title.lower())
    title_tokens.replace('  ', ' ')
    title_tokens = title_tokens.split(' ')
    title_tokens = set([token for token in title_tokens if token != ''])

    script_text = "SELECT name, count(id) FROM vacancies WHERE "

    if len(title_tokens) == 0:
        return False
    for token in title_tokens:
        script_text += "lower(name) like %s and "
    script_text = script_text[:-4]
    script_text += "GROUP BY name ORDER BY count(id) DESC"

    db_service = DbService()
    vacancies = db_service.execute_script(script_text, tuple([f"%{token}%" for token in title_tokens]))

    i = 0
    relevant_titles = []
    for vacancy in vacancies:
        if i == 4:
            break
        vacancy_tokens = set(re.sub('[^a-zа-я]', ' ', vacancy[0].lower()).split(' '))
        if vacancy_tokens == title_tokens:
            continue
        i += 1
        relevant_titles.append(vacancy[0])

    if not relevant_titles:
        return False

    return {
            'title': 'Рекомендации к желаемой должности',
            'text': f'При выборе названия для желаемой должности, рекомендуется ориентироваться на конкретную'
                    f' интересующую именно вас вакансию определенной компании. Но в том случае если вы еще только в'
                    f' поиске желаемой вакансии, то мы можем посоветовать вам следующие наименование должностей, которые'
                    f' сейчас востребованы на рынке труда и похожи на желаемую вами должность:',
            'sub_list': relevant_titles,
            'type': 'info'
        }
