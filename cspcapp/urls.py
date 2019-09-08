from django.conf.urls import url, include
from . import views
from . import api_requests
from . import dump_google_sheets
import django.contrib.auth.views

urlpatterns = [
    url(r'^base/$', views.meta_base_view, name='cspcapp_base'),
    url(r'^api/change_password/', api_requests.change_user_password, name='change_user_password'),
    url(r'^api/add_course_class/', api_requests.add_course_class, name='add_course_class'),
    url(r'^api/edit_course_class/', api_requests.edit_course_class, name='edit_course_class'),
    url(r'^api/delete_course_class/', api_requests.delete_course_class, name='delete_course_class'),
    url(r'^api/add/course_element/', api_requests.course_element_add, name='course_element_add'),
    url(r'^api/add/course_detail/', api_requests.course_detail_add, name='course_detail_add'),
    url(r'^api/add/(?P<object_type>\S+)/', api_requests.add_object, name='add_object'),
    url(r'^api/edit/(?P<object_type>\S+)/$', api_requests.data_edit, name='data_edit'),
    url(r'^api/delete/(?P<object_type>\S+)/$', api_requests.object_delete, name='object_delete'),
    url(r'^api/new_user/', api_requests.new_user, name='new_user'),
    url(r'^accounts/reg_request/$', views.reg_request, name='reg_request'),
    url(r'^accounts/', include('django_registration.backends.one_step.urls')),
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^courses/$', views.courses_view, name='cspcapp_courses_view'),
    url(r'^teachers/$', views.teachers_view, name='cspcapp_teachers_view'),
    url(r'^student_add/$', views.student_add_function, name='cspcapp_student_add'),
    url(r'^session_data/$', api_requests.get_session_data, name='get_session_data'),



    url(r'^contract/(?P<pk>\S+)/print/$', views.print_contract, name='contract_print'),

    url(r'^accounts/profile/$', views.account_settings, name='account_settings'),
    url(r'^registration_requests/submit/$', api_requests.submit_registration_form, name='registration_submit'),
    url(r'^registration_requests/$', views.registration_requests_list, name='registration_requests_list'),
    url(r'^students_requests/submit/$', api_requests.submit_student_form, name='student_submit'),
    url(r'^students_requests/$', views.students_request_list, name='students_request_list'),

    # google
    url(r'^google/api/update_form/$', dump_google_sheets.update_form_info, name='update_form_info'),
    url(r'^google/api/dump_data/$', dump_google_sheets.dump_to_local_database, name='dump_to_local_database'),

    url(r'^logout/$', django.contrib.auth.views.logout_then_login, {'login_url': '/accounts/login/'}, name='user_logout'),

    url(r'^(?P<model_name>\S+)/(?P<pk>\S+)/versions/$', views.versions, name='cspcapp_versions'),
    url(r'^(?P<model_name>\S+)/(?P<pk>\S+)/$', views.details, name='cspcapp_details'),

    url(r'^$', views.students_overview, name='cspcapp_students_overview'),


]