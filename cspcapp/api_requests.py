from .models import PersonHomeAddress, PersonDocument, Person
from django.core.handlers.wsgi import WSGIRequest
# from .forms import PersonHomeAddressForm, PersonDocumentForm, PersonInnForm, PersonBirthDateForm, PersonPhoneForm, \
#     PersonEmailForm
from django.http import JsonResponse


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
def document_data_edit(request: WSGIRequest) -> JsonResponse:
    # document = PersonHomeAddress.objects.get(pk=request.POST['person_document_id'])
    # form = PersonDocumentForm(request.POST, instance=document)
    # if form.is_valid():
    #     form.save()
    #     return JsonResponse({'result': True})
    # else:
    #     return JsonResponse({'result': False})
    # here request for update
    print(request.POST)
    print(111)
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