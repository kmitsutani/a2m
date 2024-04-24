#!/usr/bin/env python3
import json
from time import strftime
from datetime import datetime
import requests

from bs4 import BeautifulSoup, NavigableString
from loguru import logger

from a2m import __VERSION__


def parse_category_taxonomy(html_source):
    soup = BeautifulSoup(html_source, "lxml")
    ct_list = soup.find(id="category_taxonomy_list")
    ct_dict = dict()
    for node in ct_list:
        if isinstance(node, NavigableString):
            continue
        else:
            if node.name == 'h2':
                section = node.text
            elif node.name == 'div':
                ct_dict[section] = parse_section_body(node)
    return ct_dict

def parse_section_body(bsdiv):
    sym_desc = list()
    subdivs = bsdiv.find_all(name='div', attrs={"class": ["columns","divided"]})
    for subdiv in subdivs:
        if isinstance(subdiv, NavigableString):
            continue
        for elm in subdiv.h4:
            if isinstance(elm, NavigableString):
                name = elm.text.strip()
            else:
                _id = elm.text.strip()
        desc = subdiv.p.text
        sym_desc.append({"category name":name, "id":_id, "description": desc})
    return sym_desc


def initialize():
    logger.info("start initializing...")
    # make cache dir
    cachedir = Path("~/.cache/a2m")
    if not cachedir.exists():
        cachedir.mkdir(parent=True)
        logger.info(f"made a directory {cachedir}")

    # make category_taxonomy.json
    r = requests.get("https://arxiv.org/category_taxonomy")
    if r.status_code != 200:
        raise Exception("Could not get category_taxonomy retry init.")
    category_taxonomy = parse_category_taxonomy(r.text)
    category_taxonomy_json = cachedir / "category_taxonomy.json"
    with category_taxonomy_json.open('w') as fout:
        json.dump(category_taxonomy, fout)
    logger.info(f"category taxonomy is dumped into {category_taxonomy_json}")

    # make init.json 
    with (cachedir / "init.json").open('w') as fout:
        json.dump(dict(
            VERSION=__VERSION__,
            initialized=strftime("%Y-%m-%d %H:%M:%S", datetime.now()),
            category_taxonomoy=category_taxonomy_json
        ), fout)
    logger.info(f"record the initialize info {cachedir / 'init.json'}")
    logger.info("initialize process is finished.")
