import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

def main():
    os.environ['DJANGO_SETTINGS_MODULE'] = 'setup.settings'
    django.setup()

    settings.INSTALLED_APPS = [app for app in settings.INSTALLED_APPS if app not in [
        'allauth', 
        'allauth.account', 
        'allauth.socialaccount',
        'allauth.socialaccount.providers.google',
    ]]
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(['autenticacao.tests'])
    sys.exit(bool(failures))

if __name__ == '__main__':
    main()
