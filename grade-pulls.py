from github import Github
import pandas as pd
import os


githubapi = Github(os.environ['GITHUBAPI_TOKEN'])


def changes(reponame):
    org = 'assignments-for-discussion'
    repo = githubapi.get_organization(org).get_repo(reponame)
    pullrequest = repo.get_pull(1)
    files = pullrequest.get_files()
    diffs = ''
    for f in files:
        diffs += f'{f.patch}\n'
    return diffs


def add_changes():
    results = pd.read_csv('results.csv')
    success = results[results[' Status'] == ' success']
    for index, row in success.iterrows():
        reponame = row[' Repo url'].split('/')[-1]
        print(reponame)
        success.loc[index, 'Changes'] = changes(reponame)
    print(success.head())
    success.to_excel('changes.xlsx')
    print('wrote changes')


def separate_addition_deletion(patch_text):
    segregated_diffs = {'additions': '', 'deletions': ''}
    def segregate(patch_line):
        if patch_line[0] == '+':
            segregated_diffs['additions'] += f'{patch_line[1:]}\n'
        elif patch_line[0] == '-':
            segregated_diffs['deletions'] += f'{patch_line[1:]}\n'
    try:
        patch_as_lines = patch_text.split('\n')
        for line in patch_as_lines:
            if len(line) > 0: segregate(line)
    except:
        segregated_diffs['additions'] = 'not extracted'
        segregated_diffs['deletions'] = 'not extracted'
        print('--not extracted--')
    return segregated_diffs


def segregate_changes():
    changes = pd.read_excel('changes.xlsx')
    for index, row in changes.iterrows():
        segregated = separate_addition_deletion(row['Changes'])
        changes.loc[index, 'Additions'] = segregated['additions']
        changes.loc[index, 'Deletions'] = segregated['deletions']
    changes.to_excel('segregated.xlsx')


def text_for_dup_check():
    additions_digest = ''
    segregated = pd.read_excel('segregated.xlsx')
    for index, row in segregated.iterrows():
        additions_digest += f"\n---\n{row['GitHub username']}\n\n'"
        additions_digest += f"{row['Additions']}\n"
    with open('fordups.txt', 'w') as f:
        f.write(additions_digest)


# add_changes()
segregate_changes()
text_for_dup_check()
