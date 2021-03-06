import configparser
import urllib3
import socket
from tldextract import tldextract
import urllib.robotparser


config = configparser.ConfigParser()
config.read("DSSE_config.ini")


class DatabaseConfig:
    host = config.get("Database", "host")
    user = config.get("Database", "user")
    passwd = config.get("Database", "passwd")
    database = config.get("Database", "database")
    Table_Name = config.get("Database", "table_name")


class FilesConfig:
    sub_urls = config.get("Sub_urls", "sub_urls")
    text_storing = config.get("Text_storing", "text_storing")
    hash_value = config.get("Hash_storing", "hash_value")
    csv_file_name = config.get("CSV_filename", "csv_file_name")


class UnwatedUrlsConfig:
    web_sites = config.get("Unwanted_sites", "web_sites")


class CSVColumnConfig:
    csv_column_names = config.get("CSV_column_names", "column_names").split(",")
    colum_alias_dict = config.get("CSV_column_names", "colum_alias_dict")


class PoliteConfig:
    POLITE_FLAG = config.get("Robot_parser", "polite")

    def is_polite(self, url):
        ext = tldextract.extract(url)
        URL = ext.subdomain + "." + ext.domain + "." + ext.suffix
        rp = urllib.robotparser.RobotFileParser()
        URL = "https://" + URL + "/robots.txt"
        rp.set_url(URL)
        rp.read()
        flag = rp.can_fetch("*", url)
        return flag
