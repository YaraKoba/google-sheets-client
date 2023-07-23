import re

MONTH = {'01': 'Января', '02': 'февраля', '03': 'марта', '04': 'апреля',
         '05': 'майя', '06': 'июня', '07': 'июля', '08': 'августа',
         '09': 'сентября', '10': 'октября', '11': 'ноября', '12': 'декабря'}


def get_date_from_file(file_name: str):
    regex = r"(\d{4})(\d{2})(\d{2})"
    math = re.search(regex, file_name)
    day = math.group(3)
    month = math.group(2)
    year = math.group(1)

    result = f"{day} {MONTH[month]}"

    return result

if __name__ == "__main__":
    res = get_date_from_file('journal_20230725.xls')
    print(res)