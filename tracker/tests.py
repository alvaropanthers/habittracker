from django.test import TestCase
from . import utils
from . import views
from . import models
from django.utils import timezone

class TemplateTestCase(TestCase):
    def test_template_create(self):
        template = views.Template('Reading', month=11, year=2020)
        self.assertEqual(template.habit.name, 'Reading')
        
        template2 = views.Template('Programming', month=11, year=2020)
        self.assertEqual(template2.habit.name, 'Programming')

    def test_template_addDay(self):
        template = views.Template('Reading', month=11, year=2020)
        template.addDay(11)
        template.addDay(12)
        template.addDay(13)
        self.assertEqual(template.days, [11, 12, 13])

    def test_template_removeDay(self):
        template = views.Template('Reading', month=11, year=2020)
        template.removeDay(12)
        template.removeDay(13)
        template.removeDay(14)
        self.assertEqual(template.rmDays, [12, 13, 14])

        template.addDay(11)
        self.assertEqual(template.days, [11])
        template.removeDay(11)
        self.assertEqual(template.days, [])
        self.assertEqual(template.rmDays, [12, 13, 14, 11])
        
    def test_template_update(self):
        template = views.Template('Reading', month=11, year=2020)
        self.assertTrue(template.update('2 hours reading'))
        self.assertEqual(template.habit.name, '2 hours reading')

    def test_template_save(self):
        item = models.Habit.objects.create(name='Reading')
        newD = models.CheckedDay.objects.create(habit=item, date=timezone.now().replace(month=11, day=20, year=2020))
        template = views.Template('Reading', month=11, year=2020)
        template.addDay(1)
        template.addDay(2)
        template.addDay(3)
        template.addDay(4)
        template.addDay(5)
        template.removeDay(20)
        self.assertEqual(template.save(), { 'id': 1, 'name': 'Reading', 'month': 11, 'year': 2020, 'days': [ 1, 2, 3, 4, 5 ] })
        self.assertTrue(template.delete())


class TemplatesTestCase(TestCase):
    def test_template_get(self):
        template = views.Templates()  
        habit = models.Habit.objects.create(name="Workout")
        self.assertEqual(template.get(habit.id, 4, 2020), {'id': 1, 'name': 'Workout', 'month': 4, 'year': 2020, 'days': []})
        
        cd = models.CheckedDay.objects.create(habit=habit, date=timezone.now().replace(month=4, day=5, year=2020))
        cd2 = models.CheckedDay.objects.create(habit=habit, date=timezone.now().replace(month=4, day=10, year=2020))
        self.assertEqual(template.get(habit.id, 4, 2020), {'id': 1, 'name': 'Workout', 'month': 4, 'year': 2020, 'days': [5, 10]})

        #Item doesn't exist
        self.assertEqual(template.get(10, 4, 2020), {})

        models.CheckedDay.objects.create(habit=habit, date=timezone.now().replace(month=11, day=5, year=2020))
        self.assertEqual(template.get(habit.id, month=11, year=2020), {'id': 1, 'name': 'Workout', 'month': 11, 'year': 2020, 'days': [5]})

        models.CheckedDay.objects.create(habit=habit, date=timezone.now().replace(month=11, day=5, year=2013))
        self.assertEqual(template.get(habit.id, month=11, year=2013), {'id': 1, 'name': 'Workout', 'month': 11, 'year': 2013, 'days': [5]})

        #Bad inputs
        self.assertEqual(template.get(habit.id, month='string', year=2013), {})

    def test_template_get_all(self):
        template = views.Templates()
        self.assertEqual(template.getAll(month=11, year=2020), {})

        habit = models.Habit.objects.create(name="Workout")
        self.assertEqual(template.getAll(month=11, year=2020), {0: {'id': 1, 'name': 'Workout', 'month': 11, 'year': 2020, 'days': []}})
        
        
        cd = models.CheckedDay.objects.create(habit=habit, date=timezone.now().replace(month=4, day=5, year=2020))
        cd2 = models.CheckedDay.objects.create(habit=habit, date=timezone.now().replace(month=4, day=10, year=2020))
        self.assertEqual(template.getAll(month=4, year=2020), {0: {'id': 1, 'name': 'Workout', 'month': 4, 'year': 2020, 'days': [5, 10]}})

        cd3 = models.CheckedDay.objects.create(habit=habit, date=timezone.now().replace(day=20, month=11, year=2020))
        self.assertEqual(template.getAll(month=11, year=2020), {0: {'id': 1, 'name': 'Workout', 'month': 11, 'year': 2020, 'days': [20]}})

        #Incorrect param
        self.assertEqual(template.getAll(month="test", year=2020), {})

        habit2 = models.Habit.objects.create(name="Reading")
        self.assertEqual(template.getAll(month=4, year=2020), {
            0: {'id': 1, 'name': 'Workout', 'month': 4, 'year': 2020, 'days': [5, 10]}, 
            1: {'id': 2, 'name': 'Reading', 'month': 4, 'year': 2020, 'days': []}
        })

        habit3 = models.Habit.objects.create(name="Programming")
        self.assertEqual(template.getAll(month=4, year=2020), {
            0: {'id': 1, 'name': 'Workout', 'month': 4, 'year': 2020, 'days': [5, 10]}, 
            1: {'id': 2, 'name': 'Reading', 'month': 4, 'year': 2020, 'days': []},
            2: {'id': 3, 'name': 'Programming', 'month': 4, 'year': 2020, 'days': []}
        })

        models.CheckedDay.objects.create(habit=habit3, date=timezone.now().replace(month=4, day=5, year=2020))
        self.assertEqual(template.getAll(month=4, year=2020), {
            0: {'id': 1, 'name': 'Workout', 'month': 4, 'year': 2020, 'days': [5, 10]}, 
            1: {'id': 2, 'name': 'Reading', 'month': 4, 'year': 2020, 'days': []},
            2: {'id': 3, 'name': 'Programming', 'month': 4, 'year': 2020, 'days': [5]}
        })

    def test_template_save_param(self):
        models.Habit.objects.create(name="Reading")  
        template = views.Templates()  
        self.assertTrue(template.add(habit_id=1, month=11, year=2020, days=[11, 12, '03', 14, 15]))
        self.assertTrue(template.add(habit_id='1', month='11', year='2020', days=[11, '12', 13, '14', 15]))
        self.assertFalse(template.add(habit_id='1', month='11', year='2020', days=[11, 'aaaaaa', 13, 14, 15]))
        self.assertFalse(template.add(habit_id='1', month='11', year='2020', days=[11, 50, 13, 14, 15]))
        self.assertFalse(template.add(habit_id='1', month='11', year='2020', days=[11, '', 13, 14, 15]))

    def test_template_save(self):
        models.Habit.objects.create(name="Reading")
        template = views.Templates()  
        self.assertEqual(template.add(habit_id=1, month=11, year=2020, days=['04', '01', 3]), {
            'id': 1,
            'name': 'Reading',
            'month': 11,
            'year': 2020,
            'days': [4, 1, 3]
        })

        self.assertEqual(template.add(habit_id=1, month=11, year=2020, days=[3, 5, 6]), {
            'id': 1,
            'name': 'Reading',
            'month': 11,
            'year': 2020,
            'days': [4, 1, 3, 5, 6]
        })

        self.assertEqual(template.add(habit_id=1, month=11, year=2020, days=[4, 1, 3, 5, 6]), {
            'id': 1,
            'name': 'Reading',
            'month': 11,
            'year': 2020,
            'days': [4, 1, 3, 5, 6]
        })

    def test_template_delete(self):
        models.Habit.objects.create(name="Reading")
        template = views.Templates()  
        self.assertEqual(template.add(habit_id=1, month=11, year=2020, days=['04', '01', 3]), {
            'id': 1,
            'name': 'Reading',
            'month': 11,
            'year': 2020,
            'days': [4, 1, 3]
        })

        self.assertEqual(template.delete(habit_id=1, month=11, year=2020, days=[3]), {
            'id': 1,
            'name': 'Reading',
            'month': 11,
            'year': 2020,
            'days': [4, 1]
        })

        self.assertEqual(template.delete(habit_id=1, month=11, year=2020, days=[4, 1]), {
            'id': 1,
            'name': 'Reading',
            'month': 11,
            'year': 2020,
            'days': []
        })

