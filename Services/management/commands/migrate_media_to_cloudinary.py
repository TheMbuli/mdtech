from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath

from django.apps import apps
from django.conf import settings
from django.core.exceptions import SuspiciousFileOperation
from django.core.management.base import BaseCommand, CommandError
from django.db import models, transaction

from mdtech.storage_backends import (
    clean_media_name,
    cloudinary_error_is_not_found,
    configure_cloudinary,
    public_id_for_name,
)


@dataclass(frozen=True)
class MediaReference:
    relative_path: str
    model_label: str = ""
    field_name: str = ""
    object_pk: str = ""
    old_value: str = ""
    orphan: bool = False


def now_iso() -> str:
    return datetime.now(UTC).isoformat()


def file_checksum(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_public_id(relative_path: str, prefix: str, *, orphan: bool = False) -> str:
    cleaned = clean_media_name(relative_path)
    if orphan:
        cleaned = f"orphans/{cleaned}"
    return public_id_for_name(cleaned, prefix)


class Command(BaseCommand):
    help = "Migre les médias locaux vers Cloudinary de manière idempotente."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Analyse sans upload ni modification.")
        parser.add_argument("--verify", action="store_true", help="Vérifie les entrées SUCCESS du manifeste.")
        parser.add_argument("--include-orphans", action="store_true", help="Inclut les fichiers non référencés.")
        parser.add_argument("--prefix", default=getattr(settings, "CLOUDINARY_FOLDER", "mdtech"))
        parser.add_argument("--manifest", default="backups/cloudinary-media-manifest.json")
        parser.add_argument("--resume", action="store_true", help="Réutilise les entrées SUCCESS du manifeste.")
        parser.add_argument("--fail-fast", action="store_true", help="Arrête au premier échec.")
        parser.add_argument("--timeout", type=int, default=120, help="Timeout réseau Cloudinary en secondes.")

    def handle(self, *args, **options):
        prefix = clean_media_name(options["prefix"]).strip("/")
        manifest_path = Path(options["manifest"])
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest = self.load_manifest(manifest_path)

        references = self.collect_references()
        media_root = Path(settings.MEDIA_ROOT)
        media_files = sorted(path for path in media_root.rglob("*") if path.is_file()) if media_root.exists() else []
        local_paths = {path.relative_to(media_root).as_posix() for path in media_files}
        referenced_paths = {reference.relative_path for reference in references}
        orphans = [
            MediaReference(relative_path=path, old_value=path, orphan=True)
            for path in sorted(local_paths - referenced_paths)
        ]

        if options["verify"]:
            self.verify_manifest(manifest, prefix)
            return

        selected = list(references)
        if options["include_orphans"]:
            selected.extend(orphans)

        self.stdout.write(f"MEDIA_ROOT: {media_root}")
        self.stdout.write(f"Fichiers locaux: {len(local_paths)}")
        self.stdout.write(f"Références base: {len(references)}")
        self.stdout.write(f"Orphelins: {len(orphans)}")
        self.stdout.write(f"Mode dry-run: {'oui' if options['dry_run'] else 'non'}")

        uploader = None
        if not options["dry_run"]:
            uploader = self.get_uploader(options["timeout"])

        entries = []
        seen_uploads = {}
        failed = 0

        for reference in selected:
            try:
                entry = self.process_reference(
                    reference=reference,
                    media_root=media_root,
                    local_paths=local_paths,
                    prefix=prefix,
                    dry_run=options["dry_run"],
                    resume=options["resume"],
                    manifest=manifest,
                    uploader=uploader,
                    seen_uploads=seen_uploads,
                )
            except Exception as exc:
                failed += 1
                entry = self.entry_for(reference, prefix, "FAILED", str(exc))
                if options["fail_fast"]:
                    entries.append(entry)
                    self.write_manifest(manifest_path, manifest + entries)
                    raise

            entries.append(entry)
            self.stdout.write(f"{entry['status']} {reference.relative_path} {entry.get('message', '')}".strip())
            self.stdout.flush()
            self.write_manifest(manifest_path, manifest + entries)

        self.write_manifest(manifest_path, manifest + entries)
        counts = {}
        for entry in entries:
            counts[entry["status"]] = counts.get(entry["status"], 0) + 1
        self.stdout.write(self.style.SUCCESS(f"Terminé. Résumé: {counts}. Manifeste: {manifest_path}"))
        if failed:
            raise CommandError(f"{failed} média(s) en échec.")

    def collect_references(self) -> list[MediaReference]:
        references = []
        for model in apps.get_models():
            fields = [
                field
                for field in model._meta.get_fields()
                if isinstance(field, (models.ImageField, models.FileField))
            ]
            if not fields:
                continue
            for obj in model.objects.all():
                for field in fields:
                    media_file = getattr(obj, field.name)
                    value = getattr(media_file, "name", "") or ""
                    if not value:
                        continue
                    if value.startswith(("http://", "https://")):
                        references.append(
                            MediaReference(
                                relative_path=value,
                                model_label=model._meta.label,
                                field_name=field.name,
                                object_pk=str(obj.pk),
                                old_value=value,
                            )
                        )
                        continue
                    references.append(
                        MediaReference(
                            relative_path=clean_media_name(value),
                            model_label=model._meta.label,
                            field_name=field.name,
                            object_pk=str(obj.pk),
                            old_value=value,
                        )
                    )
        return references

    def process_reference(
        self,
        *,
        reference: MediaReference,
        media_root: Path,
        local_paths: set[str],
        prefix: str,
        dry_run: bool,
        resume: bool,
        manifest: list[dict],
        uploader,
        seen_uploads: dict[str, dict],
    ) -> dict:
        if reference.relative_path.startswith(("http://", "https://")):
            return self.entry_for(reference, prefix, "SKIPPED", "Déjà distant.")

        if reference.relative_path not in local_paths:
            return self.entry_for(reference, prefix, "MISSING", "Fichier local introuvable.")

        local_path = media_root / reference.relative_path
        checksum = file_checksum(local_path)
        public_id = safe_public_id(reference.relative_path, prefix, orphan=reference.orphan)
        manifest_hit = self.find_manifest_success(manifest, reference.relative_path, checksum, public_id)
        if resume and manifest_hit:
            return self.entry_for(
                reference,
                prefix,
                "SKIPPED",
                "Déjà présent dans le manifeste.",
                local_path=local_path,
                checksum=checksum,
                cloudinary=manifest_hit,
            )

        if public_id in seen_uploads:
            return self.entry_for(
                reference,
                prefix,
                "SKIPPED",
                "Public ID déjà traité dans cette exécution.",
                local_path=local_path,
                checksum=checksum,
                cloudinary=seen_uploads[public_id],
            )

        if dry_run:
            return self.entry_for(
                reference,
                prefix,
                "ORPHAN" if reference.orphan else "SKIPPED",
                "Simulation uniquement.",
                local_path=local_path,
                checksum=checksum,
            )

        remote_resource = self.remote_resource(public_id)
        if remote_resource:
            seen_uploads[public_id] = remote_resource
            return self.entry_for(
                reference,
                prefix,
                "SUCCESS",
                "Déjà présent sur Cloudinary.",
                local_path=local_path,
                checksum=checksum,
                cloudinary=remote_resource,
            )

        result = uploader(local_path, public_id)
        seen_uploads[public_id] = result
        if reference.model_label and reference.field_name and result.get("public_id"):
            self.update_field_if_needed(reference)
        return self.entry_for(
            reference,
            prefix,
            "SUCCESS",
            "Upload confirmé.",
            local_path=local_path,
            checksum=checksum,
            cloudinary=result,
        )

    def update_field_if_needed(self, reference: MediaReference):
        # Les chemins sont volontairement préservés. Cette transaction protège
        # les futures évolutions où une normalisation locale serait nécessaire.
        model = apps.get_model(reference.model_label)
        with transaction.atomic():
            obj = model.objects.select_for_update().get(pk=reference.object_pk)
            current = getattr(getattr(obj, reference.field_name), "name", "") or ""
            if current != reference.old_value:
                return
            if current != reference.relative_path:
                setattr(obj, reference.field_name, reference.relative_path)
                obj.save(update_fields=[reference.field_name])

    def entry_for(
        self,
        reference: MediaReference,
        prefix: str,
        status: str,
        message: str,
        *,
        local_path: Path | None = None,
        checksum: str = "",
        cloudinary: dict | None = None,
    ) -> dict:
        cloudinary = cloudinary or {}
        public_id = ""
        try:
            public_id = safe_public_id(reference.relative_path, prefix, orphan=reference.orphan)
        except SuspiciousFileOperation:
            pass
        return {
            "chemin_local": str(local_path) if local_path else "",
            "chemin_relatif": reference.relative_path,
            "modele": reference.model_label,
            "champ": reference.field_name,
            "identifiant_objet": reference.object_pk,
            "ancienne_valeur": reference.old_value,
            "nouvelle_valeur": reference.old_value,
            "public_id": cloudinary.get("public_id", public_id),
            "secure_url": cloudinary.get("secure_url", ""),
            "format": cloudinary.get("format", PurePosixPath(reference.relative_path).suffix.lstrip(".")),
            "taille": cloudinary.get("bytes", local_path.stat().st_size if local_path and local_path.exists() else 0),
            "checksum_sha256": checksum,
            "statut": status,
            "status": status,
            "message": message,
            "date_migration": now_iso(),
        }

    def get_uploader(self, timeout: int):
        configure_cloudinary()
        import cloudinary.uploader

        def upload(local_path: Path, public_id: str) -> dict:
            result = cloudinary.uploader.upload(
                str(local_path),
                public_id=public_id,
                resource_type="auto",
                overwrite=False,
                unique_filename=False,
                use_filename=False,
                timeout=timeout,
            )
            if not result.get("public_id"):
                raise CommandError("Cloudinary n'a pas confirmé l'upload.")
            return result

        return upload

    def remote_resource(self, public_id: str) -> dict | None:
        configure_cloudinary()
        import cloudinary.api

        for resource_type in ("image", "raw", "video"):
            try:
                return cloudinary.api.resource(public_id, resource_type=resource_type)
            except Exception as exc:
                if cloudinary_error_is_not_found(exc):
                    continue
                raise CommandError("Impossible de vérifier Cloudinary avant upload.") from exc
        return None

    def verify_manifest(self, manifest: list[dict], prefix: str):
        configure_cloudinary()
        import cloudinary.api

        successes = [entry for entry in manifest if entry.get("status") == "SUCCESS"]
        ok = failed = 0
        for entry in successes:
            public_id = entry.get("public_id") or safe_public_id(entry["chemin_relatif"], prefix)
            found = False
            for resource_type in ("image", "raw", "video"):
                try:
                    cloudinary.api.resource(public_id, resource_type=resource_type)
                    found = True
                    break
                except Exception as exc:
                    if cloudinary_error_is_not_found(exc):
                        continue
                    raise CommandError("Impossible de vérifier Cloudinary.") from exc
            if found:
                ok += 1
                self.stdout.write(f"SUCCESS {public_id}")
            else:
                failed += 1
                self.stdout.write(f"FAILED {public_id}")
        self.stdout.write(f"Vérification: {ok} OK, {failed} échec(s).")
        if failed:
            raise CommandError("Certaines ressources du manifeste sont introuvables.")

    @staticmethod
    def find_manifest_success(manifest: list[dict], relative_path: str, checksum: str, public_id: str) -> dict | None:
        for entry in manifest:
            if entry.get("status") != "SUCCESS":
                continue
            if entry.get("chemin_relatif") == relative_path and entry.get("checksum_sha256") == checksum:
                return entry
            if entry.get("public_id") == public_id and entry.get("checksum_sha256") == checksum:
                return entry
        return None

    @staticmethod
    def load_manifest(path: Path) -> list[dict]:
        if not path.exists():
            return []
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        if isinstance(data, dict):
            return data.get("entries", [])
        if isinstance(data, list):
            return data
        raise CommandError(f"Format de manifeste invalide: {path}")

    @staticmethod
    def write_manifest(path: Path, entries: list[dict]):
        payload = {
            "generated_at": now_iso(),
            "entries": entries,
        }
        with path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
