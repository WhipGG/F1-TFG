from django.db import models
from django.utils.html import mark_safe

# Create your models here.

class Driver(models.Model):
    driverId = models.IntegerField(unique=True, primary_key=True)
    driverRef = models.CharField(max_length=100, unique=True)
    number = models.IntegerField(null=True)
    code = models.CharField(max_length=3, null=True)
    forename = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    dob = models.DateField()
    nationality = models.CharField(max_length=100)
    url = models.CharField(max_length=1000)
    name = models.CharField(max_length=200,unique=True)
    photo = models.ImageField(upload_to='driver_images', null=True)
    is_recent = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.name
    
    def img_preview(self):
        return mark_safe(f'<img src="{self.photo.url}" width="300"/>')


class Constructor(models.Model):
    constructorId = models.IntegerField(unique=True, primary_key=True)
    constructorRef = models.CharField(max_length=100,unique=True)
    name = models.CharField(max_length=200,unique=True)
    nationality = models.CharField(max_length=100)
    url = models.CharField(max_length=1000)
    logo = models.ImageField(upload_to='team_logos', null=True)
    
    def __str__(self) -> str:
        return self.name
    
    def img_preview(self):
        return mark_safe(f'<img src="{self.logo.url}" width="300"/>')


class Circuit(models.Model):
    circuitId = models.IntegerField(unique=True, primary_key=True)
    circuitRef = models.CharField(max_length=100,unique=True)
    name = models.CharField(max_length=300,unique=True)
    location = models.CharField(max_length=200)
    country = models.CharField(max_length=200)
    url = models.CharField(max_length=1000)
    layout = models.ImageField(upload_to='circuit_layouts', null=True)
    is_recent = models.BooleanField(default=False)
    
    def __str__(self) -> str:
        return self.name
    
    def img_preview(self):
        return mark_safe(f'<img src="{self.layout.url}" width="600"/>')


class Grid(models.Model):
    driver = models.ForeignKey("Driver", on_delete=models.CASCADE)
    constructor = models.ForeignKey("Constructor", on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.driver.name + ' - ' +  self.constructor.name
    
    def driver_photo(self):
        return mark_safe(f'<img src="{self.driver.photo.url}" height="75"/>')
    
    def constructor_photo(self):
        return mark_safe(f'<img src="{self.constructor.logo.url}" height="75"/>')
    