from django.core.handlers.wsgi import WSGIRequest
from cspcapp.constants import REGIONS_DICT


def user_additional_info(request: WSGIRequest):
    return {'user_additional_info': request.user.authuserxperson.person, 'REGIONS_DICT': REGIONS_DICT}
