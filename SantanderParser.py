from AbstractExtractParser import AbstractExtractParser
import xlrd


class SantanderParser(AbstractExtractParser):

    def parse_file(self, file_name):
        """
        Parse file and generate debit and credit objects
        :param file_name: name of account extract file
        :return debits: dict with all debits in account
                credits: dict with all credits in account
        """

        debits = {}
        credits = {}

        print()

        workbook = xlrd.open_workbook(file_name)
        worksheet = workbook.sheet_by_index(0)

        # iterate through all relevant lines
        nrows = worksheet.nrows
        for r in range(7, nrows):
            # if we reach empty or useless info, finish loop because relevant info is already parsed
            if worksheet.cell(r, 0).value is None or "TOTAL" in worksheet.cell(r, 0).value:
                break

            # get info from
            date = worksheet.cell(r, 0).value
            description = worksheet.cell(r, 1).value
            balance = worksheet.cell(r, 6).value
            unique_key = date.strip() + "-" + balance.strip() + "-" + description

            # if credit line is not empty, it mean it is a credit
            if worksheet.cell(r, 4).value is not None and worksheet.cell(r, 4).value != " ":
                credits[unique_key] = worksheet.cell(r, 4).value

            # if debit line is not empty, it mean it is a debit
            if worksheet.cell(r, 5).value is not None and worksheet.cell(r, 5).value != " ":
                debits[unique_key] = worksheet.cell(r, 5).value

        return debits, credits