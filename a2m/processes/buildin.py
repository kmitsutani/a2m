import json
from random import shuffle
from a2m.processes.translation import translate_text
from abc import ABC, abstractmethod
import numpy as np
from copy import deepcopy
from pathlib import Path
from functools import partial
import re
import deepl

class FeedProcessor(ABC):
    @abstractmethod
    def apply(feeds):
        pass

class Filter(FeedProcessor):
    def __init__(self, config, labels):
        if 'skipped' in labels:
            raise Exception("label 'skipped' is reserved by the program.")
        self.skip_regex = config['skip']
        self.keep_regex = config['keep']

    def apply(self, feed_dict):
        new_feed_dict = dict()
        skipped_items = list()
        for label, feed in feed_dict.items():
            new_feed = list()
            for item in feed:
                if self._if_skip_item(item):
                    skipped_items.append(item)
                else:
                    new_feed.append(item)
            new_feed_dict[label] = new_feed
        new_feed_dict['skipped'] = skipped_items
        return new_feed_dict

    def _if_skip_item(self, item):
        title = item['title']
        summary = item['summary']
        return self._if_skip_buff(title) and self._is_skip_buff(summary)

    def _if_skip_buff(self, string):
        skip_flag = self._match_regex(self.skip_regex, string)
        keep_flag = self._match_regex(self.keep_regex, string)
        if not keep_flag and skip_flag:
            return True
        else:
            return False

    @staticmethod
    def _match_regex(match_regex, string):
        match_flag = False
        for match_re in match_regex:
            if match_flag:
                break
            if isinstance(match_re, str):
                match_flag = (match_re in string)
            for regex, flag_str in match_re.items():
                if match_flag:
                    break
                flags = None
                if flag_str == 'i':
                    flags = re.IGNORECASE
                if re.match(regex, string, flags):
                    match_flag = True
        return match_flag
        

class RandomSampling(FeedProcessor):
    def __init__(self, label_and_count, labels):
        self.target_and_count = dict()
        assert isinstance(label_and_count, dict)
        for k, v in label_and_count.items():
            assert k in labels
            assert isinstance(v, int) 
            self.target_and_count[k] = v

    def apply(self, feeds):
        new_feeds = deepcopy(feeds)
        for l, c in self.target_and_count.items():
            feed = feeds[l]
            shuffle(feed)
            new_feeds[l] = feed[:c]
        return new_feeds

class DeelLTranslation(FeedProcessor):
    def __init__(self, targets, label):
        credentials_path = Path("~/.credentials/deepl_authkey.json").expanduser().absolute()
        auth_key = json.load(credentials_path.open('r'))['auth_key']
        self.targets = targets
        self.translator = deepl.Translator(auth_key)

    def apply(self, feed_dict):
        if 'all' in self.targets:
            return self._translate_all(feed_dict)
        translate_feeds = dict()
        for label in self.targets:
            feed_dict[label] = self._translate_feed(feed_dict[label])
        return feed_dict

    def _translate_all(self, feed_dict):
        translated_feeds = dict()
        for label, feed in feed_dict.items():
            translated_feed = self._translate_feed(deepcopy(feed))
            translated_feeds[label] = deepcopy(translated_feed)
        return translated_feeds

    def _translate_feed(self, feed):
        translated_feed = list()
        for item in feed:
            translated_item = self._translate_item(item)
            translated_feed.append(translated_item)
        return translated_feed

    def _translate_item(self, item):
        title = item['title']
        summary = item['summary']
        translate_text = partial(self.translator.translate_text, target_lang="JA")
        try:
            title_with_trans = f"{title}  {translate_text(title)}"
            summary_with_trans = f"{summary}\n\n{translate_text(summary)}"
        except:
            title_with_trans = f"{title}"
            summary_with_trans = f"{summary}"
        translated_item = deepcopy(item) 
        translated_item['title'] = title_with_trans
        translated_item['summary'] = summary_with_trans
        return translated_item



class GoogleClooudTranslation(FeedProcessor):
    def __init__(self, targets, labels):
        for target in targets:
            assert target in labels or target == 'all'
        self.targets = targets

    def apply(self, feed_dict):
        if 'all' in self.targets:
            return self._translate_all(feed_dict)
        translate_feeds = dict()
        for label in self.targets:
            feed_dict[label] = self._translate_feed(feed_dict[label])
        return feed_dict


    @staticmethod
    def _translate_all(feed_dict):
        translated_feeds = dict()
        for label, feed in feed_dict.items():
            translated_feed = TranslateAbstract._translate_feed(deepcopy(feed))
            translated_feeds[label] = deepcopy(translated_feed)
        return translated_feeds

    @staticmethod
    def _translate_feed(feed):
        translated_feed = list()
        for item in feed:
            translated_item = TranslateAbstract._translate_item(item)
            translated_feed.append(translated_item)
        return translated_feed

    @staticmethod
    def _translate_item(item):
        title = item['title']
        summary = item['summary']
        title_with_trans = f"{title}  {translate_text(title)}"
        # title_with_trans = f"{title}"
        summary_with_trans = f"{summary}\n\n{translate_text(summary)}"
        # summary_with_trans = f"{summary}"
        translated_item = deepcopy(item) 
        translated_item['title'] = title_with_trans
        translated_item['summary'] = summary_with_trans
        return translated_item


    @staticmethod
    def check_arguments(args, labels):
        pass


class HilightingWords(FeedProcessor):
    def __init__(self, args: list, labels):
        self.hl_words = list()
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.items():
                    if k not in ("file"):
                        raise
                    with Path(v).expanduser().open('r') as fin:
                        self.hl_words.extend([x.strip() for x in fin.readlines()])
            if isinstance(arg, str):
                self.hl_words.append(arg)
 
    def apply(self, feeds: dict):
        new_feeds = dict()
        for label, feed in feeds.items():
            new_feed = list()
            for item in feed:
                for hlwd in self.hl_words:
                    new_title = item['title'].replace(
                                    f'{hlwd}', f'<strong>{hlwd}</strong>')
                    item['title'] = new_title

                    new_desc = item['summary'].replace(
                                    f'{hlwd}', f'<strong>{hlwd}</strong>')
                    item['summary'] = new_desc
                new_feed.append(item)
            new_feeds[label] = feed
        return new_feeds

alias_to_processor = dict(
    filter=Filter,
    randsamp=RandomSampling,
    transabs_g=GoogleClooudTranslation,
    transabs_d=DeelLTranslation,
    hilight_words=HilightingWords,
)
