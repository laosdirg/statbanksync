"""Handle statbank urls
"""

from . import config

from urllib.parse import quote
from collections import namedtuple
from operator import itemgetter

Param = namedtuple('Param', 'key value')


class URL:
    def __init__(self, *segments, **params):
        self.segments = segments
        self.params = params

    def __str__(self):
        rest = ''
        if self.segments:
            segments = [s for s in self.prep(self.segments) if s]
            rest += '/' + '/'.join(segments)

        if self.params:
            # sort and unzip parameter dictionary
            keys, values = zip(*sorted(self.params.items(), key=itemgetter(0)))

            # prep and re-zip
            pairs = zip([quote(k) for k in keys], self.prep(values))

            strings = ['='.join(v) for v in pairs if v[1]]
            rest += '?' + '&'.join(strings)

        return config.BASE_URL + rest

    @staticmethod
    def prep(values):
        for value in values:
            if value is None or type(value) == str:
                yield value
            else:
                try:
                    yield ','.join([str(v) for v in value])
                except TypeError:
                    yield str(value).lower()
