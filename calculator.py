from spreadsheet_access import SpreadsheetComm
import argparse
from SantanderParser import SantanderParser


#

# rows = spreadsheet.getValuesInRange("1TbTlOCpzPgivW1339bA3krSC3ztZfZxpQ9rsF9qj74A", "Especial", 'B2:R')

# print("ROWS: ")
# print(rows)

def fill_spreadsheet(old_id, new_id, extract_parser):
    spreadsheet = SpreadsheetComm()

    #spreadsheet.updateColumnInfo(old_id, 'Pagamentos', 'A4:A7', ['Frango', 'Marcella', 'Avatar', 'cansei'], 'RAW')


def dict_pretty_print(dict_to_print):
    print("{")
    for key, value in dict_to_print.items():
        print("\t" + key + " : " + str(value))
    print("}")


def main():
    args_parser = argparse.ArgumentParser(prog='bills_calculator', description='Calculate bills from month extract'
                                                                               'and auto fill google sheet')

    args_parser.add_argument('old_sheet_id', metavar='id1', help='\nSheet ID from previous month')
    args_parser.add_argument('new_sheet_id', metavar='id2', help='\nSheet ID from current month')

    args = args_parser.parse_args()

    extract_parser = SantanderParser("extrato_julho.xls")

    print("ALL DEBITS: ")
    dict_pretty_print(extract_parser.all_debits)
    print("ALL CREDITS: ")
    dict_pretty_print(extract_parser.all_credits)
    print("WEIRD DEBITS: ")
    dict_pretty_print(extract_parser.weird_debits)
    print("WEIRD CREDITS: ")
    dict_pretty_print(extract_parser.weird_credits)
    print("Pagamentos moradores: ")
    dict_pretty_print(extract_parser.residents_payment)
    print("Contas conhecidas: ")
    dict_pretty_print(extract_parser.defined_bills)

    fill_spreadsheet(args.old_sheet_id, args.new_sheet_id, extract_parser)


if __name__ == '__main__':
    main()
