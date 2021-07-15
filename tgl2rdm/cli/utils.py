import logging
from pathlib import Path

import typer
from toml import loads

from .. import http

logging = logging.getLogger(__name__)


def get_proj_attr(config, project: str, prop: str):
    if prop in config['project'][project]:
        return config['project'][project][prop]
    elif prop in config.get('default_attrs', {}):
        return config['default_attrs'][prop]
    else:
        raise ValueError(f'No {prop!r} found in {project!r} project or in default_attrs, but it\'s required')


def get_default_config():
    return str(Path(typer.get_app_dir('tgl2rdm')) / 'config.toml')


def get_default_logger_config():
    return str(Path(typer.get_app_dir('tgl2rdm')) / 'logger.toml')


def setup_config(ctx: typer.Context, config_path: Path):
    logging.info(f'Using config from {config_path.absolute()}')
    assert config_path.is_file(), 'asdf'
    config = loads(config_path.read_text())
    ctx.meta['config'] = config

    return config


def setup_http(ctx: typer.Context):
    config = ctx.meta['config']

    http.setup_toggl_auth(config["toggl"]["token"], 'api_token')
    http.setup_redmine_auth(config["redmine"]["url"], config["redmine"]["token"], 'api_token')
    http.install()


class TapAsserter:
    counter = 0
    all_valid = True

    def check(self, cond: bool, text: str):
        self.counter += 1

        self.all_valid &= cond

        if cond:
            print(f'ok {self.counter} - {text}')
        else:
            print(f'not ok {self.counter} - {text}')

    def reset(self):
        self.counter = 0

    def stat(self):
        print(f'1..{self.counter}')
