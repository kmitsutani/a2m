import os
from pathlib import Path
import base64
from email import message
import smtplib
import ssl

from pathlib import Path

from yaml import load, dump
import json
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

enc = "utf-8"


class QuotaExceedException(Exception):
    pass

import time


class Throttler:
    def __init__(self, quota_count,  quota_duration):
        self.quota_count = quota_count 
        self.quota_duration = quota_duration  
        self.counter = 0
        self.base_time = None

    def execute(self, task):
        if self.base_time is None:
            self.last_update = time.time()
        current_time = time.time()

        elapsed_time = current_time - self.last_update

        if elapsed_time >= self.quota_duration:
            self.quota_count = 0
            self.base_time = current_time

        while self.counter >= self.quota_count:
            time.sleep(0.1)

        result = task()
        self.counter += 1

        return result


class SmtpMailSender():
    def __init__(self, *args, **kwargs):
        keys = kwargs.keys()
        assert len(keys) == 1
        self.label = list(keys)[0]
        config = kwargs[self.label]
        self.server = smtplib.SMTP(config['host'], config['port'])
        with Path(config['credentials']).expanduser().open('r') as fin:
            self.credentials = json.load(fin)
        self.fromwho = config['from']
        self.to = config['to']
        if 'quota_count' not in config or 'quota_duration' not in config: 
            self.care_quota = False
        else:
            self.care_quota = True
            self.throttler = Throttler(quota_count, quota_duration)

    
    @staticmethod
    def _compose_message(sender, to, subject, message_text, subtype='text'):
        msg = message.EmailMessage()
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = to
        msg.set_content(message_text)

        return msg

    def _send_mail(self, sender, to, subject, message_text, subtype='text'):
        msg = self._compose_message(
                sender, to, subject, message_text, subtype)
        self._loginserver()
        self.server.send_message(msg)
        self.server.quit()

    def _loginserver(self):
        self.server.ehlo()
        self.server.starttls()
        self.server.ehlo()
        self.server.login(self.credentials['username'], self.credentials['password'])

    def send_mails(self, mails): 
        self._loginserver()
        for mail in mails:
            msg = self._compose_message(
                    self.fromwho, self.to, mail['subject'], mail['body'], mail['subtype'])
            self.server.send_message(msg)
            time.sleep(0.01)
        self.server.quit()

    def emit(self, feed_dict):
        mails = list()
        for label, feed in feed_dict.items():
            for item in feed:
                subject = f"[{label}] {item['title']} {item['annotype']}"
                message_text = f"""
Authors: {item['authors']}
Title: {item['title']}

Abstract:
{item['summary']}

Tags:
{', '.join(item['tags'])}
""".strip()
                mails.append(dict(
                    subject=subject,
                    body=message_text,
                    subtype='text'))
        self.send_mails(mails)

class GmailSmtpSender():

    def __init__(self, *args, **kwargs):
        keys = kwargs.keys()
        assert len(keys) == 1
        self.label = list(keys)[0]
        config = kwargs[self.label]
        self.server = smtplib.SMTP_SSL(config['host'], config['port'],
                                       context=ssl.create_default_context())
        with Path(config['credentials']).expanduser().open('r') as fin:
            self.credentials = json.load(fin)
        self.fromwho = config['from']
        self.to = config['to']
        if 'quota_count' not in config or 'quota_duration' not in config: 
            self.care_quota = False
        else:
            self.care_quota = True
            self.throttler = Throttler(quota_count, quota_duration)


    @staticmethod
    def _compose_message(sender, to, subject, message_text, subtype='text'):
        msg = message.EmailMessage()
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = to
        msg.set_content(message_text)

        return msg

    def emit(self, feed_dict):
        mails = list()
        for label, feed in feed_dict.items():
            for item in feed:
                subject = f"[{label}] {item['title']} {item['annotype']}"
                message_text = f"""
Authors: {item['authors']}
Title: {item['title']}
{item['link']}

Abstract:
{item['summary']}

Tags:
{', '.join(item['tags'])}
""".strip()
                mails.append(dict(
                    subject=subject,
                    body=message_text,
                    subtype='text'))
        self.send_mails(mails)

    def send_mails(self, mails): 
        self.server.set_debuglevel(0)
        self.server.login(self.credentials['account'], self.credentials['apikey']) 
        for mail in mails:
            msg = self._compose_message(
                    self.fromwho, self.to, mail['subject'], mail['body'], mail['subtype'])
            self.server.send_message(msg)
        self.server.quit()



if __name__ == "__main__":
    pass
