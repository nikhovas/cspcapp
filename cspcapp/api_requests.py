from .models import *
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse, HttpResponse
from django.db import connection
from .utilities import reconstruct_params, post_request_to_dict_slicer, values_from_dict_by_keys, smart_int, \
    null_check, reconstruct_args
import datetime
from .forms import UserForm


# Configuration Block


class PostRequestInfo:
    def __init__(self, _type_name, _to_date: list = (), _date_to_timestamp: list = ()):
        self.type_name = _type_name
        self.to_date = _to_date
        self.date_to_timestamp = _date_to_timestamp


MODEL_TYPES_DICT = \
    {
        'person_document': PostRequestInfo(_type_name=PersonDocument, _to_date=['issue_dt']),
        'person_home_address': PostRequestInfo(_type_name=PersonHomeAddress),
        'contract': PostRequestInfo(_type_name=Contract),
        'payment': PostRequestInfo(_type_name=ContractPayment, _date_to_timestamp=['payment_dt']),
        'person': PostRequestInfo(_type_name=Person, _to_date=['education_start_year', 'birth_dt']),
        'contract_student_phone': PostRequestInfo(_type_name=Contract),
        'student': PostRequestInfo(_type_name=StudentPerson, _to_date=['education_start_year', 'person.birth_dt']),
        'course': PostRequestInfo(_type_name=Course),
        'course_element': PostRequestInfo(_type_name=CourseElement),
        'course_class': PostRequestInfo(_type_name=CourseClass),
        'teacher': PostRequestInfo(_type_name=AuthUserXPerson, _to_date=['person.birth_dt'])
    }


CONFIG_RELINK = {'contract_student_phone': 'contract', 'contract_payer_phone': 'contract',
                 'contract_payer_inn': 'contract', 'contract_course_element': 'contract'}
# NEED_OWN_EDIT_SYSTEM = ['course_element']
DELETE_RENAMING = {'payment': 'contract_payment'}


# Edit Block


def data_edit(request: WSGIRequest, object_type: str) -> HttpResponse:
    print('in edit!')
    if object_type in CONFIG_RELINK.keys():
        object_type = CONFIG_RELINK[object_type]
    print('in edit2!')
    config = MODEL_TYPES_DICT[object_type]
    editing_object = config.type_name.objects.get(pk=request.POST['id'])

    params = post_request_to_dict_slicer(request.POST)
    del params['csrfmiddlewaretoken']
    del params['id']
    reconstruct_args(params=params, to_date=config.to_date, date_to_timestamp=config.date_to_timestamp)
    print(params)
    for i, j in params.items():
        if rgetattr(editing_object, i, None) != j:
            arr = i.split('.')
            editing_object.is_edited = True
            if len(arr) > 1:
                rgetattr(editing_object, '.'.join(arr[:-1])).is_edited = True
            print(f"not equal: {i}")
            rsetattr(editing_object, i, j)

    # editing_object.update(**params)
    editing_object.save(user_id=request.user.pk)
    return JsonResponse({})


def course_element_add(request: WSGIRequest) -> JsonResponse:
    data = dict(request.POST)
    print(data)
    course_element = CourseElement.objects.create(course_id=int(request.POST['course_id']),
                                                  teacher_person_id=int(data['teacher_id'][0]))
    course_element.save()
    course_element_id = course_element.pk
    for k in range(0, 7):
        if data['course_class_start_hour'][k] != '' and data['course_class_start_minute'][k] != '' and \
                data['course_class_end_hour'][k] != '' and data['course_class_end_minute'][k] != '':
            CourseClass(start_tm=datetime.time(int(data['course_class_start_hour'][k]),
                                               int(data['course_class_start_minute'][k])),
                        end_tm=datetime.time(int(data['course_class_end_hour'][k]),
                                             int(data['course_class_end_minute'][k])),
                        week_day_txt=str(k), course_element_id=course_element_id).save()
    return JsonResponse({'new_element_id': course_element_id})


# Add Block


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

    return JsonResponse({'new_element_id': new_element_id})


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

    return JsonResponse({})


def course_add(request: WSGIRequest) -> JsonResponse:
    Course(sphere_txt=request.POST['sphere_txt'], name_txt=request.POST['name_txt'], short_nm=request.POST['short_nm'],
           price_per_hour=int(request.POST['price_per_hour']), number_of_hours=request.POST['number_of_hours']).save()
    return JsonResponse({})


# Delete BLock


def object_delete(request: WSGIRequest, object_type: str) -> HttpResponse:
    MODEL_TYPES_DICT[object_type].type_name.objects.get(pk=request.POST['id']).custom_delete(request.user.pk)
    return JsonResponse({})


def new_user(request: WSGIRequest) -> JsonResponse:
    # form = UserForm(request.POST)
    # print(form.is_valid())
    # print(form.cleaned_data)
    print(request.POST)
    _new_user = User.objects.create_user(username=request.POST['username'], password=request.POST['password'])
    new_person = Person(person_surname_txt=request.POST['surname'],
                        person_name_txt=request.POST['name'],
                        person_father_name_txt=request.POST['father_name'],
                        birth_dt=datetime.date(int(request.POST['birth_dt_year']), int(request.POST['birth_dt_month']),
                                               int(request.POST['birth_dt_day'])))
    new_person.save(user_id=request.user.pk)
    AuthUserXPerson.objects.create(auth_user=_new_user, person=new_person)
    return JsonResponse({})


def get_teacher_users(request: WSGIRequest) -> JsonResponse:
    return JsonResponse([{
        'surname': i.person.person_surname_txt,
        'name': i.person.person_name_txt,
        'father_name': i.person.person_father_name_txt,
        'username': i.auth_user.username,
        'id': i.person.id
    } for i in AuthUserXPerson.objects.all()])
