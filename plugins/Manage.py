"""
    Description:
        Commands related to basic managment

    Contributors:
        - Patrick Hennessy
"""
from arcbot import Plugin
from arcbot import command, interval, subscriber
from arcbot.utils import Colors, Timer, readable_time
from arcbot.discord import Events

import random

class Manage(Plugin):
    def activate(self):
        self.nickname = "Λгсвοт"

    @command("^ping$")
    def ping(self, event):
        self.say(event.channel_id, f":zap: **{self.bot.websocket.ping}**ms")

    @command("^trigger$", trigger="?")
    def trigger(self, event):
        self.say(event.channel_id, f"My default trigger is `{self.bot.config.trigger}`")

    @command("^uptime$")
    def uptime(self, event):
        elapsed = time.time() - self.bot.websocket.login_time
        self.say(event.channel_id, f"I've been connected for: **{readable_time(elapsed)}**")

    @command("^list plugins$")
    def list_plugins(self, event):
        with Timer() as timer:
            plugins = self.bot.plugins

            names = "".join([type(plugin).__name__ + "\n" for plugin in plugins])
            statuses = "".join(["Enabled" + "\n" for plugin in plugins])

            embed = {
                "color": Colors.INFO,
                'fields': [
                    {'name': 'Name', 'value': names, "inline": True},
                    {'name': 'Status', 'value': statuses, "inline": True}
                ],
                "footer": {
                    "text": f"⏰ {timer.delta}ms | 🔌 Manage.list_plugins"
                }
            }
            self.say(event.channel_id, embed=embed)

    @interval(300)
    def status_rotator(self):
        statuses = [
            "{இ}ڿڰۣ-ڰۣ~—",
            "♫♪ |̲̅̅●̲̅̅|̲̅̅=̲̅̅|̲̅̅●̲̅̅| ♫♪",
            "((̲̅ ̲̅(̲̅C̲̅r̲̅a̲̅y̲̅o̲̅l̲̲̅̅a̲̅( ̲̅((>",
            "(͡ ° ͜ʖ ͡ °)",
            "(ಠ_ಠ)",
            "༼ つ ◕_◕ ༽つ",
            "¯\_(ツ)_/¯",
            "(̿▀̿ ̿Ĺ̯̿̿▀̿ ̿)̄",
            "( ˘ ³˘)♥",
            "⊂(◉‿◉)つ",
            "(งツ)ว",
            "(｡◕‿◕｡)",
            "°‿‿°",
            "٩(͡๏̯͡๏)۶",
            "( • ͜ʖ • )",
            "(⌐ ͡■ ͜ʖ ͡■)",
            "(͠≖ ͜ʖ͠≖)",
            "¯\_(ツ)_/¯",
            "¯\_(シ)_/¯",
            "( ͡ °~͡° )",
            "[̲̅$̲̅(̲̅ ͡° ͜ʖ ͡°̲̅)̲̅$̲̅]",
            "( ͡° ʖ̯ ͡°)",
            "┌( ಠ_ಠ)┘",
            "[+..••]",
            "( ‾ʖ̫‾)",
            "๏[-ิ_•ิ]๏",
            "ʀᴀɪsᴇ ᴜʀ ᴅᴏɴɢᴇʀs ヽ༼ຈل͜ຈ༽/",
            "Hide the salami (͡ ° ͜ʖ ͡ °)",
            "Whos in my mouth? (͡ ° ͜ʖ ͡ °)",
            "( ͜。 ͡ʖ ͜。) ıɯɐlɐs ǝɥʇ ǝpıɥ",
            "Hot potato",
            "with Fire 🔥",
            "Half-life 3",
            "Rocket League of Legends",
            "Fidget Spinner ߷",
            "🎮 Real life",
            "Barbie Dress-Up 💋",
            "Arc: Botting Evolved",
            "Jeopardy",
            "Family Feud",
            "Wheel of Fortune",
            "The Price is Right!",
            "Rugby",
            "Minesweeper",
            "Microsoft Word",
            "Office Communicator",
            "Explorer.exe",
            "Kernal Panic 0xD34DB33F",
            "HTTP/1.1 418 IM A TEAPOT",
            "game OR 1=1; DROP DATABASE",
            "Segmentation Fault at 0xb01dface",
            "<script>alert(document.cookie);</script>",
            "from status import swole",
            "sudo rm -rf /",
            "import antigravity"
        ]
        self.bot.websocket.status = random.choice(statuses)

    @subscriber(Events.GUILD_MEMBER_UPDATE)
    def prevent_nickname_changes(self, event):
        if event.user.id == self.bot.websocket.user_id and event.nick != self.nickname and event.nick:
            self.bot.api.modify_current_user_nick(event.guild_id, nick=self.nickname)
