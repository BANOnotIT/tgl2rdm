import pandas as pd


def rename_description_to_comments(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy(True)
    df = df.rename(columns={'description': 'comments'})
    return df


def get_issue_id_from_comments(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['issue_id'] = df['comments'].str.extract(r'#(?P<issue>\d+)').astype('object')
    return df
