from abc import ABC, abstractmethod
import json

CONFIG_FILE_NAME = "config.json"


class AbstractExtractParser(ABC):
    def __init__(self, file_name):
        # read config file
        json_file = open(CONFIG_FILE_NAME)
        self.configs = json.load(json_file)
        json_file.close()

        self.all_debits, self.all_credits = self.parse_file(file_name)
        self.residents_payment, self.weird_credits = self.discover_resident_payments()
        self.defined_bills, self.weird_debits = self.discover_defined_bills()

        super().__init__()

    @abstractmethod
    def parse_file(self, file_name):
        """
        Parse file and generate debit and credit objects
        :param file_name: name of account extract file
        :return debits: all debits in account
                credits: all credits in account
        """
        pass

    def discover_resident_payments(self):
        """
        Discover known resident payments using config file
        :return: resident_payments: dictionary with residents and found payment
                 weird_credits: dictionary with weird credits
        """

        residents_payments = {}
        weird_credits = self.all_credits.copy()

        # iterate through credits keys and values
        for cDescription, cValue in self.all_credits.items():
            # iterate through residents
            for resident in self.configs["residents"]:

                # parse who pays values
                pay_methods = resident["who_pays"].split(',')
                for pay_method in pay_methods:
                    # if any pay_method in cDescription
                    if pay_method in cDescription:
                        parsed_payment = cValue#float(str(cValue).strip().
                                         #        replace(".", "").
                                         #        replace(",", "."))
                        # allow residents two perform two payments in a month
                        if resident["name"] in residents_payments:
                            residents_payments[resident["name"]] += parsed_payment
                        else:
                            residents_payments[resident["name"]] = parsed_payment

                        # save credit to remove later
                        weird_credits.pop(cDescription)

        return residents_payments, weird_credits

    def discover_defined_bills(self):
        """
        Discover known bills using config file
        :return: defined_bills: dictionary with defined bills
                 weird_debits: dictionary with weird debits
        """

        defined_debits = {}
        weird_debits = self.all_debits.copy()

        # iterate through debits keys and values
        for dDescription, dValue in self.all_debits.items():
            # iterate through registered bills
            for bill in self.configs["house_bills"]:
                # parse bill names
                bill_names = bill["extr_name"].split(',')
                for bill_name in bill_names:
                    # if any bill_name in dDescription
                    if bill_name in dDescription:
                        parsed_bill = dValue#float(str(dValue).strip().
                                      #      replace(".", "").
                                      #      replace(",", "."))
                        # allow more than one bill type
                        if bill["name"] in defined_debits:
                            defined_debits[bill["name"]] += -parsed_bill
                        else:
                            defined_debits[bill["name"]] = -parsed_bill

                        # save debit to remove later
                        weird_debits.pop(dDescription)

        return defined_debits, weird_debits
