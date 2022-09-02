from github import Github
from sys import argv
import argparse
import os

interest = 'battery-inventory'

def collect_repos(githubapi, orgname):
  repos = []
  for repo in githubapi.get_organization(orgname).get_repos():
    print(repo.name)
    repos.append(repo)
  print(f'\n# Collected a total of {len(repos)} repositories')
  return repos


def reponame2user(repo_name):
  lang_prefixes = ['in-c-', 'in-cpp-', 'in-cs-', 'in-java-', 'in-py-']
  repo_name = repo_name.replace(f'{interest}-', '')
  for prefix in lang_prefixes:
      repo_name = repo_name.replace(prefix, '')
  return repo_name


def fill_status_in_sheet(repos, date):
  interesting_repos = [repo for repo in repos\
    if interest in repo.name and str(repo.pushed_at).startswith(date)]
  print(f'## Reporting on {len(interesting_repos)} repos\n')
  csv_out = 'GitHub username, Repo url, Pushed at, Status\n'
  for r in interesting_repos:
    csv_out += f'{reponame2user(r.name)}, {r.html_url}, {str(r.pushed_at)}, {last_status(r)}\n'
    print(f'{r.name} added in sheet')
  with open('results.csv', 'w') as f:
    f.write(csv_out)


def last_status(repo):
  # as per https://pygithub.readthedocs.io/en/stable/github_objects/Repository.html#github.Repository.Repository.get_workflow_runs
  try:
    runs = repo.get_workflow_runs()
  except:
    return 'error'
  if runs.totalCount > 0:
    run_number = runs[0].run_number
    conclusion = runs[0].conclusion
    if conclusion == 'success':
      i = 1
      while i < runs.totalCount and runs[i].run_number == run_number:
        print(f'checking more runs of #{run_number}')
        if runs[i].conclusion != 'success':
          conclusion = runs[i].conclusion
          break
        i += 1
    return conclusion
  else:
    print(f'{repo} has no workflow runs')
    return ''


def github_to_sheet(date):
  githubapi = Github(os.environ['GITHUBAPI_TOKEN'])
  org = 'assignments-for-discussion'
  repos = collect_repos(githubapi, org)
  fill_status_in_sheet(repos, date) # filter_test(repos, start, end))


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Explore assignment submissions')
  parser.add_argument('--date', required=True, help='test date (yyyy-mm-dd)')

  args = parser.parse_args()
  github_to_sheet(args.date)


# To get logs of a run:
# https://api.github.com/repos/clean-code-craft-tcq-1/typewise-alert-c/actions/runs
# look for the run with "name": "Build and Run"
# https://api.github.com/repos/clean-code-craft-tcq-1/typewise-alert-c/actions/runs/1859022428
# https://api.github.com/repos/clean-code-craft-tcq-1/typewise-alert-c/actions/runs/1859022428/logs
# See https://docs.github.com/en/rest/reference/actions#download-workflow-run-logs
