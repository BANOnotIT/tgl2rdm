from schema import Schema, Or, Optional

config_simple_schema = Schema({
    'redmine': {
        'token': str,
        'url': str,
    },
    'toggl': {
        'token': str,
        'workspace_id': int,
    },
    Optional('default_attrs'): {
        Optional('sprint_days'): int,
        Optional('rdm_activity_id'): int,
        Optional('rdm_drain_cf_id'): int,
    },
    'project': {
        str: {
            'rdm_project_id': Or(str, int),
            'tgl_project_id': int,
            Optional('sprint_days'): int,
            Optional('rdm_activity_id'): int,
            Optional('rdm_drain_cf_id'): int,
        }
    }
})


def validate_config(config: str):
    validated = config_simple_schema.validate(config)
    # todo: add access checks
    # todo: add project validations check
    return True
