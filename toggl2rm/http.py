import urllib.request as urlreq

__all__ = (
    'password_mgr', 'setup_toggl_auth', 'setup_redmine_auth', 'install'
)

password_mgr = urlreq.HTTPPasswordMgrWithPriorAuth()


def setup_toggl_auth(user: str, passwd: str):
    password_mgr.add_password(None, 'https://api.track.toggl.com/', user, passwd)
    # without this thing there will be 403 status code from Toggl
    password_mgr.update_authenticated('https://api.track.toggl.com/', True)


def setup_redmine_auth(endpoint: str, user: str, passwd: str):
    password_mgr.add_password(None, endpoint, user, passwd)
    password_mgr.update_authenticated(endpoint, True)


def install():
    auth_handler = urlreq.HTTPBasicAuthHandler(password_mgr)
    opener = urlreq.build_opener(auth_handler)
    urlreq.install_opener(opener)
