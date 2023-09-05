import re
from typing import List, Dict
from utils.parser_input import AIGUL
from edit_xls.writer_sheets import Connector
from edit_xls.google_sheets_client import SheetClient
from utils.formats import YELLOW
from pydantic import BaseModel
from dataclasses import dataclass

REGEX_CERT_INST = r'\b\d{5,8}\b'


def get_clients(sheets, group: str) -> SheetClient:
    return sheets[group]


def one_format_to_cert(number: tuple | None) -> tuple | None:
    if not number:
        return None
    m, y, n = number
    if len(n) == 3:
        if n[0] != '0':
            new_sep = ''.join((m, y, n,))
            m = new_sep[0:2]
            y = new_sep[2:4]
            n = new_sep[4:]
        else:
            n = n[1:]
    elif len(n) == 1:
        n = '0' + n

    number = (m, y, n,)

    return number


def separate_cert(cert: str):
    if not cert or cert[0].isalpha():
        return None

    if cert[0] == "0" or cert[0:2] in ["10", "11"]:
        month = cert[1:2] if cert[0] == "0" else cert[0:2]
        year = cert[2:4]
        number = cert[4:]
    elif cert[0] != '1':
        month = cert[0:1]
        year = cert[1:3]
        number = cert[3:]
    elif cert[2] != "2":
        month = cert[0:1]
        year = cert[1:3]
        number = cert[3:]
    else:
        month = cert[0:1]
        year = cert[1:3]
        number = cert[3:]

    return one_format_to_cert((month, year, number,))


def two_point_search(cert: List, data: List[List[str]]) -> Dict:
    cert = sorted([int(''.join(separate_cert(c))) for c in cert])
    len_data = len(data)
    left, right, middle = 2, len_data, len_data // 2

    result_dict = {}
    for num_cert in cert:

        while int(''.join(separate_cert(data[middle][0]))) != num_cert and left < middle:
            middle_num = int(''.join(separate_cert(data[middle][0])))
            if middle_num > num_cert:
                right = middle
            else:
                left = middle

            middle = (right + left) // 2

        right = len_data
        if left >= middle and int(''.join(separate_cert(data[middle][0]))) != num_cert:
            result_dict[num_cert] = {'is_define': False, 'line': None}
            left = middle
            middle = (left + right) // 2
        else:
            result_dict[num_cert] = {'is_define': True, 'line': middle + 1}

    return result_dict


def is_yellow(color: Dict):
    flag = False
    for c in color:
        if c in ['red', 'green'] and color[c] == 1:
            flag = True
        else:
            flag = False

    return flag


def update_cert(searched_cert: Dict[str, Dict[str, SheetClient | Dict[int, Dict[str, int | bool]]]]):
    result = {'already_fly': [], 'not_define': [], 'done': []}
    for group in searched_cert:
        client = searched_cert[group]["client"]
        for cert in searched_cert[group]["cert"]:
            cert_inf = searched_cert[group]["cert"][cert]
            number, is_define, line = cert, cert_inf["is_define"], cert_inf['line']
            print(number, line, client.get_format(f"A{line}:B{line}"))

            if not is_define:
                result['not_define'].append(number)
            else:
                val, color = client.get_format(f"A{line}:B{line}")
                if is_yellow(color):
                    result['already_fly'].append(number)
                else:
                    client.format_cell(line-1, line, 0, 7, bg_rgba=YELLOW)
                    client.update_borders(line-1, line, 0, 7)
                    client.execute()
                    result["done"].append(number)

    return result


def check_and_update_cert(google_sheet: Connector, total_report: List[List[str]], sheet_titles: List):
    sheets = {title: google_sheet.get_client_by_title(title) for title in sheet_titles}
    cert_groups = {t: [] for t in sheet_titles}
    for line in total_report:
        math = re.search(REGEX_CERT_INST, line[3])
        if math:
            cert_number = math.group(0)
            title_cert = "Серт 20" + separate_cert(cert_number)[1]
            if title_cert not in sheet_titles:
                for g in cert_groups:
                    cert_groups[g].append(cert_number)
            else:
                cert_groups[title_cert].append(cert_number)

    searched_cert = {}
    for group in cert_groups:
        cert_numbers = cert_groups[group]
        if cert_numbers:
            client = get_clients(sheets, group)
            data = client.get_data_from_sheet()
            searched_cert[group] = {}
            searched_cert[group]['cert'] = two_point_search(cert_numbers, data)
            searched_cert[group]["client"] = client

    update_certs = update_cert(searched_cert)
    print(update_certs)
    aigul = 3000 / len(total_report) * AIGUL
    our, xf_cash, xf_cert = 0, 0, 0

    for line in range(len(total_report)):
        math = re.search(REGEX_CERT_INST, total_report[line][3])
        if math:
            cert_number = ''.join(separate_cert(math.group(0)))
            if int(cert_number) in update_certs['done']:
                total_report[line].append('-4500')
            elif int(cert_number) in update_certs['not_define']:
                total_report[line].append('Не найден!')
            elif int(cert_number) in update_certs['already_fly']:
                total_report[line].append('Уже летал!')
            else:
                total_report[line].append('ОШИБКА!!!')

            total_report[line] += ['500', '', '500', aigul]
        else:
            total_report[line] += ['', '500', '', '500', aigul]
        if total_report[line][3] == "XF нал":
            xf_cash += 1
        elif total_report[line][3] == "XF серт":
            xf_cert += 1
        else:
            our += 1

    print(f'Наши - {our}\nXF нал - {xf_cash}\nXF серт - {xf_cert}\nTotal - {our+xf_cert+xf_cash}')
    return total_report


if __name__ == '__main__':
    numbr = '12301'
    print(numbr[0:2])
