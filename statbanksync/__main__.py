#!/usr/bin/env python

import statbanksync

import argparse
from distutils.util import strtobool

import concurrent.futures
import logging
import sys
logging.basicConfig(level=logging.DEBUG)


def confirm(message):
    print(message)
    print("Continue? (y/N)")
    try:
        confirmed = strtobool(input().lower())
    except:
        confirmed = False
    if not confirmed:
        exit(0)


toolbar_width = 40


def handler(x):
    sys.stdout.write("[%s%s]" % ("=" * x['value'], " " * (x['max']-x['value'])))
    sys.stdout.write("\r")
    sys.stdout.flush()

statbanksync.progress.connect(handler)
statbanksync.subprogress.connect(handler)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Update local DST mirror.')
    parser.add_argument('--reset', action='store_true', help='flush db then sync')
    parser.add_argument('tables', nargs='+', help='tables to sync')

    args = parser.parse_args()

    if args.reset:
        confirm("You are about the delete all DST data from the database.")
        statbanksync.reset()

    # Sync table in separate threads
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        for table_id, result in zip(args.tables, executor.map(statbanksync.sync_table, args.tables)):
            print('table %s is synced' % (table_id,))
