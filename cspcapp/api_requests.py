from .models import *
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse, HttpResponse
from django.db import connection
from .utilities import reconstruct_params, post_request_to_dict_slicer, values_from_dict_by_keys, smart_int, \
    null_check, reconstruct_args
import datetime
from .forms import UserForm
from django.shortcuts import redirect
from .views_kernel import add_student


# Configuration Block


class PostRequestInfo:
    def __init__(self, _type_name, _to_date: list = (), _date_to_timestamp: list = (), _to_time: list = ()):
        self.type_name = _type_name
        self.to_date = _to_date
        self.date_to_timestamp = _date_to_timestamp
        self.to_time = _to_time


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
        'teacher': PostRequestInfo(_type_name=AuthUserXPerson, _to_date=['person.birth_dt'],),
        'course_detail': PostRequestInfo(_type_name=CourseElementDefiniteClass, _to_date=['class_dt'],
                                         _to_time=['start_tm', 'end_tm']),
        'reg_form': PostRequestInfo(_type_name=RegistrationRequest, _to_date=['birth_dt']),
        'student_request': PostRequestInfo(_type_name=StudentRequest)
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
    reconstruct_args(params=params, to_date=config.to_date, date_to_timestamp=config.date_to_timestamp,
                     to_time=config.to_time)
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


def course_detail_add(request: WSGIRequest) -> JsonResponse:
    # data = dict(request.POST)
    CourseElementDefiniteClass.objects.create(class_dt=datetime.date(int(request.POST['class_dt_year']),
                                                                     int(request.POST['class_dt_month']),
                                                                     int(request.POST['class_dt_day'])),
                                              start_tm=datetime.time(int(request.POST['start_tm_hour']),
                                                                     int(request.POST['start_tm_minute'])),
                                              end_tm=datetime.time(int(request.POST['end_tm_hour']),
                                                                   int(request.POST['end_tm_minute'])),
                                              course_element_id=int(request.POST['course_element_id']))
    return JsonResponse({})


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


# Delete BLock


def object_delete(request: WSGIRequest, object_type: str) -> HttpResponse:
    id = request.POST['id']
    MODEL_TYPES_DICT[object_type].type_name.objects.get(pk=id).custom_delete(request.user.pk)
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
    conn = AuthUserXPerson(auth_user=_new_user, person=new_person)
    conn.custom_create()
    return JsonResponse({})


def get_teacher_users(request: WSGIRequest) -> JsonResponse:
    return JsonResponse([{
        'surname': i.person.person_surname_txt,
        'name': i.person.person_name_txt,
        'father_name': i.person.person_father_name_txt,
        'username': i.auth_user.username,
        'id': i.person.id
    } for i in AuthUserXPerson.objects.all()])


def submit_registration_form(request: WSGIRequest) -> JsonResponse:
    template = RegistrationRequest.objects.get(pk=request.POST['id'])
    _new_user = User.objects.create_user(username=template.username, password=template.password)
    new_person = Person(person_surname_txt=template.person_surname_txt,
                        person_name_txt=template.person_name_txt,
                        person_father_name_txt=template.person_father_name_txt,
                        birth_dt=template.birth_dt)
    new_person.save(user_id=request.user.pk)
    conn = AuthUserXPerson(auth_user=_new_user, person=new_person)
    conn.custom_create()
    return JsonResponse({})


def submit_student_form(request: WSGIRequest) -> JsonResponse:
    req = StudentRequest.objects.get(pk=request.POST['id'])
    now = datetime.datetime.now().date()
    ed_year = now.year - req.student_class
    if now.month > 6:
        ed_year += 1
    add_student(request.user.pk,
                document_no=[req.student_document_no, req.payer_document_no],
                document_series=[req.student_document_series, req.payer_document_series],
                person_surname_txt=[req.student_surname_txt, req.payer_surname_txt],
                person_name_txt=[req.student_name_txt, req.payer_name_txt],
                person_father_name_txt=[req.student_father_name_txt, req.payer_father_name_txt],
                authority_no=[req.student_authority_no, req.payer_authority_no],
                authority_txt=[req.student_authority_txt, req.payer_authority_txt],
                issue_dt=[req.student_issue_dt, req.payer_issue_dt],
                document_type_txt=[req.student_document_type_txt, req.payer_document_type_txt],

                region_cd=[req.student_region_cd, req.payer_region_cd],
                city_txt=[req.student_city_txt, req.payer_city_txt],
                street_txt=[req.student_street_txt, req.payer_street_txt],
                house_txt=[req.student_house_txt, req.payer_house_txt],
                building_no=[req.student_building_no, req.payer_building_no],
                structure_no=[req.student_structure_no, req.payer_structure_no],
                flat_nm=[req.student_flat_nm, req.payer_flat_nm],

                birth_dt=[req.student_birth_dt],
                education_dt=[datetime.date(ed_year, 9, 1)],
                school_name_txt=[req.student_school_name_txt],
                liter=[req.student_liter],

                phone=[req.student_phone_no, req.payer_phone_no],
                inn=[req.payer_inn_no],

                course_element=req.courses.split(' ')
                )
    req.delete()
    return JsonResponse({})
