from __future__ import print_function
from utils.errors import SheetNotFoundByTitleError
from edit_xls.google_sheets_client import SheetInit, SheetClient
from utils.formats import *
from googleapiclient.errors import HttpError


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
                amount = 4500
                polet = ''
        else:
            if i['sert']:
                i_sert = f'серт {i["sert_id"]}'
                amount = i['doplata']
                polet = 'оплачено' if int(i['doplata']) == 0 else ''
            else:
                i_sert = 'Инст'
                amount = 4500
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


def add_data(clients_inf, client: SheetClient):
    add_info(clients_inf, client)
    add_format(clients_inf, client)
    print("Info done")


class Connector:
    def __init__(self, sheet_id):
        self.sheet = SheetInit(sheet_id)
        self.sheet.connect()

    def create_report(self, clients_inf, title):
        sheet_list = self.sheet.add_sheet_list(title, len(clients_inf)+5, 15)
        client = self.sheet.get_client_object(sheet_list['replies'][0]['addSheet'])
        print(f'Create {title} done')
        return client

    def get_sheet_by_title(self, title: str):
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

    def read_sheet_by_id(self, title: str):
        client = self.get_sheet_by_title(title)
        return client.get_data_from_sheet()

    def get_inf_cell(self, cell):
        sheet_list = self.sheet.get_sheets()
        client = self.sheet.get_client_object(sheet_list[0])
        client.get_format(cell)
