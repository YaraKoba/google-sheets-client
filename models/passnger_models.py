from dataclasses import dataclass, field
from typing import List, Dict

from edit_xls.google_sheets_client import SheetClient
from editer.formats import YELLOW
from utils.update_cert import two_point_search


@dataclass(order=True)
class Certificate:
    is_cert: bool = field(compare=False)
    number: str | None
    is_check: bool = field(default=False, compare=False)
    line: int | None = field(default=None, compare=False)
    separated_number: tuple = field(default=tuple(), init=False, compare=False, repr=False)
    list_name: str = field(default='', init=False, compare=False)
    amount: str = field(default='', init=False, compare=False)
    video: bool = field(default=False, init=False, compare=False)
    type: str = field(default='', init=False, compare=False)
    error: str = field(default=None, init=False, compare=False)

    def __post_init__(self):
        self.separated_number = self.separate_cert()
        self.list_name = self.get_list_name()
        self.number = self.join_number()

    def check_cert(self, sheet_cert: List[List[str]]):
        if not self.number:
            return
        result = two_point_search([self.number], sheet_cert)
        print(result)
        if result[self.number]['is_define']:
            line = result[self.number]['line']
            self.is_check = True
            self.line = line

            if int(self.separated_number[1]) > 22:
                self._update_inf23(sheet_cert[line-1])
            else:
                self._update_inf22(sheet_cert[line-1])
        else:
            self.error = 'Cert not found'
            print({self.error, self.number})

    def _update_inf23(self, line: List[str]):
        self.amount = line[4]
        self.type = line[2]
        self.video = True if line[3] else False
        if len(line) > 5:
            self.is_fly(line[5])

    def _update_inf22(self, line: List[str]):
        self.amount = line[7] if line[7].isdigit() else 'not_found'
        self.type = line[4]
        self.video = True if line[5] else False
        if len(line) > 7:
            self.is_fly(line[6])

    def is_fly(self, cell: str):
        if cell:
            self.error = 'Date is not empty'


    def separate_cert(self):
        def one_format_to_cert(num: tuple | None) -> tuple | None:
            if not num:
                return None
            m, y, n = num
            if len(n) == 3:
                if n[0] != '0':
                    new_sep = ''.join((m, y, n,))
                    m = new_sep[0:2]
                    y = new_sep[2:4]
                    n = new_sep[4:]
                else:
                    n = n[1:]
            elif len(n) == 1:
                n = '0' + n
            num = (m, y, n,)
            return num

        cert = self.number
        if not cert or cert[0].isalpha():
            return None

        if cert[0] == "0" or cert[0:2] in ["10", "11"]:
            month = cert[1:2] if cert[0] == "0" else cert[0:2]
            year = cert[2:4]
            number = cert[4:]
        elif cert[0] != '1':
            month = cert[0:1]
            year = cert[1:3]
            number = cert[3:]
        elif cert[2] != "2":
            month = cert[0:1]
            year = cert[1:3]
            number = cert[3:]
        else:
            month = cert[0:1]
            year = cert[1:3]
            number = cert[3:]

        return one_format_to_cert((month, year, number,))

    def get_list_name(self):
        if not self.separated_number:
            return None
        year = self.separated_number[1]
        return f'Серт 20{year}'

    def join_number(self):
        if not self.separated_number:
            return None
        return ''.join(self.separated_number)


@dataclass(order=True)
class Passenger:
    date: str = field(compare=False)
    time: str = field(compare=False)
    name: str
    phon: str = field(compare=False)
    company: str = field(compare=False)
    full_status: str = field(compare=False)
    cert: Certificate | None = field(compare=False)
    amount: int = field(compare=False)

    def convert_to_list(self):
        values = ['', self.time, self.name, self.phon, self.company, self.amount]
        return [str(v) for v in values]

    def __eq__(self, other):
        if isinstance(other, Passenger):
            return self.name == other.name
        return False


@dataclass(order=True)
class PassengerWhoFlew(Passenger):
    payment_fly: str = field(compare=False)
    payment_video: str = field(compare=False)

    def convert_to_list(self):
        values = [
            self.date,
            self.phon,
            self.name,
            self.full_status,
            self.amount,
            self.get_video(),
            self.amount_cert(),
            '500',
            '',
            '500',
        ]
        return [str(v) for v in values]

    def amount_cert(self):
        return f'-{self.cert.amount}' if self.cert and self.cert.number else ''

    def get_video(self):
        if self.cert and self.cert.video:
            return '-200'
        elif self.payment_video:
            return '300'
        else:
            return ''


@dataclass(order=True)
class NewPassenger(Passenger):
    is_paid: bool = field(compare=False)
    is_video: bool = field(compare=False)
    surcharge: int = field(compare=False)

    def convert_to_list(self):
        values = [
            'bool_element',
            self.time,
            self.name,
            self.phon,
            self.full_status,
            self.surcharge,
            self.is_one_of_list(self.is_paid),
            self.is_one_of_list(self.is_video),
        ]
        return [str(v) for v in values]

    @staticmethod
    def is_one_of_list(flag: bool):
        return 'paid_one_of_list' if not flag else 'оплачено'
