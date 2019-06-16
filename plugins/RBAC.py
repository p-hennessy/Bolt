"""
    Description:
        Implments a naive ACL system to prevent certain users from accessing bot commands

    Contributors:
        - Patrick Hennessy
"""
from bolt import Plugin
from bolt import pre_command_hook, command
from bolt.utils import Colors


class RBAC(Plugin):
    def activate(self):
        self.rbac = self.database.rbac

    @pre_command_hook()
    def check_access(self, command, event):
        if event.message.author.id == self.config['owner']:
            return True

        author = self.rbac.find_one({"id": event.message.author.id})

        if not author:
            new_user = {
                "id": event.message.author.id,
                "roles": ["default"]
            }
            self.rbac.replace_one({"id": new_user['id']}, new_user, upsert=True)
            author = self.rbac.find_one({"id": event.message.author.id})

        for role in author['roles']:
            plugin_name, command_name = command.callback.__qualname__.split('.')

            for allowed in self.config['roles'][role]:
                allowed_plugin, allowed_command = allowed.split(".")

                if plugin_name == allowed_plugin:
                    if allowed_command == command_name or allowed_command == "*":
                        return True
        else:
            if command.trigger is not None:
                embed = {
                    "title": ":warning: You are not allowed to access this command",
                    "color": Colors.WARNING
                }

                self.say(event.message.channel_id, embed=embed)
            return False

    @command("roles")
    def list_roles(self, event):
        pass

    @command("add role <userid> <roleName>")
    def add_role_to_user(self, event):
        pass

    @command("remove role <userid> <roleName>")
    def remove_role_from_user(self, event):
        pass
