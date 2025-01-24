from __future__ import annotations

import os
import re
import subprocess
from click import ClickException, echo

import ghp_import
from packaging import version

import sphinx

default_message = """Deployed {sha} with Sphinx version: {version}"""


class Abort(ClickException, SystemExit):

    code = 1

    def show(self, *args, **kwargs) -> None:
        echo('\n' + self.format_message())

def _is_cwd_git_repo() -> bool:
    try:
        proc = subprocess.Popen(
            ['git', 'rev-parse', '--is-inside-work-tree'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except FileNotFoundError:
        print("Could not find git - is it installed and on your path?")
        raise Abort('Deployment Aborted!')
    proc.communicate()
    return proc.wait() == 0


def _get_current_sha(repo_path) -> str:
    proc = subprocess.Popen(
        ['git', 'rev-parse', '--short', 'HEAD'],
        cwd=repo_path or None,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    stdout, _ = proc.communicate()
    sha = stdout.decode('utf-8').strip()
    return sha


def _get_remote_url(remote_name: str) -> tuple[str, str] | tuple[None, None]:
    # No CNAME found.  We will use the origin URL to determine the GitHub
    # Pages location.
    remote = f"remote.{remote_name}.url"
    proc = subprocess.Popen(
        ["git", "config", "--get", remote],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    stdout, _ = proc.communicate()
    url = stdout.decode('utf-8').strip()

    if 'github.com/' in url:
        host, path = url.split('github.com/', 1)
    elif 'github.com:' in url:
        host, path = url.split('github.com:', 1)
    else:
        return None, None
    return host, path


def _check_version(branch: str) -> None:
    proc = subprocess.Popen(
        ['git', 'show', '-s', '--format=%s', f'refs/heads/{branch}'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    stdout, _ = proc.communicate()
    msg = stdout.decode('utf-8').strip()
    m = re.search(r'\d+(\.\d+)+((a|b|rc)\d+)?(\.post\d+)?(\.dev\d+)?', msg, re.X | re.I)
    previousv = version.parse(m.group()) if m else None
    currentv = version.parse(sphinx.__version__)
    if not previousv:
        print('Version check skipped: No version specified in previous deployment.')
    elif currentv > previousv:
        print(
            f'Previous deployment was done with Sphinx version {previousv}; '
            f'you are deploying with a newer version ({currentv})'
        )
    elif currentv < previousv:
        print(
            f'Deployment terminated: Previous deployment was made with Sphinx version {previousv}; '
            f'you are attempting to deploy with an older version ({currentv}). Use --ignore-version '
            'to deploy anyway.'
        )
        raise Abort('Deployment Aborted!')


def gh_deploy():
    if not _is_cwd_git_repo():
        print('Cannot deploy - this directory does not appear to be a git repository')

    remote_branch = "gh-pages"
    remote_name = "origin"
    site_dir = os.path.abspath("./build/html")

    _check_version(remote_branch)

    sha = _get_current_sha(os.getcwd())
    message = default_message.format(version=sphinx.__version__, sha=sha)

    print(f"Copying '{site_dir}' to '{remote_branch}' branch and pushing to GitHub.")

    try:
        ghp_import.ghp_import(
            site_dir,
            mesg=message,
            remote=remote_name,
            branch=remote_branch,
            push=True,
            nojekyll=True,
        )
    except ghp_import.GhpError as e:
        print(f"Failed to deploy to GitHub with error: \n{e.message}")
        raise Abort('Deployment Aborted!')

    host, path = _get_remote_url(remote_name)

    if host is None or path is None:
        # This could be a GitHub Enterprise deployment.
        print('Your documentation should be available shortly.')
    else:
        username, repo = path.split('/', 1)
        if repo.endswith('.git'):
            repo = repo[: -len('.git')]
        url = f'https://{username}.github.io/{repo}/'
        print(f"Your documentation should shortly be available at: {url}")

gh_deploy()