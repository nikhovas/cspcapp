from django import forms
from .models import PersonHomeAddress, PersonDocument, Person


# class PersonHomeAddressForm(forms.ModelForm):
#     class Meta:
#         model = PersonHomeAddress
#         fields = ['region_cd', 'city_txt', 'street_txt', 'house_txt', 'building_no', 'structure_no', 'flat_nm']
#
#
# class PersonDocumentForm(forms.ModelForm):
#     class Meta:
#         model = PersonDocument
#         fields = ['document_no', 'document_series', 'document_type_txt', 'person_surname_txt', 'person_name_txt',
#                   'person_father_name_txt', 'authority_no', 'authority_txt', 'valid_from_dt']
#
#
# class PersonInnForm(forms.ModelForm):
#     class Meta:
#         model = Person
#         fields = ['inn_no']
#
#
# class PersonBirthDateForm(forms.ModelForm):
#     class Meta:
#         model = Person
#         fields = ['birth_dt']
#
#
# class PersonPhoneForm(forms.ModelForm):
#     class Meta:
#         model = PersonPhone
#         fields = ['phone_no']
#
#
# class PersonEmailForm(forms.ModelForm):
#     class Meta:
#         model = PersonEmail
#         fields = ['email_txt']
