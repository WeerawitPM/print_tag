# Generated by Django 5.0.4 on 2024-07-23 02:15

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("print_tag_app", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Packing",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("part_no", models.CharField(max_length=255, unique=True)),
                ("std_packing", models.IntegerField(blank=True, default=0, null=True)),
            ],
        ),
    ]
