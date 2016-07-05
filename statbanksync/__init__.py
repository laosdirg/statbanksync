"""
Download data from DSTs statbank and keep it up to date in a local database

used by CLI tool, but can be used directly in other projects
"""
from statbanksync.signals import progress, subprogress
from statbanksync.services import mirrors

import statbank

import logging

import datetime
import time


def sync_table(statbank_table_id):
    """Synchronize a single table (both data and meta tables).

    When syncing multiple tables consider doing it in multiple threads
    """
    logging.info("Syncing {} table".format(statbank_table_id))
    # fetch latest metadata for remote table
    statbank_table = statbank.tableinfo(statbank_table_id)

    # make sure tables exists, create if not
    mirrors.ensure_exists(statbank_table)
    conv = mirrors.update_mapping_tables(statbank_table)

    # figure out what times we need to fetch data for
    latest_time = mirrors.get_latest_time(statbank_table)
    times_needed = [value.id for value
                    in statbank_table.variables['tid'].values.values()
                    if value.id > latest_time]

    # skip update if we are already at latest version
    if len(times_needed) == 0:
        logging.info("Nothing to sync for table {}".format(statbank_table_id))
        return

    # bulk insert data per time (to allow resuming after each time bulk)
    params = {variable: '*' for variable in statbank_table.variables if variable != 'tid'}
    logging.info("Inserting data into {} table".format(statbank_table_id))
    for time in times_needed:
        params['tid'] = statbank_table.variables['tid'].values[time].text
        rows = statbank.data(statbank_table_id,
                             stream=True,
                             variables=params)

        mirrors.insert_data(statbank_table, rows, conv)

        # signal progress event
        progress.send(dict(
            max=len(times_needed),
            value=times_needed.index(time),
        ))


def get_data(statbank_table_id, **params):
    """Fetches values at all timestamps for given params.

    Args:
        statbank_table_id (int): Table identifier

    Yeilds:
        dict: Next row in result
    """
    # why is this not used?
    pass


def reset():
    # reset meta and data tables if requested
    logging.info('Resetting database')
    try:
        mirrors.reset()
    except Exception as e:
        logging.warn('Could not reset db, is it fresh? %s' % e)
        raise e
