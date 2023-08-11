import configparser
import os

import google
from google.auth import exceptions

from pars_xls.pars_xls import get_data_from_xls
from edit_xls.writer_sheets import create_report, get_inf_cell, get_index_sheet, add_data
from pars_xls.pars_xls import get_data_from_dikidi
from utils.date_client import get_date_from_file
from dotenv import load_dotenv
from utils.parser_input import TILDA, IS_FROM_FILE
from googleapiclient.errors import HttpError

load_dotenv()

def load_config():
    work_dir = os.getenv("work_dir")
    conf = configparser.ConfigParser()
    conf.read(f'{work_dir}config.ini')
    return conf


def main():
    try:
        config = load_config()
        simple_spreadsheet_id = config.get('sheet', 'sheet_id', fallback='')
        is_from_file = IS_FROM_FILE if IS_FROM_FILE else config.getboolean('set', 'from_file', fallback=False)

        if is_from_file:
            file_path = config.get('File', 'file_path', fallback='')
            data_xls = get_data_from_xls(file_path)
            title = get_date_from_file(file_path)

        else:
            tilda = TILDA if TILDA else config.getint('conf', 'tilda', fallback=0)
            title, data_xls = get_data_from_dikidi(tilda)

        client = create_report(data_xls, title, simple_spreadsheet_id)
        add_data(data_xls, client)
    except HttpError as er:
        if er.status_code == 400 and "уже существует" in str(er.error_details):
            print(f'ОШИБКА: {str(er.error_details)}\nВыберете другой день')
            exit()
    except exceptions.RefreshError as er:
        work_dir = os.getenv("work_dir")
        os.remove(f"{work_dir}edit_xls/keys/token.json")
        print('Авторизуйтесь в google акаунт')
        main()


if __name__ == "__main__":
    main()
