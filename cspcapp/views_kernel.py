from .models import Person, PersonHomeAddress, PersonDocument, StudentPerson, Contract, StudentRequest, CourseElement
import datetime
from .utilities import reformat_request_get_params, overview_get_format, smart_int, null_check, http_basic_auth
from django.db import connection
from cspc import settings
from django.template.loader import get_template, render_to_string
from django.template import Context
from io import StringIO, BytesIO
from .constants import REGIONS_DICT, PAYMENT_TYPES
from xhtml2pdf import pisa


def add_contract(user, student: StudentPerson, course_element, **data):
    if hasattr(course_element, '__iter__'):
        course_element = course_element[0]
    payer_document = PersonDocument(
        document_no=data['document_no'][1], document_series=data['document_series'][1],
        document_type_txt=data['document_type_txt'][1], person_surname_txt=data['person_surname_txt'][1], 
        person_name_txt=data['person_name_txt'][1], person_father_name_txt=data['person_father_name_txt'][1], 
        authority_no=data['authority_no'][1], authority_txt=data['authority_txt'][1], issue_dt=data['issue_dt'][1] 
        if 'issue_dt' in data else datetime.date(int(data['issue_year'][1]), int(data['issue_month'][1]),
                                                 int(data['issue_day'][1])), change_user=user
    )
    payer_home_address = PersonHomeAddress(
        region_cd=data['region_cd'][1], area_txt=null_check(data['area_txt'][1]), city_txt=data['city_txt'][1], 
        street_txt=data['street_txt'][1], house_txt=data['house_txt'][1], 
        building_no=null_check(data['building_no'][1]), structure_no=null_check(data['structure_no'][1]), 
        flat_nm=smart_int(data['flat_nm'][1]), change_user=user
    )
    payer_document.save()
    payer_home_address.save()
    
    if data['document_type_txt'][0] and data['document_type_txt'][0] != '':
        student_document = PersonDocument(
            document_no=data['document_no'][0], document_series=data['document_series'][0],
            document_type_txt=data['document_type_txt'][0], person_surname_txt=data['person_surname_txt'][0],
            person_name_txt=data['person_name_txt'][0], person_father_name_txt=data['person_father_name_txt'][0],
            authority_no=data['authority_no'][0], authority_txt=data['authority_txt'][0], issue_dt=data['issue_dt'][0]
            if 'issue_dt' in data else datetime.date(int(data['issue_year'][0]), int(data['issue_month'][0]),
                                                     int(data['issue_day'][0])), change_user=user
        )
        student_home_address = PersonHomeAddress(
            region_cd=data['region_cd'][0], area_txt=null_check(data['area_txt'][0]), city_txt=data['city_txt'][0],
            street_txt=data['street_txt'][0], house_txt=data['house_txt'][0],
            building_no=null_check(data['building_no'][0]), structure_no=null_check(data['structure_no'][0]),
            flat_nm=smart_int(data['flat_nm'][0]), change_user=user
        )
        student_document.save()
        student_home_address.save()
        Contract.objects.create(student_person=student, student_document=student_document,
                                student_address=student_home_address, student_phone_no=data['student_phone_no'][0],
                                payer_document=payer_document, payer_address=payer_home_address,
                                payer_phone_no=data['payer_phone_no'][0], payer_inn_no=data['payer_inn_no'][0],
                                course_element_id=course_element, change_user=user)
    else:
        Contract.objects.create(student_person=student, student_document=None, student_address=None,
                                student_phone_no=None, payer_document=payer_document,
                                payer_address=payer_home_address, payer_phone_no=data['payer_phone_no'][0],
                                payer_inn_no=data['payer_inn_no'][0], course_element_id=course_element,
                                change_user=user)


def add_student(user, **data):
    person = Person(person_surname_txt=data['person_surname_txt'][0],
                    person_name_txt=data['person_name_txt'][0],
                    person_father_name_txt=data['person_father_name_txt'][0]
                    if data['person_father_name_txt'][0] != '' else None,
                    birth_dt=data['birth_dt'][0] if 'birth_dt' in data else
                    datetime.date(int(data['birth_year'][0]), int(data['birth_month'][0]), int(data['birth_day'][0])),
                    change_user=user)
    person.save()

    student = StudentPerson(education_start_year=data['education_dt'][0] if 'education_dt' in data else
                            datetime.date(int(data['education_year'][0]), int(data['education_month'][0]),
                                          int(data['education_day'][0])),
                            school_name_txt=data['school_name_txt'][0],
                            liter=data['liter'][0], person=person, change_user=user)
    student.save()

    if 'course_element' in data:
        for i in data['course_element'] if hasattr(data['course_element'], '__iter__') \
                else data['course_element'].split(' '):
            print(i)
            add_contract(user, student=student, course_element_id=i, **data)


def fetch_pdf_resources(uri, rel):
    return settings.BASE_DIR + '/cspcapp' + uri


def generate_contract_pdf(pk: int):
    result = BytesIO()
    template = get_template('docs/contract_paper.html')
    html = template.render({'contract': Contract.objects.get(pk=pk), 'REGIONS_DICT': REGIONS_DICT})
    print(settings.PROJECT_ROOT)
    pdf = pisa.CreatePDF(BytesIO(html.encode('UTF-8')), dest=result, encoding='UTF-8',
                         link_callback=fetch_pdf_resources)
    if not pdf.err:
        return result.getvalue()
    else:
        return None


def generate_contract_pdf_unchecked(student_req: StudentRequest):
    for i in student_req.courses.split(' '):
        elem = CourseElement.objects.get(pk=int(i))
        result = BytesIO()
        template = get_template('docs/contract_paper_unchecked.html')
        html = template.render({'data': student_req, 'REGIONS_DICT': REGIONS_DICT, 'course_element': elem})
        print(settings.PROJECT_ROOT)
        pdf = pisa.CreatePDF(BytesIO(html.encode('UTF-8')), dest=result, encoding='UTF-8',
                             link_callback=fetch_pdf_resources)
        yield result.getvalue()
