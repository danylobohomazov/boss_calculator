from django.db.models import Sum
from django.shortcuts import render
from django.views.generic import ListView, DetailView, UpdateView
from django.http import JsonResponse
from django.views import View
from decimal import Decimal
from django.db.models import F, Sum, FloatField
from main_app.models import Boss, Item
from main_app.price_found import find_item_price, start_driver, end_driver


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

    def make_price(self, element, divine_cost, driver):
        price = find_item_price(driver, element.name, element.type, divine_cost)
        if price:
            element.price = Decimal(price)
            print(price)
        else:
            element.price = Decimal("0")
        element.save()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        boss = self.object
        items = boss.items.all()
        passes = boss.passes.all()
        driver = start_driver()
        divine_cost = find_item_price(driver, "Divine Orb", "Currency")
        for pass_ in passes:
            self.make_price(pass_, divine_cost, driver)
        # обновляем цены для всех предметов
        for item in items:
            self.make_price(item, divine_cost, driver)
        end_driver(driver)
        context["divine"] = int(divine_cost)
        context["summa"] = boss.passes.aggregate(
            total=Sum(F("price") * F("count"), output_field=FloatField())
        )["total"]
        context["boss"] = boss
        return context