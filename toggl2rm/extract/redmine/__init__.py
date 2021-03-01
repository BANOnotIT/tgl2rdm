from typing import Union, List, Optional
import requests
import requests.utils
import urllib.parse
import pandas as pd
from io import StringIO
from datetime import date


def extract_issues(base_url: str, project: Optional[int] = None, fixed_version_id: Optional[int] = None,
                   assigned_to: Optional[Union[str, int]] = None):
    params = {
        'project_id': project,
        'fixed_version_id': fixed_version_id,
        'assigned_to_id': assigned_to,
    }

    resp = requests.get(urllib.parse.urljoin(base_url, '/issues.json'), params=params)

    df = pd.DataFrame(pd.json_normalize(resp.json(), 'issues'))

    date_cols = [
        'due_date',
        'start_date',
        'created_on',
        'updated_on',
        'closed_on',
    ]
    df[date_cols] = df[date_cols].apply(pd.to_datetime)

    return df
