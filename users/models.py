from django.db import models

# Create your models here.

class User(models.Model):
    name = models.CharField(max_length=50)
    money = models.DecimalField(max_digits=100, decimal_places=2)

    def __str__(self):
        return self.money

class Stocks(models.Model):
    ticker = models.CharField(max_length=4)
    boughtTime = models.DateTimeField()
    owned_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.ticker

