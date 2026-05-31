import factory
from factory.django import DjangoModelFactory

from apps.assets.models import Asset, AssetCategory, AssetStatus


class AssetCategoryFactory(DjangoModelFactory):
    class Meta:
        model = AssetCategory

    name = factory.Sequence(lambda n: f"Category {n}")


class AssetFactory(DjangoModelFactory):
    class Meta:
        model = Asset

    name = factory.Faker("word")
    category = factory.SubFactory(AssetCategoryFactory)
    serial_number = factory.Sequence(lambda n: f"SN-TEST-{n}")
    status = AssetStatus.AVAILABLE
