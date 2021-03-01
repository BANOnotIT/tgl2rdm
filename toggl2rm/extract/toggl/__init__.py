from typing import Union, List, Optional
import requests
import requests.utils
import pandas as pd
from io import StringIO
from datetime import date

USER_AGENT = 'toggl exporter <bano.notit@gmail.com>'


def extract_time(workspace: int, projects: Optional[Union[int, List[int]]] = None, since: Optional[date] = None,
                 until: Optional[date] = None):
    if not projects:
        projects = []

    if type(projects) is not list:
        projects = [projects]

    params = {
        'workspace_id': workspace,
        'since': since,
        'until': until,
        'user_agent': USER_AGENT,
        'project_ids': ','.join(map(str, list(projects))),
    }

    resp = requests.get('https://api.track.toggl.com/reports/api/v2/details', params=params)

    df = pd.DataFrame(pd.json_normalize(resp.json(), 'data'))

    df.columns = map(str.lower, df.columns)

    df['dur'] = pd.to_timedelta(df['dur'])

    df[['end', 'start', 'updated']] = df[['end', 'start', 'updated']].apply(pd.to_datetime)
    df = df.set_index('id')

    return df
