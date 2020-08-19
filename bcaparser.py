#!/usr/bin/env python

import pycurl
from io import BytesIO
import json
import os
import sys
import urllib.parse
import re
from datetime import date, timedelta


class BCA_parser(object):
    """Parse klikbca untuk balance dan transaction"""

    def __init__(self, username, password, ip=None):
        self.username = username
        self.password = password
        # TODO Move all paths to variables
        if ip is None:
            # Some rando website to get public IP
            self.ip = self.curl_exec("http://ip.42.pl/raw")
        else:
            self.ip = ip
        self.c = pycurl.Curl()
        # TODO Get a stable fake useragent
        self.c.setopt(self.c.USERAGENT, "Mozilla/5.0 (Linux; U; Android 2.3.7; en-us; Nexus One Build/GRK39F) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1")
        # TODO Do not store cookies to a file
        self.c.setopt(self.c.COOKIEFILE, self.file_location("cookie"))
        self.c.setopt(self.c.COOKIEJAR, self.file_location("cookiejar"))
        self.c.setopt(self.c.SSL_VERIFYHOST, 0)
        self.c.setopt(self.c.SSL_VERIFYPEER, 0)
        self.c.setopt(self.c.FOLLOWLOCATION, True)

    # TODO Remove
    def file_location(self, filename):
        __location__ = os.path.realpath(os.path.join(
            os.getcwd(), os.path.dirname(__file__)))
        return os.path.join(__location__, filename)

    def curl_exec(self, url, referer="", params={}, post=False):
        buff = BytesIO()

        self.c.setopt(self.c.URL, url)
        self.c.setopt(self.c.REFERER, referer)
        self.c.setopt(self.c.WRITEFUNCTION, buff.write)

        if post:
            self.c.setopt(self.c.POSTFIELDS, urllib.parse.urlencode(params))
            self.c.setopt(self.c.POST, 1)

        self.c.perform()

        retval = buff.getvalue()
        buff.close()

        return retval.decode('iso-8859-1')

    def login(self):
        print("logging in...")
        self.curl_exec("https://m.klikbca.com/login.jsp")

        params = {}
        params["value(user_id)"] = self.username
        params["value(pswd)"] = self.password
        params["value(Submit)"] = "LOGIN"
        params["value(actions)"] = "login"
        params["value(user_ip)"] = self.ip
        params["user_ip"] = self.ip
        params["value(mobile)"] = "true"
        params["mobile"] = "true"
        retval = self.curl_exec("https://m.klikbca.com/authentication.do",
                                "https://m.klikbca.com/login.jsp", params, True)

        if "Informasi Rekening" in retval:
            return True
        else:
            print("Gagal login, mungkin sedang digunakan")
            return False

    def logout(self):
        print("logging out...")
        self.curl_exec("https://m.klikbca.com/authentication.do?value(actions)=logout",
                       "https://m.klikbca.com/authentication.do?value(actions)=menu")

    def get_transactions(self):
        print("get transaction")
        self.curl_exec("https://m.klikbca.com/accountstmt.do?value(actions)=menu",
                       "https://m.klikbca.com/authentication.do")
        self.curl_exec("https://m.klikbca.com/accountstmt.do?value(actions)=acct_stmt",
                       "https://m.klikbca.com/accountstmt.do?value(actions)=menu")

        today = date.today()
        fromdate = date.today() - timedelta(days=7)

        params = {}
        params["r1"] = 0
        params["value(D1)"] = 0
        params["value(startDt)"] = fromdate.day
        params["value(startMt)"] = fromdate.month
        params["value(startYr)"] = fromdate.year
        params["value(endDt)"] = today.day
        params["value(endMt)"] = today.month
        params["value(endYr)"] = today.year
        retval = self.curl_exec("https://m.klikbca.com/accountstmt.do?value(actions)=acctstmtview",
                                "https://m.klikbca.com/accountstmt.do?value(actions)=acct_stmt", params, True)

        pattern_balance = re.compile(
            "<tr bgcolor='#(?:e0e0e0|f0f0f0)'><td valign='top'>([0-9/]+|PEND)<\/td><td>(.+)<td valign='top'>(DB|CR)<\/td>")
        match = pattern_balance.findall(retval)
        return match

    def get_balance(self):
        print("get balance")
        self.curl_exec("https://m.klikbca.com/accountstmt.do?value(actions)=menu",
                       "https://m.klikbca.com/authentication.do")
        retval = self.curl_exec("https://m.klikbca.com/balanceinquiry.do",
                                "https://m.klikbca.com/accountstmt.do?value(actions)=menu")

        pattern_balance = re.compile(
            "<td align='right'><font size='1' color='#0000a7'><b>([0-9,.]+)</td>")
        match = pattern_balance.search(retval)
        balance = 0
        if match:
            # print(match.group(1))
            balance = float(match.group(1).replace(",", ""))

        return balance


def main():
	# TODO Better way to get credentials
    username = os.getenv("BCA_USERNAME", "username")
    password = os.getenv("BCA_USERNAME", "password")
    bcaparser = BCA_parser(username, password)

    if bcaparser.login():
        print(bcaparser.get_balance())
        print(bcaparser.get_transactions())
        bcaparser.logout()


if __name__ == "__main__":
    main()
