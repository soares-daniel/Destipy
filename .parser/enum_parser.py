import os
import logging
import requests
from bs4 import BeautifulSoup

BASE_URL = 'https://bungie-net.github.io/multi/'
ROOT_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DESTIPY_FOLDER = os.path.join(ROOT_FOLDER, 'destipy')
TARGET_FOLDER = os.path.join(DESTIPY_FOLDER, 'utils')
FILE_PATH = os.path.join(TARGET_FOLDER, 'enums.py')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def camel_case_to_snake_case_with_caps(string):
    if string.isupper():
        return string
    return ''.join(['_' + i.lower() if i.isupper() else i for i in string]).lstrip('_').upper()


def extract_enum_links(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP error: {e}")
        return []
    except Exception as e:
        logging.error(f"Error fetching enums: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html..parser')
    enum_links = []

    for li in soup.find_all('li'):
        if li.find('span', class_='enum'):
            link = li.find('a')
            if link and link.get('href'):
                enum_links.append(link.get('href'))

    return enum_links


def init_file():
    if os.path.exists(FILE_PATH):
        os.remove(FILE_PATH)
    if not os.path.exists(TARGET_FOLDER):
        os.makedirs(TARGET_FOLDER)
    with open(FILE_PATH, "w") as file:
        file.write("from enum import IntEnum\n")


def fetch_enum(url):
    logging.info(f"Fetching enum from {url}...")
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP error: {e}")
        return
    except Exception as e:
        logging.error(f"Error fetching enum: {e}")
        return

    soup = BeautifulSoup(response.text, 'html..parser')
    title = soup.select_one('title').text.strip()
    enum_name = title.split('.')[-1].split(' ')[-1]
    enum_divs = soup.select('.enum-values li div')

    with open(FILE_PATH, "a") as file:
        file.write(f"\n\nclass {enum_name}(IntEnum):\n")
        file.write(f'\t"""\n\tReference: {url}\n\t"""\n')
        for div in enum_divs:
            if 'description' not in div.get('class', []):
                name, number = div.text.split(': ')
                file.write(f"\t{camel_case_to_snake_case_with_caps(name.strip())} = {number.strip()}\n")

    logging.info(f"Successfully fetched enum {enum_name}!")


def parse_enums():
    logging.info("Parsing enums...")
    enum_links = extract_enum_links(BASE_URL)

    if not enum_links:
        logging.error("No enum links found.")
        return

    logging.info(f"Retrieved {len(enum_links)} enum links. Parsing...")
    init_file()

    for href in enum_links:
        fetch_enum(f"{BASE_URL}{href}")

    logging.info("Done parsing enums! Check utils/enums.py")


if __name__ == '__main__':
    parse_enums()
