import logging
from datetime import datetime, timedelta
from pathlib import Path

import petl
import typer
from toml import loads

from .config_parser import validate_config as validate
from .utils import get_default_config, get_proj_attr
from .. import http, extract, transform, utils, load
from ..transform import select_drain_issues

app = typer.Typer()
logging.basicConfig(level=logging.DEBUG)
logging = logging.getLogger(__name__)


@app.callback()
def main(ctx: typer.Context, config: Path = typer.Option(
    get_default_config,
    resolve_path=True,
    exists=True,
    file_okay=True,
    dir_okay=False,
    readable=True
)):
    config = loads(config.read_text())
    ctx.meta['config'] = config
    http.setup_toggl_auth(config["toggl"]["token"], 'api_token')
    http.setup_redmine_auth(config["redmine"]["url"], config["redmine"]["token"], 'api_token')
    http.install()

    ctx.meta['rdm_user'] = extract.get_redmine_user(config["redmine"]["url"])


@app.command(name='validate-config')
def validate_config(ctx: typer.Context):
    validate(ctx.meta['config'])
    typer.echo('Config is Good!')


@app.command()
def sync(ctx: typer.Context,
         project: str,
         since: datetime = typer.Option(..., formats=['%Y-%m-%d']),
         until: datetime = typer.Option(..., formats=['%Y-%m-%d']),
         dry: bool = True,
         drain: bool = False):
    config = ctx.meta['config']
    if project not in config['project']:
        logging.error('No such project in config')
        raise typer.Exit(code=1)
    else:
        project_cfg = config['project'][project]

    time_entries = extract.from_toggl_timeenteries(workspace=config['toggl']['workspace_id'],
                                                   projects=project_cfg['tgl_project_id'],
                                                   since=since.date(),
                                                   until=until.date())
    nrows = petl.nrows(time_entries)
    if nrows == 0:
        raise typer.Exit()

    time_entries = transform.parse_datetime(time_entries, ['start', 'end', 'updated'])
    time_entries = transform.parse_duration(time_entries)
    time_entries = transform.add_issue_id_from_description(time_entries)

    # test

    args = utils.make_sprint_issues_query(project=11, current_date=since.date(), sprint_live=timedelta(weeks=1))

    issues = extract.from_redmine_issues('https://rm.onlystudio.org/', **args)
    named_object_columns = [
        # 'project', 'tracker', 'status', 'priority', 'author',
        'assigned_to',
        # 'fixed_version'
    ]
    issues = transform.extract_named_objects_to_columns(issues, named_object_columns)

    issue_ids = petl.columns(issues)['id']
    entries_to_load, unset_entries = petl.biselect(time_entries, lambda row: row['issue_id'] in issue_ids)

    if petl.nrows(unset_entries) and drain:
        logging.info('Using drain')
        empty_entries, unset_entries = petl.biselect(unset_entries, lambda row: row['issue_id'] is None)

        drain_issues = list(
            petl.dicts(
                select_drain_issues(issues,
                                    assignee_id=ctx.meta['rdm_user']['id'],
                                    drain_cf_id=get_proj_attr(config, project, 'rdm_drain_cf_id'))
            )
        )
        if len(drain_issues) > 1:
            logging.warning(f'Found {len(drain_issues)} drain issues. Will use only first one')
        if len(drain_issues):
            drain_issue = drain_issues[0]
            drained = petl.addfield(petl.cutout(empty_entries, 'issue_id'), 'issue_id', drain_issue['id'])
            entries_to_load = petl.cat(entries_to_load, drained)
        else:
            logging.error('No drain issues found')

    if petl.nrows(unset_entries):
        logging.warning(f'There\'re {petl.nrows(unset_entries)} unset entries')

    load.to_redmine_time(
        config["redmine"]["url"],
        entries_to_load,
        activity_id=get_proj_attr(config, project, 'rdm_activity_id'),
        dry=dry
    )
