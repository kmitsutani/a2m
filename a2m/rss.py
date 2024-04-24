import feedparser
import re

def build_arxiv_rss_url(categories):
    catsym_sorted=sorted(categories)
    return 'https://rss.arxiv.org/rss/' + '+'.join(catsym_sorted)
    

def trim_summary(summary):
    return re.sub("^arXiv:\d{4}\.\d+v\d+ Announce Type: [a-zA-Z]+\nAbstract: ", "", summary)


def get_and_parse_rss(rssurl):
    fpdict = feedparser.parse(rssurl)
    feeds = list()
    for item in fpdict['entries']:
        feeds.append(dict(
            title=item['title'],
            authors=item['author'],
            summary=trim_summary(item['summary']),
            tags=[x['term'] for x in item['tags']],
            link=item['link'],
            annotype=item['arxiv_announce_type']
        ))
    return feeds
    
if __name__ == "__main__":    
    url = build_arxiv_rss_url(['quant-ph'])
    print(url)
    feeds = get_and_parse_rss(url)
    print(feeds)
