from __future__ import print_function

import os
import os.path
from dotenv import load_dotenv
from typing import List
from utils.config_val import WORK_DIR

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

load_dotenv()


class SheetInit:
    def __init__(self, spreadsheet_id):
        self.SPREADSHEET_ID = spreadsheet_id
        self.creds = None

    def get_sheets(self):
        service = build('sheets', 'v4', credentials=self.creds)
        spreadsheet = service.spreadsheets().get(spreadsheetId=self.SPREADSHEET_ID).execute()
        sheet_list = spreadsheet.get('sheets')
        return sheet_list

    def add_sheet_list(self, title):
        service = build('sheets', 'v4', credentials=self.creds)
        results = service.spreadsheets().batchUpdate(
            spreadsheetId=self.SPREADSHEET_ID,
            body={
                    "requests": [
                        {
                            "addSheet": {
                                "properties": {
                                    "title": title,
                                }
                            }
                        }
                    ]
                }).execute()

        return results

    def connect(self):
        work_dir = WORK_DIR
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        if os.path.exists(f'{work_dir}google_sheet_client/keys/token.json'):
            self.creds = Credentials.from_authorized_user_file(f'{work_dir}google_sheet_client/keys/token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    f'{work_dir}google_sheet_client/keys/credentials.json', SCOPES)
                self.creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(f'{work_dir}google_sheet_client/keys/token.json', 'w') as token:
                token.write(self.creds.to_json())

    def get_client_object(self, sheet_inf):
        return SheetClient(self.creds, self.SPREADSHEET_ID, sheet_inf)


class SheetClient:
    def __init__(self, creds, spreadsheet_id, sheet_inf):
        self.service = build('sheets', 'v4', credentials=creds)
        self.spreadsheet_id = spreadsheet_id
        self.sheet_inf = sheet_inf['properties']
        self.data_body = {"requests": []}

    def get_format(self, greed):
        ranges = [f"{self.sheet_inf['title']}!{greed}"]  #

        results = self.service.spreadsheets().get(spreadsheetId=self.spreadsheet_id,
                                                  ranges=ranges, includeGridData=True).execute()
        # print('Основные данные')
        # print(results['properties'])
        # print('\nЗначения и раскраска')
        # print(results['sheets'][0]['data'][0]['rowData'])
        # print('\nВысота ячейки')
        # print(results['sheets'][0]['data'][0]['rowMetadata'])
        # print('\nШирина ячейки')
        # print(results['sheets'][0]['data'][0]['columnMetadata'])

        bg = results['sheets'][0]['data'][0]['rowData'][0]['values'][0]['effectiveFormat']['backgroundColor']
        value = results['sheets'][0]['data'][0]['rowData'][0]['values'][0]['formattedValue']

        return value, bg

    def get_data_from_sheet(self):
        results = self.service.spreadsheets().values().batchGet(spreadsheetId=self.spreadsheet_id,
                                                                ranges=self.sheet_inf['title'],
                                                                valueRenderOption='FORMATTED_VALUE',
                                                                dateTimeRenderOption='FORMATTED_STRING').execute()
        sheet_values = results['valueRanges'][0]['values']
        return sheet_values

    @staticmethod
    def convert_to_a1_notation(sr, er, sc, ec):
        start_col = chr(ord('A') + sc)
        end_col = chr(ord('A') + ec)
        if ec >= 26:
            end_col = chr(ord('A') + (ec // 26) - 1) + chr(ord('A') + (ec % 26))
        a1_notation = f'{start_col}{sr + 1}:{end_col}{er + 1}'
        return a1_notation

    def add_values(self, greed: List, values: List[List[str]]):
        start_row, end_row, sc, ec = greed
        greed = self.convert_to_a1_notation(start_row, end_row, sc, ec)
        results = self.service.spreadsheets().values().batchUpdate(spreadsheetId=self.spreadsheet_id, body={
            "valueInputOption": "USER_ENTERED",
            # Данные воспринимаются, как вводимые пользователем (считается значение формул)
            "data": [
                {"range": f"{self.sheet_inf['title']}!{greed}",
                 "majorDimension": "ROWS",  # Сначала заполнять строки, затем столбцы
                 "values": values,
                 }
            ]
        }).execute()
        return results

    def execute(self):
        results = self.service.spreadsheets().batchUpdate(
            spreadsheetId=self.spreadsheet_id,
            body=self.data_body
        ).execute()
        self.data_body = {"requests": []}
        return results

    def add_bool(self, greed: List,):
        sr, er, sc, ec = greed
        self.data_body['requests'].append({
            'repeatCell':
                {'range': {'sheetId': self.sheet_inf['sheetId'],
                           'startRowIndex': sr,
                           'endRowIndex': er,
                           'startColumnIndex': sc,
                           'endColumnIndex': ec},
                 'cell': {'dataValidation': {'condition': {'type': 'BOOLEAN'}}},
                 'fields': 'dataValidation'}})

    def add_one_of_list(self, greed: List[int], values: List[str]):
        # [{'userEnteredValue': 'нал'},
        #  {'userEnteredValue': 'карта ярику'},
        #  {'userEnteredValue': '-'}]

        sr, er, sc, ec = greed
        values_dict = [{'userEnteredValue': value} for value in values]

        self.data_body['requests'].append({
            'repeatCell':
                {'range': {'sheetId': self.sheet_inf['sheetId'],
                           'startRowIndex': sr,
                           'endRowIndex': er,
                           'startColumnIndex': sc,
                           'endColumnIndex': ec},
                 'cell': {'dataValidation': {'condition': {'type': 'ONE_OF_LIST',
                                                           'values': values_dict
                                                           },
                                             'strict': True,
                                             'showCustomUi': True},
                          },
                 'fields': 'dataValidation'}})

    def merge_cells(self, greed: List):
        sr, er, sc, ec = greed
        self.data_body['requests'].append({
            'mergeCells':
                {'range': {'sheetId': self.sheet_inf['sheetId'],
                           'startRowIndex': sr,
                           'endRowIndex': er,
                           'startColumnIndex': sc,
                           'endColumnIndex': ec},
                 'mergeType': 'MERGE_ALL'}})

    def update_borders(self, greed: List, width_top: int = 1):
        sr, er, sc, ec = greed
        self.data_body['requests'].append({'updateBorders': {'range': {'sheetId': self.sheet_inf['sheetId'],
                                                                       'startRowIndex': sr,
                                                                       'endRowIndex': er,
                                                                       'startColumnIndex': sc,
                                                                       'endColumnIndex': ec},
                                                             'bottom': {  # Задаем стиль для верхней границы
                                                                 'style': 'SOLID',  # Сплошная линия
                                                                 'width': 1,  # Шириной 1 пиксель
                                                                 'color': {'red': 0, 'green': 0, 'blue': 0,
                                                                           'alpha': 1}},  # Черный цвет
                                                             'top': {  # Задаем стиль для нижней границы
                                                                 'style': 'SOLID',
                                                                 'width': width_top,
                                                                 'color': {'red': 0, 'green': 0, 'blue': 0,
                                                                           'alpha': 1}},
                                                             'left': {  # Задаем стиль для левой границы
                                                                 'style': 'SOLID',
                                                                 'width': 1,
                                                                 'color': {'red': 0, 'green': 0, 'blue': 0,
                                                                           'alpha': 1}},
                                                             'right': {  # Задаем стиль для правой границы
                                                                 'style': 'SOLID',
                                                                 'width': 1,
                                                                 'color': {'red': 0, 'green': 0, 'blue': 0,
                                                                           'alpha': 1}},
                                                             'innerHorizontal': {
                                                                 # Задаем стиль для внутренних горизонтальных линий
                                                                 'style': 'SOLID',
                                                                 'width': 1,
                                                                 'color': {'red': 0, 'green': 0, 'blue': 0,
                                                                           'alpha': 1}},
                                                             'innerVertical': {
                                                                 # Задаем стиль для внутренних вертикальных линий
                                                                 'style': 'SOLID',
                                                                 'width': 1,
                                                                 'color': {'red': 0, 'green': 0, 'blue': 0, 'alpha': 1}}

                                                             }})

    def format_cell(self, greed: List, bg_rgba: List = (255, 255, 255, 1,), bold=False, font_size=12,
                    horizontal_alignment='CENTER'):
        sr, er, sc, ec = greed
        if len(bg_rgba) < 4:
            bg_rgba.append(1)
        self.data_body['requests'].append(
            {
                "repeatCell":
                    {
                        "cell":
                            {
                                "userEnteredFormat":
                                    {
                                        "horizontalAlignment": horizontal_alignment,
                                        "backgroundColor": {
                                            "red": bg_rgba[0] / 255,
                                            "green": bg_rgba[1] / 255,
                                            "blue": bg_rgba[2] / 255,
                                            "alpha": bg_rgba[3]
                                        },
                                        "textFormat":
                                            {
                                                "bold": bold,
                                                "fontSize": font_size
                                            }
                                    }
                            },
                        'range': {'sheetId': self.sheet_inf['sheetId'],
                                  'startRowIndex': sr,
                                  'endRowIndex': er,
                                  'startColumnIndex': sc,
                                  'endColumnIndex': ec},
                        "fields": "userEnteredFormat"
                    }
            })

    def update_dimension(self, greed: List, size: int):
        cs, ce = greed[2], greed[3]
        self.data_body['requests'].append({
            "updateDimensionProperties": {
                "range": {
                    "sheetId": self.sheet_inf['sheetId'],
                    "dimension": "COLUMNS",  # Задаем ширину колонки
                    "startIndex": cs,  # Нумерация начинается с нуля
                    "endIndex": ce  # Со столбца номер startIndex по endIndex - 1 (endIndex не входит!)
                },
                "properties": {
                    "pixelSize": size  # Ширина в пикселях
                },
                "fields": "pixelSize"  # Указываем, что нужно использовать параметр pixelSize
            }
        })

    def add_conditional_format_rule(self, greed: List, bg_rgba: List, user_entered_value: int | str = 0,
                                    type_rule: str = "NUMBER_GREATER"):
        sr, er, sc, ec = greed
        # check any type_rule
        # https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/other?hl=ru#ConditionType
        if len(bg_rgba) < 4:
            bg_rgba.append(1)

        self.data_body['requests'].append(
            {
                "addConditionalFormatRule": {
                    "rule": {
                        'ranges': {'sheetId': self.sheet_inf['sheetId'],
                                   'startRowIndex': sr,
                                   'endRowIndex': er,
                                   'startColumnIndex': sc,
                                   'endColumnIndex': ec},
                        "booleanRule": {
                            "condition": {
                                "type": f"{type_rule}",
                                "values": [
                                    {
                                        "userEnteredValue": f"{user_entered_value}"
                                    }
                                ]
                            },
                            "format": {
                                "backgroundColor": {
                                    "red": bg_rgba[0] / 255,
                                    "green": bg_rgba[1] / 255,
                                    "blue": bg_rgba[2] / 255,
                                    "alpha": bg_rgba[3]
                                }
                            }
                        }
                    },
                    "index": 0
                }
            }
        )

    def add_value_colum(self, sc, ec, values):
        results = self.service.spreadsheets().values().batchUpdate(spreadsheetId=self.spreadsheet_id, body={
            "valueInputOption": "USER_ENTERED",

            "data": [
                {"range": {
                    "sheetId": self.sheet_inf['sheetId'],
                    "dimension": "COLUMNS",  # Задаем ширину колонки
                    "startIndex": sc,  # Нумерация начинается с нуля
                    "endIndex": ec  # Со столбца номер startIndex по endIndex - 1 (endIndex не входит!)
                },
                    "majorDimension": "ROWS",  # Сначала заполнять строки, затем столбцы
                    "values": values,
                }
            ]
        }).execute()
        return results
