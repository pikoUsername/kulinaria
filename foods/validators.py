from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from foods.models import Category, Ingredients


def category_validator(value):
    cat = Category.objects.filter(name=value)
    if not cat:
        raise ValidationError(
            message=_("Category does not exists"),
            code="invalid",
        )


def ingredients_validator(value: str):
    invalid_format = ValidationError(
        message=_("Invalid format"),
        code="invalid",
    )

    for line in value.split("\n"):
        name, amount_or_mass = line.split("-")
        ing = Ingredients.objects.filter(name=name.rstrip())
        if not ing:
            ValidationError(
                message=_("Ingredient - %(ing)s does not exists"),
                code="invalid",
                params={"ing": name}
            )
        amount_or_mass = amount_or_mass.lower()
        if amount_or_mass.find("г") == -1:
            if amount_or_mass.find("шт") == -1:
                raise invalid_format
            else:
                amount, x = amount_or_mass.rsplit()
                if not amount:
                    raise invalid_format
        else:
            mass, x = amount_or_mass.rsplit()
            if not mass:
                raise invalid_format
