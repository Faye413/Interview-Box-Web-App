
""" This module contains various utilities common to the API. """

import datetime
import flask
from itertools import groupby
from operator import itemgetter

def escape_html(func):
    """ Used as a decorator to escape the function's return value, preventing XSS and injection attacks. """
    def inner(arg):
        response = func(arg)
        return flask.Markup.escape(response)
    return inner

def get_ranges(data):
    """
    Converts a an array of integers into consecutive ranges described by tuples.
    e.g. get_ranges([1,2,3,4,6]) will return [(1,4), 6]
    """
    ranges = []
    for key, group in groupby(enumerate(data), lambda (index, item): index - item):
        group = map(itemgetter(1), group)
        if len(group) > 1:
            ranges.append((group[0], group[-1]))
        else:
            ranges.append(group[0])
    return ranges

def unget_ranges(data):
    """
    Inverts get_ranges.
    e.g. unget_ranges([(1,4), 6]) will return [1,2,3,4,6]
    """
    values = []
    for i in data:
        if type(i) == int:
            values.append(i)
        else:
            values.extend(range(i[0],i[1] + 1))
    return values

