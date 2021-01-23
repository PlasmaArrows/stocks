from django.db import models

# Create your models here.

class User(models.Model):
    name = models.CharField(max_length=50)
    money = models.DecimalField(max_digits=100, decimal_places=2)

    def __str__(self):
        return self.name

class Stocks(models.Model):
    ticker = models.CharField(max_length=4)
    owned_by = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.IntegerField(default = 0)

    def __str__(self):
        return self.ticker

