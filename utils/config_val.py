import os
from dotenv import load_dotenv

load_dotenv()

WORK_DIR = os.getenv("WORK_DIR")
DIKIDI_PASSWORD = os.getenv("DIKIDI_PASSWORD")
DIKIDI_LOGIN = os.getenv("DIKIDI_LOGIN")
DIKIDI_COMPANY_ID = os.getenv("DIKIDI_COMPANY_ID")


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
