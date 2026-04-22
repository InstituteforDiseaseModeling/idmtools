"""
Dev utility script to generate changelog file and changelog for release note based on GitHub project id and release version.

Run script: python project_changelog.py --project_id 83 --version 3.1.0

Note, before run this script, you need to do following steps first:
1) Install GitHub CLI (gh)
2) Authenticate with your GitHub account (gh auth login) which need your token in prompt.
3) Provide script arg1: --project_id 83. (for example: 83 is IDMTools project number for '3.1.0 release')
4) Provide script arg2. --version 3.1.0 (3.1.0 is the current release number for IDMTools)
"""
import argparse
import os
import re
import subprocess
import json
import pandas as pd

EXCLUDE_LABELS = ['Research', 'wontfix', 'Discuss', 'duplicate', 'Exclude from Changelog', 'Epic']

SECTION_ORDER = [
    "Feature Request",
    "Bugs",
    "Platforms",
    "Core",
    "Configuration",
    "CLI",
    "Analyzers",
    "Models",
    "Documentation",
    "Developer/Test",
    "User Experience",
    "Support",
    "Dependencies",
    "Release/Packaging",
    "Other"
]

SECTION_DISPLAY_NAMES = {
    "Feature Request": "Feature Requests",
    "Bugs": "Bug Fixes",
    "Platforms": "Platforms",
    "Core": "Core",
    "Configuration": "Configuration",
    "CLI": "CLI",
    "Analyzers": "Analyzers",
    "Models": "Models",
    "Documentation": "Documentation",
    "Developer/Test": "Developer/Test",
    "User Experience": "User Experience",
    "Support": "Support",
    "Dependencies": "Dependencies",
    "Release/Packaging": "Release/Packaging",
    "Other": "Other"
}


def has_excluded_label(label_list):
    """
    Check if label is excluded from changelog.
    Args:
        label_list (list[dict]): List of label dictionaries, where each has a 'name' key.

    Returns:
        bool: True if any label in the list matches one of EXCLUDE_LABELS, otherwise False.

    """
    if not isinstance(label_list, list):
        return False
    label_names = [lbl.get('name', '').lower() for lbl in label_list if isinstance(lbl, dict)]
    return any(lbl.lower() in label_names for lbl in EXCLUDE_LABELS)


def get_issue_type(labels):
    """
    Returns the issue type based on the labels and assigns that to the issue_types map.

    Args:
        labels: Labels to evaluate

    Returns:
        None
    """
    if any(label['name'] == 'Support' for label in labels):
        return 'Support'
    elif any(label['name'] == 'bug' for label in labels):
        return 'Bugs'
    elif any(label['name'] == 'Feature Request' for label in labels):
        return 'Feature Request'
    elif any(label['name'] == 'User Experience' for label in labels):
        return 'User Experience'
    elif any(label['name'] == 'Documentation' for label in labels):
        return 'Documentation'
    elif any(label['name'] in ['Platform support', 'COMPS Platform', 'SLURM Platform', 'Container Platform', "File Platform"] for label in labels):
        return 'Platforms'
    elif any(label['name'] == 'Analyzers' for label in labels):
        return 'Analyzers'
    elif any(label['name'] == 'Configuration' for label in labels):
        return 'Configuration'
    elif any(label['name'] == 'CLI' for label in labels):
        return 'CLI'
    elif any(label['name'] in ['Models', 'COVID-19'] for label in labels):
        return 'Models'
    elif any(label['name'] in ['Core', 'Workflows', 'Architecture'] for label in labels):
        return 'Core'
    elif any(label['name'] in ['Build/Development Environment', 'Test'] for label in labels):
        return 'Developer/Test'
    elif any(label['name'] == 'Dependencies' for label in labels):
        return 'Dependencies'
    elif any(label['name'] == 'Release/Packaging' for label in labels):
        return 'Release/Packaging'
    else:
        return 'Other'


