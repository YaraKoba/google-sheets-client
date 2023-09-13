from typing import List

from google_sheet_client.google_sheets_client import SheetClient


def is_valid_method(class_obj: object, method_name: str):
    try:
        cls = class_obj
        return hasattr(cls, method_name) and callable(getattr(cls, method_name))
    except KeyError:
        return False
    except TypeError:
        return False


class ModalElement:
    def __init__(self, client: SheetClient):
        self.client = client

    def call_method(self, method_name, *args, **kwargs):
        method = getattr(self, method_name, None)
        if method:
            method(*args, **kwargs)
        else:
            print(f"Метод {method_name} не найден")

    def _one_of_list(self, greed: List[int], values: List[str]):
        self.client.add_one_of_list(greed, values)

    def paid_one_of_list(self, greed: List[int]):
        self._one_of_list(greed=greed, values=['нал', 'карта Ярика', '-'])

    def bool_element(self, greed: List[int]):
        self.client.add_bool(greed=greed)

