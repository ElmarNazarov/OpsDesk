import factory
from factory.django import DjangoModelFactory

from apps.notifications.models import Notification, NotificationType


class NotificationFactory(DjangoModelFactory):
    class Meta:
        model = Notification

    recipient = factory.SubFactory("tests.factories.accounts.UserFactory")
    title = factory.Faker("sentence")
    message = factory.Faker("paragraph")
    type = NotificationType.REQUEST_SUBMITTED
