from unittest import TestCase
from contracting.schema.validator import validate_multi_key_map


class TestSchemaValidator(TestCase):
    def test_validate_multi_key_map(self):
        d = {
            'first_name': 'string',
            'last_name': 'int'
        }

        self.assertTrue(validate_multi_key_map(d))

    def test_validate_multi_key_map_failure(self):
        d = {
            'first_name': 'string',
            'number': {
                'signed': False
            }
        }

        self.assertFalse(validate_multi_key_map(d))

