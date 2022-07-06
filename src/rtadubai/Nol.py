import requests
from bs4 import BeautifulSoup

captcha = "03AGdBq24OjYCEGdTLnTXbrCBkXqkRK-1CttobNTMZa-GTnJuu7PivfE1M73l2RJH2f8SD_YM7uh4ZDXU8tUlk_I36a0qJnYkVZHC_Lj1DLADiUe_KpCLTIegJhCO49aSeT6jfU2v3JH7diE-DSg_ZuECRXtHt7jeJMNHqhpY9EzsAKjueU4jDq3pnBcpfb0uavhULE_gZGSjG-iv4P_YTbWsHnHGsPNzSZeykEn3ToHMy0WtwNillGrqO6U5kqll22xsS"

# NOT TO BE USED IN YOUR CODE
# Used for getting data from www.rta.ae and parsing it into a BeautifulSoup object
# Type 1 is for getting balance and Type 2 is for getting transactions
# Used by other functions to reduce code


def soup(type, nol):
    nol1 = ""
    for i in str(nol):
        if i.isdigit():
            nol1 += i
    nol = nol1
    if type == 1:
        url = "https://www.rta.ae/wps/portal/rta/ae/home/!ut/p/z1/04_Sj9CPykssy0xPLMnMz0vMAfIjo8zi_QwMTNwNTAx93EPNDAwcQ4MCA8O8gowNXMz1w_Wj9KNASgIMLTycDAx9DIxDnIBKAkO8Ai29PD0MjaEKDHAARwP94NQ8_YLs7DRHR0VFAE1hpMw!/p0/IZ7_KG402B82M83EB0Q64NN5ER3GR6=CZ6_N004G041LGU600AURQQVJR30D7=NJgetNolCardBalance=/"
        data = {
            'nolTagId': nol,
            'captchaResponse': captcha
        }
    elif type == 2:
        url = "https://www.rta.ae/wps/portal/rta/ae/public-transport/nol/view-history/!ut/p/z1/jY-9DoIwAISfhQcwvZZKylhEC-VPhEbsYhiMIVF0MD6_hsEBI3LbJd-X3BFLGmL79tmd20d369vLux-sd0wUBwsEy-CJDUqTLFeVxylij-xHwK7wIbUJ8zBnEIoTO8fPt1REAWgKtw4gTVnr0tdxRN15Pn5E4r9vR8j3gwHIAa7AaSqyYg1JdVQoVjKlP8DEhwGYGFmdenK_GtOgixfScV5YvGcI/p0/IZ7_KG402B82M068F0QUK5CS641067=CZ6_KG402B82M068F0QUK5CS6410I6=NJvalidateTag=/"
        data = {
            'tagId': nol,
            'captcha': captcha
        }
    return BeautifulSoup(requests.post(url, data=data).text, 'html.parser')


def isValid(nol):
    if soup(1, nol).find('b') is None:
        return True
    else:
        return False


def CardBalance(nol):
    response = soup(1, nol)
    if response.find('b') is None:
        bal = response.find('strong', class_='font-weight-bolder font-size-18')
        return bal.text
    return response.find("b").text


def Details(nol):
    response = soup(1, nol)
    r = response.find_all('strong', class_='font-weight-bolder font-size-18')
    if len(r) != 0:
        return {
            'NolID': nol,
            'Error': False,
            'Card Balance': r[0].text,
            'Pending Balance': r[1].text,
            'Expiry Date': r[2].text
        }
    return {
        'Error': True,
        'ErrorMsg': response.find('b').text
    }


def Recent(nol, no=1):
    response = TransactionsRaw(nol)
    if response['Error'] is True:
        del response['Transactions']
        response["Transaction"] = {}
        return response
    else:
        if len(response['Transactions']) == 0:
            return {
                "Error": True,
                "ErrorMsg": "No transactions found",
                "Transaction": {}
            }
        if no > len(response['Transactions']):
            return {
                "Error": True,
                "ErrorMsg": "Number given is greater than the number of transactions",
                "Transaction": {}
            }
        elif no <= 0:
            return {
                "Error": True,
                "ErrorMsg": "Invalid Number Given",
                "Transaction": {}
            }
        else:
            return {
                "Error": False,
                'Transaction': response['Transactions'][no-1]
            }


def TransactionsRaw(nol):
    response = soup(2, nol)
    if response.find(id='nolhasErr') is None:
        data = response.find_all('span', class_='DataList')
        Date = response.find_all('div', class_='col col-lg-5 col-sm-5 col-md-5 vcenter col-xs-8 ss-table__col')
        noTransactions = int(len(Date)/2)
        Transactions = []
        for i in range(noTransactions):
            Transactions.append({
                "NolID": nol,
                "Date": Date[1+i*2].text.strip(),
                "Time": data[0+i*3].text,
                "Type": data[1+i*3].text,
                "Amount": data[2+i*3].text
            })
        return {
            "Error": False,
            "Transactions": Transactions
        }
    return {
        "Error": True,
        "ErrorMsg": response.find(id='nolmsg')['value'].strip(),
        "Transactions": []
    }


def NoOfTransactions(nol):
    response = TransactionsRaw(nol)
    return len(response['Transactions'])


class Card:
    def __init__(self, nol):
        if isValid(nol):
            details = Details(nol)
            self.id = details['NolID']
            self.balance = details['Card Balance']
            self.pending = details['Pending Balance']
            self.expiry = details['Expiry Date']
        else:
            details = Details(nol)
            raise ValueError("Invalid NOL Card")

    def __repr__(self):
        return f'Nol Card : {self.id}'

    def update(self):
        details = Details(self.id)
        self.balance = details['Card Balance']
        self.pending = details['Pending Balance']

    def transactions(self):
        return TransactionsRaw(self.id)

    def recent(self, no=1):
        return Recent(self.id, no)
