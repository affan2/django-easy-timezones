from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.db import models
from django.test import TestCase, Client

import os

from .middleware import load_db, load_db_settings, EasyTimezoneMiddleware
from .utils import get_ip_address_from_request, is_valid_ip, is_local_ip


class TimezoneTests(TestCase):
    
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2. (Sanity test.)
        """

        self.assertEqual(1 + 1, 2)

    def test_load_db_settings(self):
        settings.GEOIP_DATABASE = None
        try:
            load_db_settings()
            error_occured = False
        except ImproperlyConfigured:
            error_occured = True
        self.assertTrue(error_occured)

        settings.GEOIP_DATABASE = 'does not exist'
        try:
            load_db_settings()
            error_occured = False
        except ImproperlyConfigured:
            error_occured = True
        self.assertTrue(error_occured)

        settings.GEOIP_DATABASE = os.path.join(os.getcwd(), 'GeoLiteCity.dat')
        try:
            error_occured = False
        except ImproperlyConfigured:
            error_occured = True
        self.assertFalse(error_occured)

    def test_middleware(self):
        load_db()
        easy = EasyTimezoneMiddleware()
        easy.process_request(None)

    def test_tags(self):

        # UTC
        client = Client()
        response = client.get('/without_tz/')
        self.assertEqual(response.status_code, 200)
        without_s = response.content

        # Europe/Moscow
        client = Client(REMOTE_ADDR="93.180.5.26")
        response = client.get('/with_tz/')
        self.assertEqual(response.status_code, 200)
        with_s = response.content

        self.assertNotEqual(without_s, with_s)

        # Europe/Oslo
        client = Client(REMOTE_ADDR="2001:700:300:2321::11")
        response = client.get('/with_tz/')
        self.assertEqual(response.status_code, 200)
        with_s = response.content

        self.assertNotEqual(without_s, with_s)

        # Localhost
        client = Client(REMOTE_ADDR="127.0.0.1")
        response = client.get('/with_tz/')
        self.assertEqual(response.status_code, 200)
        with_s = response.content
        self.assertEqual(without_s, with_s)

        # Localhost IPv6
        client = Client(REMOTE_ADDR="0:0:0:0:0:0:0:1")
        response = client.get('/with_tz/')
        self.assertEqual(response.status_code, 200)
        with_s = response.content
        self.assertEqual(without_s, with_s)

    def test_is_local_ip(self):
        self.assertTrue(is_local_ip('127.0.0.1'))
        self.assertTrue(is_local_ip("0:0:0:0:0:0:0:1"))
        self.assertEqual(is_local_ip("1600 Pennyslvania Avenue"), None)

    def test_valid_ips(self):
        # IPv4
        self.assertTrue(is_valid_ip('127.0.0.1'))
        self.assertFalse(is_valid_ip('127.0.0.1.1'))

        # IPv6
        self.assertTrue(is_valid_ip('2001:cdba:0000:0000:0000:0000:3257:9652'))
        self.assertTrue(is_valid_ip('2001:cdba:0:0:0:0:3257:9652'))
        self.assertTrue(is_valid_ip('2001:cdba::3257:9652'))

        valid_6 = """
1111:2222:3333:4444:5555:6666:7777:8888
1111:2222:3333:4444:5555:6666:7777::
1111:2222:3333:4444:5555:6666::
1111:2222:3333:4444:5555::
1111:2222:3333:4444::
1111:2222:3333::
1111:2222::
1111::
::
1111:2222:3333:4444:5555:6666::8888
1111:2222:3333:4444:5555::8888
1111:2222:3333:4444::8888
1111:2222:3333::8888
1111:2222::8888
1111::8888
::8888
1111:2222:3333:4444:5555::7777:8888
1111:2222:3333:4444::7777:8888
1111:2222:3333::7777:8888
1111:2222::7777:8888
1111::7777:8888
::7777:8888
1111:2222:3333:4444::6666:7777:8888
1111:2222:3333::6666:7777:8888
1111:2222::6666:7777:8888
1111::6666:7777:8888
::6666:7777:8888
1111:2222:3333::5555:6666:7777:8888
1111:2222::5555:6666:7777:8888
1111::5555:6666:7777:8888
::5555:6666:7777:8888
1111:2222::4444:5555:6666:7777:8888
1111::4444:5555:6666:7777:8888
::4444:5555:6666:7777:8888
1111::3333:4444:5555:6666:7777:8888
::3333:4444:5555:6666:7777:8888
::2222:3333:4444:5555:6666:7777:8888
1111:2222:3333:4444:5555:6666:123.123.123.123
1111:2222:3333:4444:5555::123.123.123.123
1111:2222:3333:4444::123.123.123.123
1111:2222:3333::123.123.123.123
1111:2222::123.123.123.123
1111::123.123.123.123
::123.123.123.123
1111:2222:3333:4444::6666:123.123.123.123
1111:2222:3333::6666:123.123.123.123
1111:2222::6666:123.123.123.123
1111::6666:123.123.123.123
::6666:123.123.123.123
1111:2222:3333::5555:6666:123.123.123.123
1111:2222::5555:6666:123.123.123.123
1111::5555:6666:123.123.123.123
::5555:6666:123.123.123.123
1111:2222::4444:5555:6666:123.123.123.123
1111::4444:5555:6666:123.123.123.123
::4444:5555:6666:123.123.123.123
1111::3333:4444:5555:6666:123.123.123.123
::3333:4444:5555:6666:123.123.123.123
::2222:3333:4444:5555:6666:123.123.123.123"""

        for valid in valid_6.split('\n'):
            if len(valid) == 0:
                continue
            self.assertTrue(is_valid_ip(valid))
            #self.assertTrue(ipaddress.ip_address('' + valid))

        invalid_6 = """
