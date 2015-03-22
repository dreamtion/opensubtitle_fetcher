#!/usr/bin/env python

import sys
import os
import wget
import argparse
import xmlrpclib as xmlrpc_client
from xmlrpclib import Transport
from utils import hashfile, unzip

# MAXINT is too short by default
xmlrpc_client.MAXINT = sys.maxint

OPENSUB_URL = "http://api.opensubtitles.org/xml-rpc"
USER_AGENT = 'OSTestUserAgent'
USERNAME = ''
PASSWORD = ''
LANGUAGE = 'en'
VERBOSE = False
LANGS = ('eng', 'zht', 'chi')


class SpecialTransport(Transport):
    user_agent = USER_AGENT


class MyOpenSub(object):
    def __init__(self, url, token=None):
        try:
            # Use the verbose flag for debugging
            self.server = xmlrpc_client.ServerProxy(OPENSUB_URL,
                                                    transport=SpecialTransport(),
                                                    verbose=VERBOSE)
            self.token = token

        except xmlrpc_client.ProtocolError as err:
            print "A protocol error occurred"
            print "URL: %s" % err.url
            print "HTTP/HTTPS headers: %s" % err.headers
            print "Error code: %d" % err.errcode
            print "Error message: %s" % err.errmsg

    def login(self, username, password, language, useragent):
        if not self.token:
            result = self.server.LogIn(username, password, language, useragent)
            self.token = result['token']
            print "Token: %s" % self.token

    def logout(self):
        if not self.token:
            print "Please login first"
            return
        self.server.LogOut(self.token)

    def search_sub_links(self, file_hash, file_bytes):
        results = []
        if not self.token:
            print "Please login first"
            return
        for lang in LANGS:
            query = {'moviehash': file_hash,
                     'moviebytesize': file_bytes,
                     'sublanguageid': lang}

            result = self.server.SearchSubtitles(self.token, [query])
            if result['data']:
                for sub_item in result['data']:
                    results.append(sub_item['SubDownloadLink'])
        return results


def get_parser():
    """Return a arg parser
    """

    parser = argparse.ArgumentParser(
        description='Opensubtitle auto subtitle fetcher')

    parser.add_argument('-t', '--token')
    parser.add_argument('-d', '--directory')
    parser.add_argument('filename')

    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()
    fetch_sub(args.filename, directory=args.directory, token=args.token)


def fetch_sub(filename, directory=None, token=None):
    my_open_sub = MyOpenSub(OPENSUB_URL, token)
    if not token:
        my_open_sub.login(USERNAME, PASSWORD, LANGUAGE, USER_AGENT)
    file_hash, file_bytes = hashfile(filename)
    dl_links = my_open_sub.search_sub_links(file_hash, file_bytes)
    if not directory:
        directory = os.path.dirname(filename)
    for dl_link in dl_links:
        try:
            filename = wget.download(dl_link, out=directory)
            print "Download finished: %s" % filename
            filename = unzip(filename, directory)
            if filename:
                print "Unzipped to %s" % filename
        except IOError as io_error:
            print io_error
    #my_open_sub.logout()


if __name__ == '__main__':
    sys.exit(main())
