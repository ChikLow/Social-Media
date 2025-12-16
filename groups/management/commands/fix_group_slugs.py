from django.core.management.base import BaseCommand
from django.utils.text import slugify
from groups.models import Group

class Command(BaseCommand):
    help = 'Fix groups with null/blank slugs by generating unique slugs from name'

    def handle(self, *args, **options):
        fixed = 0
        for g in Group.objects.filter(slug__isnull=True) | Group.objects.filter(slug=''):
            base = slugify(g.name) if g.name else 'group'
            slug = base
            counter = 1
            while Group.objects.filter(slug=slug).exclude(pk=g.pk).exists():
                slug = f"{base}-{counter}"
                counter += 1
            g.slug = slug
            g.save()
            fixed += 1
            self.stdout.write(self.style.SUCCESS(f'Fixed group {g.pk} -> slug {g.slug}'))
        if fixed == 0:
            self.stdout.write('No groups needed fixing')
        else:
            self.stdout.write(self.style.SUCCESS(f'Fixed {fixed} groups'))
