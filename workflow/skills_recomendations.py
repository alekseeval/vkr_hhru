import numpy as np
from scipy.sparse import lil_matrix
import json


def recommendate(user_skills):
    # Получение матрицы расстояний
    with open('../workflow/colab_filtration/topk_matrix', 'rb') as file:
        mat = np.load(file)
        topk_matrix = lil_matrix(mat)

    # Получение отображения индексов на навык
    with open('../workflow/colab_filtration/row_to_skill', 'r') as file:
        row_to_skill = json.load(file)
        row_to_skill = {int(row): skill for row, skill in row_to_skill.items()}
        skill_to_row = {skill: row for row, skill in row_to_skill.items()}

    user_vector = vectorise(user_skills, skill_to_row).tocsr()

    # 1. перемножить матрицу item-item и вектор рейтингов пользователя A
    x = topk_matrix.dot(user_vector).tolil()
    # 2. занулить ячейки, соответствующие навыкам, которые пользователь A уже оценил
    for i, j in zip(*user_vector.nonzero()):
        x[i, j] = 0

    # превращаем столбец результата в вектор
    x = x.T.tocsr()

    # 3. отсортировать навыки в порядке убывания значений и получить top-k рекомендаций (quorum = 5)
    quorum = 5
    data_ids = np.argsort(x.data)[-quorum:][::-1]

    result = []
    for arg_id in data_ids:
        row_id, p = x.indices[arg_id], x.data[arg_id]
        result.append({"skill": row_to_skill[row_id], "weight": p})

    return result


def vectorise(skills, skill_to_row):
    user_vector = lil_matrix((len(skill_to_row), 1),)
    for s in skills:
        if skill_to_row.get(s) is None:
            continue
        user_vector[skill_to_row[s], 0] = 1
    return user_vector