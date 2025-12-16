import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'social_media.settings')
django.setup()
from django.core.management import call_command

if __name__ == '__main__':
    call_command('seed', users=2, groups=1, posts=4, likes=4, comments=4)
    print('Seed runner finished')
