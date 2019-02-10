import unittest
from bolt.discord.models.base import Model, Field, ListField
from bolt.discord.models.base import ModelMissingRequiredKeyError, ModelValidationError, ImmutableFieldError

class TestModel(unittest.TestCase):
    def test_model_basic(self):
        class CoolModel(Model):
            id = Field(int)
            name = Field(str)

        input = {"id": 123, "name": "Boltbot"}

        actual = CoolModel.marshal(input)

        self.assertEqual(actual.id, input['id'])
        self.assertEqual(actual.name, input['name'])

    def test_field_immutable(self):
        class CoolModel(Model):
            id = Field(int, immutable=True)

        input = {"id": 123}

        actual = CoolModel.marshal(input)

        with self.assertRaises(ImmutableFieldError):
            actual.id = 1000

        with self.assertRaises(ImmutableFieldError):
            del actual.id

    def test_model_blank(self):
        class CoolModel(Model):
            pass

        input = {}

        try:
            actual = CoolModel.marshal(input)
        except Exception as e:
            self.fail(f"test_field_blank raised exception {e}")

    def test_field_different_key(self):
        class CoolModel(Model):
            name = Field(str, json_key="username")

        input = {"username": "Boltbot"}

        actual = CoolModel.marshal(input)

        self.assertEqual(actual.name, input['username'])

    def test_field_default_value(self):
        class CoolModel(Model):
            name = Field(str, default="Nice")

        input = {}

        actual = CoolModel.marshal(input)

        self.assertEqual(actual.name, "Nice")

    def test_field_required(self):
        class CoolModel(Model):
            id = Field(int, required=True)
            name = Field(str)

        input = {"name": "Boltbot"}

        with self.assertRaises(ModelMissingRequiredKeyError):
            actual = CoolModel.marshal(input)


    def test_field_int(self):
        class CoolModel(Model):
            id = Field(int)

        input = {"id": 123}

        actual = CoolModel.marshal(input)
        self.assertEqual(actual.id, int(input['id']))
        self.assertIsInstance(actual.id, int)

    def test_field_str(self):
        class CoolModel(Model):
            name = Field(str)

        input = {"name": 123}

        actual = CoolModel.marshal(input)
        self.assertEqual(actual.name, str(input['name']))
        self.assertIsInstance(actual.name, str)

    def test_field_bool(self):
        class CoolModel(Model):
            flag = Field(bool)

        input = {"flag": False}

        actual = CoolModel.marshal(input)
        self.assertEqual(actual.flag, bool(input['flag']))
        self.assertIsInstance(actual.flag, bool)

    def test_list_field(self):
        class CoolModel(Model):
            alist = ListField(int)

        input = {"alist": [1,2,3,4,5]}

        actual = CoolModel.marshal(input)
        self.assertListEqual(actual.alist, input['alist'])
        self.assertIsInstance(actual.alist, list)

    def test_field_custom(self):
        class CustomType(str):
            pass

        class CoolModel(Model):
            custom = Field(CustomType)

        input = {"custom": "field"}

        actual = CoolModel.marshal(input)
        self.assertEqual(actual.custom, CustomType(input['custom']))
        self.assertIsInstance(actual.custom, CustomType)

    def test_field_model(self):
        class AnotherModel(Model):
            id = Field(int)

        class CoolModel(Model):
            foreign = Field(AnotherModel)

        input = {"foreign": {"id": 123}}

        actual = CoolModel.marshal(input)

        self.assertEqual(actual.foreign.id, input['foreign']['id'])
        self.assertIsInstance(actual.foreign, AnotherModel)
