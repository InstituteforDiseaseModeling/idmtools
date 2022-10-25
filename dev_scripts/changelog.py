#!/usr/bin/env python
"""Generates Changelog based on github issue activity.

The process is to fetch the current list of tags and commits.
We then fetch all the issues.
We then iterate over tags to determine their start-date/end-date and filter out certain labels.
We then find issues closed between start and end dates.
We then grab title and issue number from ticket and create our changelog. Tickets are grouped by labels.
"""
import argparse
import glob
import os
import re
from collections import defaultdict
from datetime import timezone
from pathlib import Path

import pygit2  # noqa: I900
from github import Github  # noqa: I900

RELEASE_EXPR = re.compile('.*?([0-9.]+).*?')
EXCLUDE_LABELS = ['Research', 'wontfix', 'Discuss', 'duplicate', 'Exclude from Changelog', 'Epic', 'Release/Packaging', 'Support', 'Transition']
EXCLUDE_MESSAGES = ['Merge branch', 'Merge pull request', 'Merge remote-tracking branch', 'Bump version']


def get_tags_from_repo(repo):
    regex = re.compile('^refs/tags')
    tags = list(sorted(list(filter(lambda r: regex.match(r), repo.listall_references()))))
    tags.append('HEAD')
    tags.reverse()
    return tags


def get_release_ranges_and_messages(repo, tags):
    release_ranges = dict()
    release_notes = defaultdict(lambda: defaultdict(list))
    for index, tag in enumerate(tags):
        ref = repo.lookup_reference(tag)
        next_release = repo.lookup_reference(tags[index + 1]) if index != len(tags) - 1 else 'Beginning'
        walker = repo.walk(ref.target if ref.name != 'HEAD' else repo.head.target,
                           pygit2.GIT_SORT_TOPOLOGICAL | pygit2.GIT_SORT_TIME)
        rm = RELEASE_EXPR.match(tag)
        release_name = rm.group(1) if rm else 'Development'
        if not isinstance(next_release, str):
            walker.hide(next_release.target)
        for commit in walker:
            if release_name not in release_ranges:
                if next_release and not isinstance(next_release, str):
                    nc = repo.walk(next_release.target)
                    nc = next(nc)
                    nc = nc.commit_time
                else:
                    nc = None
                release_ranges[release_name] = (nc, commit.commit_time)
            if next_release and (not isinstance(next_release, str) and commit.oid == next_release.target):
                break
            if not any([x in commit.message for x in EXCLUDE_MESSAGES]):
                release_notes[release_name][commit.message.strip()].append(commit)
    return release_notes, release_ranges


def get_issue_type(issue_types, issue, labels):
    """Returns the issue type based on the labels and assigns that to the issue_types map.

    Args:
        issue: Issue to identify
        labels: Labels to evaluate

    Returns:
        None
    """
    if any([x in labels for x in ['Support']]):
        issue_types[issue] = 'Support'
    elif 'bug' in labels:
        issue_types[issue] = 'Bugs'
    elif 'Feature Request' in labels:
        issue_types[issue] = 'Feature Request'
    elif 'User Experience' in labels:
        issue_types[issue] = 'User Experience'
    elif 'Documentation' in labels:
        issue_types[issue] = 'Documentation'
    elif any([x in labels for x in ['Platform support', 'COMPS', 'Local Platform', 'SLURM']]):
        issue_types[issue] = 'Platforms'
    elif 'Analyzers' in labels:
        issue_types[issue] = 'Analyzers'
    elif 'Configuration' in labels:
        issue_types[issue] = 'Configuration'
    elif 'CLI' in labels:
        issue_types[issue] = 'CLI'
    elif any([x in labels for x in ['Models', 'COVID-19']]):
        issue_types[issue] = 'Models'
    elif any([x in labels for x in ['Core', 'Workflows', 'Architecture']]):
        issue_types[issue] = 'Core'
    elif any([x in labels for x in ['Build/Development Environment', 'Test']]):
        issue_types[issue] = 'Developer/Test'
    elif any([x in labels for x in ['dependencies']]):
        issue_types[issue] = 'Dependencies'


def generate_changelog_index(docs_dir):
    cl_name = docs_dir.joinpath('changelog', 'changelog.rst')
    with open(cl_name, 'w') as out:
        out.write("=========\n")
        out.write("Changelog\n")
        out.write("=========\n")
        out.write("\n.. toctree::\n\n")
        files = sorted(list(glob.glob(str(docs_dir.joinpath('changelog', 'changelog_*.rst')))))
        for file in files:
            rf = RELEASE_EXPR.match(file)
            if rf:
                fn = rf.group(1)[0:-1]
                out.write(f'    changelog_{fn}\n')


