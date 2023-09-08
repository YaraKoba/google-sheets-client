from dataclasses import dataclass, field
from typing import List
from utils.errors import EmptyInfError


@dataclass
class Block:
    start_row: int
    start_colum: int
    end_row: int
    end_colum: int

    def get_greet(self):
        return [self.start_row, self.end_row, self.start_colum, self.end_colum]

    def get_cell(self, row: int, colum: int):
        return [
            self.start_row + row,
            self.start_row + row + 1,
            self.start_colum + colum,
            self.start_colum + colum + 1
        ]


@dataclass
class TableBlock(Block):
    inf: List[List[str]]
    end_row: int = field(init=False)
    end_colum: int = field(init=False)
    title: List[List[str]] = None
    numerate: bool = False
    body: List[List[str]] = field(init=False)

    def __post_init__(self):
        self._check_inf()
        self.body = self._create_table()
        self.end_row = self.start_row + len(self.body)
        self.end_colum = self.start_colum + self._get_bigger_row()

    def _get_bigger_row(self) -> int:
        longest_string = 0

        for sublist in self.body:
            if len(sublist) > longest_string:
                longest_string = len(sublist)

        return longest_string


    def _create_table(self) -> List[List[str]]:
        result = []
        if self.title:
            result += self.title
        if self.numerate:
            numbered_inf = [[str(index + 1)] + line for index, line in enumerate(self.inf)]
            result += numbered_inf
        else:
            result += self.inf
        return result

    def _check_inf(self):
        if not self.inf:
            raise EmptyInfError("Inf to create table should not be empty")


@dataclass
class FormatBlock(Block):
    def get_row(self, row: int, cut: tuple = (0, 0,), width: int = 1) -> List:
        left_cut = cut[0]
        right_cut = cut[1]
        return [
            self.start_row + row,
            self.start_row + row + width,
            self.start_colum + left_cut,
            self.end_colum - right_cut
        ]

    def get_colum(self, colum: int, cut: tuple = (0, 0,), width: int = 1) -> List:
        top_cut = cut[0]
        down_cut = cut[1]
        return [
            self.start_row + top_cut,
            self.end_row - down_cut,
            self.start_colum + colum,
            self.start_colum + colum + width
        ]

    def get_rectangle(self, upper_indent: int, left_indent: int, bottom_indent: int = 0, right_indent: int = 0) -> List:
        return [
            self.start_row + upper_indent,
            self.end_row - bottom_indent,
            self.start_colum + left_indent,
            self.end_colum - right_indent
        ]
