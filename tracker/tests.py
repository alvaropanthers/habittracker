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

from . import views
from . import models
from django.utils import timezone
class ViewTestClases(TestCase):
    def test_create_template(self):
        habit = models.Habit.objects.create(name="Workout")
        self.assertEqual(views.create_template(habit, {}),  {'id': 1, 'name': 'Workout', 'checkeddays': {}})

        cd = models.CheckedDay.objects.create(habit=habit, date=timezone.now().replace(month=4, day=5, year=2020))
        cd2 = models.CheckedDay.objects.create(habit=habit, date=timezone.now().replace(month=4, day=10, year=2020))
        self.assertEqual(views.create_template(habit, habit.checkedday_set.all()),  {
            'id': 1, 'name': 'Workout', 'checkeddays': {0: {'04-05-2020'}, 1: {'04-10-2020'}}
            })

    def test_get_all_templates(self):

        self.assertEqual(views.get_all_templates(), {})

        habit = models.Habit.objects.create(name="Workout")
        self.assertEqual(views.get_all_templates(), {0: {'id': 1, 'name': 'Workout', 'checkeddays': {}}})
        
        
        cd = models.CheckedDay.objects.create(habit=habit, date=timezone.now().replace(month=4, day=5, year=2020))
        cd2 = models.CheckedDay.objects.create(habit=habit, date=timezone.now().replace(month=4, day=10, year=2020))
        self.assertEqual(views.get_all_templates(), {0: {'id': 1, 'name': 'Workout', 'checkeddays': {0: {'04-05-2020'}, 1: {'04-10-2020'}}}})

        cd3 = models.CheckedDay.objects.create(habit=habit, date=timezone.now().replace(day=20, month=11, year=2020))
        self.assertEqual(views.get_all_templates(month=11), {0: {'id': 1, 'name': 'Workout', 'checkeddays': {0: {'11-20-2020'}}}})

        cd3 = models.CheckedDay.objects.create(habit=habit, date=timezone.now().replace(day=20, month=11, year=2013))
        self.assertEqual(views.get_all_templates(month=11, year=2013), {0: {'id': 1, 'name': 'Workout', 'checkeddays': {0: {'11-20-2013'}}}})

        self.assertEqual(views.get_all_templates(month="test"), {})

        habit2 = models.Habit.objects.create(name="Reading")
        self.assertEqual(views.get_all_templates(), {
            0: {'id': 1, 'name': 'Workout', 'checkeddays': {0: {'04-05-2020'}, 1: {'04-10-2020'}}}, 
            1: {'id': 2, 'name': 'Reading', 'checkeddays': {}}
            })

        habit3 = models.Habit.objects.create(name="Programming")
        self.assertEqual(views.get_all_templates(), {
            0: {'id': 1, 'name': 'Workout', 'checkeddays': {0: {'04-05-2020'}, 1: {'04-10-2020'}}}, 
            1: {'id': 2, 'name': 'Reading', 'checkeddays': {}},
            2: {'id': 3, 'name': 'Programming', 'checkeddays': {}}
            })

        models.CheckedDay.objects.create(habit=habit3, date=timezone.now().replace(month=4, day=5, year=2020))
        self.assertEqual(views.get_all_templates(), {
            0: {'id': 1, 'name': 'Workout', 'checkeddays': {0: {'04-05-2020'}, 1: {'04-10-2020'}}}, 
            1: {'id': 2, 'name': 'Reading', 'checkeddays': {}},
            2: {'id': 3, 'name': 'Programming', 'checkeddays': {0: {'04-05-2020'}}}
            })

    def test_get_template(self):
        habit = models.Habit.objects.create(name="Workout")
        self.assertEqual(views.get_template(habit.id), {'id': 1, 'name': 'Workout', 'checkeddays': {}})
        
        cd = models.CheckedDay.objects.create(habit=habit, date=timezone.now().replace(month=4, day=5, year=2020))
        cd2 = models.CheckedDay.objects.create(habit=habit, date=timezone.now().replace(month=4, day=10, year=2020))
        self.assertEqual(views.get_template(habit.id), {'id': 1, 'name': 'Workout', 'checkeddays': {0: {'04-05-2020'}, 1: {'04-10-2020'}}})

        self.assertEqual(views.get_template(10), {})

        models.CheckedDay.objects.create(habit=habit, date=timezone.now().replace(month=11, day=5, year=2020))
        self.assertEqual(views.get_template(habit.id, month=11), {'id': 1, 'name': 'Workout', 'checkeddays': {0: {'11-05-2020'}}})

        models.CheckedDay.objects.create(habit=habit, date=timezone.now().replace(month=11, day=5, year=2013))
        self.assertEqual(views.get_template(habit.id, month=11, year=2013), {'id': 1, 'name': 'Workout', 'checkeddays': {0: {'11-05-2013'}}})

        self.assertEqual(views.get_template(habit.id, month='string', year=2013), {})

    #SHOULD RETURN THE CREATED OBJECT
    def test_save_template(self):
        self.assertFalse(views.save_template(1, [1, 2, 3]))
        
        habit = models.Habit.objects.create(name="Workout")
        self.assertEqual(views.save_template(habit_id=1, dates=['04-20-2020', '04-11-2020', '04-15-2020', '04-01-2020', '04-02-2020']), {
            'id': 1,
            'name': 'Workout',
            'checkeddays': {0: {'04-20-2020'}, 1: {'04-11-2020'}, 2: {'04-15-2020'}, 3: {'04-01-2020'}, 4: {'04-02-2020'}}
        })

        self.assertFalse(views.save_template(habit_id=10, dates=['04-20-2020', '04-11-2020', '04-15-2020', '04-01-2020', '04-02-2020']))
        self.assertFalse(views.save_template(habit_id=1, dates=['04-20-20', '04-11-2020', '04-15-2020', '04-01-2020', '04-02-2020']))

        habit = models.Habit.objects.create(name="Reading")
        self.assertEqual(views.save_template(habit_id=2, dates=['04-20-2013']), {
            'id': 2,
            'name': 'Reading',
            'checkeddays': {0: {'04-20-2013'}}
        })

        

