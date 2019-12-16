import unittest
from bolt.discord.models.base import Model, Field, ListField
from bolt.discord.models.base import ModelMissingRequiredKeyError, ModelValidationError, ImmutableFieldError


class TestModel(unittest.TestCase):
    def test_model_basic(self):
        class CoolModel(Model):
            id = Field(int)
            name = Field(str)

        input_data = {"id": 123, "name": "Boltbot"}

        actual = CoolModel.marshal(input_data)

        self.assertEqual(actual.id, input_data['id'])
        self.assertEqual(actual.name, input_data['name'])

    def test_model_missingfield(self):
        class CoolModel(Model):
            id = Field(int, required=True)

        input_data = {"name": 123}

        with self.assertRaises(ModelMissingRequiredKeyError):
            CoolModel.marshal(input_data)

    def test_field_immutable(self):
        class CoolModel(Model):
            id = Field(int, immutable=True)

        input_data = {"id": 123}

        actual = CoolModel.marshal(input_data)

        with self.assertRaises(ImmutableFieldError):
            actual.id = 1000

        with self.assertRaises(ImmutableFieldError):
            del actual.id

    def test_model_blank(self):
        class CoolModel(Model):
            pass

        input_data = {}

        try:
            CoolModel.marshal(input_data)
        except Exception as e:
            self.fail(f"test_field_blank raised exception {e}")

    def test_field_different_key(self):
        class CoolModel(Model):
            name = Field(str, json_key="username")

        input_data = {"username": "Boltbot"}

        actual = CoolModel.marshal(input_data)

        self.assertEqual(actual.name, input_data['username'])

    def test_field_length(self):
        class CoolModel(Model):
            name = Field(str, max_length=10)

        input_data = {"name": "b" * 100}

        with self.assertRaises(ModelValidationError):
            CoolModel.marshal(input_data)

    def test_field_default_value(self):
        class CoolModel(Model):
            name = Field(str, default="Nice")

        input_data = {}

        actual = CoolModel.marshal(input_data)

        self.assertEqual(actual.name, "Nice")

    def test_field_required(self):
        class CoolModel(Model):
            id = Field(int, required=True)
            name = Field(str)

        input_data = {"name": "Boltbot"}

        with self.assertRaises(ModelMissingRequiredKeyError):
            CoolModel.marshal(input_data)

    def test_field_int(self):
        class CoolModel(Model):
            id = Field(int)

        input_data = {"id": 123}

        actual = CoolModel.marshal(input_data)
        self.assertEqual(actual.id, int(input_data['id']))
        self.assertIsInstance(actual.id, int)

    def test_field_str(self):
        class CoolModel(Model):
            name = Field(str)

        input_data = {"name": 123}

        actual = CoolModel.marshal(input_data)
        self.assertEqual(actual.name, str(input_data['name']))
        self.assertIsInstance(actual.name, str)

    def test_field_bool(self):
        class CoolModel(Model):
            flag = Field(bool)

        input_data = {"flag": False}

        actual = CoolModel.marshal(input_data)
        self.assertEqual(actual.flag, bool(input_data['flag']))
        self.assertIsInstance(actual.flag, bool)

    def test_list_field(self):
        class CoolModel(Model):
            alist = ListField(int)

        input_data = {"alist": [1, 2, 3, 4, 5]}

        actual = CoolModel.marshal(input_data)
        self.assertListEqual(actual.alist, input_data['alist'])
        self.assertIsInstance(actual.alist, list)

    def test_field_custom(self):
        class CustomType(str):
            pass

        class CoolModel(Model):
            custom = Field(CustomType)

        input_data = {"custom": "field"}

        actual = CoolModel.marshal(input_data)
        self.assertEqual(actual.custom, CustomType(input_data['custom']))
        self.assertIsInstance(actual.custom, CustomType)

    def test_field_model(self):
        class AnotherModel(Model):
            id = Field(int)

        class CoolModel(Model):
            foreign = Field(AnotherModel)

        input_data = {"foreign": {"id": 123}}

        actual = CoolModel.marshal(input_data)

        self.assertEqual(actual.foreign.id, input_data['foreign']['id'])
        self.assertIsInstance(actual.foreign, AnotherModel)
