from statbanksync.database import Base, engine

import sqlalchemy
from sqlalchemy import Column, Sequence, types


class Mirror(Base):
    """Creates mirror objects that hold information on the last updated row of statbank table
    """
    __tablename__ = 'mirrors'
    statbank_table_id = Column(types.Text(), primary_key=True)
    unit = Column(types.Text())


def make_table(statbank_table):
    """Makes a list of the tableschemas of the inputted statbank table
    """
    metadata = sqlalchemy.MetaData(bind=engine)

    columns = []
    columns.append(sqlalchemy.Column('value', sqlalchemy.Numeric()))
    for variable in statbank_table.variables:
        if variable not in 'tid':
            columns.append(Column(variable,
                                  types.SmallInteger,
                                  primary_key=True))

    columns.append(sqlalchemy.Column('time', types.DateTime(), primary_key=True))

    schema = sqlalchemy.Table('mirrors_{}'.format(statbank_table.id),
                              metadata,
                              *columns)
    return schema


def make_mapping_tables(statbank_table):
    """Makes a mapping schema from a variable name

    Mapping schemas map a text variable column to a unique key id for less memory consumption and speed
    """
    #TODO: consider using sqlalchemys mapping objects for this
    metadata = sqlalchemy.MetaData(bind=engine)
    schema = []
    for variable in statbank_table.variables:
        mapping_columns = [Column('key',
                                  types.SmallInteger,
                                  Sequence('sequence_{}_{}'.format(variable, statbank_table.id)),
                                  primary_key = True),
                          Column('dst_id', types.DateTime() if variable == 'time' else types.Text),
                          Column(variable, types.Text())]
        table_name = '{}_map_{}'.format(variable, statbank_table.id)
        schema.append(sqlalchemy.Table(table_name,
                                      metadata,
                                      *mapping_columns))
    return schema
