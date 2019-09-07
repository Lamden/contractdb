from unittest import TestCase
from contracting.schema.type_definitions.primitives import *
from contracting.schema.type_definitions.base import TypeDefinition, InvalidOptionPassed


class TestPrimitives(TestCase):
    def test_string_bad_optional(self):
        with self.assertRaises(InvalidOptionPassed):
            String().validate_options(optional=5)

    def test_string_bad_length(self):
        with self.assertRaises(InvalidOptionPassed):
            String().validate_options(length=-5)

    def test_string_good_length(self):
        String().validate_options(length=5)

    def test_string_bad_regex(self):
        with self.assertRaises(InvalidOptionPassed):
            String().validate_options(regex=r'[')

    def test_string_good_regex(self):
        String().validate_options(regex=r'good')

    def test_int_bad_signed(self):
        with self.assertRaises(InvalidOptionPassed):
            Int().validate_options(signed=4)

    def test_int_good_signed(self):
        Int().validate_options(signed=True)

    def test_int_bad_bits(self):
        with self.assertRaises(InvalidOptionPassed):
            Int().validate_options(bits='bbb')

    def test_int_good_bits(self):
        Int().validate_options(bits=32)

    def test_number_bad_precision(self):
        with self.assertRaises(InvalidOptionPassed):
            Number().validate_options(precision=-1)

    def test_number_precision_cant_be_greater_than_64(self):
        with self.assertRaises(InvalidOptionPassed):
            Number().validate_options(precision=100)

    def test_number_precision_inbetween_0_and_64_works(self):
        Number().validate_options(precision=6)

    def test_hex_works_with_positive_bytes(self):
        Hex().validate_options(bytes=1)

    def test_hex_cant_be_zero(self):
        with self.assertRaises(InvalidOptionPassed):
            Hex().validate_options(bytes=0)

    def test_hex_cant_be_less_than_zero(self):
        with self.assertRaises(InvalidOptionPassed):
            Hex().validate_options(bytes=-10)

    def test_binary_works_with_positive_bytes(self):
        Binary().validate_options(bytes=1)

    def test_binary_cant_be_zero(self):
        with self.assertRaises(InvalidOptionPassed):
            Binary().validate_options(bytes=0)

    def test_binary_cant_be_less_than_zero(self):
        with self.assertRaises(InvalidOptionPassed):
            Binary().validate_options(bytes=-10)

    def test_enum_works_with_list_of_strings(self):
        Enum().validate_options(values=['hello', 'there', 'red', 'blue'])

    def test_enum_breaks_if_list_has_repeating_elements(self):
        with self.assertRaises(InvalidOptionPassed):
            Enum().validate_options(values=['hello', 'there', 'red', 'blue', 'blue'])