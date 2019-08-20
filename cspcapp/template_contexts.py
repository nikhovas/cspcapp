from django.core.handlers.wsgi import WSGIRequest
from cspcapp.constants import REGIONS_DICT, PAYMENT_TYPES
from .models import AuthUserXPerson, Course


def user_additional_info(request: WSGIRequest):
    return {
        'user_additional_info':
            request.user.authuserxperson.person if hasattr(request.user, 'authuserxperson') else None,
        'REGIONS_DICT': REGIONS_DICT,
        'teachers': AuthUserXPerson.objects.all(),
        'regions': REGIONS_DICT,
        'payment_types': PAYMENT_TYPES,
        'courses': Course.objects.all()
    }
