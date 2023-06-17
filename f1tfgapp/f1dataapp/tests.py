from django.test import TestCase
from .models import Driver, Constructor, Circuit, Grid
from .populateDB import populate_drivers, populate_constructors, populate_circuits

# Create your tests here.
class DatabaseModelTests(TestCase):
    #populate_drivers()
    #populate_constructors()
    #populate_circuits()
    
    def test_grid_correct_objects(self):
        self.assertIs(len(Grid.objects.all())==20, True)
        print(len(Grid.objects.all()))

    def test_drivers_database_not_too_may(self):
        self.assertIs(len(Driver.objects.all())<=870, True)
    
    def test_drivers_database_not_too_few(self):
        self.assertIs(len(Driver.objects.all())>=840, True)

    def test_constructos_database_not_too_may(self):
        self.assertIs(len(Constructor.objects.all())<=220, True)
    
    def test_constructos_database_not_too_few(self):
        self.assertIs(len(Constructor.objects.all())>=200, True)

    def test_circuits_database_not_too_may(self):
        self.assertIs(len(Circuit.objects.all())<=85, True)
    
    def test_circuits_database_not_too_few(self):
        self.assertIs(len(Circuit.objects.all())>=70, True)