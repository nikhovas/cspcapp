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
from django.db.utils import IntegrityError
import sys


# Configuration Block


DELETE_RENAMING = {'payment': 'contract_payment'}


# Edit Block


def data_edit(request: WSGIRequest, object_type: str) -> HttpResponse:
    config = MODEL_TYPES_DICT[object_type]
    params = post_request_to_dict_slicer(request.POST)
    editing_object = config.type_name.objects.get(pk=request.POST['id'])
    del params['csrfmiddlewaretoken']
    del params['id']
    reconstruct_args(params=params, to_date=config.to_date, date_to_timestamp=config.date_to_timestamp,
                     to_time=config.to_time)
    for i, j in params.items():
        rsetattr(editing_object, i, j)
    if hasattr(editing_object, 'change_user'):
        editing_object.change_user = request.user
    editing_object.save()
    return JsonResponse({})


def course_element_add(request: WSGIRequest) -> JsonResponse:
    data = dict(request.POST)
    print(data)
    course_element = CourseElement.objects.create(course_id=request.POST['course_id'],
                                                  teacher_person_id=request.POST['teacher_id'])
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
    print(data)
    contract_payment = ContractPayment(payment_amt=request.POST['payment_amt'],
                                       contract_id=request.POST['contract_id'],
                                       payment_type=request.POST['payment_type'],
                                       voucher_no=request.POST['voucher_no'],
                                       change_user_id=request.user.pk,
                                       payment_dt=datetime.datetime(int(data['payment_dt_year'][0]),
                                                                    int(data['payment_dt_month'][0]),
                                                                    int(data['payment_dt_day'][0]))
                                       )
    contract_payment.save()
    return JsonResponse({'new_element_id': contract_payment.pk})


# Delete BLock


def object_delete(request: WSGIRequest, object_type: str) -> HttpResponse:
    id = request.POST['id']
    try:
        MODEL_TYPES_DICT[object_type].type_name.objects.get(pk=id).delete()
    except IntegrityError:
        exc_type, value, exc_traceback = sys.exc_info()
        return JsonResponse({
            'success': False,
            'error_msg': f"Ошибка: есть зависимости, не подлежащие автоматическому удалению\n\n\n{value}"
        })
    except HasRelatedObjectsException as error:
        res = 'Ошибка: есть зависимости, не подлежащие автоматическому удалению:'
        for i in error.relations_set:
            res += f"\n{i[0].ru_localization} -> {i[1].ru_localization}"
        return JsonResponse({'success': False, 'error_msg': res})
    return JsonResponse({'success': True})


def new_user(request: WSGIRequest) -> JsonResponse:
    _new_user = User.objects.create_user(username=request.POST['username'], password=request.POST['password'],
                                         first_name=request.POST['name'], last_name=request.POST['surname'])
    new_person = Person(person_surname_txt=request.POST['surname'],
                        person_name_txt=request.POST['name'],
                        person_father_name_txt=request.POST['father_name'],
                        birth_dt=datetime.date(int(request.POST['birth_dt_year']), int(request.POST['birth_dt_month']),
                                               int(request.POST['birth_dt_day'])))
    new_person.save()
    conn = AuthUserXPerson(auth_user=_new_user, person=new_person)
    conn.save()
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
    _new_user.save()
    new_person = Person(person_surname_txt=template.person_surname_txt,
                        person_name_txt=template.person_name_txt,
                        person_father_name_txt=template.person_father_name_txt,
                        birth_dt=template.birth_dt, change_user=request.user)
    new_person.save()
    AuthUserXPerson.objects.create(auth_user=_new_user, person=new_person)
    return JsonResponse({})


def submit_student_form(request: WSGIRequest) -> JsonResponse:
    req = StudentRequest.objects.get(pk=request.POST['id'])
    now = datetime.datetime.now().date()
    ed_year = now.year - req.student_class
    if now.month > 6:
        ed_year += 1
    add_student(request.user,
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
                area_txt=[req.student_area_txt, req.payer_area_txt],
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

                student_phone_no=[req.student_phone_no],
                payer_phone_no=[req.payer_phone_no],
                payer_inn_no=[req.payer_inn_no],

                course_element=req.courses.split(' ')
                )
    req.delete()
    return JsonResponse({})
