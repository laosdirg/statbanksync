"""
This service provides mirrors of the statbank tables
"""

from statbanksync.database import create_session
from statbanksync.models.mirror import Mirror, make_table, make_mapping_tables
from statbanksync.signals import subprogress

from datetime import datetime
import logging

from sqlalchemy.sql.expression import select
from sqlalchemy.exc import SQLAlchemyError

def create_mirror(statbank_table):
    Mirror.__table__.create(checkfirst=True)
    with create_session() as session:
        mirror = Mirror(statbank_table_id=statbank_table.id,
                        unit=statbank_table.unit)

        query = mirror.__table__.select().\
            where(mirror.statbank_table_id == statbank_table.id)
        result = session.execute(query)
        row = result.fetchone()
        if not row:
            session.add(mirror)


def create(statbank_table):
    """Create table to hold statbank table data
    """
    with create_session() as session:
        table = make_table(statbank_table)
        table.create(checkfirst=True)


def create_map(mapping_table):
    """Create table to hold mappings of statbank variables
    """
    mapping_table.create(checkfirst=True)

    return mapping_table


def get_latest_time(statbank_table):
    """Look at table contents and figure out the latest timestamp of any row

    This is used when figuring out which new rows to fetch from statbank API
    """
    table = make_table(statbank_table)
    try:
        with create_session() as session:
            query = select([table.c.time]).\
                order_by(table.c.time.desc()).\
                group_by(table.c.time).limit(1)
            first = session.execute(query).fetchone()
            return first[0]
    except:
            return datetime.min


def update_mapping_tables(statbank_table):
    '''Updates the tables used for mapping statbank variables.
    New mappings are inserted if the statbank maps attribute contains new values.
    '''
    mapping_tables = make_mapping_tables(statbank_table)

    with create_session() as session:
        #conversion dictionary to convert the inserted values according to the mappings
        conv = {}
        for mapping_table in mapping_tables:
            variable_id, _, table_name = mapping_table.name.split('_')
            dst_id_column, key_column = ('dst_id', 'key')
            value_column = mapping_table.c[variable_id].name
            try:
                current_map = {
                    mapping[dst_id_column]: mapping[key_column]
                    for mapping in session.execute(select([mapping_table]))
                }

                conv[variable_id] = current_map
                #insert new mappings if they do not exist already
                variables = statbank_table.variables[variable_id].values.values()
                for variable in variables:
                    if variable.id not in current_map.keys():
                        if variable_id == 'tid':
                            row = {value_column: variable.id, key_column: variable.text}
                        else:
                            row = {dst_id_column: variable.id, value_column: variable.text}
                        if not variable_id == 'tid' and all([variable.id.isdigit() for variable in variables]):
                            row[key_column] = variable.id
                        result = session.execute(mapping_table.insert().values(**row))
                        inserted_key = str(result.inserted_primary_key[0])
                        conv[variable_id][variable.id] = inserted_key
            except SQLAlchemyError as err:
                logging.warn('Encountered a database error when updating the mapping tables')
                raise err
    return conv


def insert_data(statbank_table, rows, conv):
    """Inserts all given rows into mirror data table

    Args:
        rows: An iterator of rows
    """
    insert_errmsg = 'Encountered a database error when inserting row with value: {} at time: {}'
    table = make_table(statbank_table)

    with create_session() as session:
        for i, row in enumerate(rows):
            try:
                for variable_id, value in row.variables.items():
                    row.variables[variable_id] = conv[variable_id][value.id]
                session.execute(table.insert().values(value=row.value, time=row.time, **row.variables))
            except SQLAlchemyError as err:
                logging.exception(inserterr.format(row.value, row.time))
                raise err
                break
            finally:
                subprogress.send(dict(
                    max=100,
                    value=i % 100,
                ))



def ensure_exists(statbank_table):
    """Create both meta table and data table if they do not exist.
    """
    create_mirror(statbank_table)
    for mapping_table in make_mapping_tables(statbank_table):
        create_map(mapping_table)
    create(statbank_table)


def reset():
    """Delete tables.

    Useful if schema has changed
    """
    try:
        with create_session() as session:
            for mirror in session.query(Mirror):
                session.execute('DROP TABLE mirrors_{};'.format(mirror.statbank_table_id))
    except:
        print("Something went wrong when dropping old tables, might no be problematic")
    try:
        Mirror.__table__.drop()
    except:
        print("Could not drop table, hopefully it just didn't exist")
    Mirror.__table__.create()
