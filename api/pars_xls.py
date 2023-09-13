import datetime
import re
from utils.config_val import DIKIDI_COMPANY_ID, DIKIDI_LOGIN, DIKIDI_PASSWORD, AMOUNT
from dotenv import load_dotenv
from api.dikidi_api import DikidiAPI
from utils.errors import DayIsEmptyError
import pandas as pd
import phonenumbers
from models.passnger_models import Certificate, NewPassenger
from utils.regex import *
from utils.date_client import get_date_from_str

load_dotenv()


class NewPassengers:
    def __init__(self, date: int | datetime.datetime):
        if type(date) == int:
            self.date_object = datetime.datetime.combine(datetime.date.today() + datetime.timedelta(days=date),
                                                         datetime.time.min)
        else:
            self.date_object = date

    def get_data_from_xls(self, file_path):
        df = pd.read_excel(file_path, index_col=0)
        data_dict = []

        for index, row in df.iterrows():
            if type(row.values.item()) is str:
                text = row.values.item()
                one_client = self._search_inf_in_text(text)
                data_dict.append(one_client)

        return data_dict

    def get_data_from_dikidi(self):
        log = DIKIDI_LOGIN
        password = DIKIDI_PASSWORD
        company_id = DIKIDI_COMPANY_ID

        api = DikidiAPI(
            login=log,
            password=password)

        lists = api.get_appointment_list(company_id=company_id, date_start=self.date_object.strftime('%Y-%m-%d'),
                                         date_end=self.date_object.strftime('%Y-%m-%d'), limit=50)

        if not lists:
            raise DayIsEmptyError("Day is empty, change day or add clients in dikidi")

        data_list = []
        for l in lists:
            tmp_str = ""
            tmp_str += l["time"][11:] + "\n"
            tmp_str += l["client_title"] + "\n"
            tmp_str += l["services"][0]["cost"] + " RUB" + "\n"
            tmp_str += l["client_phone"] + "\n"
            tmp_str += l["comment"] if l["comment"] else ''
            one_client = self._search_inf_in_text(tmp_str)
            data_list.append(one_client)

        date = get_date_from_str(lists[0]["time"])
        sorted_clients = sorted(data_list, key=lambda x: x.time)
        return date, sorted_clients

    def _search_inf_in_text(self, text):
        match_time = re.search(REGEX_TIME, text)
        time = match_time.group(0)

        match_name = re.search(REGEX_NAME, text, re.MULTILINE)
        name = match_name.group(1)

        m = phonenumbers.PhoneNumberMatcher(text, 'RU').next()
        phon = phonenumbers.format_number(m.number, phonenumbers.PhoneNumberFormat.E164)

        match_amount = re.search(REGEX_AMOUNT, text, re.MULTILINE)
        amount = match_amount.group(1)

        match_company = re.search(REGEX_COMPANY, text)
        company = 'Инст' if not match_company else 'XF'

        match_cert_xf = re.search(REGEX_CERT_XF, text)
        match_cert_inst = re.search(REGEX_CERT_INST, text)
        if match_cert_inst:
            cert = Certificate(number=match_cert_inst.group(0), is_cert=True)
        elif match_cert_xf:
            cert = Certificate(is_cert=True, number=None)
        else:
            cert = None

        match_video = re.search(REGEX_VIDEO, text)
        video = True if match_video else False

        match_payment = re.search(REGEX_PAYMENT, text)
        paid = True if match_payment else False

        match_dop = re.search(REGEX_DOP, text)
        if (not match_dop and paid) or (cert and not match_dop):
            surcharge = 0
            paid = True
        elif match_dop:
            surcharge = match_dop.group(1)
        else:
            surcharge = AMOUNT

        if company == 'XF':
            full_status = company + ' серт' if cert else company + ' нал'
        else:
            full_status = company if not cert else f'серт {cert.number}'

        return NewPassenger(
            date=self.date_object.strftime("%d.%m.%y"),
            time=time,
            name=name,
            phon=phon,
            amount=amount,
            company=company,
            full_status=full_status,
            cert=cert,
            is_video=video,
            surcharge=surcharge,
            is_paid=paid
        )
