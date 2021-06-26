from pathlib import Path

import typer


def get_proj_attr(config, project: str, prop: str):
    if prop in config['project'][project]:
        return config['project'][project][prop]
    elif prop in config.get('default_attrs', {}):
        return config['default_attrs'][prop]
    else:
        raise ValueError(f'No "{prop}" found in "{project}" project or in default_attrs, but it\'s required')


def get_default_config():
    return str(Path(typer.get_app_dir('tgl2rdm')) / 'config.toml')
