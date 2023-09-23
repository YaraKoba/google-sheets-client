import json
import re
from dataclasses import asdict
from typing import List, Dict

from googleapiclient.errors import HttpError

from google_sheet_client.google_sheets_client import SheetInit, SheetClient
from editer.writer import StartWriter, CertWriter, EndWriter
from models.passnger_models import Certificate, Passenger, NewPassenger, PassengerWhoFlew
from models.table_models import TableBlock
from api.pars_xls import NewPassengers
from utils.config_val import WORK_DIR
from utils.date_client import convert_in_datetime, get_date_to_general_report
from utils.errors import SheetNotFoundByTitleError, GetPassengerFromFileError
from utils.parser_input import AIGUL, FATHER
from utils.regex import REGEX_CERT_INST


class Connector:
    def __init__(self, sheet_id):
        self.sheet = SheetInit(sheet_id)
        self.sheet.connect()

    def create_report(self, title) -> SheetClient:
        sheet_list = self.sheet.add_sheet_list(title)
        client = self.sheet.get_client_object(sheet_list['replies'][0]['addSheet'])
        print(f'Create {title} done')
        return client

    def get_client_by_title(self, title: str):
        print(f"reading sheet {title}")
        sheet_lists = self.sheet.get_sheets()
        current_sheet = {}
        for one_list in sheet_lists:
            if one_list['properties']['title'] == title:
                current_sheet = one_list
                break

        if not current_sheet:
            raise SheetNotFoundByTitleError({"title": title})

        client = self.sheet.get_client_object(current_sheet)
        return client

    def read_sheet_by_title(self, title: str):
        client = self.get_client_by_title(title)
        return client.get_data_from_sheet()

    def get_inf_cell(self, title, cell_greed):
        client = self.get_client_by_title(title)
        client.get_format(cell_greed)


class SheetList:
    def __init__(self, list_name: str, connector: Connector):
        self.list_name = list_name
        self.connector = connector
        self.client = self._get_client()

    def _get_client(self):
        try:
            client = self.connector.get_client_by_title(self.list_name)
        except SheetNotFoundByTitleError as er:
            print(f"Таблица с название {er.args[0]['title']} НЕ НАЙДЕНА!")
            exit(1)
        return client

    def get_data(self):
        return self.client.get_data_from_sheet()


class Daily(SheetList):
    def __init__(self, list_name: str, connector: Connector, date: str):
        super().__init__(list_name, connector)
        self.date = convert_in_datetime(date)
        self._get_passengers()

    @staticmethod
    def _get_cert(company) -> Certificate | None:
        math_is_cert = re.search('серт', company)
        if math_is_cert:
            math_number = re.search(REGEX_CERT_INST, company)
            number = None if not math_number else math_number.group(0)
            cert = Certificate(number=number, is_cert=True)
        else:
            cert = None

        return cert

    def _create_passenger_object(self, line: List[str | int]) -> Passenger:
        cert = self._get_cert(line[5])
        return Passenger(
            date=self.date.strftime("%d.%m.%y"),
            time=line[2],
            name=line[3],
            phon=line[4],
            company=line[5],
            full_status=line[5],
            cert=cert,
            amount=line[6],
        )

    def _get_passengers(self):
        result = []
        sheet_inf = self.get_data()
        for line_index in range(2, len(sheet_inf)):
            line: List = sheet_inf[line_index]
            if len(line) > 1 and line[1] == "TRUE":
                passenger = self._create_passenger_object(line)
                result.append(passenger)
        self.passengers = result

    def get_certs(self):
        return [ps for ps in self.passengers if ps.cert and ps.cert.number]


class StartDaily(Daily):
    def __init__(self, list_name: str,
                 connector: Connector,
                 date: str,
                 is_from_file: bool = False,
                 file_path: str | None = None,
                 debug: bool = False,
                 ):
        if is_from_file and not file_path:
            raise GetPassengerFromFileError("not found file_path")
        self.is_from_file = is_from_file
        self.file_path = file_path
        self.debug = debug
        super().__init__(list_name, connector, date)

    def _get_client(self):
        try:
            print(f"Creating new list {self.list_name}")
            return self.connector.create_report(self.list_name)
        except HttpError as er:
            if er.status_code == 400 and "уже существует" in str(er.error_details):
                print(f'ОШИБКА: {str(er.error_details)}\nВыберете другой день')
                if self.debug:
                    return self.connector.get_client_by_title(self.list_name)
                else:
                    exit(1)

    def _get_passengers(self):
        passengers = NewPassengers(self.date)
        if self.is_from_file:
            self.passengers = passengers.get_data_from_xls(self.file_path)
        else:
            self.passengers = passengers.get_data_from_dikidi()[1]

    def write_passengers_to_json(self):
        with open(f"{WORK_DIR}passengers.json", "w", encoding='utf-8') as file:
            json.dump([asdict(passenger) for passenger in self.passengers], file, indent=4, ensure_ascii=False)

    def write_passengers_to_sheet(self):
        names_columns = ['№', 'Отлетал', 'Время', 'ФИО', 'Номер', 'серт', 'сумма', 'Оплата', 'Видео', 'комментарии']
        title = [['Дата', self.list_name], names_columns]
        inf = [one.convert_to_list() for one in self.passengers]

        table = TableBlock(
            start_row=0,
            start_colum=0,
            inf=inf,
            title=title,
            numerate=True
        )

        title_dop = [['', 'Доп. клиенты'], names_columns]
        inf_dop = ['bool_element'] + ['' for _ in range(5)] + ['paid_one_of_list', 'paid_one_of_list', '']
        dop_table = TableBlock(
            start_row=len(table.body) + 2,
            start_colum=0,
            title=title_dop,
            inf=[inf_dop for _ in range(4)],
            numerate=True
        )

        w = StartWriter(self.client, table)
        w.execute_all()

        dop = StartWriter(self.client, dop_table)
        dop.execute_all()


