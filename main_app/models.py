from django.db import models

TYPE_CHOICES = (
    ("Guaranteed unique", "Guaranteed unique"),
    ("Additional item", "Additional item"),
)


class Boss(models.Model):
    name = models.CharField(max_length=100)


class Item(models.Model):
    name = models.CharField(max_length=100)
    chance = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    boss = models.ForeignKey(Boss, on_delete=models.CASCADE, related_name="items")
    category = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    img = models.TextField(default="")

class Pass(models.Model):
    boss = models.ForeignKey(Boss, on_delete=models.CASCADE, related_name="passes")
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    count = models.IntegerField()
    type = models.CharField(max_length=100)
    img = models.TextField(default="")
