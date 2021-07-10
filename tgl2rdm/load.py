from datetime import timedelta
from logging import getLogger
from urllib.error import HTTPError
from urllib.request import Request
from urllib.parse import urljoin
from urllib.request import urlopen
from json import dumps

logging = getLogger(__name__)


def to_redmine_time(base_url: str, data, activity_id, user_id, dry=False):
    it = iter(data)
    head = next(it)

    dur = head.index('dur')
    spent = head.index('start')
    issue = head.index('issue_id')
    desc = head.index('description')

    url = urljoin(base_url, '/time_entries.json')

    stats = {
        'loaded': 0,
        'errored': 0
    }

    if dry: logging.info('Using dry run')

    for row in it:
        entry = {
            'user_id': user_id,
            'issue_id': row[issue],
            'spent_on': row[spent].date().isoformat(),
            'hours': row[dur] / timedelta(hours=1),
            'activity_id': activity_id,
            'comments': row[desc]
        }
        logging.info(
            'Entry: [usr:{user_id} issue:{issue_id} spent_on:{spent_on} activity:{activity_id}]'
            ' {hours}h: {comments}'.format(**entry)
        )

        try:
            jsondata = dumps({'time_entry': entry})
            jsondataasbytes = jsondata.encode('utf-8')  # needs to be bytes

            req = Request(url, method='POST')
            req.add_header('Content-Type', 'application/json; charset=utf-8')
            req.add_header('Content-Length', str(len(jsondataasbytes)))

            if not dry:
                logging.debug('Opening connection...')
                urlopen(req, jsondataasbytes)
            else:
                logging.debug('Simulating connection...')

            logging.debug('Entry created!')
            stats['loaded'] += 1
        except HTTPError as e:
            logging.error(
                'Error loading '
                'Entry: [usr:{user_id} issue:{issue_id} spent_on:{spent_on} activity:{activity_id}]'
                ' {hours}h: {comments}'.format(**entry)
            )

            logging.exception(e)
            logging.error(e.fp.read().decode('utf8'))
            stats['errored'] += 1

    return stats
