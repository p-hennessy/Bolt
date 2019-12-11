# Events Names

See [Discord's official API documentation](https://discordapp.com/developers/docs/topics/gateway#connecting-and-resuming) for more information.

```python
from bolt.discord import Events
```

| Event Name | Description |
| :--- | :--- |
| [READY](https://discordapp.com/developers/docs/topics/gateway#ready) | Contains the initial state information |
| [RESUMED](https://discordapp.com/developers/docs/topics/gateway#resumed) | Response to [Resume](https://discordapp.com/developers/docs/topics/gateway#resume) |
| [CHANNEL\_CREATE](https://discordapp.com/developers/docs/topics/gateway#channel-create) | New channel created |
| [CHANNEL\_UPDATE](https://discordapp.com/developers/docs/topics/gateway#channel-update) | Channel was updated |
| [CHANNEL\_DELETE](https://discordapp.com/developers/docs/topics/gateway#channel-delete) | Channel was deleted |
| [CHANNEL\_PINS\_UPDATE](https://discordapp.com/developers/docs/topics/gateway#channel-pins-update) | Message was pinned or unpinned |
| [GUILD\_CREATE](https://discordapp.com/developers/docs/topics/gateway#guild-create) | Unavailable guild, guild became available, bot joined new guild |
| [GUILD\_UPDATE](https://discordapp.com/developers/docs/topics/gateway#guild-update) | Guild was updated |
| [GUILD\_DELETE](https://discordapp.com/developers/docs/topics/gateway#guild-delete) | Guild became unavailable, bot left, bot was removed from guild |
| [GUILD\_BAN\_ADD](https://discordapp.com/developers/docs/topics/gateway#guild-ban-add) | User was banned from a guild |
| [GUILD\_BAN\_REMOVE](https://discordapp.com/developers/docs/topics/gateway#guild-ban-remove) | User was unbanned from a guild |
| [GUILD\_EMOJIS\_UPDATE](https://discordapp.com/developers/docs/topics/gateway#guild-emojis-update) | Guild emojis were updated |
| [GUILD\_INTEGRATIONS\_UPDATE](https://discordapp.com/developers/docs/topics/gateway#guild-integrations-update) | Guild integration was updated |
| [GUILD\_MEMBER\_ADD](https://discordapp.com/developers/docs/topics/gateway#guild-member-add) | New user joined a guild |
| [GUILD\_MEMBER\_REMOVE](https://discordapp.com/developers/docs/topics/gateway#guild-member-remove) | User was removed from a guild |
| [GUILD\_MEMBER\_UPDATE](https://discordapp.com/developers/docs/topics/gateway#guild-member-update) | Guild member was updated |
| [GUILD\_MEMBERS\_CHUNK](https://discordapp.com/developers/docs/topics/gateway#guild-members-chunk) | Response to Request Guild Members |
| [GUILD\_ROLE\_CREATE](https://discordapp.com/developers/docs/topics/gateway#guild-role-create) | Guild role was created |
| [GUILD\_ROLE\_UPDATE](https://discordapp.com/developers/docs/topics/gateway#guild-role-update) | Guild role was updated |
| [GUILD\_ROLE\_DELETE](https://discordapp.com/developers/docs/topics/gateway#guild-role-delete) | Guild role was deleted |
| [MESSAGE\_CREATE](https://discordapp.com/developers/docs/topics/gateway#message-create) | Message was created |
| [MESSAGE\_UPDATE](https://discordapp.com/developers/docs/topics/gateway#message-update) | Message was edited |
| [MESSAGE\_DELETE](https://discordapp.com/developers/docs/topics/gateway#message-delete) | Message was deleted |
| [MESSAGE\_DELETE\_BULK](https://discordapp.com/developers/docs/topics/gateway#message-delete-bulk) | Multiple messages were deleted at once |
| [MESSAGE\_REACTION\_ADD](https://discordapp.com/developers/docs/topics/gateway#message-reaction-add) | User reacted to a message |
| [MESSAGE\_REACTION\_REMOVE](https://discordapp.com/developers/docs/topics/gateway#message-reaction-remove) | User removed a reaction from a message |
| [MESSAGE\_REACTION\_REMOVE\_ALL](https://discordapp.com/developers/docs/topics/gateway#message-reaction-remove-all) | All reactions were removed from a message |
| [PRESENCE\_UPDATE](https://discordapp.com/developers/docs/topics/gateway#presence-update) | User was updated |
| [TYPING\_START](https://discordapp.com/developers/docs/topics/gateway#typing-start) | User started typing in a channel |
| [USER\_UPDATE](https://discordapp.com/developers/docs/topics/gateway#user-update) | Properties about the bot user changed |
| [VOICE\_STATE\_UPDATE](https://discordapp.com/developers/docs/topics/gateway#voice-state-update) | User joined, left, or moved a voice channel |
| [VOICE\_SERVER\_UPDATE](https://discordapp.com/developers/docs/topics/gateway#voice-server-update) | Guild's voice server was updated, \(such as voice region\) |
| [WEBHOOKS\_UPDATE](https://discordapp.com/developers/docs/topics/gateway#webhooks-update) | Guild channel webhook was created, update, or deleted |

