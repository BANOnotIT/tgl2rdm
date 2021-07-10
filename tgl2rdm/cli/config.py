import logging as logging
from pathlib import Path

import typer
from schema import SchemaError
from toml import loads, TomlDecodeError

from ..config import config_schema
from .utils import TapAsserter, setup_http
from ..extract import get_toggl_user, get_redmine_user, get_redmine_project

config_app = typer.Typer()
logging = logging.getLogger(__name__)


@config_app.command()
def validate(ctx: typer.Context):
    tap = TapAsserter()

    path: Path = ctx.meta['config_path']
    tap.check(path.is_file(), f'Using config from {path}')

    config = path.read_text()
    tap.check(len(config) > 0, f'Config is not empty')

    valid = True
    try:
        config = loads(config)
    except TomlDecodeError as e:
        valid = False
        logging.exception(str(e))

    tap.check(valid, f'Config is valid toml')

    valid = True
    try:
        config_schema.validate(config)
    except SchemaError as e:
        valid = False
        logging.exception(str(e))
    tap.check(valid, 'Config is valid against Schema')

    # checking access
    ctx.meta['config'] = config
    setup_http(ctx)

    tgl_user = None

    valid = True
    try:
        tgl_user = get_toggl_user()
    except Exception as e:
        valid = False
        logging.exception(str(e))
    tap.check(valid, 'Has access to toggl user')

    tgl_projects = list(map(lambda proj: proj.get('id'), tgl_user.get('projects', [])))

    valid = True
    try:
        get_redmine_user(config["redmine"]["url"])
    except Exception as e:
        valid = False
        logging.exception(str(e))
    tap.check(valid, 'Has access to redmine user')

    # checking projects
    for project_alias, project in config['project'].items():
        valid = True
        rdm_id = project.get('rdm_project_id')
        try:
            get_redmine_project(config['redmine']['url'], rdm_id)
        except Exception:
            valid = False
        tap.check(valid, f'Redmine project {rdm_id!r} accessable within alias {project_alias!r}')

        tgl_id = project.get("tgl_project_id")
        tap.check(tgl_id in tgl_projects, f'Toggl project {tgl_id} accessable within alias {project_alias!r}')

        # todo check custom redmine fields validness

    tap.stat()

    if not tap.all_valid:
        exit(1)
