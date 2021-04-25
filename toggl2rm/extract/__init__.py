import urllib
import urllib.parse
import urllib.request
from datetime import date
from typing import Union, List, Optional
from urllib.error import HTTPError

from petl.io import fromdicts
from json import loads

USER_AGENT = 'toggl exporter <bano.notit@gmail.com>'


def from_toggl_timeenteries(workspace: int, projects: Optional[Union[int, List[int]]] = None,
                            since: Optional[date] = None, until: Optional[date] = None):
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

    params = {k: v for k, v in params.items() if bool(v)}
    print(params)
    params = urllib.parse.urlencode(params)
    try:
        resp = urllib.request.urlopen(f'https://api.track.toggl.com/reports/api/v2/details?{params}')
    except HTTPError as e:
        print(e.fp.read())
        raise e

    json = loads(resp.read())
    return fromdicts(json.get('data'))
