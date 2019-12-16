import unittest
from bolt.discord.permissions import Permission


class TestPermission(unittest.TestCase):

    def test_permission_from_list_to_list(self):
        expected = ['MANAGE_WEBHOOKS', 'USE_EXTERNAL_EMOJIS']

        permission = Permission(['MANAGE_WEBHOOKS', 'USE_EXTERNAL_EMOJIS'])
        actual = permission.to_list()

        self.assertListEqual(sorted(actual), sorted(expected))

    def test_permission_from_int_to_list(self):
        expected = ['ADMINISTRATOR', 'SEND_MESSAGES']

        permission = Permission(2056)
        actual = permission.to_list()

        self.assertListEqual(sorted(actual), sorted(expected))

    def test_permission_in_permission(self):
        self.assertTrue("ADMINISTRATOR" in Permission(2056))

    def test_permissions_in_permission(self):
        self.assertTrue(["ADMINISTRATOR", "SEND_MESSAGES"] in Permission(2056))

    def test_permission_not_in_permission(self):
        self.assertTrue("USE_VAD" not in Permission(2056))

    def test_permissions_not_in_permission(self):
        self.assertTrue(["SPEAK", "MANAGE_EMOJIS"] not in Permission(2056))

    def test_permission_add(self):
        permission = Permission(2056)
        self.assertTrue(permission.allows("ADMINISTRATOR"))
        self.assertFalse(permission.allows("MENTION_EVERYONE"))

        permission.add("MENTION_EVERYONE")
        self.assertTrue(permission.allows("MENTION_EVERYONE"))

    def test_permission_remove(self):
        permission = Permission(2056)
        self.assertTrue(permission.allows("ADMINISTRATOR"))
        self.assertTrue(permission.allows("SEND_MESSAGES"))

        permission.remove("SEND_MESSAGES")
        self.assertFalse(permission.allows("SEND_MESSAGES"))
