from typing import List, Dict


def separate_cert(cert):
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


def two_point_search(cert: List[str], data: List[List[str]]) -> Dict:
    cert = sorted([int(''.join(separate_cert(c))) for c in cert])
    len_data = len(data)
    left, right, middle = 2, len_data, len_data // 2

    result_dict = {}
    for num_cert in cert:

        while int(''.join(separate_cert(data[middle][0]))) != num_cert and left < middle:
            middle_num = int(''.join(separate_cert(data[middle][0])))
            if middle_num > num_cert:
                right = middle
            else:
                left = middle

            middle = (right + left) // 2

        right = len_data
        if left >= middle and int(''.join(separate_cert(data[middle][0]))) != num_cert:
            result_dict[str(num_cert)] = {'is_define': False, 'line': None}
            left = middle
            middle = (left + right) // 2
        else:
            result_dict[str(num_cert)] = {'is_define': True, 'line': middle + 1}

    return result_dict
