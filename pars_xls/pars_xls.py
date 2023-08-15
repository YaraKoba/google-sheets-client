import datetime
import re
from utils.config_val import DIKIDI_COMPANY_ID, DIKIDI_LOGIN, DIKIDI_PASSWORD
from dotenv import load_dotenv
from pars_xls.dikidi_api import DikidiAPI
from utils.errors import DayIsEmptyError
import pandas as pd
import phonenumbers

from utils.date_client import get_date_from_str

REGEX_NAME = r'^(?:.*\n){1}(.*)$'
REGEX_AMOUNT = r'(\d{4}) RUB'
REGEX_COMPANY = r'[Xx][Ff]'
REGEX_SERT_INST = r'\b\d{5,8}\b'
REGEX_SERT_XF = r'[Сс]ерт(?:ификат)?'
REGEX_VIDEO = r'\+\s?[Вв](?:идео)?\b'
REGEX_TIME = r'\d{2}:\d{2}'
REGEX_DOP = r'[Дд]оплата.(\d+)'
REGEX_PAYMENT = r'[Оо]пла(?:чено|тила?)'

load_dotenv()


def get_data_from_xls(file_path):
    # Чтение файла XLS
    df = pd.read_excel(file_path, index_col=0)

    # Инициализация словаря
    data_dict = []

    # Преобразование данных в словарь
    for index, row in df.iterrows():
        if type(row.values.item()) is str:
            text = row.values.item()

            one_client = search_inf_in_text(text)

            data_dict.append(one_client)

    return data_dict


def get_data_from_dikidi(tilda):
    log = DIKIDI_LOGIN
    password = DIKIDI_PASSWORD
    company_id = DIKIDI_COMPANY_ID

    date_object = datetime.datetime.combine(datetime.date.today() + datetime.timedelta(days=tilda),
                                            datetime.time.min).strftime('%Y-%m-%d')

    api = DikidiAPI(
        login=log,
        password=password)

    lists = api.get_appointment_list(company_id=company_id, date_start=date_object, date_end=date_object, limit=50)

    if not lists:
        raise DayIsEmptyError("Day is empty, change day or add clients in dikidi")

    data_dict = []
    for l in lists:
        tmp_str = ""
        tmp_str += l["time"][11:] + "\n"
        tmp_str += l["client_title"] + "\n"
        tmp_str += l["services"][0]["cost"] + " RUB" + "\n"
        tmp_str += l["client_phone"] + "\n"
        tmp_str += l["comment"] if l["comment"] else ''
        one_client = search_inf_in_text(tmp_str)

        data_dict.append(one_client)
    date = get_date_from_str(lists[0]["time"])
    sorted_clients = sorted(data_dict, key=lambda x: x["time"])
    return date, sorted_clients


def search_inf_in_text(text):
    tmp_dict = {
        'time': '',
        'name': '',
        'amount': 0,
        'company': '',
        'number': 0,
        'sert': False,
        'sert_id': 0,
        'video': False,
        'PAID': False,
        'doplata': 0,
    }

    match_time = re.search(REGEX_TIME, text)
    tmp_dict['time'] = match_time.group(0)

    match_name = re.search(REGEX_NAME, text, re.MULTILINE)
    tmp_dict['name'] = match_name.group(1)

    for m in phonenumbers.PhoneNumberMatcher(text, 'RU'):
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

    match_payment = re.search(REGEX_PAYMENT, text)
    tmp_dict['paid'] = True if match_payment else False

    return tmp_dict
