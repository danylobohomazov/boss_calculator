from django.db import models

TYPE_CHOICES = (
    ("Guaranteed unique", "Guaranteed unique"),
    ("Additional item", "Additional item"),
)


class Boss(models.Model):
    name = models.CharField(max_length=100)


class Item(models.Model):
    name = models.CharField(max_length=100)
    chance = models.FloatField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    boss = models.ForeignKey(Boss, on_delete=models.CASCADE, related_name="items")
    type = models.CharField(choices=TYPE_CHOICES, max_length=100)
