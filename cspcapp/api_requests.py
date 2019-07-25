from .models import PersonHomeAddress, PersonDocument, Person, Contract, ContractPayment
from django.core.handlers.wsgi import WSGIRequest
# from .forms import PersonHomeAddressForm, PersonDocumentForm, PersonInnForm, PersonBirthDateForm, PersonPhoneForm, \
#     PersonEmailForm
from django.http import JsonResponse, HttpResponse
from django.db import connection
from django.core import serializers
import json
from .utilities import reconstruct_params, post_request_to_dict_slicer, values_from_dict_by_keys, smart_int, null_check
import datetime


# def edit_address_info(request: WSGIRequest) -> JsonResponse:
#     address = PersonHomeAddress.objects.get(pk=request.POST['person_home_address_id'])
#     form = PersonHomeAddressForm(request.POST, instance=address)
#     if form.is_valid():
#         form.save()
#         return JsonResponse({'result': True})
#     else:
#         return JsonResponse({'result': False})
#
#


class PostRequestInfo:
    def __init__(self, _type_name, _id_name: str, _call_order: list,
                 _reformat_params: dict, _procedure_name: str):
        self.type_name = _type_name
        self.id_name = _id_name
        self.call_order = _call_order
        self.reformat_params = _reformat_params
        self.procedure_name = _procedure_name

MODEL_TYPES_DICT = \
    {
        'person_document': PostRequestInfo(
            _type_name=PersonDocument,
            _id_name='person_document_id',
            _call_order=['person_document_id', 'document_no', 'document_series', 'document_type_txt', 'person_id',
                           'person_surname_txt', 'person_name_txt', 'person_father_name_txt', 'authority_no',
                           'authority_txt', 'issue_dt', 'change_user_id'],
            _reformat_params={
                'to_int': ['id', 'document_no'],
                'to_date': ['issue_dt'],
                'renaming': {'id': 'person_document_id'}
            },
            _procedure_name='person_document_update'
        ),
        'person_home_address': PostRequestInfo(
            _type_name=PersonHomeAddress,
            _id_name='person_home_address_id',
            _call_order=['person_home_address_id', 'person_id', 'region_cd', 'city_txt', 'street_txt', 'house_txt',
                         'building_no', 'structure_no', 'flat_nm', 'change_user_id'],
            _reformat_params={
                'to_int': ['id', 'region_cd', 'flat_nm'],
                'renaming': {'id': 'person_home_address_id'}
            },
            _procedure_name='person_home_address_update'
        ),
        'contract': PostRequestInfo(
            _type_name=Contract,
            _id_name='',
            _call_order=['contract_id', 'contract_dttm', 'student_document_id', 'student_address_id',
                         'student_phone_no', 'payer_document_id', 'payer_address_id', 'payer_phone_no', 'payer_inn_no',
                         'course_element_id', 'change_user_id'],
            _reformat_params={
                'to_int': ['id', 'student_document_id', 'student_address_id', 'payer_document_id', 'payer_address_id',
                           'course_element_id'],
                'renaming': {'id': 'contract_id'}
            },
            _procedure_name='contract_update'
        ),
        'payment': PostRequestInfo(
            _type_name=ContractPayment,
            _id_name='contract_payment_id',
            _call_order=['contract_payment_id', 'payment_dt', 'payment_amt', 'contract_id', 'payment_type',
                         'voucher_no', 'change_user_id'],
            _reformat_params={
                'to_int': ['id', 'payment_amt'],
                'date_to_timestamp': ['payment_dt'],
                'renaming': {'id': 'contract_payment_id'}
            },
            _procedure_name='contract_payment_update'
        )
    }


CONFIG_RELINK = {'contract_student_phone': 'contract', 'contract_payer_phone': 'contract', 'contract_payer_inn': 'contract'}