def fetch_project_items(project_id: str) -> list:
    """Fetch all items from a GitHub org project, handling pagination automatically.

    Args:
        project_id: GitHub project number (e.g. "83")

    Returns:
        list: All item nodes from the project across all pages.
    """
    all_nodes = []
    after_cursor = None

    while True:
        after_part = f', after: "{after_cursor}"' if after_cursor else ''
        paginated_query = f"""query {{
    organization(login: "InstituteforDiseaseModeling") {{
        projectV2(number: {project_id}) {{
            items(first: 100{after_part}) {{
                pageInfo {{
                    hasNextPage
                    endCursor
                }}
                nodes {{
                    content {{
                        ... on Issue {{
                            title
                            url
                            state
                            author {{ login url }}
                            labels(first: 15) {{ nodes {{ name }} }}
                        }}
                        ... on PullRequest {{
                            title
                            url
                            state
                            author {{ login url }}
                            labels(first: 15) {{ nodes {{ name }} }}
                        }}
                    }}
                }}
            }}
        }}
    }}
}}"""
        result = subprocess.run(
            ["gh", "api", "graphql", "-f", f"query={paginated_query}"],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"Error fetching project items: {result.stderr}")
            return all_nodes

        data = json.loads(result.stdout)
        items = data['data']['organization']['projectV2']['items']
        all_nodes.extend(items['nodes'])
        print(f"Fetched {len(items['nodes'])} items (total so far: {len(all_nodes)})")

        if items['pageInfo']['hasNextPage']:
            after_cursor = items['pageInfo']['endCursor']
        else:
            break

    return all_nodes


def update_markdown_changelog(project_df: pd.DataFrame, version: str, docs_path: str):
    """Replace the ## [version] section in docs/changelog.md with project issues.

    Args:
        project_df: DataFrame containing changelog data from a specific GitHub project.
        version: Release version string, e.g. "3.1.0".
        docs_path: Relative path to the docs directory (e.g. "docs").

    Returns:
        None
    """
    project_df = project_df[~project_df['label'].apply(has_excluded_label)]

    all_issue_types = project_df['issue_type'].unique()
    ordered_issue_types = [s for s in SECTION_ORDER if s in all_issue_types] + \
                          [s for s in all_issue_types if s not in SECTION_ORDER]

    lines = [f"## [{version}]\n"]
    for issue_type in ordered_issue_types:
        display_name = SECTION_DISPLAY_NAMES.get(issue_type, issue_type)
        lines.append(f"\n### {display_name}\n\n")
        section_data = project_df[project_df['issue_type'] == issue_type]
        for _, issue in section_data.iterrows():
            url = issue.get('url', '')
            if not isinstance(url, str) or 'issues' not in url.lower():
                continue
            lines.append(f"- [#{issue['issue_number']}]({issue['url']}) - {issue['title']}\n")

    new_section = "".join(lines)

    changelog_file = os.path.join("..", docs_path, 'changelog.md')
    with open(changelog_file, 'r') as f:
        content = f.read()

    # Replace existing [version] section up to the next --- divider
    pattern = rf'## \[{re.escape(version)}\].*?(?=\n---)'
    if re.search(pattern, content, re.DOTALL):
        new_content = re.sub(pattern, new_section.rstrip('\n'), content, flags=re.DOTALL)
    else:
        # Insert as the first release section after the file header
        insert_pos = content.find('\n---\n') + 5
        new_content = content[:insert_pos] + new_section + '\n---\n' + content[insert_pos:]

    with open(changelog_file, 'w') as f:
        f.write(new_content)
    print(f"Markdown changelog updated: {changelog_file}")


def generate_release_change_log(project_df: pd.DataFrame, docs_path: str):
    """
    Generate changelog_x.x.x.rst.
    Args:
        project_df: DataFrame containing changelog data from specific GitHub project
        docs_path: docs directory

    Returns:
        None
    """
    # --- Filter out excluded labels ---
    project_df = project_df[~project_df['label'].apply(has_excluded_label)]

    release_templates = '''

{release_under}
{release}
{release_under}
'''
    section_template = '''
{section}
{section_under}
'''

    releases = project_df['release'].unique()
    final_out = f'.. _changelog-{releases[0]}:\n'
    release_file = os.path.join("..", docs_path, 'changelog', f'changelog_{releases[0]}.rst')
    if os.path.exists(release_file):
        os.remove(release_file)
    final_out += release_templates.format(release=releases[0], release_under='=' * len(releases[0]))
    all_issue_types = project_df['issue_type'].unique()
    ordered_issue_types = [s for s in SECTION_ORDER if s in all_issue_types] + \
                          [s for s in all_issue_types if s not in SECTION_ORDER]
    section_out = final_out
    for issue in ordered_issue_types:
        section_out += section_template.format(section=issue, section_under='-' * len(issue))
        section_data = project_df[project_df['issue_type'] == issue]
        for _, issue in section_data.iterrows():
            url = issue.get('url', '')
            # Skip rows with empty or not issues, we do not include pull requests
            if not isinstance(url, str) or 'issues' not in url.lower():
                continue
            section_out += f"* `#{issue['issue_number']} <{issue['url']}>`_ - {issue['title']}\n"
    with open(release_file, 'w') as out:
        out.write(section_out)
    print(f"Changelog_version.rst generated: {release_file}")


