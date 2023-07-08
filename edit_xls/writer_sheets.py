from __future__ import print_function

from edit_xls.google_sheets_client import SheetInit, SheetClient
from utils.formats import *
from googleapiclient.errors import HttpError

SAMPLE_SPREADSHEET_ID = '11TYQV03ctwbcDUZyIkjFx3L1Xm-DWo5D5SWgumXhdHU'
DATA = [
    {'time': '16:00', 'name': 'Ильмир xf', 'amount': '4500', 'company': 'xf', 'number': '+79174393270', 'sert': False,
     'sert_id': 0, 'video': False, 'doplata': 0},
    {'time': '16:30', 'name': 'Сильвия xf', 'amount': '4500', 'company': 'xf', 'number': '+79176743630', 'sert': False,
     'sert_id': 0, 'video': False, 'doplata': 0},
    {'time': '17:00', 'name': 'Тимур xf', 'amount': '4500', 'company': 'xf', 'number': '+79586298098', 'sert': False,
     'sert_id': 0, 'video': False, 'doplata': '500'},
    {'time': '17:30', 'name': 'Тимур xf', 'amount': '4500', 'company': 'xf', 'number': '+79586298098', 'sert': False,
     'sert_id': 0, 'video': False, 'doplata': 0},
    {'time': '17:45', 'name': 'Тимур xf', 'amount': '4500', 'company': 'xf', 'number': '+79586298098', 'sert': False,
     'sert_id': 0, 'video': False, 'doplata': 0},
    {'time': '18:00', 'name': 'Марков Григорий', 'amount': '4500', 'company': 'Инст', 'number': '+79047608503',
     'sert': True, 'sert_id': '072208', 'video': False, 'doplata': 0},
    {'time': '18:30', 'name': 'Кириллов Роман', 'amount': '4500', 'company': 'Инст', 'number': '+79278683879',
     'sert': False, 'sert_id': 0, 'video': False, 'doplata': 0},
    {'time': '18:45', 'name': 'Хакимов Руслан Айратович', 'amount': '4500', 'company': 'Инст', 'number': '+79662407700',
     'sert': False, 'sert_id': 0, 'video': False, 'doplata': 0},
    {'time': '19:00', 'name': 'Даулиев Айназ', 'amount': '4500', 'company': 'Инст', 'number': '+79274243585',
     'sert': True, 'sert_id': '0722042', 'video': False, 'doplata': 0},
    {'time': '19:30', 'name': 'Галина Арафаилова xf', 'amount': '4500', 'company': 'xf', 'number': '+79872345667',
     'sert': False, 'sert_id': 0, 'video': False, 'doplata': 0}]


def create_list(data, row_count, colum_count, client: SheetClient):
    result = client.add_sheet_list(data, row_count, colum_count)
    return result


def add_skeleton(client: SheetClient):
    pass


def add_info(inf, client: SheetClient):
    client.merge_cells(0, 1, 1, 10)
    client.add_values('B1', [[client.sheet_inf['title']]])
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
                client.add_one_of_list(n + 2, n + 3, 7, 8)
                polet = ''
        else:
            if i['sert']:
                i_sert = f'серт {i["sert_id"]}'
                amount = i['doplata']
                polet = 'оплачено' if int(i['doplata']) == 0 else ''
            else:
                i_sert = 'Инст'
                amount = 4500
                client.add_one_of_list(n + 2, n + 3, 7, 8)
                polet = ''

        if int(i['doplata']) > 0:
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


def create_report(clients_inf):
    sheet = SheetInit(SAMPLE_SPREADSHEET_ID)
    sheet.connect()
    sheet_list = sheet.add_sheet_list('08.07.23-test', len(clients_inf) + 5, 15)
    client = sheet.get_client_object(sheet_list['replies'][0]['addSheet'])
    print('Create done')
    return client


def get_index_sheet(index):
    sheet = SheetInit(SAMPLE_SPREADSHEET_ID)
    sheet.connect()
    sheet_list = sheet.get_sheets()
    client = sheet.get_client_object(sheet_list[index])
    return client


def add_data(clients_inf, client: SheetClient):
    add_info(clients_inf, client)
    add_format(clients_inf, client)


def get_inf_cell(cell):
    sheet = SheetInit(SAMPLE_SPREADSHEET_ID)
    sheet.connect()
    sheet_list = sheet.get_sheets()
    client = sheet.get_client_object(sheet_list[0])
    client.get_format(cell)


def main():
    try:
        sheet = SheetInit(SAMPLE_SPREADSHEET_ID)
        sheet.connect()
        sheet_list = sheet.get_sheets()
        client = sheet.get_client_object(sheet_list[-1])
        # client.get_format('I3:I3')
        add_info(sheet_list[-1]['properties']['title'], DATA, client)
        # print(sheet.get_sheets())
        # client = sheet.connect()
        # create_list('6-7-23', len(DATA)+5, 15, client)
        # add_info('6-7-23', DATA, client)



    except HttpError as err:
        print(err)


if __name__ == '__main__':
    main()

    # 610244484861 - 3befk039venvhik0geh0uoir7ti3nurh.apps.googleusercontent.com ['https://www.googleapis.com/auth/spreadsheets',
    #                                                                                   'https://www.googleapis.com/auth/drive'])
    #
    # httpAuth = credentials.authorize(httplib2.Http()) # Авторизуемся в системе