XXXX:XXXX:XXXX:XXXX:XXXX:XXXX:XXXX:XXXX
1111:2222:3333:4444:5555:6666:7777:8888:9999
1111:2222:3333:4444:5555:6666:7777:8888::
::2222:3333:4444:5555:6666:7777:8888:9999
1111:2222:3333:4444:5555:6666:7777
1111:2222:3333:4444:5555:6666
1111:2222:3333:4444:5555
1111:2222:3333:4444
1111:2222:3333
1111:2222
1111
11112222:3333:4444:5555:6666:7777:8888
1111:22223333:4444:5555:6666:7777:8888
1111:2222:33334444:5555:6666:7777:8888
1111:2222:3333:44445555:6666:7777:8888
1111:2222:3333:4444:55556666:7777:8888
1111:2222:3333:4444:5555:66667777:8888
1111:2222:3333:4444:5555:6666:77778888
1111:2222:3333:4444:5555:6666:7777:8888:
1111:2222:3333:4444:5555:6666:7777:
1111:2222:3333:4444:5555:6666:
1111:2222:3333:4444:5555:
1111:2222:3333:4444:
1111:2222:3333:
1111:2222:
1111:
:
:8888
:7777:8888
:6666:7777:8888
:5555:6666:7777:8888
:4444:5555:6666:7777:8888
:3333:4444:5555:6666:7777:8888
:2222:3333:4444:5555:6666:7777:8888
:1111:2222:3333:4444:5555:6666:7777:8888
:::2222:3333:4444:5555:6666:7777:8888
1111:::3333:4444:5555:6666:7777:8888
1111:2222:::4444:5555:6666:7777:8888
1111:2222:3333:::5555:6666:7777:8888
1111:2222:3333:4444:::6666:7777:8888
1111:2222:3333:4444:5555:::7777:8888
1111:2222:3333:4444:5555:6666:::8888
1111:2222:3333:4444:5555:6666:7777:::
::2222::4444:5555:6666:7777:8888
::2222:3333::5555:6666:7777:8888
::2222:3333:4444::6666:7777:8888
::2222:3333:4444:5555::7777:8888
::2222:3333:4444:5555:7777::8888
::2222:3333:4444:5555:7777:8888::
1111::3333::5555:6666:7777:8888
1111::3333:4444::6666:7777:8888
1111::3333:4444:5555::7777:8888
1111::3333:4444:5555:6666::8888
1111::3333:4444:5555:6666:7777::
1111:2222::4444::6666:7777:8888
1111:2222::4444:5555::7777:8888
1111:2222::4444:5555:6666::8888
1111:2222::4444:5555:6666:7777::
1111:2222:3333::5555::7777:8888
1111:2222:3333::5555:6666::8888
1111:2222:3333::5555:6666:7777::
1111:2222:3333:4444::6666::8888
1111:2222:3333:4444::6666:7777::
1111:2222:3333:4444:5555::7777::
XXXX:XXXX:XXXX:XXXX:XXXX:XXXX:1.2.3.4
1111:2222:3333:4444:5555:6666:256.256.256.256
1111:2222:3333:4444:5555:6666:7777:8888:1.2.3.4
1111:2222:3333:4444:5555:6666:7777:1.2.3.4
1111:2222:3333:4444:5555:6666::1.2.3.4
::2222:3333:4444:5555:6666:7777:1.2.3.4
1111:2222:3333:4444:5555:6666:1.2.3.4.5
1111:2222:3333:4444:5555:1.2.3.4
1111:2222:3333:4444:1.2.3.4
1111:2222:3333:1.2.3.4
1111:2222:1.2.3.4
1111:1.2.3.4
11112222:3333:4444:5555:6666:1.2.3.4
1111:22223333:4444:5555:6666:1.2.3.4
1111:2222:33334444:5555:6666:1.2.3.4
1111:2222:3333:44445555:6666:1.2.3.4
1111:2222:3333:4444:55556666:1.2.3.4
1111:2222:3333:4444:5555:66661.2.3.4
1111:2222:3333:4444:5555:6666:255255.255.255
1111:2222:3333:4444:5555:6666:255.255255.255
1111:2222:3333:4444:5555:6666:255.255.255255
:1.2.3.4
:6666:1.2.3.4
:5555:6666:1.2.3.4
:4444:5555:6666:1.2.3.4
:3333:4444:5555:6666:1.2.3.4
:2222:3333:4444:5555:6666:1.2.3.4
:1111:2222:3333:4444:5555:6666:1.2.3.4
:::2222:3333:4444:5555:6666:1.2.3.4
1111:::3333:4444:5555:6666:1.2.3.4
1111:2222:::4444:5555:6666:1.2.3.4
1111:2222:3333:::5555:6666:1.2.3.4
1111:2222:3333:4444:::6666:1.2.3.4
1111:2222:3333:4444:5555:::1.2.3.4
::2222::4444:5555:6666:1.2.3.4
::2222:3333::5555:6666:1.2.3.4
::2222:3333:4444::6666:1.2.3.4
::2222:3333:4444:5555::1.2.3.4
1111::3333::5555:6666:1.2.3.4
1111::3333:4444::6666:1.2.3.4
1111::3333:4444:5555::1.2.3.4
1111:2222::4444::6666:1.2.3.4
1111:2222::4444:5555::1.2.3.4
1111:2222:3333::5555::1.2.3.4
::.
::..
::...
::1...
::1.2..
::1.2.3.
::.2..
::.2.3.
::.2.3.4
::..3.
::..3.4
::...4
:1111:2222:3333:4444:5555:6666:7777::
:1111:2222:3333:4444:5555:6666::
:1111:2222:3333:4444:5555::
:1111:2222:3333:4444::
:1111:2222:3333::
:1111:2222::
:1111::
:::
:1111:2222:3333:4444:5555:6666::8888
:1111:2222:3333:4444:5555::8888
:1111:2222:3333:4444::8888
:1111:2222:3333::8888
:1111:2222::8888
:1111::8888
:::8888
:1111:2222:3333:4444:5555::7777:8888
:1111:2222:3333:4444::7777:8888
:1111:2222:3333::7777:8888
:1111:2222::7777:8888
:1111::7777:8888
:::7777:8888
:1111:2222:3333:4444::6666:7777:8888
:1111:2222:3333::6666:7777:8888
:1111:2222::6666:7777:8888
:1111::6666:7777:8888
:::6666:7777:8888
:1111:2222:3333::5555:6666:7777:8888
:1111:2222::5555:6666:7777:8888
:1111::5555:6666:7777:8888
:::5555:6666:7777:8888
:1111:2222::4444:5555:6666:7777:8888
:1111::4444:5555:6666:7777:8888
:::4444:5555:6666:7777:8888
:1111::3333:4444:5555:6666:7777:8888
:::3333:4444:5555:6666:7777:8888
:::2222:3333:4444:5555:6666:7777:8888
:1111:2222:3333:4444:5555:6666:1.2.3.4
:1111:2222:3333:4444:5555::1.2.3.4
:1111:2222:3333:4444::1.2.3.4
:1111:2222:3333::1.2.3.4
:1111:2222::1.2.3.4
:1111::1.2.3.4
:::1.2.3.4
:1111:2222:3333:4444::6666:1.2.3.4
:1111:2222:3333::6666:1.2.3.4
:1111:2222::6666:1.2.3.4
:1111::6666:1.2.3.4
:::6666:1.2.3.4
:1111:2222:3333::5555:6666:1.2.3.4
:1111:2222::5555:6666:1.2.3.4
:1111::5555:6666:1.2.3.4
:::5555:6666:1.2.3.4
:1111:2222::4444:5555:6666:1.2.3.4
:1111::4444:5555:6666:1.2.3.4
:::4444:5555:6666:1.2.3.4
:1111::3333:4444:5555:6666:1.2.3.4
:::3333:4444:5555:6666:1.2.3.4
:::2222:3333:4444:5555:6666:1.2.3.4
1111:2222:3333:4444:5555:6666:7777:::
1111:2222:3333:4444:5555:6666:::
1111:2222:3333:4444:5555:::
1111:2222:3333:4444:::
1111:2222:3333:::
1111:2222:::
1111:::
:::
1111:2222:3333:4444:5555:6666::8888:
1111:2222:3333:4444:5555::8888:
1111:2222:3333:4444::8888:
1111:2222:3333::8888:
1111:2222::8888:
1111::8888:
::8888:
1111:2222:3333:4444:5555::7777:8888:
1111:2222:3333:4444::7777:8888:
1111:2222:3333::7777:8888:
1111:2222::7777:8888:
1111::7777:8888:
::7777:8888:
1111:2222:3333:4444::6666:7777:8888:
1111:2222:3333::6666:7777:8888:
1111:2222::6666:7777:8888:
1111::6666:7777:8888:
::6666:7777:8888:
1111:2222:3333::5555:6666:7777:8888:
1111:2222::5555:6666:7777:8888:
1111::5555:6666:7777:8888:
::5555:6666:7777:8888:
1111:2222::4444:5555:6666:7777:8888:
1111::4444:5555:6666:7777:8888:
::4444:5555:6666:7777:8888:
1111::3333:4444:5555:6666:7777:8888:
::3333:4444:5555:6666:7777:8888:
::2222:3333:4444:5555:6666:7777:8888:"""

        for invalid in invalid_6.split('\n'):
            if len(invalid) == 0:
                continue
            self.assertFalse(is_valid_ip(invalid))
