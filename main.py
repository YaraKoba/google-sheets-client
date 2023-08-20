import configparser
import os
from google.auth import exceptions
from pars_xls.pars_xls import get_data_from_xls
from edit_xls.writer_sheets import Connector, add_data, create_total_report, add_to_global_report
from pars_xls.pars_xls import get_data_from_dikidi
from utils.date_client import get_date_from_file, get_date_from_str_dot, get_inf_date_from_str_dot
from utils.errors import DayIsEmptyError, SheetNotFoundByTitleError
from utils.parser_input import TILDA, IS_FROM_FILE, MODE, DATE
from utils.config_val import check_env_val, WORK_DIR
from utils.update_cert import check_and_update_cert
from googleapiclient.errors import HttpError


def load_config():
    conf = configparser.ConfigParser()
    conf.read(f'{WORK_DIR}config.ini')
    return conf


config = load_config()
simple_spreadsheet_id = config.get('sheet', 'sheet_id', fallback='')
general_sheet_id = config.get('sheet', "sheet_id_general_report", fallback='')

def main():
    try:
        check_env_val()
        google_sheet = Connector(simple_spreadsheet_id)

        is_from_file = IS_FROM_FILE if IS_FROM_FILE else config.getboolean('set', 'from_file', fallback=False)

        if is_from_file:
            file_path = config.get('File', 'file_path', fallback='')
            data_xls = get_data_from_xls(file_path)
            title = get_date_from_file(file_path)

        else:
            tilda = TILDA if TILDA is not None else config.getint('conf', 'tilda', fallback=0)
            title, data_xls = get_data_from_dikidi(tilda)

        client = google_sheet.create_report(data_xls, title)
        add_data(data_xls, client)

    except HttpError as er:
        if er.status_code == 400 and "уже существует" in str(er.error_details):
            print(f'ОШИБКА: {str(er.error_details)}\nВыберете другой день')
            exit(1)
    except exceptions.RefreshError as er:
        os.remove(f"{WORK_DIR}edit_xls/keys/token.json")
        print('Авторизуйтесь в google акаунт')
        main()
    except DayIsEmptyError as er:
        print("На выбранный день нет записей!\nВыберете другой день или добавьте клиентов в dikidi")
        exit(1)
    except SheetNotFoundByTitleError as er:
        print(f'Таблица с заголовком "{er.args[0]["title"]}" не найдена')


def test(date):
    try:
        title_day = get_date_from_str_dot(date)
        title_total = get_inf_date_from_str_dot(date)
        sheet_titles_certs = ["Серт 2022", "Серт 2023"]

        google_sheet = Connector(simple_spreadsheet_id)
        daily_report = google_sheet.read_sheet_by_id(title_day)
        total_report = create_total_report(daily_report, date)

        google_sheet = Connector(general_sheet_id)
        update_total_report = check_and_update_cert(google_sheet, total_report, sheet_titles_certs)
        add_to_global_report(google_sheet, update_total_report, title_total)

    except SheetNotFoundByTitleError as er:
        print(f'Таблица с заголовком "{er.args[0]["title"]}" не найдена')


if __name__ == "__main__":
    if MODE:
        if not DATE:
            print('-u and -day=13.08.23')
            exit(1)
        test(DATE)
    else:
        main()
