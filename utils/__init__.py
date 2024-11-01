import re
from datetime import datetime
from pathlib import Path

import requests
from slugify import slugify
from yaml import Loader, load


def get_settings(key=None):
    with open("settings.yml", "r") as stream:
        data = load(stream, Loader=Loader)

    if not key:
        return data
    return data[key]


def get_html_cache(page):
    page_slugified = slugify(page)
    html_cache = Path(f"cache/{page_slugified}.html")
    html_cache.parent.mkdir(parents=True, exist_ok=True)
    return html_cache


def get_output(page):
    page_slugified = slugify(page)
    output = Path(f"output/{page_slugified}.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    return output


def expired(file):
    now = datetime.now()
    file_age = datetime.fromtimestamp(file.stat().st_mtime)
    diff = now - file_age

    return diff.days > 7


def download_pages(pages):
    ACCESS_TOKEN = get_settings("ACCESS_TOKEN")
    APP_NAME = get_settings("APP_NAME")
    EMAIL = get_settings("EMAIL")

    for page in pages:
        html_cache = get_html_cache(page)
        if not html_cache.exists() or (html_cache.exists() and expired(html_cache)):
            page_url = page.replace("'", "%27").replace(" ", "_").replace("(", "").replace(")", "")
            url = f"https://api.wikimedia.org/core/v1/wikipedia/en/page/{page_url}/html"

            headers = {
                "Authorization": f"Bearer {ACCESS_TOKEN}",
                "User-Agent": f"{APP_NAME} (f{EMAIL})",
            }

            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                text = response.text
                html_cache.write_text(text)
            else:
                print(f"Could not download page {page} ({page_url})", response.status_code)


def strip_from_wiki_refs(text):
    if not isinstance(text, str):
        return text

    fixed = re.sub(r"\[(\d+|[a-z]|lower-alpha \d+)\]", "", text)

    fixed = fixed.strip()

    try:
        fixed = int(fixed)
    except ValueError:
        pass

    # if fixed:
    #     print(text, "-->", fixed)

    return fixed
