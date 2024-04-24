arXiv RSS feeds to mail
=======================

## Install

In some python virtual environment
```
pip install https://github.com/kmitsutani/a2m
```

## Initialization

If you run
```
python -m a2m init
```
it makes
- $HOME/.cache/a2m/
- $HOME/.cache/a2m/init.json
- $HOME/.cache/a2m/category_taxonomy.json


## one-time emit
```
python -m a2m emit -c /path/to/config.yml
```

example of `config.yml` is [conf/config.yml.example]


## set systemd.timer and boot daily

templates of service and timer files are in [conf/systemd/].

fill placeholder then start and enable them.

