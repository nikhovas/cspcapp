from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from .constants import REGIONS_DICT

from .models import *
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse, HttpResponse
from django.db import connection
from django.core.mail import send_mail, EmailMessage

from .utilities import reconstruct_params, post_request_to_dict_slicer, values_from_dict_by_keys, smart_int, \
    null_check, reconstruct_args

from .views_kernel import generate_contract_pdf, generate_contract_pdf_unchecked

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1Sweq_eZ03PXz6LwbhIWRzLN51G-ooEXa8CYP0KeHbSg'
SPREADSHEET_ID = '1Sweq_eZ03PXz6LwbhIWRzLN51G-ooEXa8CYP0KeHbSg'
SAMPLE_RANGE_NAME = 'data'


def open_spreadsheet():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('sheets', 'v4', credentials=creds)


def dump_to_local_database(reuqest: WSGIRequest) -> HttpResponse:
    service = open_spreadsheet()
    range = 'student_14_elder_form_answers!A2:BB1102'

    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=range).execute()
    values = result.get('values', [])

    for row in values:
        if len(row) == 0:
            continue
        courses_vals = ' '.join([i.split(' ')[0] for i in ''.join(row[38]).split(', ')])
        new_elem = StudentRequest(
            is_two_side=True, student_surname_txt=row[1], student_name_txt=row[2], student_father_name_txt=row[3],
            student_birth_dt=datetime.datetime.strptime(row[4], '%d.%m.%Y').date(), student_class=row[5],
            student_school_name_txt=row[6], student_liter=row[7], student_phone_no=row[20], student_document_no=row[9],
            student_document_series=null_check(row[8]), student_document_type_txt=row[39], student_authority_no=row[11],
            student_authority_txt=row[10], student_issue_dt=datetime.datetime.strptime(row[12], '%d.%m.%Y').date(),
            student_region_cd=int(str(row[13]).split(' ')[0]),  student_city_txt=row[14], student_street_txt=row[15],
            student_house_txt=row[16], student_building_no=null_check(row[17]),
            student_structure_no=null_check(row[18]), student_flat_nm=smart_int(row[19]),
            payer_surname_txt=row[21], payer_name_txt=row[22], payer_father_name_txt=row[23], payer_inn_no=row[36],
            payer_phone_no=row[37], payer_document_no=row[25], payer_document_series=null_check(row[24]),
            payer_document_type_txt=row[40], payer_authority_no=row[27], payer_authority_txt=row[26],
            payer_issue_dt=datetime.datetime.strptime(row[28], '%d.%m.%Y').date(),
            payer_region_cd=int(str(row[29]).split(' ')[0]), payer_city_txt=row[30], payer_street_txt=row[31],
            payer_house_txt=row[32], payer_building_no=null_check(row[33]), payer_structure_no=null_check(row[34]),
            payer_flat_nm=smart_int(row[35]),
            courses=courses_vals
        )
        new_elem.save()
        email = EmailMessage('Договора платных курсов', 'Письмо прислано автоматически, не отвечайте на него',
                             'cspcapp@gmail.com', [row[41]])
        email.content_subtype = 'html'
        new_num = 1
        for i in generate_contract_pdf_unchecked(new_elem):
            email.attach(f"contract_{new_num}.pdf", i, 'application/pdf')
            new_num += 1
        email.send()

    sheet.values().clear(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=range).execute()

    range = 'student_14_lower_form_answers!A2:AB1102'

    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=range).execute()
    values = result.get('values', [])

    for row in values:
        if len(row) == 0:
            continue
        courses_vals = ' '.join([i.split(' ')[0] for i in ''.join(row[26]).split(', ')])
        new_elem = StudentRequest(
            is_two_side=False, student_surname_txt=row[1], student_name_txt=row[2], student_father_name_txt=row[3],
            student_birth_dt=datetime.datetime.strptime(row[4], '%d.%m.%Y').date(), student_class=row[5],
            student_school_name_txt=row[6], student_liter=row[7],
            payer_surname_txt=row[8], payer_name_txt=row[9], payer_father_name_txt=row[10], payer_inn_no=row[24],
            payer_phone_no=row[25], payer_document_no=row[13], payer_document_series=null_check(row[12]),
            payer_document_type_txt=row[14], payer_authority_no=row[15], payer_authority_txt=row[16],
            payer_issue_dt=datetime.datetime.strptime(row[16], '%d.%m.%Y').date(),
            payer_region_cd=int(str(row[17]).split(' ')[0]), payer_city_txt=row[18], payer_street_txt=row[19],
            payer_house_txt=row[20], payer_building_no=null_check(row[21]), payer_structure_no=null_check(row[22]),
            payer_flat_nm=smart_int(row[23]),
            courses=courses_vals
        )
        new_elem.save()

        email = EmailMessage('Договора платных курсов', 'Письмо прислано автоматически, не отвечайте на него',
                             'cspcapp@gmail.com', [row[27]])
        email.content_subtype = 'html'
        new_num = 1
        for i in generate_contract_pdf_unchecked(new_elem):
            email.attach(f"contract_{new_num}.pdf", i, 'application/pdf')
            new_num += 1
        email.send()

    sheet.values().clear(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=range).execute()

    return HttpResponse()


def update_form_info(reuqest: WSGIRequest) -> HttpResponse:
    service = open_spreadsheet()

    values = [[str(i) + " " + j] for i, j in REGIONS_DICT.items()]
    body = {'values': values}
    result = service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range='regions_list!A2:A100',
        valueInputOption='RAW',
        body=body).execute()

    service = open_spreadsheet()

    values = [[
        f"{i.pk} {i.course.sphere_txt} {i.course.name_txt} {i.course.short_nm} - {i.teacher_person.person_surname_txt} "
        f"{i.teacher_person.person_name_txt} {i.teacher_person.person_father_name_txt or ''} {i.get_week_days_str}"]
        for i in CourseElement.objects.all()
    ]
    body = {'values': values}
    result = service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range='course_list!A2:A100',
        valueInputOption='RAW',
        body=body).execute()

    return HttpResponse()
