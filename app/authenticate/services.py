from django.db import transaction
from rest_framework.exceptions import ValidationError

from .models import User, Company


@transaction.atomic
def create_company_for_user(user, title, inn):
    user = User.objects.select_for_update().get(pk=user.pk)

    if user.company_id is not None:
        raise ValidationError("You already have a company")

    company = Company.objects.create(
        title=title,
        inn=inn
    )

    user.company = company
    user.is_company_owner = True
    user.save(update_fields=["company", "is_company_owner"])

    return company