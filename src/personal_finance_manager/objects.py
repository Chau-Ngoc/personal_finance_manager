import re
from abc import ABC, abstractmethod

from bs4 import BeautifulSoup


class BIDVHTMLDocument(ABC):
    def __init__(self, html_document: str):
        self.soup = BeautifulSoup(html_document, "html.parser")

    @abstractmethod
    def get_meaningful_information(self) -> list:
        pass


class BIDVCareDocument(BIDVHTMLDocument):
    def __init__(self, html_document: str):
        super().__init__(html_document)

    def get_meaningful_information(self) -> list:
        fields = (
            "Transaction type",
            "Original amount",
            "Currency",
            "Transaction status",
            "Received time",
            "At",
            "Approval code",
        )
        information = []
        for field in fields:
            try:
                information.append(self.soup.find("i", string=field).next_sibling.next_sibling.get_text(strip=True))
            except AttributeError:
                information.append(None)
        return information


class BIDVSmartBankingDocument(BIDVHTMLDocument):
    def __init__(self, html_document: str):
        super().__init__(html_document)
        self.main_table = self.soup.find("table", attrs={"role": False})

    def get_meaningful_information(self) -> list:
        fields = (
            "Transaction type",
            "Transaction amount",
            "Currency",
            "Transaction status",
            "Received time",
            "Transaction remark",
            "Reference number",
        )
        information = []
        for field in fields:
            try:
                information.append(
                    self.main_table.find("span", string=re.compile(field)).parent.next_sibling.next_sibling.get_text(
                        strip=True
                    )
                )
            except AttributeError:
                information.append(None)
        return information
