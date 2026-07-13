"""
Run product scraper from CLI (same dual-write as admin).

Examples:
  python manage.py scrape_products -q skincare -c US -n 50
  python manage.py scrape_products --all-niches -n 500
  python manage.py scrape_products --sync-sheet
  python manage.py scrape_products --clean-dupes
  python manage.py scrape_products --purge-dead
  python manage.py scrape_products --clean-prices
"""

from django.core.management.base import BaseCommand

from apps.catalog.models import ScrapeRun
from apps.catalog.scraper.sheets_client import sheet_tab_default
from apps.catalog.services.pipeline import execute_scrape_run


class Command(BaseCommand):
    help = "Scrape Meta Ads → Shopify products → Google Sheet + Django DB"

    def add_arguments(self, parser):
        parser.add_argument("-q", "--query", default="fashion")
        parser.add_argument("-c", "--country", default="US")
        parser.add_argument("-n", "--rows", type=int, default=50)
        parser.add_argument("--per-store", type=int, default=10)
        parser.add_argument("--sheet", default="")
        parser.add_argument("--all-niches", action="store_true")
        parser.add_argument("--sync-sheet", action="store_true", help="Sheet → Django DB only")
        parser.add_argument("--clean-dupes", action="store_true")
        parser.add_argument(
            "--fill-ids",
            action="store_true",
            help="Add/fill stable id column on Sheet (zp_*) then sync DB",
        )
        parser.add_argument(
            "--purge-dead",
            action="store_true",
            help="Delete vault products whose source page or images return 404",
        )
        parser.add_argument(
            "--clean-prices",
            action="store_true",
            help="Rewrite Sheet Price/Compare Price to USD dollars (12000→120.00)",
        )

    def handle(self, *args, **options):
        if options["clean_prices"]:
            mode = ScrapeRun.Mode.CLEAN_PRICES
        elif options["purge_dead"]:
            mode = ScrapeRun.Mode.PURGE_DEAD
        elif options["fill_ids"]:
            mode = ScrapeRun.Mode.FILL_IDS
        elif options["sync_sheet"]:
            mode = ScrapeRun.Mode.SYNC_SHEET
        elif options["clean_dupes"]:
            mode = ScrapeRun.Mode.CLEAN_DUPES
        elif options["all_niches"]:
            mode = ScrapeRun.Mode.ALL_NICHES
        else:
            mode = ScrapeRun.Mode.SINGLE

        run = ScrapeRun.objects.create(
            mode=mode,
            query=options["query"],
            country=options["country"],
            target_rows=options["rows"],
            products_per_store=options["per_store"],
            sheet_tab=options["sheet"] or sheet_tab_default(),
        )
        self.stdout.write(f"Starting scrape run #{run.pk} ({mode})…")
        execute_scrape_run(run.pk)
        run.refresh_from_db()
        if run.status == ScrapeRun.Status.SUCCESS:
            self.stdout.write(self.style.SUCCESS(f"OK — rows={run.rows_written}"))
        else:
            self.stderr.write(self.style.ERROR(f"FAILED: {run.error[:500]}"))
