#!/usr/bin/python
# -*- coding: utf-8 -*-

from base import Base

class Wenzhi(Base):
    requestHost = 'wenzhi.api.qcloud.com'

def main():
    action = 'TextSentiment'
    config = {
        'Region': 'bj',
        'secretId': 'AKID0IvaSG3K260IgxG7dcRZITv54y0Wvn8L',
        'secretKey': 'ctzE5bet9iTWGXieMYMijN6yYRfW0vyA',
        'method': 'post'
    }
    params = {
        "content" : "苹果手机是未激活正品，质量很好，2g运行快",
    }
    service = Wenzhi(config)
    print service.call(action, params)

if __name__ == '__main__':
    main()
