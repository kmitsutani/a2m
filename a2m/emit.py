from a2m.config import parse_config
from a2m.rss import get_and_parse_rss, build_arxiv_rss_url
from a2m.processes.buildin import alias_to_processor
from a2m.outputs.mail import SmtpMailSender


def emit(config_yml):
    parsed_config = parse_config(config_yml)
    inputs = parsed_config['inputs']
    catsym2label = {x.category: x.label for x in inputs}
    categories = [x.category for x in inputs]
    rssurl = build_arxiv_rss_url(categories)
    feeds = get_and_parse_rss(rssurl)


    feed_dict = dict()
    for cat in categories:
        entries = [
            x for x in feeds if cat in x['tags']
        ]
        if isinstance(entries[0], list):
            entries = entries[0]
        feed_dict[catsym2label[cat]] = entries

    processes = parsed_config['processes']
    for process in processes:
        feed_dict = process.apply(feed_dict)

    outputs = parsed_config['outputs']
    for output in outputs:
        output.emit(feed_dict)
