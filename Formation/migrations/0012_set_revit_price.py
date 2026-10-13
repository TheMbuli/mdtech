from decimal import Decimal

from django.db import migrations


def set_revit_price(apps, schema_editor):
    Formation = apps.get_model("Formation", "Formation")
    Formation.objects.filter(slug="revit").update(prix_pro=Decimal("200.00"))


def restore_revit_price(apps, schema_editor):
    Formation = apps.get_model("Formation", "Formation")
    Formation.objects.filter(slug="revit").update(prix_pro=Decimal("300.00"))


class Migration(migrations.Migration):
    dependencies = [
        ("Formation", "0011_formation_inscriptions_ouvertes"),
    ]

    operations = [
        migrations.RunPython(set_revit_price, restore_revit_price),
    ]
