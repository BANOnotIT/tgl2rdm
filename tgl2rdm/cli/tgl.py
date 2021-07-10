import logging

import petl
import typer
from petl import fromdicts

from .utils import setup_http, setup_config
from ..extract import get_toggl_user

tgl = typer.Typer()
logging = logging.getLogger(__name__)


@tgl.callback()
def context(ctx: typer.Context):
    setup_config(ctx, ctx.meta['config_path'])
    setup_http(ctx)


@tgl.command()
def projects(ctx: typer.Context):
    data = fromdicts(get_toggl_user()['projects'])
    data = petl.selecteq(data, 'wid', ctx.meta['config']['toggl']['workspace_id'])
    print(petl.lookall(data))
