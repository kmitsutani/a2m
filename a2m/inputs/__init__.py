import json
from pathlib import Path
from collections import namedtuple
Feed = namedtuple('Feed', 'label category')

category_names = list()
with Path("~/.cache/a2m/category_taxonomy.json").expanduser().open('r') as fin:
    taxonomy = json.load(fin)
    for genre, categories in taxonomy.items():
        category_names.extend([elm['category name'] for elm in categories])
