from pars_xls.pars_xls import get_data_from_xls
from edit_xls.writer_sheets import create_report, get_inf_cell, get_index_sheet, add_data
from utils.date_client import get_date_from_file
import configparser


def load_config():
    conf = configparser.ConfigParser()
    conf.read('./config.ini')
    return conf


def main():
    config = load_config()
    simple_spreadsheet_id = config.get('sheet', 'sheet_id', fallback='')
    file_path = config.get('File', 'file_path', fallback='')
    data_xls = get_data_from_xls(file_path)

    title = get_date_from_file(file_path)
    client = create_report(data_xls, title, simple_spreadsheet_id)

    add_data(data_xls, client)


if __name__ == "__main__":
    main()
