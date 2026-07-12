from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Formation", "0010_alter_formation_prix_etudiant_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="formation",
            name="inscriptions_ouvertes",
            field=models.BooleanField(
                default=True,
                help_text="Décochez cette option pour suspendre les nouvelles inscriptions.",
                verbose_name="Inscriptions ouvertes",
            ),
        ),
    ]
