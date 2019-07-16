from .models import PersonHomeAddress, PersonDocument, Person
from django.core.handlers.wsgi import WSGIRequest
# from .forms import PersonHomeAddressForm, PersonDocumentForm, PersonInnForm, PersonBirthDateForm, PersonPhoneForm, \
#     PersonEmailForm
from django.http import JsonResponse, HttpResponse
from django.core import serializers
import json


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
def document_data_edit(request: WSGIRequest) -> HttpResponse:
    print(request.POST)
    return JsonResponse({'result': True})


def address_data_edit(request: WSGIRequest) -> HttpResponse:
    print(request.POST)
    return JsonResponse({'result': True})


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