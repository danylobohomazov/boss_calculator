import dataclasses
import json
from django.core.management.base import BaseCommand
from main_app.models import Boss, Item, Pass


class Command(BaseCommand):
    help = "Import data from JSON"

    def add_arguments(self, parser):
        parser.add_argument("file", type=str)

    def handle(self, *args, **kwargs):
        with open(kwargs["file"], "r", encoding="utf-8") as f:
            data = json.load(f)

        items = []
        passes = []
        for bosses in data.values():
            for boss in bosses:
                for name, value in boss.items():
                    for key, value_ in value.items():
                        if key == "normal":
                            boss_name = name
                        else:
                            boss_name = "Uber " + name
                        boss = Boss.objects.create(name=boss_name)
                        for type_, value_list in value_.items():
                            for item in value_list:
                                if type_ == "passes":
                                    passes.append(
                                        Pass(
                                            name=item["name"],
                                            boss=boss,
                                            price=0,
                                            count=item["count"],
                                            type=item["type"],
                                        )
                                    )
                                else:
                                    items.append(
                                        Item(
                                            name=item["name"],
                                            chance=item["chance"],
                                            boss=boss,
                                            price=0,
                                            category=item["category"],
                                            type=item["type"],
                                        )
                                    )

        Item.objects.bulk_create(items)
        Pass.objects.bulk_create(passes)

        self.stdout.write(self.style.SUCCESS("Data imported"))


@dataclasses.dataclass
class TestItem:
    name: str
    chance: int
    boss: str
    type: str


if __name__ == "__main__":
    items = []
    with open("../../../data.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    for item in data.values():
        for boss in item:
            for name, value in boss.items():
                for key, value_ in value.items():
                    for end in value_:
                        if key == "normal":
                            new_item = TestItem(
                                name=end["name"],
                                chance=end["chance"],
                                boss=name,
                                type=end["category"]
                            )
                        else:
                            new_item = TestItem(
                                name=end["name"],
                                chance=end["chance"],
                                boss="Uber " + name,
                                type=end["category"]
                            )
                        items.append(new_item)
    for item in items:
        print(item)
