"""
Dev utility script to generate changelog file and changelog for release note based on GitHub project id and release version.

Run script: python project_changelog.py --project_id 53 --version 2.0.2

Note, before run this script, you need to do following steps first:
1) Install GitHub CLI (gh)
2) Authenticate with your GitHub account (gh auth login) which need your token in prompt.
3) Provide script arg1: --project_id 53. (for example: 53 is IDMTools project number for 'MPI Slurm and Container Support')
4) Provide script arg2. --version 2.0.2 (2.0.2 is the current release number for IDMTools)
"""
import argparse
import os
import subprocess
import json
import pandas as pd


def generate_changelog_index_from_df(df, docs_dir):
    """
    Generate changelog index from DataFrame.
    Args:
        df: DataFrame containing changelog data
        docs_dir: doc directory

    Returns:
        None
    """
    cl_name = os.path.join("..", docs_dir, 'changelog', 'changelog.rst')
    with open(cl_name, 'w') as out:
        out.write("=========\n")
        out.write("Changelog\n")
        out.write("=========\n")
        out.write("\n.. toctree::\n\n")
        releases = df['release'].unique()
        for release in sorted(releases, reverse=True):
            out.write(f'    changelog_{release}\n')


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
    elif any(label['name'] in ['Platform support', 'COMPS', 'SLURM', 'Container Workflow'] for label in labels):
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


def generate_release_change_log(df, docs_dir):
    """
    Generate release note files from DataFrame.
    Args:
        df: DataFrame containing changelog data
        docs_dir: doc directory

    Returns:
        None
    """
    release_templates = '''

{release_under}
{release}
{release_under}
'''
    section_template = '''
{section}
{section_under}
'''

    releases = df['release'].unique()
    final_out = f'.. _changelog-{releases[0]}:\n'
    release_file = os.path.join("..", docs_dir, 'changelog', f'changelog_{releases[0]}.rst')
    if os.path.exists(release_file):
        os.remove(release_file)
    final_out += release_templates.format(release=releases[0], release_under='=' * len(releases[0]))
    issue_types = df['issue_type'].unique()
    section_out = final_out
    for issue in sorted(issue_types):

        section_out += section_template.format(section=issue, section_under='-' * len(issue))
        section_data = df[df['issue_type'] == issue]
        for _, issue in section_data.iterrows():
            section_out += f"* `#{issue['issue_number']} <{issue['url']}>`_ - {issue['title']}\n"
    with open(release_file, 'w') as out:
        out.write(section_out)


def update_changelog(release, docs_dir):
    """
    Update changelog index file with the new release.
    Args:
        release: Release number
        docs_dir: doc directory

    Returns:
        None
    """
    changelog_file = os.path.join("..", docs_dir, 'changelog', 'changelog.rst')
    new_entry = f'    changelog_{release}\n'
    # Read the existing content
    with open(changelog_file, 'r') as file:
        lines = file.readlines()

    # Find the index of the toctree line
    toctree_index = lines.index('.. toctree::\n') + 2

    # Insert the new entry after the toctree line
    lines.insert(toctree_index, new_entry)

    # Write the updated content back to the file
    with open(changelog_file, 'w') as file:
        file.writelines(lines)


def generate_changelog_for_releasenote(df, docs_dir):
    """
    Generate release note files from DataFrame.
    Args:
        df: DataFrame containing changelog data
        docs_dir: doc directory

    Returns:
        None
    """
    section_template = '''
{section}
'''
    import os
    dir_path = "release_notes"
    os.makedirs(dir_path, exist_ok=True)

    releases = df['release'].unique()
    release_file = os.path.join(dir_path, f'changelog_release_{releases[0]}.rst')

    if os.path.exists(release_file):
        os.remove(release_file)

    issue_types = df['issue_type'].unique()
    section_out = '## Change log:'
    for issue in sorted(issue_types):
        section_out += section_template.format(section='### ' + issue)
        section_data = df[df['issue_type'] == issue]
        for _, issue in section_data.iterrows():
            section_out += f"* #{issue['issue_number']} - {issue['title']}\n"
    with open(release_file, 'w') as out:
        out.write(section_out)


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

# run this script: python project_changelog.py --project_id 53 --version 2.0.2
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--project_id', default="", help="Github Project ID")
    parser.add_argument('--version', default="", help='Release version')

    args = parser.parse_args()

    if args.project_id == "" or not args.project_id.isdigit() or int(args.project_id) < 52:
        print("Please provide correct project id")
        exit(1)
    if args.version == "":
        print("Please provide the correct release version")
        exit(1)

    query = query.replace("project_number", args.project_id)
    result = subprocess.run(
        ["gh", "api", "graphql", "-f", f"query={query}"],
        capture_output=True,
        text=True
    )
    # Check for errors
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
    else:
        # Parse JSON output
        data = json.loads(result.stdout)

        # Convert to DataFrame
        df = pd.json_normalize(data, record_path=["data", "organization", "projectV2", "items", "nodes"])

        docs_dir = 'docs'
        release = args.version
        df['release'] = release
        df.rename(columns={'content.title': 'title', 'content.url': 'url', 'content.state': 'status', 'content.author.login': 'author', 'content.labels.nodes': 'label'}, inplace=True)
        df['issue_number'] = df['url'].str.extract(r'(\d+)')
        df['issue_type'] = df.apply(lambda x: get_issue_type(x['label']), axis=1)
        generate_release_change_log(df, docs_dir)
        generate_changelog_for_releasenote(df, docs_dir)
        update_changelog(release, docs_dir)
