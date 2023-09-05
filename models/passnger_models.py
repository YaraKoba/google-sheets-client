from dataclasses import dataclass


@dataclass
class Certificate:
    is_cert: bool
    number: str
    separated_number: tuple | None
    list_name: str | None
    is_check: bool = False
    line: int | None = None

    def __init__(self, number, is_cert):
        self.number = number
        self.is_cert = is_cert
        self.separated_number = self.separate_cert()
        self.list_name = self.get_list_name()
        self.is_check = False
        self.line = None

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
        year = self.separated_number[1]
        return f'Серт 20{year}'


@dataclass
class Passenger:
    date: str
    time: str
    name: str
    phon: str
    company: str
    cert: Certificate | None
    amount: int

    def convert_to_list(self):
        return [self.time, self.name, self.phon, self.company, self.amount]


@dataclass
class PassengerWhoFlew(Passenger):
    payment_fly: str
    payment_video: str

    def __init__(self, parent_passenger, payment_fly, payment_video):
        super().__init__(**vars(parent_passenger))
        self.payment_fly = payment_fly
        self.payment_video = payment_video



