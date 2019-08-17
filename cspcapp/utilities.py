from django.http.request import QueryDict
from datetime import date, datetime, time
import functools
from functools import wraps


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


def make_date_in_dict(d: dict, name: str):
    d[name] = date(int(d[name + '_year']), int(d[name + '_month']), int(d[name + '_day']))
    del d[name + '_year']
    del d[name + '_month']
    del d[name + '_day']


def rename_arg_in_dict(d: dict, _from: str, to: str):
    d[to] = d[_from]
    del d[_from]


def reformat_date_to_timestamp(d: dict, name: str):
    d[name] = datetime(int(d[name + '_year']), int(d[name + '_month']), int(d[name + '_day']))
    del d[name + '_year']
    del d[name + '_month']
    del d[name + '_day']


def make_time_in_dict(d: dict, name: str):
    d[name] = time(int(d[name + '_hour']), int(d[name + '_minute']))
    del d[name + '_hour']
    del d[name + '_minute']


def reconstruct_params(params: dict, to_int: list = [], to_date: list = [], date_to_timestamp = [], renaming: dict = {},
                       deleting: list = [], add: dict = {}, value_edit: dict = {}):
    for i in to_int:
        try:
            params[i] = int(params[i])
        except ValueError:
            params[i] = None
    for i in to_date:
        make_date_in_dict(params, i)
    for i in date_to_timestamp:
        reformat_date_to_timestamp(params, i)
    for i, j in renaming.items():
        rename_arg_in_dict(params, i, j)
    for i in deleting:
        del params[i]
    for i in params:
        if params[i] in value_edit.keys():
            params[i] = value_edit[params[i]]
    params.update(add)


def reconstruct_args(params: dict, to_int: list = [], to_date: list = [], date_to_timestamp = [], renaming: dict = {},
                       deleting: list = [], add: dict = {}, to_time = []):
    for i in to_int:
        try:
            params[i] = int(params[i])
        except ValueError:
            del params[i]
        except KeyError:
            pass

    for i in to_date:
        make_date_in_dict(params, i)
    for i in date_to_timestamp:
        reformat_date_to_timestamp(params, i)
    for i in to_time:
        make_time_in_dict(params, i)
    for i, j in renaming.items():
        rename_arg_in_dict(params, i, j)
    for i in deleting:
        del params[i]
    params.update(add)


def post_request_to_dict_slicer(post) -> dict:
    return {i: j[0] if len(j) == 1 else j for i, j in dict(post).items()}


def values_from_dict_by_keys(d: dict, keys: list):
    return [d[i] for i in keys]


def smart_int(data: str):
    # return '' if data == '' else int(data)
    return None if data == '' or data is None else int(data)


def null_check(data: str):
    # return data
    return None if data == '' else data


def setattr_nested(base, path: str, value):
    if '.' not in path:
        setattr(base, path, value)
    else:
        path, _, target = path.rpartition('.')
        for attrname in path.split('.'):
            base = getattr(base, attrname)
        setattr(base, target, value)


def rsetattr(obj, attr, val):
    pre, _, post = attr.rpartition('.')
    return setattr(rgetattr(obj, pre) if pre else obj, post, val)

# using wonder's beautiful simplification: https://stackoverflow.com/questions/31174295/getattr-and-setattr-on-nested-objects/31174427?noredirect=1#comment86638618_31174427

def rgetattr(obj, attr, *args):
    def _getattr(obj, attr):
        return getattr(obj, attr, *args)
    return functools.reduce(_getattr, [obj] + attr.split('.'))


def http_basic_auth(func):
    @wraps(func)
    def _decorator(request, *args, **kwargs):
        from django.contrib.auth import authenticate, login
        if 'HTTP_AUTHORIZATION' in request.META:
            authmeth, auth = request.META['HTTP_AUTHORIZATION'].split(' ', 1)
            if authmeth.lower() == 'basic':
                auth = auth.strip().decode('base64')
                username, password = auth.split(':', 1)
                user = authenticate(username=username, password=password)
                if user:
                    login(request, user)
        return func(request, *args, **kwargs)
    return _decorator
