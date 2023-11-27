import json
import os
import shutil
import subprocess
from functools import cache
import requests
from bs4 import BeautifulSoup
import logging

from .enum_parser import parse_enums

BASE_URL = "https://bungie-net.github.io/multi/"
ROOT_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DESTIPY_FOLDER = os.path.join(ROOT_FOLDER, "destipy")
TEMPLATE_FOLDER = os.path.join(ROOT_FOLDER, ".template")
TARGET_FOLDER = os.path.join(DESTIPY_FOLDER, "endpoints")
UTILS_FOLDER = os.path.join(DESTIPY_FOLDER, "utils")

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

session = requests.Session()


def clean_text(text):
    return " ".join(text.split())


@cache
def parse_array_contents(url):
    try:
        response = session.get(url)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        logging.error(f"HTTP error occurred: {err}")
        return []
    except Exception as err:
        logging.error(f"Other error occurred: {err}")
        return []

    soup = BeautifulSoup(response.text, "html..parser")
    selected = soup.select(".properties .property .box > .box-contents")
    schema_response = []
    for prop in selected:
        if prop.find(class_="title"):
            key = clean_text(prop.find(class_="title").find_all("strong")[0].text)
            type_info = prop.find(class_="type-info")
            if not type_info.find(class_="attributes"):
                # Nested type
                href = type_info.find("a")["href"]
                schema_prop = parse_schema_page(BASE_URL + href)
            else:
                # Primitive type
                schema_prop = {
                    "Name": key,
                    "Type": clean_text(
                        type_info.find(class_="type").text.split(": ")[1]
                    ),
                    "Description": clean_text(type_info.find(class_="description").text)
                    if type_info.find(class_="description")
                    else "",
                    "Attributes": [
                        clean_text(span.text)
                        for span in type_info.find(class_="attributes").find_all("span")
                    ]
                    if type_info.find(class_="attributes")
                    else [],
                }
            schema_response.append({key: schema_prop})
        else:
            logging.warning(f"Skipping prop because it doesn't have a title")

    return schema_response


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

    soup = BeautifulSoup(response.text, "html..parser")

    schema_response = {}
    selected = soup.select(".properties .property .box > .box-contents")
    for prop in selected:
        if prop.find(class_="title"):
            key = clean_text(prop.find(class_="title").find_all("strong")[0].text)
            type_info = prop.find(class_="type-info")
            if not type_info.find(class_="attributes"):
                # Nested type
                href = type_info.find("a")["href"]
                schema_prop = parse_schema_page(BASE_URL + href)
            else:
                if type_info.find(class_="items"):
                    # Array type
                    items = type_info.find(class_="items")
                    href = items.find("a")["href"] if items.find("a") else None
                    schema_prop = {
                        "Name": key,
                        "Type": clean_text(
                            type_info.find(class_="type").text.split(": ")[1]
                        ),
                        "Description": clean_text(
                            type_info.find(class_="description").text
                        )
                        if type_info.find(class_="description")
                        else "",
                        "Attributes": [
                            clean_text(span.text)
                            for span in type_info.find(class_="attributes").find_all(
                                "span"
                            )
                        ]
                        if type_info.find(class_="attributes")
                        else [],
                        "Array Contents": parse_array_contents(BASE_URL + href)
                        if href
                        else clean_text(items.text.split(":")[1].strip()),
                    }
                else:
                    # Primitive type
                    schema_prop = {
                        "Name": key,
                        "Type": clean_text(
                            type_info.find(class_="type").text.split(": ")[1]
                        ),
                        "Description": clean_text(
                            type_info.find(class_="description").text
                        )
                        if type_info.find(class_="description")
                        else "",
                        "Attributes": [
                            clean_text(span.text)
                            for span in type_info.find(class_="attributes").find_all(
                                "span"
                            )
                        ]
                        if type_info.find(class_="attributes")
                        else [],
                    }
            schema_response[key] = schema_prop
        else:
            logging.warning(f"Skipping prop because it doesn't have a title")

    return schema_response


def parse_response_properties(soup):
    response = {}
    selected = soup.select(".response .property .box-contents")
    for prop in selected:
        key = clean_text(prop.find(class_="title").find_all("strong")[0].text)
        type_info = prop.find(class_="type-info")
        if type_info.find("a"):
            # Nested type
            href = type_info.find("a")["href"]
            schema_props = parse_schema_page(BASE_URL + href)
            response[key] = schema_props
        else:
            # Primitive type
            value = {
                "Name": key,
                "Type": clean_text(type_info.find(class_="type").text.split(": ")[1]),
                "Description": clean_text(type_info.find(class_="description").text)
                if type_info.find(class_="description")
                else "",
                "Attributes": [
                    clean_text(span.text)
                    for span in type_info.find(class_="attributes").find_all("span")
                ]
                if type_info.find(class_="attributes")
                else [],
            }
            response[key] = value
    return response


