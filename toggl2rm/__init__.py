import pandas as pd
from extract.toggl import extract_time
from extract.redmine import extract_issues
from transform import rename_description_to_comments, get_issue_id_from_comments

df = rename_description_to_comments(extract_time(workspace=4_513_131, projects=166_567_787))
df = get_issue_id_from_comments(df)
print(pd.isnull(df['issue_id']))
print(df)

df = extract_issues('https://rm.onlystudio.org/', project=11, assigned_to='me')
print(df.dtypes)
print(df)
