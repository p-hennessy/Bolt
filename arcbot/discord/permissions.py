class Permission():
    flags = {
        "CREATE_INSTANT_INVITE": 0x00000001,
        "KICK_MEMBERS": 0x00000002,
        "BAN_MEMBERS": 0x00000004,
        "ADMINISTRATOR": 0x00000008,
        "MANAGE_CHANNELS": 0x00000010,
        "MANAGE_GUILD": 0x00000020,
        "ADD_REACTIONS": 0x00000040,
        "VIEW_AUDIT_LOG": 0x00000080,
        "READ_MESSAGES": 0x00000400,
        "SEND_MESSAGES": 0x00000800,
        "SEND_TTS_MESSAGES": 0x00001000,
        "MANAGE_MESSAGES": 0x00002000,
        "EMBED_LINKS": 0x00004000,
        "ATTACH_FILES": 0x00008000,
        "READ_MESSAGE_HISTORY": 0x00010000,
        "MENTION_EVERYONE": 0x00020000,
        "USE_EXTERNAL_EMOJIS": 0x00040000,
        "CONNECT": 0x00100000,
        "SPEAK": 0x00200000,
        "MUTE_MEMBERS": 0x00400000,
        "DEAFEN_MEMBERS": 0x00800000,
        "MOVE_MEMBERS": 0x01000000,
        "USE_VAD": 0x02000000,
        "CHANGE_NICKNAME": 0x04000000,
        "MANAGE_NICKNAMES": 0x08000000,
        "MANAGE_ROLES": 0x10000000,
        "MANAGE_WEBHOOKS": 0x20000000,
        "MANAGE_EMOJIS": 0x40000000
    }

    def __init__(self, value):
        if isinstance(value, list):
            self.bitarray = 0
            for item in items:
                self.bitarray |= cls.flags.get(item, 0x00000000)
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

    def allows(self, permission_name):
        permission = self.__class__.flags[permission_name]
        return bool(self.bitarray & permission)

    def add(self, permission_name):
        self.bitarray |= self.__class__.flags[permission_name]

    def remove(self, permission_name):
        self.bitarray &= ~self.__class__.flags[permission_name]

    def to_list(self):
        output = []

        for flag in self.__class__.flags.keys():
            if self.allows(flag):
                output.append(flag)

        return output
