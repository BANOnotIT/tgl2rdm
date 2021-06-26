import re
from datetime import timedelta
from typing import Tuple, List

import pandas as pd
import petl as etl
from dateutil.parser import parse as parsedatetime


def parse_datetime(inp, date_fields: List[str]):
    return etl.convert(inp, date_fields, parsedatetime)


def parse_duration(inp):
    return etl.convert(inp, 'dur', lambda v: timedelta(milliseconds=v))


def add_issue_id_from_description(inp):
    def m(row):
        try:
            match = re.search(r'#(\d+)', row['description'])
            return int(match.group(1))
        except AttributeError:
            return None

    return etl.addfield(inp, 'issue_id', m)


def extract_named_objects_to_columns(inp, named_object_columns: List[str]):
    res = inp

    def m(column1: str, prop1: str):
        def mod(row):
            if row.get(column1):
                return row[column1].get(prop1, None)
            return None

        return mod

    for column in named_object_columns:
        for prop in ('id', 'name'):
            res = etl.addfield(res, f'{column}_{prop}', m(column, prop))

    return res


def select_drain_issues(inp, assignee_id: int, drain_cf_id: int):
    print(assignee_id, drain_cf_id)
    def is_drain(fields: list) -> bool:
        return any(map(lambda field: field['id'] == drain_cf_id and field['value'] == '1', fields))

    # custom fields have more selectivity
    inp = etl.select(inp, 'custom_fields', is_drain)
    return etl.selecteq(inp, 'assigned_to_id', assignee_id)
