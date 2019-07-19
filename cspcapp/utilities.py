from django.http.request import QueryDict
from datetime import date


def reformat_request_get_params(params: QueryDict) -> dict:
    return dict((i, None) if j == '' else (i, j) for i, j in params.items())


def overview_get_format(params: dict) -> dict:
    for i, j in params.items():
        if i == 'passport_no':
            yield (i, int(j)) if j is not None else (i, 0)
        else:
            yield i, j


def make_date_in_dict(d: dict, name: str):
    d[name] = date(int(d[name + '_year']), int(d[name + '_month']), int(d[name + '_day']))
    del d[name + '_year']
    del d[name + '_month']
    del d[name + '_day']


def rename_arg_in_dict(d: dict, _from: str, to: str):
    d[to] = d[_from]
    del d[_from]


def reconstruct_params(params: dict, to_int: list = [], to_date: list = [], renaming: dict = {},
                       deleting: list = [], add: dict = {}, value_edit: dict = {}):
    for i in params:
        print(type(i))
    for i in to_int:
        params[i] = int(params[i])
    for i in to_date:
        make_date_in_dict(params, i)
    for i, j in renaming.items():
        rename_arg_in_dict(params, i, j)
    for i in deleting:
        del params[i]
    for i in params:
        if params[i] in value_edit.keys():
            params[i] = value_edit[params[i]]
    params.update(add)


def post_request_to_dict_slicer(post) -> dict:
    return {i: j[0] for i, j in dict(post).items()}


def values_from_dict_by_keys(d: dict, keys: list):
    return [d[i] for i in keys]