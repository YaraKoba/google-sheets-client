from pars_xls.pars_xls import get_data_from_xls
from edit_xls.writer_sheets import create_report, get_inf_cell, get_index_sheet, add_data


def main():
    data_xls = get_data_from_xls('journal_20230708.xls')
    client = create_report(data_xls)
    # get_inf_cell('G7:G7')
    add_data(data_xls, client)


if __name__ == "__main__":
    main()
