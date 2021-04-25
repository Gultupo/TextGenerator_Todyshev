import json
import os
from flask import Flask, request

from text_generator import *

app = Flask(__name__)


storage = {}


@app.route('/', methods=['POST'])
def alice_skill():
    global storage
    req = request.json
    user_id = req["session"]["user_id"]

    if req["session"]["new"]:
        storage[user_id] = {}
        storage[user_id]['is_titled'] = False
        storage[user_id]['is_ended'] = False
        storage[user_id]['curr_on_text'] = 0
        return generate_response(req, "Генератор коротких рассказов включён. Как Вы хотите назвать ваш рассказ?")

    context = storage[user_id]
    answer = req["request"]["original_utterance"].lower()
    print(context, storage)

    if not context['is_titled']:
        storage[user_id]['is_titled'] = True
        storage[user_id]['title'] = answer.capitalize()
        storage[user_id]['is_world'] = False
        return generate_response(req,
                                 'Хорошее название! В каком мире будут происходить действия Вашего рассказа?'
                                 'Есть возможность создания мира фантастики/фэнтези/современности')
    if not context['is_world']:
        if answer not in {'фантастика', 'фэнтези', 'современность'}:
            print(context, storage, 1)
            return generate_response(req, 'Попробуйте назвать тип мира еще раз!')

        storage[user_id]['is_world'] = True
        storage[user_id]['world_type'] = answer
        storage[user_id]['is_genre'] = False
        return generate_response(req,
                                 'Выберите жанр Вашего рассказа. Вы можете выбрать из жанров романтика/приключения/ужасы.')

    if not context['is_genre']:
        if answer not in {'романтика', 'приключения', 'ужасы'}:
            return generate_response(req, 'Попробуйте назвать жанр истории еще раз!')
        storage[user_id]['is_genre'] = True
        storage[user_id]['genre'] = answer
        storage[user_id]['is_line'] = False
        return generate_response(req, 'Выберите основную линию сюжета из доступных(восхождение, падение)')

    if not context['is_line']:
        if answer not in {'восхождение', 'падение'}:
            return generate_response(req, 'Попробуйте назвать основную линию сюжета еще раз!')
        storage[user_id]['is_line'] = True
        storage[user_id]['line'] = answer
        storage[user_id]['is_characters'] = False
        return generate_response(req, 'Назовите число персонажей.')

    if not context['is_characters']:
        answer = answer.split()[0]
        if not answer.isdigit():
            return generate_response(req, 'Назовите число персонажей.')
        storage[user_id]['is_characters'] = True
        storage[user_id]['n_char'] = int(answer)
        storage[user_id]['all_char'] = []
        return generate_response(req,
                                 'Как зовут первого персонажа и какого он пола?(говорить необходимо в формате имя пол)')

    if context['n_char'] > 0:
        if len(answer.split()) < 2:
            return generate_response(req, 'Назовите имя персонажа и его пол.')
        elif answer.split()[-1] not in {'мужчина', 'женщина', 'девушка', 'парень'}:
            return generate_response(req, 'Назовите имя персонажа и его пол.')
        else:
            name = ' '.join(answer.split()[:-1])
            gender = answer.split()[-1]
        storage[user_id]['all_char'].append(tuple([name, gender]))
        storage[user_id]['n_char'] -= 1
        if storage[user_id]['n_char'] == 0:
            context = storage[user_id]
            storage[user_id]['story'] = Story(context['title'], context['world_type'], context['genre'],
                                              context['line'])
            for char in context['all_char']:
                char = Character(char[0], char[1])
                storage[user_id]['story'].add_character(char)
            storage[user_id]['name_plot'] = False
            storage[user_id]['is_script_generated'] = False
            return generate_response(req, 'С какого действия начать рассказ?')
        storage[user_id]['is_script_generated'] = False
        return generate_response(req, 'Назовите имя следующего персонажа')

    if storage[user_id]['story'].curr <= 3:
        if context['is_script_generated']:
            if answer == 'нет':
                storage[user_id]['is_script_generated'] = False
                storage[user_id]['name_plot'] = False
                storage[user_id]['charatersforscript'] = []
                return generate_response(req, 'С какого действия продолжить рассказ?')
            else:
                storage[user_id]['story'].curr -= 1
                storage[user_id]['is_script_generated'] = False
                storage[user_id]['story'].text.pop()
                storage[user_id]['name_plot'] = False
                storage[user_id]['charatersforscript'] = []
                return generate_response(req, 'О каком действии пойдет речь?')

        if answer not in {'мольба', 'спасение', 'месть', 'загадка', 'мятеж'} and not context['name_plot']:
            return generate_response(req, 'Назовите действие из предложенного списка(мольба, спасение, месть, загадка, мятеж)')
        if not context['name_plot']:
            storage[user_id]['name_plot'] = answer
            storage[user_id]['charactersforscript'] = []
            return generate_response(req, 'Назовите первого персонажа для этого фрагмента, чтобы закончить ввод персонажей скажите стоп')
        if answer == 'начни генерацию':
            storage[user_id]['story'].curr += 1
            storage[user_id]['is_script_generated'] = True
            part = context['story'].generate_part(MPart(context['name_plot'], context['charactersforscript'], context['story']))
            storage[user_id]['name_plot'] = False
            storage[user_id]['charatersforscript'] = []
            storage[user_id]['story'].text.append(part)
            return generate_response(req, part + '\nХотите сгенерировать этот отрывок еще раз?')
        elif answer in context['story'].list_all_char():
            storage[user_id]['charactersforscript'].append(answer)
            return generate_response(req, 'Назовите следующего персонажа этого отрывка')
        else:
            return generate_response(req, 'Назовите персонажа из созданных вами')
    if context['curr_on_text'] < 3:
        if context['curr_on_text'] == 0:
            storage[user_id]['curr_on_text'] += 1
            return generate_response(req, context['story'].title + '\n' + context['story'].text[context['curr_on_text']])
        storage[user_id]['curr_on_text'] += 1
        return generate_response(req, context['story'].text[context['curr_on_text']])

    return generate_response(req, 'У вас получилась отличная история!', end_session=True)


def generate_response(req, text, end_session=False):
    res = {
        "version": req["version"],
        "session": req["session"],
        "response": {
            "end_session": end_session,
            "text": text
        }
    }
    return json.dumps(res, indent=2)


if __name__ == '__main__':
    app.run('127.0.0.1', '5000')
