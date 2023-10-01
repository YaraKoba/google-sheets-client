import re
from dataclasses import dataclass, field
from typing import List

from utils.config_val import AMOUNT, MIN_PRICE, XF_price
from utils.search import separate_cert, two_point_search
from utils.regex import REGEX_COMPANY


@dataclass(order=True)
class Certificate:
    is_cert: bool
    number: str | None
    is_check: bool = field(default=False)
    line: int | None = field(default=None)
    separated_number: tuple = field(default=tuple(), init=False, repr=False)
    list_name: str = field(default='', init=False)
    amount: str = field(default='', init=False)
    video: bool = field(default=False, init=False)
    type: str = field(default='', init=False)
    error: str = field(default=None, init=False)

    def __post_init__(self):
        if self.number:
            self.separated_number = separate_cert(self.number)
            self.list_name = self.get_list_name()
            self.number = self.join_number()

    def check_cert(self, sheet_cert: List[List[str]]):
        if not self.number:
            return
        result = two_point_search([self.number], sheet_cert)
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
        self.video = True if line[3] else False
        self.amount = int(line[4]) - 500 if self.video else line[4]
        self.type = line[2]
        if len(line) > 5:
            self.is_fly(line[5])

    def _update_inf22(self, line: List[str]):
        self.video = True if line[5] else False
        if line[7].isdigit():
            self.amount = int(line[7]) - 500 if self.video else line[7]
        else:
            self.amount = 'not_found'
        self.type = line[4]
        if len(line) > 7:
            self.is_fly(line[6])

    def is_fly(self, cell: str):
        if cell:
            self.error = 'Date is not empty'

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
    date: str
    time: str
    name: str
    phon: str
    company: str
    full_status: str
    cert: Certificate | None
    amount: int = field(compare=False)

    def convert_to_list(self) -> List[str]:
        values = ['', self.time, self.name, self.phon, self.company, self.amount]
        return [str(v) for v in values]


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
            self.get_amount(),
            self.get_video(),
            self.amount_cert(),
            '500',
            '',
            '500',
        ]
        return [str(v) for v in values]

    def amount_cert(self):
        return f'-{self.cert.amount}' if self.cert and self.cert.number else ''

    def get_amount(self):
        amount = 0
        if re.search(REGEX_COMPANY, self.company):
            amount -= XF_price
        if self.cert and self.cert.amount:
            amount = int(self.cert.amount)
        elif not self.amount or int(self.amount) < MIN_PRICE:
            amount += int(AMOUNT)
        else:
            amount += int(self.amount)
        return str(amount)

    def get_video(self):
        if self.cert and self.cert.video:
            return '-200'
        elif self.payment_video in ['нал', 'карта Ярика', 'оплачено']:
            return '300'
        else:
            return ''


@dataclass(order=True)
class NewPassenger(Passenger):
    is_paid: bool
    is_video: bool
    surcharge: int

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
