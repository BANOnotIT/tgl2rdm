from datetime import date, timedelta


def make_sprint_issues_query(project: int, current_date: date, sprint_live: timedelta) -> dict:
    return {
        'project_id': project,
        'start_date': f'><{(current_date - sprint_live).isoformat()}|{current_date.isoformat()}',
        'limit': 1_000_000,
        'status_id': 'open'
    }
