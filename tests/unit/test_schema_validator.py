from unittest import TestCase
from contracting.schema.validator import *


class TestSchemaValidator(TestCase):
    def test_no_schema_in_doc(self):
        d = '''
not_schema:
  - 3
  - 4
  - 5
        '''

        with self.assertRaises(InvalidSchema):
            is_valid(d)

    def test_schema_no_maps_fails(self):
        d = '''
schema:
  - 3
  - 4
  - 5
        '''

        with self.assertRaises(AttributeError):
            is_valid(d)

    def test_schema_with_primitive_as_property_fails(self):
        d = '''
schema:
  string: int
        '''

        with self.assertRaises(InvalidTypeDefault):
            is_valid(d)

    def test_schema_with_primitive_works(self):
        d = '''
schema:
  thing: int
        '''

        is_valid(d)

    def test_schema_with_wrong_primitive_fails(self):
        d = '''
schema:
  thing: set
        '''

        with self.assertRaises(InvalidTypeDefault):
            is_valid(d)

    def test_schema_with_multi_maps_works(self):
        d = '''
schema:
  thing: int
  yo: string
  another: number
  woohoo: bool
        '''

        is_valid(d)

    def test_schema_inner_map(self):
        d = '''
schema:
  thing:
    string:
      length: 10
        '''

        is_valid(d)

    def test_schema_inner_map_fails_if_unexpected_kwarg(self):
        d = '''
schema:
  thing:
    string:
      woohoo: 10
        '''

        with self.assertRaises(TypeError):
            is_valid(d)