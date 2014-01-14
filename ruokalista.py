#!/usr/bin/python3

from urllib.request import urlopen
from html.parser import HTMLParser
from pprint import pprint
from time import time

url='http://campusravita.fi/index.php?id=2&week=true'

class Tag:
    def __init__(self, name, tag, typ, arg=None, action=None, expect=None):
        self.name = name
        assert tag in ['table', 'thead', 'tr', 'th', 'td', 'abbr', 'span']
        self.tag = tag
        assert typ in ['start', 'data', 'end']
        self.typ = typ
        assert not arg or (type(arg) == tuple and len(arg) == 2)
        self.arg = arg
        assert action == None or callable(action)
        self.action = action
        self.expect = expect

class LunchlistParser(HTMLParser):
    def __init__(self):
        super().__init__(self)
        self.data = []
        self.expect = [Tag('lunch', 'table', 'start', arg=('class', 'lunchlist'))]
        self.starttags = [
                Tag('lunch', 'table', 'start', arg=('class', 'lunchlist'),
                        expect=[Tag('lunch', 'thead', 'start')]),
                Tag('lunch', 'thead', 'start',
                        expect=[Tag('lunch', 'thead', 'end')]),
                Tag('day', 'tr', 'start', arg=('class', 'day_tr'),
                        expect=[Tag('day', 'th', 'start')]),
                Tag('day', 'th', 'start', arg=('class', 'day'),
                        expect=[Tag('day', 'th', 'data')]),
                Tag('meal_or_food', 'tr', 'start',
                        expect=[Tag('meal', 'th', 'start'), Tag('food_name', 'td', 'start')]),
                Tag('meal', 'th', 'start',
                        expect=[Tag('meal', 'th', 'data'), Tag('meal', 'th', 'end')]),
                Tag('food_name', 'td', 'start',
                        expect=[Tag('food_name', 'td', 'data')]),
                Tag('food_details', 'span', 'start', arg=('class', 'details'),
                        expect=[Tag('food_details', 'span', 'data')]),
                Tag('food_flags', 'td', 'start',
                        expect=[Tag('food_flags', 'abbr', 'start'), Tag('food_flags', 'td', 'end')]),
                Tag('food_flags', 'abbr', 'start',
                        expect=[Tag('food_flags', 'abbr', 'data')]),
                Tag('food_price', 'td', 'start',
                        expect=[Tag('food_price', 'abbr', 'start'), Tag('food_price', 'td', 'end')]),
                Tag('food_price', 'abbr', 'start',
                        expect=[Tag('food_price', 'abbr', 'data'), Tag('food_price', 'abbr', 'end')])]
        self.datatags = [
                Tag('day', 'th', 'data', action = self.add_day,
                        expect=[Tag('day', 'th', 'end')]),
                Tag('meal', 'th', 'data', action = self.add_meal,
                        expect=[Tag('meal', 'th', 'end')]),
                Tag('food_name', 'td', 'data', action = self.add_food,
                        expect=[Tag('food_name', 'td', 'end'), Tag('food_details', 'span', 'start')]),
                Tag('food_details', 'span', 'data', action = self.add_food_detail,
                        expect=[Tag('food_details', 'span', 'end')]),
                Tag('food_flags', 'abbr', 'data', action = self.add_food_flag,
                        expect=[Tag('food_flags', 'abbr', 'end')]),
                Tag('food_price', 'abbr', 'data', action = self.add_food_price,
                        expect=[Tag('food_price', 'abbr', 'end')])]
        self.endtags = [
                Tag('lunch', 'thead', 'end',
                        expect=[Tag('day', 'tr', 'start')]),
                Tag('day', 'th', 'end',
                        expect=[Tag('day', 'tr', 'end')]),
                Tag('day', 'tr', 'end',
                        expect=[Tag('meal_or_food', 'tr', 'start')]),
                Tag('meal', 'th', 'end',
                        expect=[Tag('meal', 'tr', 'end')]),
                Tag('meal', 'tr', 'end',
                        expect=[Tag('meal_or_food', 'tr', 'start'), Tag('lunch', 'table', 'end')]),
                Tag('food_details', 'span', 'end',
                        expect=[Tag('food_name', 'td', 'end'), Tag('food_details', 'span', 'start')]),
                Tag('food_name', 'td', 'end',
                        expect=[Tag('food_flags', 'td', 'start')]),
                Tag('food_flags', 'abbr', 'end',
                        expect=[Tag('food_flags', 'abbr', 'start'), Tag('food_flags', 'td', 'end')]),
                Tag('food_flags', 'td', 'end',
                        expect=[Tag('food_price', 'td', 'start')]),
                Tag('food_price', 'abbr', 'end',
                        expect=[Tag('food_price', 'td', 'end')]),
                Tag('food_price', 'td', 'end',
                        expect=[Tag('food', 'tr', 'end')]),
                Tag('food', 'tr', 'end',
                        expect=[Tag('day', 'tr', 'start'), Tag('meal_or_food', 'tr', 'start'), Tag('lunch', 'table', 'end')]),
                Tag('lunch', 'table', 'end',
                        expect=[])]

    def add_day(self, data):
        self.data.append({'date': data, 'meals': []})

    def add_meal(self, data):
        self.data[-1]['meals'].append({'meal': data, 'foods': []})

    def add_food(self, data):
        self.data[-1]['meals'][-1]['foods'].append({'name': data, 'details': [], 'flags': [], 'price': None})
    
    def add_food_detail(self, data):
        self.data[-1]['meals'][-1]['foods'][-1]['details'].append(data)
    
    def add_food_flag(self, data):
        self.data[-1]['meals'][-1]['foods'][-1]['flags'].append(data)

    def add_food_price(self, data):
        self.data[-1]['meals'][-1]['foods'][-1]['price'] = data

    def handle_starttag(self, tag, args):
        for e in self.expect:
            if e.tag == tag and e.typ == 'start':
                for t in self.starttags:
                    if t.name == e.name and t.tag == e.tag:
                        if t.arg != None and t.arg not in args:
                            continue
                        self.expect = t.expect
                        return

    def handle_data(self, data):
        for e in self.expect:
            if e.typ == 'data':
                for t in self.datatags:
                    if t.name == e.name:
                        self.expect = t.expect
                        if t.action:
                            t.action(data)
                        return

    def handle_endtag(self, tag):
        for e in self.expect:
            if e.tag == tag and e.typ == 'end':
                for t in self.endtags:
                    if t.name == e.name and t.tag == e.tag and t.typ == e.typ:
                        if t.arg != None and t.arg not in args:
                            continue
                        self.expect = t.expect
                        return


l = LunchlistParser()
r = urlopen(url)
t = time()
l.feed(r.read().decode())
t = time() - t
pprint(l.data)
print(t)
