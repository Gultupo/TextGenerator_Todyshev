import json
from random import choice, randint

import requests

from event_sentences import d_sentences
from fantasy_words import f_d
from modernity_words import m_d
from rom_words import horr_words, rom_words, adv_words
from scifi_words import sf_d
from words_for_all_stages import start, middle, end

s_types = [['char', 'verb', 'adj', 'nomen'], ['char', 'adv', 'verb', 'nomen'], ['nomen', 'adj'], ['char', 'adj'],
           ['char', 'verb', 'nomen']]


def capitalize(string):
    f_chr = False
    new_string = ''
    for chr in string:
        if not f_chr:
            new_string += chr.upper()
            f_chr = True
        else:
            new_string += chr

    return new_string


def universe_handler(universe):
    d = {"фэнтези": f_d, "фантастика": sf_d, "современность": m_d}


class MPart:
    def __init__(self, name, args, story):
        self.curr = 0
        self.name = name
        for i in range(len(args)):
            args[i] = story.get_char(args[i])

        self.characters = {}
        self.curr = 0
        for i in range(len(args)):
            char = args[i].name
            self.characters[f'p{i + 1}'] = char


class Story:
    def __init__(self, title, universe, genre, plot):
        self.text = []
        self.curr = 0
        self.title = title
        self.universe = universe
        self.genre = genre
        self.plot = plot
        self.characters = []
        self.middle = middle
        if plot == 'восхождение':
            self.start = end
            self.end = start
        else:
            self.start = start
            self.end = end

    def add_character(self, character):
        self.characters.append(character)

    def get_char(self, name):
        r = ''
        for chr in self.characters:
            if chr.name == name:
                r = chr
                break
        return r

    def list_all_char(self):
        s = []
        for char in self.characters:
            s.append(char.name)
        return s

    def generate_part(self, mplot):
        part = ''
        while mplot.curr < 3:
            n = randint(1, 4)
            for _ in range(n):
                s = ''
                t = choice(s_types)
                for e in t:
                    if e == 'char':
                        name_prob = randint(0, 99)
                        char = choice(list(mplot.characters.keys()))
                        if name_prob > 60:
                            chr = self.get_char(mplot.characters[char])
                            if chr.gender == 'm':
                                s += 'он '
                            else:
                                s += 'она '
                        else:
                            s += mplot.characters[char].capitalize() + ' '
                    else:
                        if self.genre == 'романтика':
                            g = rom_words
                        elif self.genre == 'приключения':
                            g = adv_words
                        else:
                            g = horr_words
                        if self.curr == 0:
                            all_words = self.start
                        elif self.curr == 1:
                            all_words = self.middle
                        else:
                            all_words = self.end
                        if self.universe == 'фантастика':
                            u_words = sf_d
                        elif self.universe == 'фэнтези':
                            u_words = f_d
                        else:
                            u_words = m_d
                    if e == 'verb':
                        s += choice(choice([all_words, u_words, g])['глаголы']) + ' '
                    if e == 'nomen':
                        s += choice(choice([all_words, u_words, g])['существительные']) + ' '
                    if e == 'adj':
                        s += choice(choice([all_words, u_words, g])['прилагательные']) + ' '
                    if e == '.':
                        s += '.'
                s += '.'
                part += s
            if mplot.curr == 0:
                s = choice(list(d_sentences[mplot.name][0])[1:])
                for e in mplot.characters:
                    s = s.replace(e, f'{mplot.characters[e].capitalize()}')
                part += s

            if mplot.curr == 1:
                s = choice(list(d_sentences[mplot.name][1])[1:])
                for e in mplot.characters:
                    s = s.replace(e, f'{mplot.characters[e].capitalize()}')
                part += s

            if mplot.curr == 2:
                s = choice(list(d_sentences[mplot.name][2])[1:])
                for e in mplot.characters:
                    s = s.replace(e, f'{mplot.characters[e].capitalize()}')
                part += s
            mplot.curr += 1

        fr_nw = requests.post("https://pelevin.gpt.dobro.ai/generate/",
                              data=json.dumps({"prompt": part, "length": 20})).json()
        fr_nw = fr_nw['replies'][0]
        if fr_nw[-1] == '.':
            part += fr_nw
        else:
            part += fr_nw + '.'
        part = part.replace(' .', '.').replace('.', '. ').replace('  ', ' ')
        n_part = ''
        part = part.split('.')
        for e in part:
            if e == ' ':
                continue
            e = e.strip().replace('\n', ' ')
            n_part += capitalize(e) + '. '
        return n_part


class Character:
    def __init__(self, name, gender):
        if gender in {'мужчина', 'парень', 'мальчик'}:
            self.gender = 'm'
        else:
            self.gender = 'f'
        self.name = name
