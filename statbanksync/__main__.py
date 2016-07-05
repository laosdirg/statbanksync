# CLI tool for statbanksync

import statbanksync

import argparse
from distutils.util import strtobool
from apscheduler.schedulers.blocking import BlockingScheduler

import concurrent.futures
import logging
import sys
logging.basicConfig(level=logging.DEBUG)

from . import database

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


def handler(sender):
    sys.stdout.write("[%s%s]" % ("=" * sender['value'], " " * (sender['max']-sender['value'])))
    sys.stdout.write("\r")
    sys.stdout.flush()

def sync_tables(tables):
    # Sync table in separate threads
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        for table_id, result in zip(tables, executor.map(statbanksync.sync_table, tables)):
            print('table {} is synced'.format(table_id))


statbanksync.progress.connect(handler)
statbanksync.subprogress.connect(handler)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Update local DST mirror.')
    parser.add_argument('--reset', action='store_true', help='flush db then sync')
    parser.add_argument('--schedule', action='store_true', help='schedule for execution every sunday at 3 am')
    parser.add_argument('tables', nargs='+', help='tables to sync')

    args = parser.parse_args()

    if not database.works():
        print("ERROR: Could not connect to database")
        exit(0)

    if args.reset:
        confirm("You are about the delete all DST data from the database.")
        statbanksync.reset()
        sync_tables(args.tables)

    if args.schedule:
        # Start a scheduler
        sched = BlockingScheduler()
        sched.add_job(lambda: sync_tables(args.tables), 'cron', day_of_week='sun', hour=3)
        sched.start()
    else:
        sync_tables(args.tables)
