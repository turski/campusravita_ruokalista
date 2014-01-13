#!/usr/bin/python3

from urllib.request import urlopen
from html.parser import HTMLParser
from pprint import pprint

url='http://campusravita.fi/index.php?id=2&week=true'

class LunchlistParser(HTMLParser):
    def __init__(self):
        super().__init__(self)
        self.data = []
        self.stack = []
        self.expect = ['lunch_table']

    def handle_starttag(self, tag, args):
        if 'lunch_table' in self.expect:
            if tag == 'table' and ('class', 'lunchlist') in args:
                self.stack.append('lunch_table')
                self.expect = ['lunch_thead']
                return
        if 'lunch_thead' in self.expect:
            if tag == 'thead':
                self.stack.append('lunch_thead')
                self.expect = ['lunch_thead_end']
                return
        if 'day_tr' in self.expect:
            if tag == 'tr' and ('class', 'day_tr') in args:
                self.stack.append('day_tr')
                self.expect = ['day_th']
                return
        if 'day_th' in self.expect:
            if tag == 'th' and ('class', 'day') in args:
                self.stack.append('day_th')
                self.expect = ['day_th_data']
                return
        if 'meal_tr' in self.expect:
            if tag == 'tr':
                self.stack.append('meal_tr')
                self.expect = ['meal_th', 'food_name_td']
                return
        if 'meal_th' in self.expect:
            if tag == 'th':
                self.stack.append('meal_th')
                self.expect = ['meal_th_data']
                return
        if 'food_tr' in self.expect:
            if tag == 'tr':
                self.stack.append('food_tr')
                self.expect = ['food_name_td']
                return
        if 'food_name_td' in self.expect:
            if tag == 'td':
                self.stack.append('food_name_td')
                self.expect = ['food_name_td_data']
                return
        if 'food_name_td_details_span' in self.expect:
            if tag == 'span' and ('class', 'details') in args:
                self.stack.append('food_name_td_details_span')
                self.expect = ['food_name_td_details_span_data']
                return
        if 'food_flags_td' in self.expect:
            if tag == 'td':
                self.stack.append('food_flags_td')
                self.expect = ['food_flags_td_abbr', 'food_flags_td_end']
                return
        if 'food_flags_td_abbr' in self.expect:
            if tag == 'abbr':
                self.stack.append('food_flags_td_abbr')
                self.expect = ['food_flags_td_abbr_data']
                return
        if 'food_price_td' in self.expect:
            if tag == 'td' and ('class', 'print_menu_price') in args:
                self.stack.append('food_price_td')
                self.expect = ['food_price_td_abbr']
                return
        if 'food_price_td_abbr' in self.expect:
            if tag == 'abbr':
                self.stack.append('food_price_td_abbr')
                self.expect = ['food_price_td_abbr_data']
                return

    def handle_data(self, data):
        if 'day_th_data' in self.expect:
            self.data.append({'date': data, 'meals': []})
            self.expect = ['day_th_end']
            return
        if 'meal_th_data' in self.expect:
            self.data[-1]['meals'].append({'meal': data, 'foods': []})
            self.expect = ['meal_th_end']
            return
        if 'food_name_td_data' in self.expect:
            self.data[-1]['meals'][-1]['foods'].append({'name': data, 'details': [], 'flags': [], 'price': None})
            self.expect = ['food_name_td_end', 'food_name_td_details_span']
            return
        if 'food_name_td_details_span_data' in self.expect:
            self.data[-1]['meals'][-1]['foods'][-1]['details'].append(data)
            self.expect = ['food_name_td_details_span_end']
            return
        if 'food_flags_td_abbr_data' in self.expect:
            self.data[-1]['meals'][-1]['foods'][-1]['flags'].append(data)
            self.expect = ['food_flags_td_abbr_end']
            return
        if 'food_price_td_abbr_data' in self.expect:
            self.data[-1]['meals'][-1]['foods'][-1]['price'] = data
            self.expect = ['food_price_td_abbr_end']
            return

    def handle_endtag(self, tag):
        if 'lunch_thead_end' in self.expect:
            if tag == 'thead':
                self.stack.pop()
                self.expect = ['day_tr']
                return
        if 'day_th_end' in self.expect:
            if tag == 'th':
                self.stack.pop()
                self.expect = ['day_tr_end']
                return
        if 'day_tr_end' in self.expect:
            if tag == 'tr':
                self.stack.pop()
                self.expect = ['meal_tr']
                return
        if 'meal_th_end' in self.expect:
            if tag == 'th':
                self.stack.pop()
                self.expect = ['meal_tr_end']
                return
        if 'meal_tr_end' in self.expect:
            if tag == 'tr':
                self.stack.pop()
                self.expect = ['food_tr']
                return
        if 'food_name_td_details_span_end' in self.expect:
            if tag == 'span':
                self.stack.pop()
                self.expect = ['food_name_td_end', 'food_name_td_details_span']
                return
        if 'food_name_td_end' in self.expect:
            if tag == 'td':
                self.stack.pop()
                self.expect = ['food_flags_td']
                return
        if 'food_flags_td_abbr_end' in self.expect:
            if tag == 'abbr':
                self.stack.pop()
                self.expect = ['food_flags_td_abbr', 'food_flags_td_end']
                return
        if 'food_flags_td_end' in self.expect:
            if tag == 'td':
                self.stack.pop()
                self.expect = ['food_price_td']
                return
        if 'food_price_td_abbr_end' in self.expect:
            if tag == 'abbr':
                self.stack.pop()
                self.expect = ['food_price_td_end']
                return
        if 'food_price_td_end' in self.expect:
            if tag == 'td':
                self.stack.pop()
                self.expect = ['food_tr_end']
                return
        if 'food_tr_end' in self.expect:
            if tag == 'tr':
                self.stack.pop()
                self.expect = ['food_tr', 'meal_tr', 'day_tr']


d = urlopen(url).read().decode()
l = LunchlistParser()
l.feed(d)
pprint(l.data)
