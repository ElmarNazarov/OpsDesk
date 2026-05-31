import factory
from factory.django import DjangoModelFactory

from apps.requests.models import Request, RequestCategory, RequestStatus


class RequestCategoryFactory(DjangoModelFactory):
    class Meta:
        model = RequestCategory

    name = factory.Sequence(lambda n: f"Category {n}")
    slug = factory.Sequence(lambda n: f"category-{n}")
    requires_manager_approval = True


class RequestFactory(DjangoModelFactory):
    class Meta:
        model = Request

    public_id = factory.Sequence(lambda n: f"REQ-2026-{n:04d}")
    title = factory.Faker("sentence", nb_words=4)
    description = factory.Faker("paragraph")
    category = factory.SubFactory(RequestCategoryFactory)
    requester = factory.SubFactory("tests.factories.accounts.UserFactory")
    priority = "MEDIUM"
    status = RequestStatus.DRAFT
