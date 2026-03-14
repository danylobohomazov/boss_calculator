from django.db.models import Sum
from django.shortcuts import render
from django.views.generic import ListView, DetailView, UpdateView
from django.http import JsonResponse
from django.views import View
from decimal import Decimal

from main_app.models import Boss, Item
from main_app.price_found import find_item_price


def index(request):
    """View function for the home page of the site."""

    num_bosses = Boss.objects.all().count()
    bosses = Boss.objects.all()
    num_items = Item.objects.all().count()

    num_visits = request.session.get("num_visits", 0)
    request.session["num_visits"] = num_visits + 1

    context = {
        "num_bosses": num_bosses,
        "bosses": bosses,
        "num_items": num_items,
        "num_visits": num_visits + 1,
    }

    return render(request, "main_app/index.html", context=context)


class BossDetailView(DetailView):
    model = Boss
    context_object_name = "boss"

    def make_price(self, element):
        price = find_item_price(element.name, element.type)
        if price:
            element.price = Decimal(price["price"])
            print(price)
        else:
            element.price = Decimal("0")
        element.save()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        boss = self.object
        items = boss.items.all()
        passes = boss.passes.all()
        for pass_ in passes:
            self.make_price(pass_)
        # обновляем цены для всех предметов
        for item in items:
            self.make_price(item)
        divine_cost = find_item_price("Divine Orb", "Currency")
        context["divine"] = divine_cost["price"]
        context["summa"] = boss.passes.aggregate(Sum("price"))["price__sum"]
        context["boss"] = boss
        return context