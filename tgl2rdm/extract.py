import urllib
import urllib.parse
import urllib.parse
import urllib.request
from datetime import date
from json import loads
from typing import List
from typing import Union, Optional
from urllib.error import HTTPError
from logging import getLogger

from petl.io import fromdicts

from .http import USER_AGENT, BASE_TOGGL_URL

rdm_log = getLogger(f'{__name__}.redmine')
tgl_log = getLogger(f'{__name__}.toggl')


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
    params = urllib.parse.urlencode(params)
    try:
        resp = urllib.request.urlopen(f'{BASE_TOGGL_URL}/reports/api/v2/details?{params}')
    except HTTPError as e:
        tgl_log.exception(e)
        tgl_log.error(e.fp.read())
        raise e

    json = loads(resp.read())
    tgl_log.debug(f"Got {len(json.get('data'))} toggl entries")
    return fromdicts(json.get('data'))


def from_redmine_issues(base_url: str, **kwargs):
    params = {k: v for k, v in kwargs.items() if v is not None}
    params = urllib.parse.urlencode(params)

    try:
        url = urllib.parse.urljoin(base_url, '/issues.json')
        resp = urllib.request.urlopen(f'{url}?{params}')
    except HTTPError as e:
        rdm_log.exception(e)
        rdm_log.error(e.fp.read())
        raise e

    json = loads(resp.read())
    rdm_log.debug(f"Got {len(json.get('issues'))} redmine issues")
    return fromdicts(json.get('issues'))


def get_toggl_user():
    try:
        resp = urllib.request.urlopen(f'{BASE_TOGGL_URL}/api/v8/me?with_related_data=true')
    except HTTPError as e:
        tgl_log.exception(e)
        tgl_log.error(e.fp.read())
        raise e

    json = loads(resp.read())
    tgl_log.debug(f"Got toggl user data")
    return json.get('data')


def get_redmine_user(base_url: str):
    try:
        url = urllib.parse.urljoin(base_url, '/my/account.json')
        resp = urllib.request.urlopen(url)
    except HTTPError as e:
        rdm_log.exception(e)
        rdm_log.error(e.fp.read())
        raise e

    json = loads(resp.read()).get('user')
    rdm_log.debug(f"Got user #{json['id']}: {json['login']!r}")
    return json


def get_redmine_project(base_url: str, pid: Union[int, str]):
    try:
        url = urllib.parse.urljoin(base_url, f'/projects/{str(pid)}.json')
        resp = urllib.request.urlopen(url)
    except HTTPError as e:
        rdm_log.exception(e)
        rdm_log.error(e.fp.read())
        raise e

    json = loads(resp.read())
    rdm_log.debug(f"Got redmine project {json.get('project').get('name')!r}")
    return json.get('project')
