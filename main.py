import configparser
import os
from google.auth import exceptions
from pars_xls.pars_xls import get_data_from_xls
from edit_xls.writer_sheets import Connector, add_data
from pars_xls.pars_xls import get_data_from_dikidi
from utils.date_client import get_date_from_file
from utils.errors import DayIsEmptyError, SheetNotFoundByTitleError
from utils.parser_input import TILDA, IS_FROM_FILE
from utils.config_val import check_env_val, WORK_DIR
from googleapiclient.errors import HttpError


def load_config():
    conf = configparser.ConfigParser()
    conf.read(f'{WORK_DIR}config.ini')
    return conf


def main():
    try:
        check_env_val()
        config = load_config()
        simple_spreadsheet_id = config.get('sheet', 'sheet_id', fallback='')
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


def test():
    try:
        config = load_config()
        simple_spreadsheet_id = config.get('sheet', 'sheet_id', fallback='')
        google_sheet = Connector(simple_spreadsheet_id)
        title = "16 августа"
        new_list = []
        result = google_sheet.read_sheet_by_id(title)
        for index in range(2, len(result)):
            line = result[index]

            print(line)
    except SheetNotFoundByTitleError as er:
        print(f'Таблица с заголовком "{er.args[0]["title"]}" не найдена')


if __name__ == "__main__":
    main()
