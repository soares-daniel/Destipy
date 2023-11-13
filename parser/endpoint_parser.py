from functools import cache
import requests
from bs4 import BeautifulSoup
import logging

BASE_URL = 'https://bungie-net.github.io/multi/'
to_fix = []

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

session = requests.Session()


def clean_text(text):
    return ' '.join(text.split())


@cache
def parse_schema_page(url):
    try:
        response = session.get(url)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        logging.error(f"HTTP error occurred: {err}")
        return []
    except Exception as err:
        logging.error(f"Other error occurred: {err}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')

    schema_props = []
    for prop in soup.select('.properties .property .box > .box-contents'):
        if prop.find(class_='title'):
            key_name = clean_text(prop.find('strong').text)
            type_info = prop.find(class_='type-info')

            attributes, description, prop_type = '', '', ''
            for div in type_info.find_all('div', recursive=False):
                if 'attributes' in div.get('class', []):
                    attributes = div.text.strip()
                elif 'description' in div.get('class', []):
                    description = div.text.strip()
                elif 'type' in div.get('class', []):
                    prop_type = div.text.strip().split(': ')[1]

            if type_info.select_one('.enum-values, .mapped'):
                continue

            schema_props.append((key_name, attributes, description, prop_type))
        else:
            logging.warning(f"Skipping prop because it doesn't have a title")

    return schema_props


def parse_response_properties(soup):
    response_props = []
    for prop in soup.select('.response .property .box-contents'):
        key_name = clean_text(prop.find('strong').text)
        type_info = prop.find(class_='type-info')

        if type_info and type_info.find('a'):
            href = type_info.find('a')['href']
            linked_props = parse_schema_page(BASE_URL + href)
            response_props.append((key_name, linked_props))
        else:
            attributes = []
            for div in type_info.find_all('div', recursive=False):
                if div.find('strong'):
                    attr_name = clean_text(div.find('strong').text)
                    attr_value = clean_text(':'.join(div.text.split(':')[1:]))
                    attributes.append((attr_name, attr_value))

            response_props.append((key_name, tuple(attributes) if attributes else ''))

    return response_props


def parse_endpoint_page(url):
    logging.info(f"Starting parsing endpoint page: {url}")
    try:
        response = session.get(url)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        logging.error(f"HTTP error occurred: {err}")
        to_fix.append(url)
        return None, None, None, None, None, None
    except Exception as err:
        logging.error(f"Other error occurred: {err}")
        to_fix.append(url)
        return None, None, None, None, None, None

    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract category and method name
    to_extract = soup.find('title').text.strip().split(' - ')[1]
    category, method_name = to_extract.split('.')

    # Extract endpoint URL
    endpoint_url = soup.find(lambda tag: tag.name == "div" and "Path:" in tag.text)
    if endpoint_url:
        endpoint_url = endpoint_url.text.split('Path:')[1].split('\n')[0].strip()

    # Extract parameters
    params = []
    for param in soup.select('.parameters .box-contents ul li'):
        param_name = clean_text(param.find('strong').text)
        param_type = clean_text(param.find(class_='type').text.split(': ')[1])
        param_desc = clean_text(param.find(class_='description').text) if param.find(class_='description') else ''
        params.append((param_name, param_type, param_desc))

    # Extract description
    description = soup.find(class_='description').text.strip()

    # Extract response
    response_keys = parse_response_properties(soup)

    logging.info(f"Completed parsing endpoint page: {url}")
    return category.strip(), method_name.strip(), endpoint_url, params, description, response_keys


def parse_all_endpoints():
    logging.info("Starting parsing all endpoints...")
    try:
        response = session.get(BASE_URL)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        logging.error(f"HTTP error occurred: {err}")
        return {}
    except Exception as err:
        logging.error(f"Other error occurred: {err}")
        return {}

    soup = BeautifulSoup(response.text, 'html.parser')
    categories = {}
    processed_urls = set()

    endpoints_section = soup.find('h2', string="Contents - Endpoints (Grouped by Tag)").find_next(
        'div', class_='sidebar-box-contents')

    for category_section in endpoints_section.select('ul > li'):
        category_header = category_section.find('h3')
        category_name = clean_text(category_header.text) if category_header else 'Uncategorized'

        endpoints = []
        for endpoint in category_section.select('a'):
            endpoint_url = BASE_URL + endpoint.get('href')
            if endpoint_url in processed_urls:
                continue  # Skip already processed URLs
            processed_urls.add(endpoint_url)
            endpoint_details = parse_endpoint_page(endpoint_url)
            if endpoint_details:
                endpoints.append(endpoint_details)
        categories[category_name] = endpoints

    logging.info("Completed parsing all endpoints!")
    return categories


if __name__ == '__main__':
    all_endpoints = parse_all_endpoints()
    for category, endpoints in all_endpoints.items():
        print(category)
        for endpoint in endpoints:
            print(endpoint)

    print("To fix:")
    print(to_fix)
