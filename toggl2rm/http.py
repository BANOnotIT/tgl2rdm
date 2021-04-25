import urllib.request as urlreq

__all__ = (
    'password_mgr', 'setup_toggl_auth', 'setup_redmine_auth', 'install'
)

password_mgr = urlreq.HTTPPasswordMgrWithPriorAuth()


def setup_toggl_auth(auth: str):
    user, passwd = auth.split(':', maxsplit=1)
    print(user, passwd)
    password_mgr.add_password(None, 'https://api.track.toggl.com/', user, passwd)
    # without this thing there will be 403 status code from Toggl
    password_mgr.update_authenticated('https://api.track.toggl.com/', True)


def setup_redmine_auth(endpoint: str, auth: str):
    user, passwd = auth.split(':', maxsplit=1)
    password_mgr.add_password(None, endpoint, user, passwd)


def install():
    auth_handler = urlreq.HTTPBasicAuthHandler(password_mgr)
    opener = urlreq.build_opener(auth_handler)
    urlreq.install_opener(opener)