def generate_release_note_files(docs_dir, release_notes_final):
    release_templates = '''
    {release_under}
    {release}
    {release_under}
    '''
    section_template = '''

    {section}
    {section_under}
    '''
    final_out = ''
    for release, contents in release_notes_final.items():
        release_file = docs_dir.joinpath('changelog', f'changelog_{release}.rst')
        if not release_file.exists():
            final_out = release_templates.format(**dict(release=release, release_under='=' * len(release)))
            scontents = sorted(contents.keys())
            for section in scontents:
                issues = contents[section]
                unique_issues = sorted(set(issues))
                final_out += section_template.format(**dict(section=section, section_under='-' * len(section)))
                for issue in unique_issues:
                    final_out += f"* {issue}\n"
            with open(release_file, 'w') as out:
                out.write(final_out)


def generate_release_note_messages(docs_dir, issue_types, issues_to_references, regex_fix, release_notes, release_notes_final):
    for release, contents in release_notes.items():
        for message in contents.keys():
            m = regex_fix.match(message)
            if m and int(m.group(1)) in issues_to_references and issues_to_references[int(m.group(1))] is not None:
                cmsg = f'`#{int(m.group(1)):04d} ' \
                       f'<https://github.com/InstituteforDiseaseModeling/idmtools/issues/{int(m.group(1))}>`_' \
                       f' - {issues_to_references[int(m.group(1))].title}'
                if int(m.group(1)) in issue_types:
                    release_notes_final[release][issue_types[int(m.group(1))]].append(cmsg)
                else:
                    release_notes_final[release]['Additional Changes'].append(cmsg)


def main(token):
    gh = Github(token)
    gh_repo = gh.get_repo("InstituteforDiseaseModeling/idmtools")
    base_dir = Path(__file__).parent.parent
    repo = pygit2.Repository(base_dir)
    docs_dir = base_dir.joinpath("docs")
    tags = get_tags_from_repo(repo)
    release_notes, release_ranges = get_release_ranges_and_messages(repo, tags)

    release_notes_final = defaultdict(lambda: defaultdict(list))
    regex_fix = re.compile(r'.*?#([0-9]+).*?')
    issues_to_references = dict()
    issue_types = dict()

    # fetch issue details

    for issue in issues_to_references.keys():
        issue_data = gh_repo.get_issue(issue)
        labels = [label.name for label in issue_data.labels]
        if (issue_data.pull_request is None or issue_data.pull_request.html_url != issue_data.html_url) \
                and not any(x in labels for x in EXCLUDE_LABELS):
            issues_to_references[issue] = issue_data
            get_issue_type(issue_types, issue, labels)
        elif "dependencies" in labels:
            issues_to_references[issue] = issue_data
            get_issue_type(issue_types, issue, labels)

    # fetch rest of issues
    for issue in gh_repo.get_issues(state='closed'):
        if issue.number not in issues_to_references:
            for release, vals in release_ranges.items():
                start, end = vals
                if start is None:
                    start = 0
                labels = [label.name for label in issue.labels]
                if end >= issue.closed_at.replace(tzinfo=timezone.utc).timestamp() >= start \
                        and not any(x in labels for x in EXCLUDE_LABELS):
                    release_file = docs_dir.joinpath(f'changelog_{release}.rst')
                    if issue.pull_request is None or issue.pull_request.html_url != issue.html_url:
                        if not os.path.exists(release_file):
                            issues_to_references[issue.number] = issue
                            release_notes[release][f'#{issue.number} - {issue.title}'] = [issue]
                            get_issue_type(issue_types, issue.number, labels)
                    elif "dependencies" in labels and issue.as_pull_request().merged_at is not None and not release_file.exists():
                        issues_to_references[issue.number] = issue
                        release_notes[release][f'#{issue.number} - {issue.title}'] = [issue]
                        get_issue_type(issue_types, issue.number, labels)
    generate_release_note_messages(docs_dir, issue_types, issues_to_references, regex_fix, release_notes, release_notes_final)
    generate_release_note_files(docs_dir, release_notes_final)
    generate_changelog_index(docs_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", required=True, help="Github Token")

    args = parser.parse_args()
    main(args.token)
