import re
from datetime import timedelta
from typing import Tuple

import pandas as pd
import petl as etl
from dateutil.parser import parse as parsedatetime


def rename_description_to_comments(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy(True)
    df = df.rename(columns={'description': 'comments'})
    return df


def get_issue_id_from_comments(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['issue_id'] = df['comments'].str.extract(r'#(?P<issue>\d+)').astype('object')
    return df


def parse_datetime(inp, date_fields: Tuple[str]):
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
