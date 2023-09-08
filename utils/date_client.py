import datetime
import re

MONTH = {'01': 'Января', '02': 'февраля', '03': 'марта', '04': 'апреля',
         '05': 'майя', '06': 'июня', '07': 'июля', '08': 'августа',
         '09': 'сентября', '10': 'октября', '11': 'ноября', '12': 'декабря'}

INF_MONTH = {'01': 'Январь', '02': 'Февраль', '03': 'Март', '04': 'Апрель',
             '05': 'Май', '06': 'Июнь', '07': 'Июль', '08': 'Август',
             '09': 'Сентябрь', '10': 'Октябрь', '11': 'Ноябрь', '12': 'Декабрь'}


def convert_in_datetime(date: str) -> datetime.datetime:
    return datetime.datetime.strptime(date, "%d.%m.%y")


def get_date_from_file(file_name: str):
    regex = r"(\d{4})(\d{2})(\d{2})"
    math = re.search(regex, file_name)
    day = math.group(3)
    month = math.group(2)
    year = math.group(1)

    result = f"{day} {MONTH[month]}"

    return result


def get_date_from_str(time: str):
    regex = r"(\d{4})-(\d{2})-(\d{2})"
    math = re.search(regex, time)
    day = math.group(3)
    month = math.group(2)

    return f"{day} {MONTH[month]}"


def get_date_to_daly_report(time: str):
    print(time)
    regex = r"(\d{2}).(\d{2}).(\d{2})"
    math = re.search(regex, time)
    day = math.group(1)
    month = math.group(2)

    return f"{day} {MONTH[month]}"


def get_date_to_general_report(time: str):
    regex = r"(\d{2}).(\d{2}).(\d{2})"
    math = re.search(regex, time)
    year = math.group(3)
    month = math.group(2)

    return f"{INF_MONTH[month]} {year}"


if __name__ == "__main__":
    res = get_date_from_str('2023-08-01 19:00:00')
    print(res)
