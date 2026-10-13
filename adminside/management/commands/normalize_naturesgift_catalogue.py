from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from adminside.models import Package, PackageCategory


class Command(BaseCommand):
    help = 'Merge the legacy Kenya Safari category into the canonical Kenya Safaris category.'

    @transaction.atomic
    def handle(self, *args, **options):
        try:
            canonical = PackageCategory.objects.get(slug='kenya-safaris')
            legacy = PackageCategory.objects.get(slug='kenya-safari')
        except PackageCategory.DoesNotExist as exc:
            raise CommandError('Expected Kenya category records were not found.') from exc

        direct_count = Package.objects.filter(category=legacy).update(category=canonical)
        tagged_packages = list(legacy.tagged_packages.all())
        tagged_count = 0
        for package in tagged_packages:
            package.categories.add(canonical)
            package.categories.remove(legacy)
            tagged_count += 1

        legacy.is_active = False
        legacy.show_in_navigation = False
        legacy.save(update_fields=['is_active', 'show_in_navigation', 'updated_at'])

        self.stdout.write(self.style.SUCCESS(
            f'Merged Kenya Safari into Kenya Safaris: {direct_count} primary and '
            f'{tagged_count} tagged package references migrated; legacy category deactivated.'
        ))
