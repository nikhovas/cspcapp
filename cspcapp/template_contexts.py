from django.core.handlers.wsgi import WSGIRequest


def user_additional_info(request: WSGIRequest):
    return {
        'user_additional_info': request.user.authuserxperson.person,
    }