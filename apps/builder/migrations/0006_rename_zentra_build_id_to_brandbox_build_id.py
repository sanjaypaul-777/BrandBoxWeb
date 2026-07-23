"""
apps/builder/migrations/0006_rename_zentra_build_id_to_brandbox_build_id.py — Django migration: 0006_rename_zentra_build_id_to_brandbox_build_id.
"""

# Rename BuildJob.zentra_build_id → brandbox_build_id (BrandBox rebrand)

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("builder", "0005_remove_winningproduct"),
    ]

    operations = [
        migrations.RenameField(
            model_name="buildjob",
            old_name="zentra_build_id",
            new_name="brandbox_build_id",
        ),
    ]
