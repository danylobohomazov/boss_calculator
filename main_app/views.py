from django.shortcuts import render

from main_app.models import Boss, Item


def index(request):
    """View function for the home page of the site."""

    num_bosses = Boss.objects.all().count()
    num_items = Item.objects.all().count()

    num_visits = request.session.get("num_visits", 0)
    request.session["num_visits"] = num_visits + 1

    context = {
        "num_bosses": num_bosses,
        "num_items": num_items,
        "num_visits": num_visits + 1,
    }

    return render(request, "main_app/index.html", context=context)