def update_changelog(version: str, docs_path: str):
    """
    Update changelog.rst.
    Args:
        version: Release number
        docs_path: docs directory

    Returns:
        None
    """
    changelog_file = os.path.join("..", docs_path, 'changelog', 'changelog.rst')
    new_entry = f'    changelog_{version}\n'
    # Read the existing content
    with open(changelog_file, 'r') as file:
        lines = file.readlines()

    # Find the index of the toctree line
    toctree_index = lines.index('.. toctree::\n') + 2

    # Insert the new entry after the toctree line
    if new_entry not in lines:
        lines.insert(toctree_index, new_entry)

    # Write the updated content back to the file
    with open(changelog_file, 'w') as file:
        file.writelines(lines)
    print(f"Changelog.rst generated: {changelog_file}")


def generate_changelog_for_releasenote(project_df: pd.DataFrame):
    """
    Generate release note files from DataFrame.
    Args:
        project_df: DataFrame containing changelog data from specific GitHub project

    Returns:
        None
    """
    section_template = '''
{section}
'''
    import os
    dir_path = "release_notes"
    os.makedirs(dir_path, exist_ok=True)
    # --- Filter out excluded labels ---
    if 'label' in project_df.columns:
        project_df = project_df[~project_df['label'].apply(has_excluded_label)]

    releases = project_df['release'].unique()
    release_file = os.path.join(dir_path, f'changelog_release_{releases[0]}.rst')

    if os.path.exists(release_file):
        os.remove(release_file)

    all_issue_types = project_df['issue_type'].unique()
    ordered_issue_types = [s for s in SECTION_ORDER if s in all_issue_types] + \
                          [s for s in all_issue_types if s not in SECTION_ORDER]
    section_out = '## Change log:'
    for issue_type in ordered_issue_types:
        section_out += section_template.format(section='### ' + issue_type)
        section_data = project_df[project_df['issue_type'] == issue_type]
        for _, issue in section_data.iterrows():
            url = issue.get('url', '')
            # Skip rows with empty or not issues, we do not include pull requests
            if not isinstance(url, str) or 'issues' not in url.lower():
                continue
            section_out += f"* #{issue['issue_number']} - {issue['title']}\n"
    with open(release_file, 'w') as out:
        out.write(section_out)
    print(f"Release note file generated: {release_file}")


# Define your GraphQL query
query = """
query {
    organization(login: \"InstituteforDiseaseModeling\") {
    projectV2(number: project_number) {
      id
      title
      url
      owner {
        ... on Organization {
          login
        }
      }

      items(first: 30) {
        nodes {
          content {
            ... on Issue {
              title
              url
              state
              author {
                login
                url
              }
              labels(first: 15) {
                nodes {
                  name
                }
              }
            }
            ... on PullRequest {
              title
              url
              state
              author {
                login
                url
              }
              labels(first: 15) {
                nodes {
                  name
                }
              }
            }
          }
        }
      }
    }
  }
}
"""

# run this script: python project_changelog.py --project_id 83 --version 3.1.0
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--project_id', default="", help="Github Project ID")
    parser.add_argument('--version', default="", help='Release version')

    args = parser.parse_args()

    if args.project_id == "" or not args.project_id.isdigit() or int(args.project_id) < 1:
        print("Please provide correct project id")
        exit(1)
    if args.version == "":
        print("Please provide the correct release version")
        exit(1)

    nodes = fetch_project_items(args.project_id)
    if not nodes:
        print("No items fetched from project.")
        exit(1)

    df = pd.json_normalize(nodes)
    docs_dir = 'docs'
    release = args.version
    df['release'] = release
    df.rename(columns={
        'content.title': 'title',
        'content.url': 'url',
        'content.state': 'status',
        'content.author.login': 'author',
        'content.labels.nodes': 'label'
    }, inplace=True)
    df['issue_number'] = df['url'].str.extract(r'(\d+)')
    df['issue_type'] = df.apply(lambda x: get_issue_type(x['label']), axis=1)
    update_markdown_changelog(df, release, docs_dir)
