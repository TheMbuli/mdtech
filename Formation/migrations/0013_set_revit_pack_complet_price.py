from decimal import Decimal

from django.db import migrations


def set_revit_pack_complet_price(apps, schema_editor):
    Formation = apps.get_model("Formation", "Formation")
    Formation.objects.filter(slug="revitpc").update(prix_pro=Decimal("350.00"))


def restore_revit_pack_complet_price(apps, schema_editor):
    Formation = apps.get_model("Formation", "Formation")
    Formation.objects.filter(slug="revitpc").update(prix_pro=Decimal("450.00"))


class Migration(migrations.Migration):
    dependencies = [
        ("Formation", "0012_set_revit_price"),
    ]

    operations = [
        migrations.RunPython(
            set_revit_pack_complet_price,
            restore_revit_pack_complet_price,
        ),
    ]
