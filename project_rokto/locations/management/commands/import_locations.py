import csv
import io
import zipfile

import requests
from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand
from geopy.geocoders import ArcGIS

from project_rokto.locations.models import Location


class Command(BaseCommand):
    help = "Import Bangladesh post codes and geocode them using GeoNames and ArcGIS"

    CSV_URL = "https://gist.githubusercontent.com/msrumon/caa9fcfdda0b45ce4bed36e8be1451f4/raw/c5ad2a481b1f8121de328d94c8eda97cb566b765/bd_post_codes.csv"
    GEONAMES_URL = "http://download.geonames.org/export/zip/BD.zip"
    REQUEST_TIMEOUT = 30
    BULK_BATCH_SIZE = 1000
    GEONAMES_EXPECTED_COLS = 11

    def handle(self, *args, **options):
        self.sync_from_csv()
        gn_map = self.fetch_geonames_data()
        remaining = self.geocode_with_geonames(gn_map)

        if remaining:
            self.geocode_with_arcgis(remaining)

        self.stdout.write(self.style.SUCCESS("Geocoding process complete."))

    def sync_from_csv(self):
        self.stdout.write("Fetching CSV data from Gist...")
        try:
            response = requests.get(self.CSV_URL, timeout=self.REQUEST_TIMEOUT)
            response.raise_for_status()
        except requests.RequestException as e:
            self.stdout.write(self.style.ERROR(f"Failed to fetch CSV: {e}"))
            return

        lines = response.content.decode("utf-8").splitlines()
        reader = csv.DictReader(lines)

        self.stdout.write("Syncing locations from CSV...")
        existing_codes = set(
            Location.objects.values_list("post_code", "area_name").iterator(),
        )
        locations_to_create = []
        new_count = 0

        for row in reader:
            if (row["code"], row["name"]) not in existing_codes:
                location = Location(
                    post_code=row["code"],
                    area_name=row["name"],
                    station=row["station"],
                    district=row["district"],
                    division=row["division"],
                )
                locations_to_create.append(location)
                new_count += 1

            if len(locations_to_create) >= self.BULK_BATCH_SIZE:
                Location.objects.bulk_create(locations_to_create)
                locations_to_create = []

        if locations_to_create:
            Location.objects.bulk_create(locations_to_create)

        self.stdout.write(self.style.SUCCESS(f"Imported {new_count} new locations."))

    def fetch_geonames_data(self):
        self.stdout.write("Downloading GeoNames data for fast geocoding...")
        try:
            gn_response = requests.get(self.GEONAMES_URL, timeout=self.REQUEST_TIMEOUT)
            gn_response.raise_for_status()
        except requests.RequestException as e:
            self.stdout.write(self.style.WARNING(f"Failed to fetch GeoNames: {e}"))
            return {}

        gn_map = {}
        with (
            zipfile.ZipFile(io.BytesIO(gn_response.content)) as z,
            z.open("BD.txt") as f,
        ):
            for line in f:
                parts = line.decode("utf-8").split("\t")
                if len(parts) >= self.GEONAMES_EXPECTED_COLS:
                    post_code = parts[1]
                    lat = float(parts[9])
                    lon = float(parts[10])
                    gn_map[post_code] = (lat, lon)

        self.stdout.write(f"Loaded {len(gn_map)} post codes from GeoNames.")
        return gn_map

    def geocode_with_geonames(self, gn_map):
        locations_to_geocode = Location.objects.filter(point__isnull=True)
        total = locations_to_geocode.count()
        self.stdout.write(f"Found {total} locations to geocode.")

        gn_success_count = 0
        remaining_locations = []

        for loc in locations_to_geocode:
            if loc.post_code in gn_map:
                lat, lon = gn_map[loc.post_code]
                loc.point = Point(lon, lat)
                loc.save()
                gn_success_count += 1
            else:
                remaining_locations.append(loc)

        if gn_success_count > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Geocoded {gn_success_count} locations using GeoNames.",
                ),
            )
        return remaining_locations

    def geocode_with_arcgis(self, remaining_locations):
        total_remaining = len(remaining_locations)
        self.stdout.write(
            f"Geocoding remaining {total_remaining} locations using ArcGIS...",
        )
        geolocator = ArcGIS(user_agent="project_rokto")
        arcgis_count = 0

        for i, loc in enumerate(remaining_locations, 1):
            try:
                location = self._perform_arcgis_lookup(geolocator, loc)
                if location:
                    loc.point = Point(location.longitude, location.latitude)
                    loc.save()
                    arcgis_count += 1
                    self.stdout.write(f"[{i}/{total_remaining}] Geocoded: {loc}")
                else:
                    self.stdout.write(
                        self.style.WARNING(f"[{i}/{total_remaining}] Not found: {loc}"),
                    )
            except Exception as e:  # noqa: BLE001
                self.stdout.write(
                    self.style.ERROR(
                        f"[{i}/{total_remaining}] Error geocoding {loc}: {e}",
                    ),
                )

        self.stdout.write(
            self.style.SUCCESS(f"Geocoded {arcgis_count} locations using ArcGIS."),
        )

    def _perform_arcgis_lookup(self, geolocator, loc):
        # Strategy 1: Post Code + District
        query = f"{loc.post_code}, {loc.district}, Bangladesh"
        location = geolocator.geocode(query, timeout=10)

        if not location:
            # Strategy 2: Area Name + Station + District
            query = f"{loc.area_name}, {loc.station}, {loc.district}, Bangladesh"
            location = geolocator.geocode(query, timeout=10)

        return location
