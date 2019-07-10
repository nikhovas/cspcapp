from django.core.handlers.wsgi import WSGIRequest
from django.http.request import QueryDict


# def get_params(request: WSGIRequest) -> dict:
#     return {i: j[0] for i, j in request.GET}


def reformat_request_get_params(params: QueryDict) -> dict:
    for i, j in params.items():
        yield i, j
        # if i == 'passport' or i == 'document_no' or i == 'document_series':
        #     continue
        # if j == '' or j == 0:
        #     yield i, None
        # else:
        #     yield i, j


def overview_get_format(params: dict) -> dict:
    for i, j in params.items():
        if i == 'passport_no' and j is not None:
            yield i, int(j)
        else:
            yield i, j
