from spreadsheet_access import SpreadsheetComm
import argparse
from SantanderParser import SantanderParser
import json


def getJsonData(fileName):
    json_file = open(fileName)
    configs = json.load(json_file)
    json_file.close()

    return configs

def clear_previous_bills(spreadsheet, new_id):
    spreadsheet.updateColumnInfo(new_id, 'Balanço Mensal', 'C4', [""]*25, 'RAW')
    spreadsheet.updateColumnInfo(new_id, 'Balanço Mensal', 'E4', [""] * 25, 'RAW')
    spreadsheet.updateColumnInfo(new_id, 'Balanço Mensal', 'G4', [""] * 25, 'RAW')
    spreadsheet.updateColumnInfo(new_id, 'Balanço Mensal', 'I4', [""] * 25, 'RAW')

# fill next month bills
def fill_defined_bills(spreadsheet, new_id, extract_parser):
    clear_previous_bills(spreadsheet, new_id)
    house_bills = getJsonData('config.json')['house_bills']

    pos = 4
    # fill known bills
    for name, value in extract_parser.defined_bills.items():
        for bill in house_bills:
            if name == bill['name']:
                spreadsheet.updateColumnInfo(new_id, 'Balanço Mensal', 'C'+str(pos), bill['number'], 'RAW')
                spreadsheet.updateColumnInfo(new_id, 'Balanço Mensal', 'E' + str(pos), value, 'RAW')
                spreadsheet.updateColumnInfo(new_id, 'Balanço Mensal', 'G' + str(pos), '12', 'RAW')
                spreadsheet.updateColumnInfo(new_id, 'Balanço Mensal', 'I' + str(pos), bill['descr'], 'RAW')
                pos+=1

    pos += 2
    # fill unknown bills
    for name, value in extract_parser.weird_debits.items():
        if "PAGAMENTO DE TITULOS" not in name:
            spreadsheet.updateColumnInfo(new_id, 'Balanço Mensal', 'C' + str(pos), '?', 'RAW')
            spreadsheet.updateColumnInfo(new_id, 'Balanço Mensal', 'E' + str(pos), -value, 'RAW')
            spreadsheet.updateColumnInfo(new_id, 'Balanço Mensal', 'G' + str(pos), '12', 'RAW')
            pos += 1



# fill last month  resident debts in next month sheet
def fill_debts(spreadsheet, old_id, new_id):
    parsed_debts = []
    debts = spreadsheet.getValuesInRange(old_id, 'Pagamentos', 'L4:L13')
    for debt in debts:
        parsed_debts.append(float(debt[0].replace('R$ ', '')))

    spreadsheet.updateColumnInfo(new_id, 'Pagamentos', 'I4', parsed_debts, 'RAW')


# fill payments on last month sheet
def fill_payments(spreadsheet, old_id, extract_parser):
    orderedPayments = [0] * 10
    residents_data = getJsonData('config.json')['residents']

    for name, payment in extract_parser.residents_payment.items():
        for resident in residents_data:
            if name == resident['name']:
                orderedPayments[resident['number'] - 1] = payment


    spreadsheet.updateColumnInfo(old_id, 'Pagamentos', 'K4', orderedPayments, 'RAW')


def fill_spreadsheet(old_id, new_id, extract_parser):
    print("Connect to Sheets API")
    spreadsheet = SpreadsheetComm()

    print("Fill last month Spreadsheet payments")
    fill_payments(spreadsheet, old_id, extract_parser)

    print("Fill next month resident debts")
    fill_debts(spreadsheet, old_id, new_id)

    print("Fill next month defined bills")
    fill_defined_bills(spreadsheet, new_id, extract_parser)



def dict_pretty_print(dict_to_print):
    print("{")
    for key, value in dict_to_print.items():
        print("\t" + key + " : " + str(value))
    print("}")


def log_final_information(extract_parser):
    print("\n###########################################")
    print("\nScript is done, but there is some things you need to check manually:")
    print("\t- Check unknown bills in 'Balanço Mensal' tab")
    print("\t- Check unknown payments:")

    weird_payments = extract_parser.weird_credits.copy()
    for name, value in extract_parser.weird_credits.items():
        if value < 10:
            weird_payments.pop(name, None)

    dict_pretty_print(weird_payments)


def main():
    args_parser = argparse.ArgumentParser(prog='bills_calculator', description='Calculate bills from month extract'
                                                                               'and auto fill google sheet')

    args_parser.add_argument('old_sheet_id', metavar='id1', help='\nSheet ID from previous month')
    args_parser.add_argument('new_sheet_id', metavar='id2', help='\nSheet ID from current month')

    args = args_parser.parse_args()

    extract_parser = SantanderParser("extrato_janeiro.xls")

    print("ALL DEBITS: ")
    dict_pretty_print(extract_parser.all_debits)
    print("ALL CREDITS: ")
    dict_pretty_print(extract_parser.all_credits)
    print("WEIRD DEBITS: ")
    dict_pretty_print(extract_parser.weird_debits)
    print("WEIRD CREDITS: ")
    dict_pretty_print(extract_parser.weird_credits)
    print("Resident payments: ")
    dict_pretty_print(extract_parser.residents_payment)
    print("Defined bills: ")
    dict_pretty_print(extract_parser.defined_bills)

    fill_spreadsheet(args.old_sheet_id, args.new_sheet_id, extract_parser)

    log_final_information(extract_parser)


if __name__ == '__main__':
    main()
