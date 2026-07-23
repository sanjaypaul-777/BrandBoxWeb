"""
apps/builder/migrations/0005_remove_winningproduct.py — Django migration: 0005_remove_winningproduct.
"""

# Drop dummy WinningProduct table (UI samples removed)

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("builder", "0004_buildjob_zentra_build_id"),
    ]

    operations = [
        migrations.DeleteModel(name="WinningProduct"),
    ]
