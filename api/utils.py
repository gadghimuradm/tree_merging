import difflib
import re
import json
import xmltodict
from xml.etree import ElementTree
from dateutil import parser
from abc import ABC, abstractmethod


class Animal(ABC):

    @abstractmethod
    def speak(self):
        pass


class TreeMerger(ABC):
    tree = None

    def __init__(self, request_body):
        try:
            self.merge_trees(self.parser(request_body))
            self.normalize_data(self.tree)
        except Exception:
            self.tree = None

    @abstractmethod
    def parser(self, request_body) -> dict:
        pass

    def make_lists(self, dictionary):
        result = {}
        for key, value in dictionary.items():
            if key.endswith(']'):
                key = key.split('[')[0]
                if key in result.keys():
                    if isinstance(result[key], dict):
                        result[key].update(self.make_lists(value))
                    elif isinstance(result[key], list):
                        result[key].append(value)
                    else:
                        result[key] = [result[key], value]
                else:
                    result[key] = value
            else:
                result[key] = value
        return result

    def merge_trees(self, data):
        result = {}

        for _, tree in data.items():
            for key, value in tree.items():
                key = key.split('[')[0]
                if key in result.keys():
                    if isinstance(result[key], dict):
                        result[key].update(self.make_lists(value))
                    elif isinstance(result[key], list):
                        result[key].append(value)
                    else:
                        result[key] = [result[key], value]
                else:
                    result[key] = value
        self.tree = result

    def get_tree(self):
        return self.tree

    def get_normalizers(self):
        return {
            'ДатаДокумента': self.normalize_date,
            'СрокОплаты': self.normalize_time_period,
        }

    def normalize_data(self, data):
        if isinstance(data, dict):
            for key, value in data.items():
                if key in self.get_normalizers():
                    data[key] = self.get_normalizers()[key](value)
                elif isinstance(value, dict):
                    result = self.normalize_data(value)
                    if result is not None:
                        return result

    @staticmethod
    def normalize_date(date):
        try:
            parsed_date = parser.parse(date, dayfirst=True, fuzzy=True)
            return parsed_date.strftime('%d.%m.%Y')
        except ValueError:
            return date

    @staticmethod
    def normalize_time_period(input_str):
        result = {
            "Г": 0,
            "М": 0,
            "Н": 0,
            "Д": 0
        }

        matches = re.findall(r'(\d+)\s*(\w+)', input_str)

        units = ["год", "месяц", "неделя", "день"]

        for match in matches:
            if not match[0].isdigit():
                continue
            value = int(match[0])
            unit = match[1]

            closest_unit = difflib.get_close_matches(unit, units, n=1, cutoff=0.5)
            if closest_unit:
                closest_unit = closest_unit[0]
            else:
                continue

            index = units.index(closest_unit)

            result[list(result.keys())[index]] += value

        return f"{result['Г']}_{result['М']}_{result['Н']}_{result['Д']}"


class XMLTreeMerger(TreeMerger):

    def parser(self, request_body) -> dict:
        return json.loads(json.dumps(xmltodict.parse(request_body), indent=4), object_hook=self._decode)["root"]

    def _decode(self, o):
        if isinstance(o, str) and o.isdigit():
            return int(o)
        elif isinstance(o, dict):
            return {k: self._decode(v) for k, v in o.items()}
        elif isinstance(o, list):
            return [self._decode(v) for v in o]
        else:
            return o


class JSONTreeMerger(TreeMerger):
    def parser(self, request_body) -> dict:
        return json.loads(request_body)
