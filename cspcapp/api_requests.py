from .models import PersonHomeAddress, PersonDocument, Person
from django.core.handlers.wsgi import WSGIRequest
# from .forms import PersonHomeAddressForm, PersonDocumentForm, PersonInnForm, PersonBirthDateForm, PersonPhoneForm, \
#     PersonEmailForm
from django.http import JsonResponse, HttpResponse
from django.db import connection
from django.core import serializers
import json
from .utilities import reconstruct_params, post_request_to_dict_slicer, values_from_dict_by_keys
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
    def __init__(self, _type_name, _id_name: str, _need_person_id: bool, _call_order: list,
                 _reformat_params: dict, _procedure_name: str):
        self.type_name = _type_name
        self.id_name = _id_name
        self.need_person_id = _need_person_id
        self.call_order = _call_order
        self.reformat_params = _reformat_params
        self.procedure_name = _procedure_name


MODEL_TYPES_DICT = \
    {
        'document': PostRequestInfo(
            _type_name=PersonDocument,
            _id_name='person_document_id',
            _need_person_id=True,
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
        'address': PostRequestInfo(
            _type_name=PersonHomeAddress,
            _id_name='person_home_address_id',
            _need_person_id=True,
            _call_order=['person_home_address_id', 'person_id', 'region_cd', 'city_txt', 'street_txt', 'house_txt',
                         'building_no', 'structure_no', 'flat_nm', 'change_user_id'],
            _reformat_params={
                'to_int': ['id', 'region_cd', 'flat_nm'],
                'renaming': {'id': 'person_home_address_id'}
            },
            _procedure_name='person_home_address_update'
        )
    }


def data_edit(request: WSGIRequest, object_type: str) -> HttpResponse:
    config = MODEL_TYPES_DICT[object_type]
    editing_object = config.type_name.objects.get(pk=int(request.POST['id']))
    # object = config.type_name.objects.get(**{config.id_name: int(request.POST['id'])})
    params = post_request_to_dict_slicer(request.POST)
    adding_dict = {'change_user_id': request.user.pk}
    if config.need_person_id:
        adding_dict['person_id'] = editing_object.person_id

    reconstruct_params(params=params, **config.reformat_params, add=adding_dict, deleting=['csrfmiddlewaretoken'],
                       value_edit={"": None})
    if editing_object.dict_equal(params):
        return JsonResponse({'result': True, 'sent_request': False})
    else:
        try:
            cur = connection.cursor()
            aaa = values_from_dict_by_keys(params, config.call_order)
            print(aaa)
            cur.callproc(MODEL_TYPES_DICT[object_type]['procedure_name'], aaa)
        except Exception as error:
            print(error)
            return JsonResponse({'result': False, 'sent_request': True})
        return JsonResponse({'result': True, 'sent_request': True})



def document_data_edit(request: WSGIRequest) -> HttpResponse:
    object = PersonDocument.objects.get(person_document_id=int(request.POST['id']))
    params = post_request_to_dict_slicer(request.POST)

    call_order = ['person_document_id', 'document_no', 'document_series', 'document_type_txt', 'person_id',
                  'person_surname_txt', 'person_name_txt', 'person_father_name_txt', 'authority_no', 'authority_txt',
                  'issue_dt', 'change_user_id']

    reconstruct_params(params=params,
                       to_int=['id', 'document_no'],
                       to_date=['issue_dt'],
                       renaming={'id': 'person_document_id'},
                       deleting=['csrfmiddlewaretoken'],
                       add={'person_id': object.person_id, 'change_user_id': request.user.pk})
    if object.dict_equal(params):
        return JsonResponse({'result': True, 'sent_request': False})
    else:
        try:
            cur = connection.cursor()
            aaa = values_from_dict_by_keys(params, call_order)
            print(aaa)
            cur.callproc('person_document_update', aaa)
        except Exception as error:
            print(error)
            return JsonResponse({'result': False, 'sent_request': True})
        return JsonResponse({'result': True, 'sent_request': True})


def address_data_edit(request: WSGIRequest) -> HttpResponse:
    object = PersonDocument.objects.get(person_document_id=int(request.POST['id']))
    params = post_request_to_dict_slicer(request.POST)

    call_order = ['person_home_address_id', 'person_id', 'region_cd', 'city_txt', 'street_txt', 'house_txt',
                  'building_no', 'structure_no', 'flat_nm', 'change_user_id']

    reconstruct_params(params=params,
                       to_int=['id', 'region_cd', 'flat_nm'],
                       renaming={'id': 'person_document_id'},
                       deleting=['csrfmiddlewaretoken'],
                       add={'person_id': object.person_id, 'change_user_id': request.user.pk},
                       value_edit={"": None})
    if object.dict_equal(params):
        return JsonResponse({'result': True, 'sent_request': False})
    else:
        try:
            cur = connection.cursor()
            aaa = values_from_dict_by_keys(params, call_order)
            print(aaa)
            cur.callproc('person_document_update', aaa)
        except Exception as error:
            print(error)
            return JsonResponse({'result': False, 'sent_request': True})
        return JsonResponse({'result': True, 'sent_request': True})


def inn_data_edit(request: WSGIRequest) -> HttpResponse:
    print(request.POST)
    return JsonResponse({'result': True})


def phone_data_edit(request: WSGIRequest) -> HttpResponse:
    print(request.POST)
    return JsonResponse({'result': True})


def payer_phone_data_edit(request: WSGIRequest) -> HttpResponse:
    print(request.POST)
    return JsonResponse({'result': True})


def payment_data_edit(request: WSGIRequest) -> HttpResponse:
    print(request.POST)
    return JsonResponse({'result': True})


def payment_add(request: WSGIRequest) -> HttpResponse:
    # do db logic
    new_element_id = 9999
    return JsonResponse({'result': True, 'new_element_id': new_element_id})


def add_new_contract(request: WSGIRequest) -> HttpResponse:
    print(request.POST)
    return JsonResponse({'result': True})


def course_element_data_edit(request: WSGIRequest) -> HttpResponse:
    print(request.POST)
    return JsonResponse({'result': True})


#
#
# def edit_inn(request: WSGIRequest) -> JsonResponse:
#     person = Person.objects.get(pk=request.POST['person_id'])
#     form = PersonInnForm(request.POST, instance=person)
#     if form.is_valid():
#         form.save()
#         return JsonResponse({'result': True})
#     else:
#         return JsonResponse({'result': False})
#
#
# def edit_birth_date(request: WSGIRequest) -> JsonResponse:
#     person = Person.objects.get(pk=request.POST['person_id'])
#     form = PersonBirthDateForm(request.POST, instance=person)
#     if form.is_valid():
#         form.save()
#         return JsonResponse({'result': True})
#     else:
#         return JsonResponse({'result': False})

#
# def edit_phone(request: WSGIRequest) -> JsonResponse:
#     person = PersonPhone.objects.get(pk=request.POST['person_id'])
#     form = PersonInnForm(request.POST, instance=person)
#     if form.is_valid():
#         form.save()
#         return JsonResponse({'result': True})
#     else:
#         return JsonResponse({'result': False})
#
#
# def edit_email(request: WSGIRequest) -> JsonResponse:
#     person = PersonEmail.objects.get(pk=request.POST['person_id'])
#     form = PersonEmailForm(request.POST, instance=person)
#     if form.is_valid():
#         form.save()
#         return JsonResponse({'result': True})
#     else:
#         return JsonResponse({'result': False})