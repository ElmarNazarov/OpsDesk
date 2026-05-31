import pytest


@pytest.mark.django_db
def test_django_setup():
    from django.conf import settings

    assert "apps.accounts" in settings.INSTALLED_APPS
