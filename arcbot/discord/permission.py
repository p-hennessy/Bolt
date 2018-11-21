"""
    This module provides an enum containing permission flags as per discord API
    This module provides a class for talking about permissions within the bot

    Contributors:
        - Patrick Hennessy

    License:
        Arcbot is free software: you can redistribute it and/or modify it under the terms of the GNU
        General Public License v3; as published by the Free Software Foundation
"""

from enum import Enum


class PermissionFlag(Enum):
    CREATE_INSTANT_INVITE = 0x00000001
    KICK_MEMBERS = 0x00000002
    BAN_MEMBERS = 0x00000004
    ADMINISTRATOR = 0x00000008
    MANAGE_CHANNELS = 0x00000010
    MANAGE_GUILD = 0x00000020
    ADD_REACTIONS = 0x00000040
    VIEW_AUDIT_LOG = 0x00000080
    READ_MESSAGES = 0x00000400
    SEND_MESSAGES = 0x00000800
    SEND_TTS_MESSAGES = 0x00001000
    MANAGE_MESSAGES = 0x00002000
    EMBED_LINKS = 0x00004000
    ATTACH_FILES = 0x00008000
    READ_MESSAGE_HISTORY = 0x00010000
    MENTION_EVERYONE = 0x00020000
    USE_EXTERNAL_EMOJIS = 0x00040000
    CONNECT = 0x00100000
    SPEAK = 0x00200000
    MUTE_MEMBERS = 0x00400000
    DEAFEN_MEMBERS = 0x00800000
    MOVE_MEMBERS = 0x01000000
    USE_VAD = 0x02000000
    CHANGE_NICKNAME = 0x04000000
    MANAGE_NICKNAMES = 0x08000000
    MANAGE_ROLES = 0x10000000
    MANAGE_WEBHOOKS = 0x20000000
    MANAGE_EMOJIS = 0x40000000


class Permission():
    def __init__(self, value):
        if isinstance(value, list):
            self.bitarray = 0
            for item in value:
                self.bitarray |= self._get_permission_value(item)
        else:
            self.bitarray = value

    def __contains__(self, item):
        if isinstance(item, list):
            for i in item:
                if not self.allows(i):
                    return False
            else:
                return True
        else:
            return self.allows(item)

    def __repr__(self):
        classname = f"{type(self).__name__}"
        return f"{classname}({self.bitarray})"

    def allows(self, permission_name):
        permission = self._get_permission_value(permission_name)
        return bool(self.bitarray & permission)

    def add(self, permission_name):
        self.bitarray |= self._get_permission_value(permission_name)

    def remove(self, permission_name):
        self.bitarray &= ~self._get_permission_value(permission_name)

    @staticmethod
    def _get_permission_value(name):
        return getattr(PermissionFlag, name).value or 0x00000000

    def to_list(self):
        return [flag.name for flag in PermissionFlag if self.allows(flag.name)]
