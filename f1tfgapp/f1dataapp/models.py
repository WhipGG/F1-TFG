from django.db import models

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
    photoUrl = models.CharField(max_length=1000, null=True)

    def __str__(self) -> str:
        return self.name


class Constructor(models.Model):
    constructorId = models.IntegerField(unique=True, primary_key=True)
    constructorRef = models.CharField(max_length=100,unique=True)
    name = models.CharField(max_length=200,unique=True)
    nationality = models.CharField(max_length=100)
    url = models.CharField(max_length=1000)
    logoUrl = models.CharField(max_length=1000, null=True)
    
    def __str__(self) -> str:
        return self.name


class Circuit(models.Model):
    circuitId = models.IntegerField(unique=True, primary_key=True)
    circuitRef = models.CharField(max_length=100,unique=True)
    name = models.CharField(max_length=300,unique=True)
    location = models.CharField(max_length=200)
    country = models.CharField(max_length=200)
    url = models.CharField(max_length=1000)
    layoutUrl = models.CharField(max_length=1000, null=True)
    
    def __str__(self) -> str:
        return self.name


class Grid(models.Model):
    driver = models.ForeignKey("Driver", on_delete=models.CASCADE)
    constructor = models.ForeignKey("Constructor", on_delete=models.CASCADE)
    