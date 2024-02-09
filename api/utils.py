import difflib
import re

from dateutil import parser


def _decode(o):
    if isinstance(o, str) and o.isdigit():
        return int(o)
    elif isinstance(o, dict):
        return {k: _decode(v) for k, v in o.items()}
    elif isinstance(o, list):
        return [_decode(v) for v in o]
    else:
        return o


def make_lists(json_data):
    result = {}
    for key, value in json_data.items():
        key_name = key.split("[")[0]

        if key_name in result:
            result[key_name].append(value)
        else:
            result[key_name] = [value]
    return result


def merge_trees(data):
    result = {}

    for _, tree in data.items():
        for key, value in tree.items():
            key = key.split("[")[0]

            if key in result.keys():
                if isinstance(result[key], dict):
                    result[key].update(value)
                elif isinstance(result[key], list):
                    result[key].append(value)
                else:
                    result[key] = [result[key], value]
            else:
                result[key] = value

    return result


def normalize_date(date):
    try:
        parsed_date = parser.parse(date, dayfirst=True, fuzzy=True)
        normalized_date = parsed_date.strftime('%d.%m.%Y')
        return normalized_date
    except ValueError:
        return date


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


def normalize_data(data):
    normalizers = {
        'ДатаДокумента': normalize_date,
        'СрокОплаты': normalize_time_period,
    }
    if isinstance(data, dict):
        for key, value in data.items():
            if key in normalizers:
                data[key] = normalizers[key](value)
            elif isinstance(value, dict):
                result = normalize_data(value)
                if result is not None:
                    return result
