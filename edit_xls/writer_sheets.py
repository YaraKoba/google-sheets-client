from __future__ import print_function

import datetime
from typing import List

from utils.errors import SheetNotFoundByTitleError
from edit_xls.google_sheets_client import SheetInit, SheetClient
from editer.formats import *
from utils.config_val import AMOUNT


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

    def get_inf_cell(self, cell):
        sheet_list = self.sheet.get_sheets()
        client = self.sheet.get_client_object(sheet_list[0])
        client.get_format(cell)


def add_info(inf, client: SheetClient):
    client.merge_cells(0, 1, 1, 10)
    client.add_values(f'A1:A{len(inf) + 2}', [['Дата'], ['№']] + [[str(i + 1)] for i in range(len(inf))])
    client.add_values('B2:J2',
                      [['Отлетал', 'Время', 'ФИО', 'Номер', 'серт', 'сумма', 'Оплата', 'Видео', 'комментарии']])
    val = []
    for n, i in enumerate(inf):
        if not i['video']:
            video = ''
            client.add_one_of_list(n + 2, n + 3, 8, 9)
        else:
            video = 'оплачено'

        if i['company'] == 'XF':
            i_sert = 'XF'
            if i['sert']:
                i_sert += ' серт'
                amount = i['doplata']
                polet = 'оплачено' if int(i['doplata']) == 0 else ''
            else:
                i_sert += ' нал'
                amount = AMOUNT
                polet = ''
        else:
            if i['sert']:
                i_sert = f'серт {i["sert_id"]}'
                amount = i['doplata']
                polet = 'оплачено' if int(i['doplata']) == 0 else ''
            else:
                i_sert = 'Инст'
                amount = AMOUNT
                polet = ''

        if i['paid']:
            amount = 0
            polet = 'оплачено'

        if int(amount) > 0:
            client.add_one_of_list(n + 2, n + 3, 7, 8)

        val.append([i['time'], i['name'], i['number'], i_sert, amount, polet, video])

    client.add_values(f'C3:J{len(inf) + 3}', val)
    client.add_bool(2, len(inf) + 2, 1, 2)
    client.execute()


def add_format(inf, client: SheetClient):
    len_inf = len(inf)
    client.add_conditional_format_rule(2, len_inf + 2, 6, 7, bg_rgba=COLOR_AMOUNT)

    # title
    client.format_cell(0, 1, 1, 10, bg_rgba=COLOR_TITLE, bold=True, font_size=18)

    # № numbers
    client.format_cell(0, len_inf + 2, 0, 1, bg_rgba=COLOR_BORDER, bold=True, font_size=12)
    client.format_cell(1, 2, 1, 10, bg_rgba=COLOR_BORDER, bold=True, font_size=12)

    # text
    client.format_cell(2, len_inf + 2, 4, 10)

    # update dimension №
    client.update_dimension(0, 3, 70)

    # update dimension name
    client.update_dimension(3, 4, 220)
    client.format_cell(2, len_inf + 2, 3, 4, horizontal_alignment='LEFT')

    # update dimension number
    client.update_dimension(4, 5, 120)

    # update dimension sert
    client.update_dimension(5, 6, 120)

    # update dimension comment
    client.update_dimension(9, 10, 150)

    client.update_borders(0, len_inf + 3, 0, 10)
    client.execute()

    client.add_values('B1', [[client.sheet_inf['title']]])


def is_datetime(date):
    try:
        datetime.datetime.strptime(date, "%d.%m.%y")
        return True
    except ValueError:
        return False


def get_end_entry(sheet_data: List[List[str]]):
    for index in range(len(sheet_data) - 1, 0, -1):
        line = sheet_data[index]
        if line and is_datetime(line[0]):
            return index + 1


def add_global_format(cl: SheetClient, len_new_inf: int, start_point: int):
    start_point -= 1
    end_point = start_point + len_new_inf

    cl.add_conditional_format_rule(start_point, end_point, 6, 7, bg_rgba=COLOR_CERT, user_entered_value=-5500)
    cl.add_conditional_format_rule(start_point, end_point, 3, 4, bg_rgba=COLOR_XF, user_entered_value="XF",
                                   type_rule="TEXT_CONTAINS")
    cl.add_conditional_format_rule(start_point, end_point, 3, 4, bg_rgba=COLOR_CERT, user_entered_value=2,
                                   type_rule="TEXT_CONTAINS")

    # border
    cl.format_cell(start_point, end_point, 0, 1, bg_rgba=COLOR_DATE, bold=False, font_size=12)

    # table
    cl.format_cell(start_point, end_point, 1, 13, font_size=13)

    cl.update_borders(start_point, end_point, 0, 13)
    cl.update_borders(start_point, start_point + 1, 0, 13, width_top=3)
    cl.execute()


def add_to_global_report(google: Connector, report, title):
    client = google.get_client_by_title(title)

    data = client.get_data_from_sheet()
    end_entry = get_end_entry(data) + 1

    add_global_format(client, len(report), end_entry)
    client.add_values(f"A{end_entry}:M{end_entry + len(report)}", report)


def add_data(clients_inf, client: SheetClient):
    add_info(clients_inf, client)
    add_format(clients_inf, client)
    print("Info done")


def get_amount(company: str) -> str:
    return str(AMOUNT - 500) if company in ["XF нал", "XF серт"] else str(AMOUNT)


def get_video(video: str):
    if video in ["карта ярику", "нал"]:
        return "300"
    elif video == "оплачено":
        return "-200"
    else:
        return ''


def create_total_report(daily_report: List[List[str]], date):
    result = []
    for line_index in range(2, len(daily_report)):
        line = daily_report[line_index]

        if len(line) > 1 and line[1] == "TRUE":
            amount = get_amount(line[5])
            video = get_video(line[8])
            result.append([
                date, line[4], line[3], line[5], amount, video
            ])

    return result
