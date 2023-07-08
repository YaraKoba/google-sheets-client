import pandas as pd
import phonenumbers
import re

REGEX_NAME = r'^(?:.*\n){1}(.*)$'
REGEX_AMOUNT = r'(\d{4}) RUB'
REGEX_COMPANY = r'[Xx][Ff]'
REGEX_SERT_INST = r'(?:(?<=\s)0\d+)|(?<=\s)\d{5,6}(?=\s)'
REGEX_SERT_XF = r'[Сс]ерт'
REGEX_VIDEO = r'\+\s?[Вв]идео'
REGEX_TIME = r'^\d{2}:\d{2}'
REGEX_DOP = r'[Дд]оплата.(\d+)'


def get_data_from_xls(file_path):
    # Чтение файла XLS
    df = pd.read_excel(file_path, index_col=0)

    # Инициализация словаря
    data_dict = []

    # Преобразование данных в словарь
    for index, row in df.iterrows():
        if type(row.values.item()) is str:
            tmp_dict = {
                        'time': '',
                        'name': '',
                        'amount': 0,
                        'company': '',
                        'number': 0,
                        'sert': False,
                        'sert_id': 0,
                        'video': False,
                        'doplata': 0,
                        }

            text = row.values.item()

            match_time = re.search(REGEX_TIME, text)
            tmp_dict['time'] = match_time.group(0)

            match_name = re.search(REGEX_NAME, text, re.MULTILINE)
            tmp_dict['name'] = match_name.group(1)

            for m in phonenumbers.PhoneNumberMatcher(row.values.item(), 'RU'):
                tmp_dict['number'] = phonenumbers.format_number(m.number, phonenumbers.PhoneNumberFormat.E164)

            match_amount = re.search(REGEX_AMOUNT, text, re.MULTILINE)
            tmp_dict['amount'] = match_amount.group(1)

            match_company = re.search(REGEX_COMPANY, text)
            tmp_dict['company'] = 'Инст' if not match_company else 'XF'

            if tmp_dict['company'] == 'XF':
                match_sert_xf = re.search(REGEX_SERT_XF, text)
                if match_sert_xf:
                    tmp_dict['sert'] = True

            else:
                match_sert_inst = re.search(REGEX_SERT_INST, text)
                if match_sert_inst:
                    tmp_dict['sert'] = True
                    tmp_dict['sert_id'] = match_sert_inst.group(0)

            match_video = re.search(REGEX_VIDEO, text)
            tmp_dict['video'] = True if match_video else False

            match_dop = re.search(REGEX_DOP, text)
            tmp_dict['doplata'] = 0 if not match_dop else match_dop.group(1)

            data_dict.append(tmp_dict)

    return data_dict
