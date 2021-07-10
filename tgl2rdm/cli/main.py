import logging
from logging import config as logging_configurator, INFO
from datetime import datetime, timedelta
from pathlib import Path

import petl
import typer
from toml import loads

from .utils import get_default_config, get_proj_attr, setup_config, setup_http, get_default_logger_config
from .. import extract, transform, utils, load
from .config import config_app
from .tgl import tgl

app = typer.Typer()
app.add_typer(config_app, name='config')
app.add_typer(tgl, name='toggl')
log = logging.getLogger(__name__)


@app.callback()
def main(
        ctx: typer.Context,
        config_path: Path = typer.Option(
            get_default_config,
            resolve_path=True,
        ),
        logger_config: Path = typer.Option(
            get_default_logger_config,
            resolve_path=True,
        ),
):
    ctx.meta['config_path'] = config_path

    if logger_config.exists():
        if logger_config.suffix == '.toml':
            conf = loads(logger_config.read_text())
            logging_configurator.dictConfig(conf)
        elif logger_config.suffix == '.ini':
            logging_configurator.fileConfig(str(logger_config))
    else:
        logging.basicConfig(level=INFO)
        log.info('Using default logger config')


@app.command(help='Synchronize issues from toggl to readmine from --since to --until dates including')
def sync(ctx: typer.Context,
         project: str = typer.Argument(..., help='The name for the project, specified in config file'),
         since: datetime = typer.Option(..., formats=['%Y-%m-%d']),
         until: datetime = typer.Option(..., formats=['%Y-%m-%d']),
         dry: bool = typer.Option(False, help='Use log entries instead of uploading them to redmine'),
         drain: bool = typer.Option(False, help='Use drain issues for entries without specified dest')):
    config = setup_config(ctx, ctx.meta['config_path'])
    setup_http(ctx)

    ctx.meta['rdm_user'] = extract.get_redmine_user(config["redmine"]["url"])

    time_entries = get_toggl_enteries(config, project, since, until)

    issues = get_redmine_issues(config, project, since)

    issue_ids = petl.columns(issues)['id']
    entries_to_load, unset_entries = petl.biselect(time_entries, lambda row: row['issue_id'] in issue_ids)

    if drain and petl.nrows(unset_entries):
        log.info('Using drain')

        drained, unset_entries = drained_entries(ctx, issues, unset_entries, project)

        log.info(f'Drained {petl.nrows(drained)} issues')

        entries_to_load = petl.cat(entries_to_load, drained)

    if petl.nrows(unset_entries):
        log.warning(f'There\'re {petl.nrows(unset_entries)} unset entries')

    if get_proj_attr(config, project, 'group_entries'):
        log.info('Using group by day and description')

        entries_to_load = transform.group_entries_by_day(entries_to_load)

    load.to_redmine_time(
        config["redmine"]["url"],
        entries_to_load,
        activity_id=get_proj_attr(config, project, 'rdm_activity_id'),
        user_id=ctx.meta['rdm_user'].get('id'),
        dry=dry
    )


def drained_entries(ctx: typer.Context, issues, entries, project):
    config = ctx.meta['config']
    empty_entries, unset_entries = petl.biselect(entries, lambda row: row['issue_id'] is None)

    drain_issues = list(
        petl.dicts(
            transform.select_drain_issues(
                issues,
                assignee_id=ctx.meta['rdm_user']['id'],
                drain_cf_id=get_proj_attr(config, project, 'rdm_drain_cf_id')
            )
        )
    )

    if not len(drain_issues):
        log.error('No drain issues found')
        return petl.head(unset_entries, 0), entries

    if len(drain_issues) > 1:
        log.warning(f'Found {len(drain_issues)} drain issues. Will use only first one')

    drain_issue = drain_issues[0]
    drained = petl.addfield(petl.cutout(empty_entries, 'issue_id'), 'issue_id', drain_issue['id'])
    return drained, unset_entries


def get_redmine_issues(config, project, since):
    args = utils.make_sprint_issues_query(project=get_proj_attr(config, project, 'rdm_project_id'),
                                          current_date=since.date(),
                                          sprint_live=timedelta(days=get_proj_attr(config, project, 'sprint_days')))
    issues = extract.from_redmine_issues('https://rm.onlystudio.org/', **args)
    named_object_columns = [
        # 'project', 'tracker', 'status', 'priority', 'author',
        'assigned_to',
        # 'fixed_version'
    ]
    issues = transform.extract_named_objects_to_columns(issues, named_object_columns)
    return issues


def get_toggl_enteries(config, project, since, until):
    if project not in config['project']:
        log.error('No such project in config')
        raise typer.Exit(code=1)
    else:
        project_cfg = config['project'][project]
    time_entries = extract.from_toggl_timeenteries(workspace=config['toggl']['workspace_id'],
                                                   projects=project_cfg['tgl_project_id'],
                                                   since=since.date(),
                                                   until=until.date())
    nrows = petl.nrows(time_entries)
    if nrows == 0:
        log.info('No entries found')
        raise typer.Exit()
    time_entries = transform.parse_datetime(time_entries, ['start', 'end', 'updated'])
    time_entries = transform.parse_duration(time_entries)
    time_entries = transform.add_issue_id_from_description(time_entries)
    return time_entries
