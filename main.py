import os

from google.auth import exceptions
from googleapiclient.errors import HttpError

from edit_xls.writer_sheets import Connector, add_data, create_total_report, add_to_global_report
from pars_xls.pars_xls import get_data_from_dikidi
from pars_xls.pars_xls import get_data_from_xls
from utils.date_client import get_date_from_file, get_date_to_daly_report, get_date_to_general_report
from utils.errors import DayIsEmptyError, SheetNotFoundByTitleError
from utils.parser_input import TILDA, IS_FROM_FILE, MODE, DATE
from utils.update_cert import check_and_update_cert

from utils.config_val import \
    check_env_val, \
    WORK_DIR, \
    SIMPLE_SHEET_ID, \
    IS_FROM_FILE_CONF, \
    TILDA_CONF, \
    FILE_PATH, \
    GENERAL_SHEET_ID


def main():
    check_env_val()
    google_sheet = Connector(SIMPLE_SHEET_ID)

    is_from_file = IS_FROM_FILE if IS_FROM_FILE else IS_FROM_FILE_CONF

    if is_from_file:
        file_path = FILE_PATH
        data_xls = get_data_from_xls(file_path)
        title = get_date_from_file(file_path)

    else:
        tilda = TILDA if TILDA is not None else TILDA_CONF
        title, data_xls = get_data_from_dikidi(tilda)

    client = google_sheet.create_report(data_xls, title)
    add_data(data_xls, client)


def test(date):
    title_day = get_date_to_daly_report(date)
    title_total = get_date_to_general_report(date)
    sheet_titles_certs = ["Серт 2022", "Серт 2023"]

    google_sheet = Connector(SIMPLE_SHEET_ID)
    daily_report = google_sheet.read_sheet_by_title(title_day)
    total_report = create_total_report(daily_report, date)

    google_sheet = Connector(GENERAL_SHEET_ID)
    update_total_report = check_and_update_cert(google_sheet, total_report, sheet_titles_certs)
    add_to_global_report(google_sheet, update_total_report, title_total)


if __name__ == "__main__":
    try:
        if MODE:
            print("Mode")
            if not DATE:
                print('-u and -day=13.08.23')
                exit(1)
            test(DATE)
        else:
            main()

    except HttpError as er:
        if er.status_code == 400 and "уже существует" in str(er.error_details):
            print(f'ОШИБКА: {str(er.error_details)}\nВыберете другой день')
            exit(1)
    except exceptions.RefreshError as er:
        os.remove(f"{WORK_DIR}edit_xls/keys/token.json")
        print('Авторизуйтесь в google акаунт')
        if MODE:
            print("Mode")
            if not DATE:
                print('-u and -day=13.08.23')
                exit(1)
            test(DATE)
        else:
            main()
    except DayIsEmptyError as er:
        print("На выбранный день нет записей!\nВыберете другой день или добавьте клиентов в dikidi")
        exit(1)
    except SheetNotFoundByTitleError as er:
        print(f'Таблица с заголовком "{er.args[0]["title"]}" не найдена')
