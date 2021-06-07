import configparser
import json

import requests

from constant.consts import *
from exception.null_exception import NullException


class PushPlusUtil:

    def __init__(self, config_file):
        if config_file is None or config_file == '':
            raise NullException("配置文件不能为空.")

        self.config_file = config_file
        cf = configparser.ConfigParser()
        cf.read(config_file)
        pushplus = cf[PUSH_PLUS]
        scheme = pushplus[SCHEME]
        host = pushplus[HOST]
        self.url = scheme + "://" + host
        self.send_url = self.url + pushplus[SEND]
        self.token = pushplus[TOKEN]
        self.topic = pushplus[TOPIC]
        self.template = pushplus[TEMPLATE]

    def send(self, title, content):
        data = {
            "token": self.token,
            "topic": self.topic,
            "title": title,
            "content": content,
            "template": self.template
        }
        body = json.dumps(data).encode('utf-8')
        headers = {'Content-Type': 'application/json'}
        requests.post(self.send_url, body, headers)
