import json
import os
from typing import List

from google.auth import exceptions
from googleapiclient.errors import HttpError

from google_sheet_client.connectors import StartDaily, EndDaily, AllCerts
from google_sheet_client.connectors import Connector
from models.passnger_models import PassengerWhoFlew, NewPassenger, Certificate
from utils.config_val import \
    check_env_val, \
    WORK_DIR, \
    SIMPLE_SHEET_ID, \
    FILE_PATH, \
    GENERAL_SHEET_ID
from utils.date_client import get_date_to_daly_report
from utils.errors import DayIsEmptyError, SheetNotFoundByTitleError
from utils.parser_input import IS_FROM_FILE, MODE, DATE


def get_passengers(list_name, date) -> StartDaily:
    con = Connector(SIMPLE_SHEET_ID)
    day = StartDaily(list_name=list_name, date=date, connector=con, debug=True)
    return day


def read_passenger_from_json(date):
    with open(f'{WORK_DIR}tests/tests_data/{date}.json', 'r', encoding='utf-8') as file:
        result = json.load(file)
        res = []
        for one in result:
            new_ps = NewPassenger(**one)
            if new_ps.cert:
                new_ps.cert = Certificate(is_cert=new_ps.cert['is_cert'], number=new_ps.cert['number'])

            res.append(new_ps)

        return res


def check_passengers(one: List, two: List):
    while one and two:
        ps1 = one.pop(0)
        ps2 = two.pop(0)

        print(ps1)
        print(ps2)

        assert ps1 == ps2


def test_passengers():
    list_days = ['18.08.23']
    for day in list_days:
        name = get_date_to_daly_report(day)
        passengers = get_passengers(name, day).passengers
        correct_passengers = read_passenger_from_json(day)
        check_passengers(correct_passengers, passengers)