def parse_request_body(soup):
    select = ".request-body .box-contents"
    selected = soup.select(select)
    params = []
    # Get link
    for prop in selected:
        type_info = prop.find(class_="type-info")
        if type_info and type_info.find("a"):
            href = type_info.find("a")["href"]
            try:
                response = session.get(BASE_URL + href)
                response.raise_for_status()
            except requests.exceptions.HTTPError as err:
                logging.error(f"HTTP error occurred: {err}")
                return []
            except Exception as err:
                logging.error(f"Other error occurred: {err}")
                return []

            soup2 = BeautifulSoup(response.text, "html..parser")
            select2 = ".properties .property .box > .box-contents"
            selected2 = soup2.select(select2)
            for param in selected2:
                if "stop-nesting-boxes" in param.attrs.get("class", []):
                    continue  # Enums
                param_name = clean_text(param.find("strong").text)
                param_type = clean_text(param.find(class_="type").text.split(": ")[1])
                param_desc = (
                    clean_text(param.find(class_="description").text)
                    if param.find(class_="description")
                    else ""
                )
                param_attributes_spans = (
                    param.find(class_="attributes").find_all("span")
                    if param.find(class_="attributes")
                    else []
                )
                param_attributes = [
                    clean_text(span.text) for span in param_attributes_spans
                ]

                params.append((param_name, param_type, param_desc, param_attributes))
    return params


def parse_endpoint_page(doc_url):
    logging.info(f"Starting parsing endpoint page: {doc_url}")
    try:
        response = session.get(doc_url)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        logging.error(f"HTTP error occurred: {err}")
        return None, None, None, None, None, None, None, None
    except Exception as err:
        logging.error(f"Other error occurred: {err}")
        return None, None, None, None, None, None, None, None

    soup = BeautifulSoup(response.text, "html..parser")

    # Extract category and method name
    to_extract = soup.find("title").text.strip().split(" - ")[1]
    category, method_name = to_extract.split(".")

    # Extract endpoint URL
    endpoint_url = soup.find(lambda tag: tag.name == "div" and "Path:" in tag.text)
    if endpoint_url:
        endpoint_url = endpoint_url.text.split("Path:")[1].split("\n")[0].strip()

    # Extract parameters
    params = []
    for param in soup.select(".parameters .box-contents ul li"):
        param_name = clean_text(param.find("strong").text)
        param_type = clean_text(param.find(class_="type").text.split(": ")[1])
        param_desc = (
            clean_text(param.find(class_="description").text)
            if param.find(class_="description")
            else ""
        )
        param_attributes_spans = (
            param.find(class_="attributes").find_all("span")
            if param.find(class_="attributes")
            else []
        )
        param_attributes = [clean_text(span.text) for span in param_attributes_spans]
        params.append((param_name, param_type, param_desc, param_attributes))

    # Extract description
    description = soup.find(class_="description").text.strip()

    # Extract scope
    scopes = []
    for scope in soup.select(".required-scopes .box-contents ul li"):
        scope_str = clean_text(scope.text)
        scope.append(scope_str)

    # Extract response
    response = parse_response_properties(soup)

    # Extract verb
    verb = soup.find(lambda tag: tag.name == "div" and "Verb:" in tag.text)
    if verb:
        verb = verb.text.split("Verb:")[1].split("\n")[0].strip()
    # Body (optional)
    if verb == "POST":
        request_body = parse_request_body(soup)
    else:
        request_body = None

    logging.info(f"Completed parsing endpoint page: {doc_url}")
    return (
        category.strip(),
        method_name.strip(),
        endpoint_url,
        params,
        description,
        scopes,
        response,
        verb,
        request_body,
        doc_url,
    )


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

    soup = BeautifulSoup(response.text, "html..parser")
    categories = {}
    processed_urls = set()

    endpoints_section = soup.find(
        "h2", string="Contents - Endpoints (Grouped by Tag)"
    ).find_next("div", class_="sidebar-box-contents")

    for category_section in endpoints_section.select("ul > li"):
        category_header = category_section.find("h3")
        category_name = (
            clean_text(category_header.text) if category_header else "Uncategorized"
        )

        endpoints = []
        for endpoint in category_section.select("a"):
            endpoint_url = BASE_URL + endpoint.get("href")
            if endpoint_url in processed_urls:
                continue  # Skip already processed URLs
            processed_urls.add(endpoint_url)
            endpoint_details = parse_endpoint_page(endpoint_url)
            if endpoint_details:
                endpoints.append(endpoint_details)
        categories[category_name] = endpoints

    logging.info("Completed parsing all endpoints!")
    return categories