from django.test import Client
from . import status
class TemplateViewTestCase(TestCase):
    def test_post(self):
        c = Client()
        response = c.post('/api/template', data={'name': 'Working Out'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        time = timezone.now()
        self.assertEqual(response.content.decode(), '{"id": 1, "name": "Working Out", "month": 4, "year": 2020, "days": []}')

        response = c.post('/api/template', data={'name': 'Wo'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = c.post('/api/template', data={"name": "Working Out", 'days': (1, 2, 3, 4, 5, 6, 7, 8, 9, 10), 'month': 4, 'year': 2020})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content.decode(), '{"id": 1, "name": "Working Out", "month": "4", "year": "2020", "days": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}')


    def test_put(self):
        c = Client()
        response = c.post('/api/template', data={'name': 'Working Out'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = c.put('/api/template', data={'name': 'Working Out', 'newName': 'Workout'}, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content.decode(), '{"id": 1, "name": "Workout", "month": 4, "year": 2020, "days": []}')

    def test_delete(self):
        c = Client()
        response = c.post('/api/template', data={'name': 'Working Out'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = c.delete('/api/template', data={'name': 'Working Out'}, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


        response = c.post('/api/template', data={'name': 'Working Out'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = c.post('/api/template', data={"name": "Working Out", 'days': (1, 2, 3, 4, 5, 6, 7, 8, 9, 10), 'month': 4, 'year': 2020})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
 
        response = c.delete('/api/template', data={'name': 'Working Out', 'month': 4, 'year': 2020, 'days': (1, 2, 3, 4)}, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content.decode(), '{"id": 2, "name": "Working Out", "month": 4, "year": 2020, "days": [5, 6, 7, 8, 9, 10]}')


    def test_get(self):
        c = Client()
        response = c.post('/api/template', data={'name': 'reading'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = c.get('/api/template', data={'name': 'reading', 'month': 4, 'year': 2020})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content.decode(), '{"id": 1, "name": "reading", "month": "4", "year": "2020", "days": []}')

class TemplatesViewTestCase(TestCase):
    def test_get(self):
        c = Client()
        response = c.post('/api/template', data={'name': 'reading'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = c.get('/api/templates', data={'month': 4, 'year': 2020})
        self.assertEqual(response.status_code, status.HTTP_200_OK)