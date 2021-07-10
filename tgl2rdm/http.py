import urllib.request as urlreq
from logging import getLogger

logging = getLogger(__name__)

__all__ = (
    'password_mgr', 'setup_toggl_auth', 'setup_redmine_auth', 'install', 'USER_AGENT', 'BASE_TOGGL_URL'
)

USER_AGENT = 'tgl2rdm <bano.notit@gmail.com>'
BASE_TOGGL_URL = 'https://api.track.toggl.com'

password_mgr = urlreq.HTTPPasswordMgrWithPriorAuth()


def setup_toggl_auth(user: str, passwd: str):
    logging.debug('Toggl api authorisation set up')
    password_mgr.add_password(None, BASE_TOGGL_URL, user, passwd)
    # without this thing there will be 403 status code from Toggl
    password_mgr.update_authenticated(BASE_TOGGL_URL, True)


def setup_redmine_auth(endpoint: str, user: str, passwd: str):
    logging.debug(f'Redmine api authorisation set up for {endpoint}')
    password_mgr.add_password(None, endpoint, user, passwd)
    password_mgr.update_authenticated(endpoint, True)


def install():
    logging.debug('HTTP authorization manager setup')
    auth_handler = urlreq.HTTPBasicAuthHandler(password_mgr)
    opener = urlreq.build_opener(auth_handler)
    urlreq.install_opener(opener)
