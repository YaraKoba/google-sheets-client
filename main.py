import os
from typing import List

from google.auth import exceptions
from googleapiclient.errors import HttpError

from google_sheet_client.connectors import StartDaily, EndDaily, AllCerts
from google_sheet_client.connectors import Connector
from models.passnger_models import PassengerWhoFlew
from utils.config_val import \
    check_env_val, \
    WORK_DIR, \
    SIMPLE_SHEET_ID, \
    FILE_PATH, \
    GENERAL_SHEET_ID
from utils.date_client import get_date_to_daly_report
from utils.errors import DayIsEmptyError, SheetNotFoundByTitleError
from utils.parser_input import IS_FROM_FILE, MODE, DATE


class Main:
    def __init__(self, mode_program: str = 'start'):
        check_env_val()
        self.mode = mode_program
        self.daly_list_name = get_date_to_daly_report(DATE)

        if mode_program == 'start':
            self.start_day()
        else:
            self.end_day()

    def start_day(self):
        google_sheet = Connector(SIMPLE_SHEET_ID)
        start_day = StartDaily(self.daly_list_name, google_sheet, DATE, is_from_file=IS_FROM_FILE, file_path=FILE_PATH)
        start_day.write_passengers_to_sheet()

    def end_day(self):
        con = Connector(SIMPLE_SHEET_ID)
        end_day = EndDaily(self.daly_list_name, con, DATE)
        self.check_cert(end_day.passengers, mark=True)

    @staticmethod
    def check_cert(passengers: List[PassengerWhoFlew], mark: bool = False):
        con = Connector(GENERAL_SHEET_ID)
        certs = AllCerts(passengers, con)
        certs.check_cert(mark)
        certs.write_global_sheet()
        certs.create_terminal_report()


if __name__ == "__main__":
    try:
        main = Main(MODE)

    except HttpError as er:
        if er.status_code == 400 and "уже существует" in str(er.error_details):
            print(f'ОШИБКА: {str(er.error_details)}\nВыберете другой день')
            exit(1)
    except exceptions.RefreshError as er:
        os.remove(f"{WORK_DIR}google_sheet_client/keys/token.json")
        print('Авторизуйтесь в google акаунт')
        mode = Main(MODE)
    except DayIsEmptyError as er:
        print("На выбранный день нет записей!\nВыберете другой день или добавьте клиентов в dikidi")
        exit(1)
    except SheetNotFoundByTitleError as er:
        print(f'Таблица с заголовком "{er.args[0]["title"]}" не найдена')
