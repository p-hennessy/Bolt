"""
    Description:
        Posts in a channel when getting webhooks from Github

    Contributors:
        - Patrick Hennessy
"""
from arcbot import Plugin
from arcbot import command, webhook, interval, subscriber
from arcbot.discord import Events
from arcbot.utils import Colors
from arcbot.utils import Timer

import ujson as json

class Github(Plugin):
    @command("^(github|source code|repo)$")
    def repo(self, event):
        self.say(event.channel_id, "You can find my code at: https://github.com/ns-phennessy/Arcbot")

    @webhook('/github', methods=['POST'])
    def webhook(self, request):
        self.admin_channel_id = "249770653534650378"

        with Timer() as timer:
            data = json.loads(request.stream.read())
            headers = request.headers
            event = headers['X-GITHUB-EVENT']
            embed = None

            if event == 'push':
                embed = self.handle_push(data)
            elif event == 'issues':
                embed = self.handle_issue(data)

            if not embed:
                return

            embed["footer"] = {"text": f"⏰ {timer.delta}ms | 🔌 Github.webhook"}
            self.say(self.admin_channel_id, embed=embed)

    def handle_push(self, data):
        repo_name = data['repository']['full_name']
        repo_url = data['repository']['html_url']

        branch = data['ref'].replace('refs/heads/', '')
        commits = ""

        for commit in data['commits']:
            commit_hash = commit['id'][0:7]
            commit_url = commit['url']
            commit_message = commit['message']
            commit_author = commit['author']['name']

            commits += f"[`{branch}:{commit_hash}`]({commit_url}) {commit_message}\n"

        embed = {
            "title": f":zap: Commits pushed",
            "description": f"[{repo_name}]({repo_url})\n\n",
            "thumbnail": {"url": "http://git-class.gr/images/GitHub_Logo.png"},
            "color": Colors.INFO,
            "fields": [
                {
                    "name": f"Commits",
                    "value": f"{commits}"
                }
            ]
        }
        return embed

    def handle_issue(self, data):
        repo_name = data['repository']['full_name']
        repo_url = data['repository']['html_url']

        issue_action = data['action']
        issue_title = data['issue']['title']
        issue_author = data['issue']['user']['login']
        issue_number = data['issue']['number']
        issue_body = data['issue']['body']
        issue_url = data['issue']['html_url']

        if not issue_action == "opened":
            return

        embed = {
            "title": f":warning: Issue Opened by {issue_author}",
            "description": f"[{repo_name}#{issue_number}]({issue_url})\n\n",
            "thumbnail": {"url": "http://git-class.gr/images/GitHub_Logo.png"},
            "color": Colors.WARNING,
            "fields": [
                {
                    "name": f"{issue_title}",
                    "value": f"{issue_body}"
                }
            ]
        }
        return embed

    def handle_fork(self, data):
        repo_name = data['repository']['full_name']
        repo_url = data['repository']['html_url']

        embed = {
            "title": f":fork_and_knife: Repo forked by {issue_author}",
            "description": f"[{repo_name}#{issue_number}]({issue_url})\n\n",
            "color": Colors.CRITICAL,
            "fields": [
                {
                    "name": "Original",
                    "value": "[ns-phennessy/Arcbot]()",
                    "inline": true
                },
                {
                    "name": "Fork",
                    "value": "[Nihilz2/Arcbot]()",
                    "inline": true
                }
            ],
        }
        return embed
