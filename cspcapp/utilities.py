from django.http.request import QueryDict


def reformat_request_get_params(params: QueryDict) -> dict:
    return dict((i, None) if j == '' else (i, j) for i, j in params.items())


def overview_get_format(params: dict) -> dict:
    for i, j in params.items():
        if i == 'passport_no':
            yield (i, int(j)) if j is not None else (i, 0)
        else:
            yield i, j
