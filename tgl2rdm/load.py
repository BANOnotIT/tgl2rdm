from datetime import timedelta
from urllib.error import HTTPError
from urllib.request import Request
from urllib.parse import urljoin
from urllib.request import urlopen
from json import dumps


def to_redmine_time(base_url: str, data, activity_id=8, dry=False):
    it = iter(data)
    head = next(it)

    dur = head.index('dur')
    spent = head.index('start')
    issue = head.index('issue_id')
    desc = head.index('description')

    url = urljoin(base_url, '/time_entries.json')
    for row in it:
        try:
            req = Request(url, method='POST')
            req.add_header('Content-Type', 'application/json; charset=utf-8')
            jsondata = dumps({'time_entry': {
                'user_id': 43,
                'issue_id': row[issue],
                'spent_on': row[spent].date().isoformat(),
                'hours': row[dur] / timedelta(hours=1),
                'activity_id': activity_id,
                'comments': row[desc]
            }})
            # todo use logging
            print(jsondata)
            jsondataasbytes = jsondata.encode('utf-8')  # needs to be bytes
            req.add_header('Content-Length', str(len(jsondataasbytes)))
            print(req.__repr__())
            if not dry:
                resp = urlopen(req, jsondataasbytes)
                print(resp.getcode())
                print(resp.read())
        except HTTPError as e:
            print(e)
            # todo make error handling
            print(e.fp.read())
            raise e
