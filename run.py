import os
import re
import time
from abc import ABC, abstractmethod
from typing import ClassVar, List

from bs4 import BeautifulSoup
from bs4.element import PageElement
import requests


class VpnProvider(ABC):

    @abstractmethod
    def url(self) -> str: pass

    @abstractmethod
    def folder_name(self) -> str: pass

    @abstractmethod
    def parse_html(self, soup: BeautifulSoup) -> List[str]: pass

    def __get_links__(self) -> List[str]:
        response = requests.get(self.url())
        soup = BeautifulSoup(response.content, "html.parser")
        return self.parse_html(soup)

    def __download_ovpn_file__(self, link: str):
        response = requests.get(link)
        content_disposition_header = response.headers['content-disposition']
        filename = re.findall("filename=\"(.+)\"", content_disposition_header)[0]
        with open(self.folder_name() + "/" + filename, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded {filename} from {link}")

    def download(self):
        if not os.path.exists(self.folder_name()):
            os.mkdir(self.folder_name())
        for idx, link in enumerate(self.__get_links__()):
            self.__download_ovpn_file__(link)
            if idx % 5 == 0:
                time.sleep(0.5)


# VPN providers
class GhostFile(VpnProvider):
    host: ClassVar[str] = "https://ghostpath.com"

    def folder_name(self) -> str:
        return "ghost_path"

    def url(self) -> str:
        return self.host + "/servers"

    @staticmethod
    def __should_ignore__(element: PageElement) -> bool:
        return element.parent.parent["data-country"] == "Ukraine"

    def parse_html(self, soup: BeautifulSoup) -> [str]:
        links = []
        for link in soup.find_all("a", {"class": "openvpn-graphic"}):
            if self.__should_ignore__(link):
                continue
            links.append(self.host + link["href"])
        return links


if __name__ == '__main__':
    providers = [
        GhostFile()
    ]
    for provider in providers:
        provider.download()
