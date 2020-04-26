from django.test import TestCase
from . import utils

class UtilTestCases(TestCase):
    def test_break_formatted_date(self):
        self.assertEqual(utils.break_formatted_date('11-20-2001'), [11, 20, 2001])
        self.assertEqual(utils.break_formatted_date('01-01-2001'), [1, 1, 2001])
        self.assertEqual(utils.break_formatted_date('1-1-2001-20'), [])

    def test_format_date(self):
        self.assertEqual(utils.format_date(11, 20, 1995), '11-20-1995')
        self.assertEqual(utils.format_date(1, 20, 1995), '01-20-1995')
        with self.assertRaises(ValueError):
            utils.format_date(1, 20, 19)

        self.assertEqual(utils.format_date(0, 20, 2020), '01-20-2020')
        self.assertEqual(utils.format_date(0, 0, 2020), '01-01-2020')

    def test_is_month(self):
        for index in range(1, 13):
            self.assertTrue(utils.is_month(index))

        self.assertTrue(utils.is_month('11'))
        self.assertTrue(utils.is_month('1'))
        self.assertTrue(utils.is_month('01'))
        self.assertTrue(utils.is_month('000001'))
        self.assertFalse(utils.is_month('100'))
        self.assertFalse(utils.is_month('0'))
        self.assertFalse(utils.is_month('13'))
        self.assertFalse(utils.is_month('string'))

    def test_is_day(self):
        for index in range(1, 32):
            self.assertTrue(utils.is_day(index))

        self.assertTrue(utils.is_day('11'))
        self.assertTrue(utils.is_day('1'))
        self.assertTrue(utils.is_day('01'))
        self.assertTrue(utils.is_day('000001'))
        self.assertFalse(utils.is_day('100'))
        self.assertFalse(utils.is_day('0'))
        self.assertFalse(utils.is_day('32'))
        self.assertFalse(utils.is_day('string'))

    def test_is_year(self):
        for index in range(2000, 2021):
            self.assertTrue(utils.is_year(index))
        
        self.assertTrue(utils.is_year('2000'))
        self.assertTrue(utils.is_year('0002000'))
        self.assertFalse(utils.is_year('200'))
        self.assertFalse(utils.is_year('0200'))
        self.assertFalse(utils.is_year('string'))
        self.assertFalse(utils.is_year('1995'))

    def test_is_date(self):
        self.assertTrue(utils.is_date('11-20-2020'))
        self.assertFalse(utils.is_date('11-20-1995'))
        self.assertFalse(utils.is_date('11-20-1995-10-100'))
        self.assertTrue(utils.is_date('01-20-2020'))
        self.assertTrue(utils.is_date('01-09-2020'))

        for index in range(1, 13):
            self.assertTrue(utils.is_date(f'{index}-{index}-2020'))