class EndDaily(Daily):
    def _create_passenger_object(self, line: List[str | int]) -> Passenger:
        if len(line) < 9 or not line[8] or not line[7]:
            print("Не заполнены поля Оплата и Видео!")
            exit(1)

        cert = self._get_cert(line[5])
        return PassengerWhoFlew(
            date=self.date.strftime("%d.%m.%y"),
            time=line[2],
            name=line[3],
            phon=line[4],
            company=line[5],
            full_status=line[5],
            cert=cert,
            amount=line[6],
            payment_fly=line[7],
            payment_video=line[8]
        )

    @staticmethod
    def _read_passenger_from_json():
        with open(f'{WORK_DIR}passengers.json', 'r', encoding='utf-8') as file:
            result = json.load(file)
            result = [NewPassenger(**ps) for ps in result]
            return result


class AllCerts:
    def __init__(self, passengers: List[PassengerWhoFlew], connector: Connector):
        self.connector = connector
        self.passengers = passengers
        self.global_list_name = self._get_global_list_name()
        self.our_certs, self.xf_certs = self._divide_certs()
        self.clients = self._get_clients()

    def _get_global_list_name(self) -> str:
        if self.passengers:
            ps_dt = self.passengers[0].date
            return get_date_to_general_report(ps_dt)
        else:
            print('Не найдено клиентов!')
            exit(1)

    def write_global_sheet(self):
        client = self.connector.get_client_by_title(self.global_list_name)
        end_entry = self.get_end_entry(client.get_data_from_sheet())
        inf = self.get_inf(end_entry)
        table = TableBlock(
            inf=inf,
            start_row=end_entry,
            start_colum=0
        )

        w = EndWriter(client, inf=table)
        w.execute_all()

    def get_inf(self, end_entry: int) -> List[List[str]]:
        aigul = 3000 / len(self.passengers) * AIGUL
        result = []
        for index, ps in enumerate(self.passengers):
            base_inf = ps.convert_to_list() + [aigul]
            row = end_entry + index + 1
            salary_father = [f'=(E{row}-H{row}-J{row}-K{row})*{FATHER}%']
            salary_all = [f'=E{row}-H{row}-J{row}-I{row}-K{row}-L{row}+F{row}+G{row}']
            result.append(base_inf + salary_father + salary_all)
        return result


    @staticmethod
    def get_end_entry(sheet_data: List[List[str]]) -> int:
        for index in range(len(sheet_data) - 1, 0, -1):
            line = sheet_data[index]
            if line and line[0]:
                return index + 1

    def _divide_certs(self) -> tuple:
        our_cert, xf_cert = [], []
        for cert in self.passengers:
            if cert.cert:
                if cert.cert.number:
                    our_cert.append(cert)
                else:
                    xf_cert.append(cert)
        return our_cert, xf_cert

    def _get_clients(self) -> Dict[str, SheetClient]:
        list_names = set([ps.cert.list_name for ps in self.our_certs])
        return {list_name: self.connector.get_client_by_title(list_name) for list_name in list_names}

    def check_cert(self, mark: bool = False):
        sheet_data = {name: cl.get_data_from_sheet() for name, cl in self.clients.items()}
        for passenger in self.our_certs:
            data: List[List[str]] = sheet_data[passenger.cert.list_name]
            passenger.cert.check_cert(data)
            if mark and passenger.cert.is_check:
                self.mark_cert(passenger)

    def mark_cert(self, ps: Passenger):
        if ps.cert.error:
            print(f'Серт НЕ был отмечен {ps.cert.number} line {ps.cert.line} {ps.cert.error}')
            return
        date = [[ps.date]]
        column = 6 if ps.cert.list_name == 'Серт 2022' else 5
        table = TableBlock(
            inf=date,
            start_row=ps.cert.line - 1,
            start_colum=column,
        )
        cert = CertWriter(
            client=self.clients[ps.cert.list_name],
            inf=table
        )
        cert.execute_all()

    def create_terminal_report(self):
        all_ps = len(self.passengers)
        our_cert = len(self.our_certs)
        xf_cash = len([xf for xf in self.passengers if xf.company == 'XF' and not xf.cert])
        xf_cert = len(self.xf_certs)
        video = len([ps for ps in self.passengers if ps.payment_video and ps.payment_video != '-'])
        report = '_____________________________\n'
        report += f"total: {all_ps}\nour_cert: {our_cert}\nxf_cash: {xf_cash}\nxf_cert: {xf_cert}\nvideo: {video}"
        report += '\n_____________________________\nCerts:'
        table_cert = [
            f'num:{c.cert.number} line:{c.cert.line} video:{c.cert.video} {c.cert.amount}p. err:{c.cert.error}'
            for c in self.passengers if c.cert and c.cert.number
        ]

        print(report)
        for r in table_cert:
            print(r)
