import glob
import os
import re
import sys
from collections import defaultdict
from github import Github
import pygit2

if os.getenv('GIT_TOKEN') is None and len(sys.argv) != 2:
    print('You must specify GIT_TOKEN through argument or environment variable GIT_TOKEN')
    sys.exit(-1)
gh = Github(os.getenv('GIT_TOKEN', sys.argv[2]))
gh_repo = gh.get_repo("InstituteforDiseaseModeling/idmtools")
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
repo = pygit2.Repository(BASE_DIR)
DOCS_DIR = os.path.join(BASE_DIR, 'docs')

regex = re.compile('^refs/tags')
tags = list(sorted(list(filter(lambda r: regex.match(r), repo.listall_references()))))
tags.append('HEAD')
tags.reverse()
next_release = None
exclude_messages = ['Merge branch', 'Merge pull request', 'Merge remote-tracking branch', 'Bump version']
release_expr = re.compile('.*?([0-9.]+).*?')

release_notes = defaultdict(lambda: defaultdict(list))
for index, tag in enumerate(tags):
    ref = repo.lookup_reference(tag)
    next_release = repo.lookup_reference(tags[index + 1]) if index != len(tags) - 1 else 'Beginning'
    walker = repo.walk(ref.target if ref.name != 'HEAD' else repo.head.target,
                       pygit2.GIT_SORT_TOPOLOGICAL | pygit2.GIT_SORT_TIME)
    rm = release_expr.match(tag)
    release_name = rm.group(1) if rm else 'Development'
    if not isinstance(next_release, str):
        walker.hide(next_release.target)
    for commit in walker:
        if next_release and (not isinstance(next_release, str) and commit.oid == next_release.target):
            break
        if not any([x in commit.message for x in exclude_messages]):
            release_notes[release_name][commit.message.strip()].append(commit)

release_notes_final = defaultdict(lambda: defaultdict(list))
regex_fix = re.compile(r'.*?#([0-9]+).*?')
issues_to_references = dict()
issue_types = dict()
for release, contents in release_notes.items():
    if not os.path.exists(os.path.join(DOCS_DIR, f'changelog_{release}.rst')):
        for message, commits in contents.items():
            m = regex_fix.match(message)
            if m:
                issues_to_references[int(m.group(1))] = None

# fetch issue details
for issue in issues_to_references.keys():
    issue_data = gh_repo.get_issue(issue)
    labels = [label.name for label in issue_data.labels]
    issues_to_references[issue] = issue_data
    if 'bug' in labels:
        issue_types[issue] = 'Bugs'
    elif 'Feature Request' in labels:
        issue_types[issue] = 'Feature Request'
    elif 'User Experience' in labels:
        issue_types[issue] = 'User Experience'
    elif 'Documentation' in labels:
        issue_types[issue] = 'Documentation'
    elif any([x in labels for x in ['Platform support', 'COMPS', 'Local Platform', 'SLURM']]):
        issue_types[issue] = 'Platforms'
    elif any([x in labels for x in ['Core', 'CLI', 'Analyzers', 'Workflows']]):
        issue_types[issue] = 'Core'

print(issues_to_references)
for release, contents in release_notes.items():
    release_file = os.path.join(DOCS_DIR, f'changelog_{release}.rst')
    if not os.path.exists(release_file):
        for message, commits in contents.items():
            m = regex_fix.match(message)
            authors = [c.author.name for c in commits]
            if m:
                cmsg = f'[#{int(m.group(1)):04d}]' \
                       f'(https://github.com/InstituteforDiseaseModeling/idmtools/issues/{int(m.group(1))})' \
                       f' - {issues_to_references[int(m.group(1))].title} by {",".join(authors)}'
                if int(m.group(1)) in issue_types:
                    release_notes_final[release][issue_types[int(m.group(1))]].append(cmsg)
                else:
                    release_notes_final[release]['Additional Changes'].append(cmsg)

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
    release_file = os.path.join(DOCS_DIR, f'changelog_{release}.rst')
    if not os.path.exists(release_file):
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

cl_name = os.path.join(DOCS_DIR, 'changelog.rst')
with open(cl_name, 'w') as out:
    out.write("=========\n")
    out.write("Changelog\n")
    out.write("=========\n")
    files = sorted(list(glob.glob(os.path.join(DOCS_DIR, 'changelog_*.rst'))))
    for file in files:
        rf = release_expr.match(file)
        fn = rf.group(1)[0:-1]
        out.write(f'* :doc:`changelog_{fn}`\n')
