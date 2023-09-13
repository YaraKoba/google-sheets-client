from google_sheet_client.google_sheets_client import SheetClient
from models.table_models import TableBlock, FormatBlock
from editer.formats import COLOR_AMOUNT, COLOR_TITLE, COLOR_BORDER, YELLOW, COLOR_CERT, COLOR_XF, COLOR_DATE
from editer.modal import ModalElement, is_valid_method


class Writer:
    def __init__(self, client: SheetClient, inf: TableBlock):
        self.client = client
        self.inf = inf
        self._add_format()
        self._change_modal_element()

    def _change_modal_element(self):
        modal = ModalElement(self.client)
        for row in range(len(self.inf.body)):
            for colum, value in enumerate(self.inf.body[row]):
                if value and is_valid_method(modal, value):
                    cell = self.inf.get_cell(row=row, colum=colum)
                    modal.call_method(value, cell)
                    self.inf.body[row][colum] = ''

    def execute_all(self):
        print(f'Writing to {self.client.sheet_inf["title"]}')
        self.client.execute()
        self.client.add_values(self.inf.get_greet(), self.inf.body)

    def _add_format(self):
        pass


class StartWriter(Writer):
    def _add_format(self):
        greed = FormatBlock(
            start_row=self.inf.start_row,
            end_row=self.inf.end_row,
            start_colum=self.inf.start_colum,
            end_colum=self.inf.end_colum
        )
        self.client.merge_cells(greed.get_row(0, (1, 0)))
        self.client.add_conditional_format_rule(greed.get_colum(6, (2, 0,)), bg_rgba=COLOR_AMOUNT)

        # title
        self.client.format_cell(greed.get_row(0, (1, 0)), bg_rgba=COLOR_TITLE, bold=True, font_size=18)

        # № numbers
        self.client.format_cell(greed.get_colum(0), bg_rgba=COLOR_BORDER, bold=True, font_size=12)
        self.client.format_cell(greed.get_row(1), bg_rgba=COLOR_BORDER, bold=True, font_size=12)

        # text
        self.client.format_cell(greed.get_rectangle(2, 1))

        # update dimension №
        self.client.update_dimension(greed.get_colum(0, width=3), 70)

        #  update dimension name
        self.client.update_dimension(greed.get_colum(3), 220)
        self.client.format_cell(greed.get_colum(3, cut=(2, 0)), horizontal_alignment='LEFT')

        # update dimension number and cert
        self.client.update_dimension(greed.get_colum(4, width=2), 120)

        # update dimension comment
        self.client.update_dimension(greed.get_colum(9), 150)

        # border
        self.client.update_borders(greed.get_greet())


class EndWriter(Writer):
    def _add_format(self):
        greed = FormatBlock(
            start_row=self.inf.start_row,
            end_row=self.inf.end_row,
            start_colum=self.inf.start_colum,
            end_colum=self.inf.end_colum
        )

        # format rule
        self.client.add_conditional_format_rule(greed.get_colum(6), bg_rgba=COLOR_CERT, user_entered_value=-5500)
        self.client.add_conditional_format_rule(greed.get_colum(3), bg_rgba=COLOR_XF, user_entered_value="XF",
                                                type_rule="TEXT_CONTAINS")
        self.client.add_conditional_format_rule(greed.get_colum(3), bg_rgba=COLOR_CERT, user_entered_value=2,
                                                type_rule="TEXT_CONTAINS")

        # border
        self.client.format_cell(greed.get_colum(0), bg_rgba=COLOR_DATE, bold=False, font_size=12)

        # table
        self.client.format_cell(greed.get_rectangle(0, 1), font_size=13)
        self.client.update_borders(greed.get_greet())
        self.client.update_borders(greed.get_row(0), width_top=3)


class CertWriter(Writer):
    def _add_format(self):
        greed = FormatBlock(
            start_row=self.inf.start_row,
            end_row=self.inf.end_row,
            start_colum=0,
            end_colum=self.inf.end_colum + 1
        )
        self.client.format_cell(greed.get_greet(), bg_rgba=YELLOW)
        self.client.update_borders(greed.get_greet())
