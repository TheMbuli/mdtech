from django.db import migrations, models


def creer_configuration_par_defaut(apps, schema_editor):
    configuration = apps.get_model("Workspace", "ConfigurationWorkspace")
    configuration.objects.get_or_create(pk=1)


class Migration(migrations.Migration):
    dependencies = [
        ("Workspace", "0002_reservationworkspace_workspace_fin_apres_debut"),
    ]

    operations = [
        migrations.CreateModel(
            name="ConfigurationWorkspace",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "reservations_ouvertes",
                    models.BooleanField(
                        default=True,
                        help_text="Décochez cette option pour suspendre les nouvelles réservations.",
                        verbose_name="Réservations ouvertes",
                    ),
                ),
            ],
            options={
                "verbose_name": "Configuration des réservations",
                "verbose_name_plural": "Configuration des réservations",
            },
        ),
        migrations.RunPython(creer_configuration_par_defaut, migrations.RunPython.noop),
    ]