def data_edit(request: WSGIRequest, object_type: str) -> HttpResponse:
    if object_type in CONFIG_RELINK.keys():
        object_type = CONFIG_RELINK[object_type]
    config = MODEL_TYPES_DICT[object_type]
    editing_object = config.type_name.objects.get(pk=int(request.POST['id']))
    params = post_request_to_dict_slicer(request.POST)
    adding_dict = {'change_user_id': request.user.pk}
    editing_object.uppend_dict(params)
    reconstruct_params(params=params, **config.reformat_params, add=adding_dict, deleting=['csrfmiddlewaretoken'],
                       value_edit={"": None, 'None': None})
    if editing_object.dict_equal(params):
        return JsonResponse({'result': True, 'sent_request': False})
    else:
        print(222)
        cur = connection.cursor()
        aaa = values_from_dict_by_keys(params, config.call_order)
        print(111)
        print(aaa)
        cur.callproc(config.procedure_name, aaa)
        # try:
        #     print(222)
        #     cur = connection.cursor()
        #     aaa = values_from_dict_by_keys(params, config.call_order)
        #     print(111)
        #     print(aaa)
        #     cur.callproc(config.procedure_name, aaa)
        # except Exception as error:
        #     print('error down')
        #     print(error)
        #     return JsonResponse({'result': False, 'sent_request': True})
        return JsonResponse({'result': True, 'sent_request': True})


def payment_add(request: WSGIRequest) -> HttpResponse:
    data = dict(request.POST)
    data['payment_type'] = ['1']
    print(data)
    arg_list = [int(data['payment_amt'][0]), int(data['contract_id'][0]), int(data['payment_type'][0]),
                data['voucher_no'][0], request.user.pk,
                datetime.datetime(int(data['payment_dt_year'][0]), int(data['payment_dt_month'][0]),
                                  int(data['payment_dt_day'][0]))]
    cur = connection.cursor()
    try:
        cur.callproc('contract_payment_insert', arg_list)
    except Exception as err:
        print(err)

    new_element_id = 0
    for row in cur:
        new_element_id = row[0]

    return JsonResponse({'result': True, 'new_element_id': new_element_id})


def add_new_contract(request: WSGIRequest) -> HttpResponse:
    data = dict(request.POST)
    data['course_element_id'] = '3'  # select now is not working
    print(data)
    arg_list = \
        [
            int(data['student_id'][0]), request.user.pk,

            int(data['document_no'][0]), str(data['document_series'][0]), str(data['document_type_txt'][0]),
            data['person_surname_txt'][0], data['person_name_txt'][0],
            data['person_father_name_txt'][0], data['authority_no'][0], data['authority_txt'][0],
            datetime.date(int(data['issue_dt_year'][0]), int(data['issue_dt_month'][0]), int(data['issue_dt_day'][0])),

            int(data['region_cd'][0]), data['city_txt'][0], data['street_txt'][0], data['house_txt'][0],
            null_check(data['building_no'][0]), null_check(data['structure_no'][0]), smart_int(data['flat_nm'][0]),

            int(data['document_no'][1]), data['document_series'][1], data['document_type_txt'][1],
            data['person_surname_txt'][1], data['person_name_txt'][1],
            data['person_father_name_txt'][1], data['authority_no'][1], data['authority_txt'][1],
            datetime.date(int(data['issue_dt_year'][1]), int(data['issue_dt_month'][1]), int(data['issue_dt_day'][1])),

            int(data['region_cd'][1]), data['city_txt'][1], data['street_txt'][1], data['house_txt'][1],
            null_check(data['building_no'][1]), null_check(data['structure_no'][1]), smart_int(data['flat_nm'][1]),

            data['student_phone_no'][0], data['payer_phone_no'][0], data['payer_inn_no'][0],
            int(data['course_element_id'][0])
        ]
    cur = connection.cursor()
    try:
        cur.callproc('full_contract_insert', arg_list)
    except Exception as err:
        print(err)

    return JsonResponse({'result': True})


def contract_delete(request: WSGIRequest) -> HttpResponse:
    print(request.POST)
    contract_id = request.POST['id']
    try:
        cur = connection.cursor()
        cur.execute(f"CALL contract_delete({contract_id}, {request.user.pk})")
    except Exception as error:
        print(error)
    return JsonResponse({'result': True})


def payment_delete(request: WSGIRequest) -> HttpResponse:
    print(request.POST)
    contract_payment_id = request.POST['id']
    try:
        cur = connection.cursor()
        cur.execute(f"CALL contract_payment_delete({contract_payment_id}, {request.user.pk})")
    except Exception as error:
        print(error)
    return JsonResponse({'result': True})


def course_element_data_edit(request: WSGIRequest) -> HttpResponse:
    print(request.POST)
    return JsonResponse({'result': True})
