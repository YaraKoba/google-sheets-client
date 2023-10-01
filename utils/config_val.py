import configparser
import os
from dotenv import load_dotenv

load_dotenv()

WORK_DIR = os.getenv("WORK_DIR")
DIKIDI_PASSWORD = os.getenv("DIKIDI_PASSWORD")
DIKIDI_LOGIN = os.getenv("DIKIDI_LOGIN")
DIKIDI_COMPANY_ID = os.getenv("DIKIDI_COMPANY_ID")


def load_config():
    conf = configparser.ConfigParser()
    conf.read(f'{WORK_DIR}config.ini')
    return conf


config = load_config()

SIMPLE_SHEET_ID = config.get('sheet', 'sheet_id', fallback='')
GENERAL_SHEET_ID = config.get('sheet', "sheet_id_general_report", fallback='')
IS_FROM_FILE_CONF = config.getboolean('set', 'from_file', fallback=False)
TILDA_CONF = config.getint('conf', 'tilda', fallback=0)
FILE_PATH = config.get('File', 'file_path', fallback='')
AMOUNT = config.getint('conf', 'amount', fallback=5000)
MIN_PRICE = config.getint('conf', 'min_price', fallback=3500)
XF_price = config.getint('conf', 'xf_price', fallback=500)


def check_env_val():
    if not WORK_DIR:
        print("Add 'WORK_DIR' in .env file")
        exit(1)
    if not DIKIDI_PASSWORD:
        print("Add 'DIKIDI_PASSWORD' in .env file")
        exit(1)
    if not DIKIDI_LOGIN:
        print("Add 'DIKIDI_LOGIN' in .env file")
        exit(1)
    if not DIKIDI_COMPANY_ID:
        print("Add 'DIKIDI_COMPANY_ID' in .env file")
        exit(1)
