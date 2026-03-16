from django.shortcuts import render, redirect
from django.views.generic import DetailView
from decimal import Decimal
from django.db.models import F, Sum, FloatField, Q
from main_app.models import Boss, Item
from main_app.price_found import start_driver, end_driver, new_logic, better_finder, trade_finder, CACHE, cache_clear


def index(request):
    """View function for the home page of the site."""
    if not CACHE:
        load_data_to_cache()
    num_bosses = Boss.objects.all().count()
    calculate()
    bosses = Boss.objects.annotate(total=F("profit_per_run") * F("runs_per_our")).order_by("-total")
    num_items = Item.objects.all().count()
    num_visits = request.session.get("num_visits", 0)
    request.session["num_visits"] = num_visits + 1
    context = {
        "num_bosses": num_bosses,
        "bosses": bosses,
        "num_items": num_items,
    }
    return render(request, "main_app/index.html", context=context)


def calculate():
    for boss in Boss.objects.all():
        passes = boss.passes.all()
        items = boss.items.all()
        divine_cost = better_finder()

        # items search in poe ninja (CACHE)
        for pass_ in passes:
            make_price(pass_, divine_cost, "ninja")
        for item in items:
            make_price(item, divine_cost, "ninja")
        guaranteed_unique = boss.items.filter(category="GuaranteedUnique")
        additional_items = boss.items.filter(category="Additionaldrops")
        guaranteed_unique_income = sum(
            float(item.chance) * float(item.price) for item in guaranteed_unique
        ) / 100
        # print(f"GU = {guaranteed_unique_income}")
        additional_items_income = sum(
            float(item.chance) * float(item.price) for item in additional_items
        ) / 100
        # print(f"AI = {additional_items_income}")
        lost = boss.passes.aggregate(
            total=Sum(F("price") * F("count"), output_field=FloatField())
        )["total"]
        # print(f"Lost = {lost}")
        divine_cost = better_finder()
        profit_per_run = round(guaranteed_unique_income + additional_items_income - lost, 2)
        profit_per_run = Decimal(str(profit_per_run / divine_cost))
        boss.profit_per_run = profit_per_run.quantize(Decimal("0.00"))
        boss.save()


def reload_data(request):
    cache_clear()
    load_data_to_cache()
    return redirect("main_app:index")


def load_data_to_cache():
    print("Loading...")
    driver = start_driver()
    new_logic(driver)
    end_driver(driver)
    print("Done!")


def make_price(element, divine_cost, site):
    if site == "ninja":
        price = better_finder(element.name, element.type, divine_cost)
    else:
        price = trade_finder(element.name, divine_cost)
    if price:
        element.price = Decimal(price)
    else:
        element.price = Decimal("0")
    element.save()


class BossDetailView(DetailView):
    model = Boss
    context_object_name = "boss"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        boss = self.object
        divine_cost = better_finder()


        context["divine"] = int(divine_cost)
        context["summa"] = boss.passes.aggregate(
            total=Sum(F("price") * F("count"), output_field=FloatField())
        )["total"]
        context["boss"] = boss
        return context
