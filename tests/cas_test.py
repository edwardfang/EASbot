#!/usr/bin/env python3

import logging
import json
from eas_bot.cas import CASSession

def test_run(caplog):
    caplog.set_level(logging.DEBUG)
    # logging.basicConfig(level=logging.DEBUG)
    with open("./tests/account_info.json") as account_info:
        info = account_info.read().replace('\n', '')
    info = json.loads(info)
    uid = info['studentId']
    passwd = info['password']
    c = CASSession()
    c.setAuthInfo(uid, passwd)
    assert c.loginService()