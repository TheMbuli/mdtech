from pathlib import Path
from tempfile import TemporaryDirectory

from django.core.exceptions import SuspiciousFileOperation
from django.core.management import call_command
from django.test import TestCase

from mdtech.storage_backends import clean_media_name, public_id_for_name
from .models import PhotoService, Service


class ServiceModelTests(TestCase):
    def test_relation_et_representations(self):
        service = Service.objects.create(
            nom="Architecture",
            description="Conception",
            pricing="Sur devis",
        )
        photo = PhotoService.objects.create(service=service, image="services/test.jpg")
        self.assertEqual(str(service), "Architecture")
        self.assertEqual(str(photo), "Photo du service Architecture")
        self.assertEqual(service.images.get(), photo)


class CloudinaryMediaMigrationTests(TestCase):
    def test_public_id_preserve_media_path_without_extension(self):
        self.assertEqual(
            public_id_for_name("services/facade.jpg", "mdtech"),
            "mdtech/services/facade",
        )

    def test_clean_media_name_rejects_traversal(self):
        with self.assertRaises(SuspiciousFileOperation):
            clean_media_name("../secret.jpg")

    def test_command_dry_run_without_cloudinary_credentials(self):
        with TemporaryDirectory() as tmpdir:
            manifest = Path(tmpdir) / "manifest.json"
            call_command("migrate_media_to_cloudinary", "--dry-run", f"--manifest={manifest}")
            self.assertTrue(manifest.exists())