def save_to_json(data, filename):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)


def load_from_json(filename):
    with open(filename, "r") as file:
        return json.load(file)


class EndpointsGenerator:
    def __init__(self, endpoints):
        self.endpoints = endpoints
        self.base_url = "https://www.bungie.net/Platform"

    @staticmethod
    def format_code(path):
        subprocess.run(["ruff", "check", path, "--fix"])
        subprocess.run(["ruff", "format", path])

    @staticmethod
    def tuple_to_dict_string(tuple_list):
        return ", ".join([f'"{t[0]}": {t[1]}' for t in tuple_list])

    @staticmethod
    def map_type_to_python(type_str):
        type_mapping = {
            "int16": "int",
            "int32": "int",
            "int64": "int",
            "string": "str",
            "date-time": "datetime",
            "byte": "int",  # assuming byte is used as an integer value
            "object": "dict",
            "array": "list",
            "boolean": "bool",
            "uint32": "int",
        }
        return type_mapping.get(type_str, type_str)

    def generate_method(self, endpoint):
        (
            category,
            method_name,
            url,
            params,
            description,
            scopes,
            response,
            verb,
            request_body_params,
            doc_url,
        ) = endpoint
        param_str = ", ".join(
            [f"{p[0]}: {self.map_type_to_python(p[1])}" for p in params]
        )
        request_body_param_str = (
            ", ".join(
                [
                    f"{p[0]}: {self.map_type_to_python(p[1])}"
                    for p in request_body_params
                ]
            )
            if request_body_params
            else ""
        )

        request_body = (
            f"""
        request_body = {{
            {', '.join([f'"{p[0]}": {p[0]}' for p in request_body_params])}
        }}
            """
            if request_body_params
            else ""
        )

        # Parameters docstring
        param_docs = "\n        ".join(
            [f"{p[0]} ({self.map_type_to_python(p[1])}): {p[2]}" for p in params]
        )

        # Response docstring
        return_docs = json.dumps(response["Response"], indent=4)

        method_docstring = f'"""{description}\n\n    Args:\n        {param_docs}\n\n    Returns:\n{return_docs}\n        \n\n.. seealso:: {doc_url}"""'

        return f"""
    async def {method_name}(self, {param_str} {',' if param_str else ''}{request_body_param_str}{", access_token: str" if scopes else ""}) -> dict:
        {method_docstring}
        {request_body}
        try:
            self.logger.info(f"Executing {method_name}...")
            url = self.base_url + f"{url}".format({', '.join([f'{p[0]}={p[0]}' for p in params])})
            return await self.requester.request(method=HTTPMethod.{verb}, url=url{", data=request_body" if request_body_params else ""}{", access_token=access_token" if scopes else ""})
        except Exception as ex:
            self.logger.exception(ex)
        """

    def generate_class(self, class_name: str = ""):
        if class_name == "":
            class_name = "Base"

        # Access the list of endpoints for the given category
        category_endpoints = self.endpoints.get(class_name, [])

        methods = [self.generate_method(endpoint) for endpoint in category_endpoints]
        class_def = f"""
class {class_name}:
    \"\"\"{class_name} endpoints.\"\"\"
    def __init__(self, requester, logger):
        self.requester: Requester = requester
        self.logger = logger
        self.base_url = "{self.base_url}"
    {"".join(methods)}
        """
        return class_def

    def generate_file(self, class_name: str = ""):
        if class_name == "":
            class_name = "Base"
        if class_name == "Uncategorized":
            return
        imports = """
from datetime import datetime
from destipy.utils.http_method import HTTPMethod
from destipy.utils.requester import Requester
    """

        with open(f"{TARGET_FOLDER}/{class_name.lower()}.py", "w") as file:
            file.write(imports)
            file.write(self.generate_class(class_name))

        self.format_code(f"{TARGET_FOLDER}/{class_name.lower()}.py")


def do_work(endpoints_data):
    setup_destipy_folder()
    parse_enums()
    generator = EndpointsGenerator(endpoints_data)
    for category, _ in endpoints_data.items():
        generator.generate_file(category)


def setup_destipy_folder():
    if os.path.exists(DESTIPY_FOLDER):
        shutil.rmtree(DESTIPY_FOLDER)
    shutil.copytree(TEMPLATE_FOLDER, DESTIPY_FOLDER)


if __name__ == "__main__":
    endpoints_file = f"{ROOT_FOLDER}/endpoints.json"
    if os.path.exists(endpoints_file):
        endpoints_data = load_from_json(endpoints_file)
    else:
        endpoints_data = parse_all_endpoints()
        save_to_json(endpoints_data, endpoints_file)

    do_work(endpoints_data)
