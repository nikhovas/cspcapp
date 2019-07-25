from django.conf.urls import url, include
from . import views
from . import api_requests


urlpatterns = [
    url(r'^student/detail/(?P<pk>\S+)/$', views.student_detail_view, name='cspcapp_student_detail'),
    url(r'^base/$', views.meta_base_view, name='cspcapp_base'),
    url(r'^api/payment_add/', api_requests.payment_add, name='payment_add'),
    url(r'^api/add_new_contract/', api_requests.add_new_contract, name='add_new_contract'),
    url(r'^api/edit/(?P<object_type>\S+)/$', api_requests.data_edit, name='data_edit'),
    url(r'^api/delete/contract/$', api_requests.contract_delete, name='contract_delete'),
    url(r'^api/delete/payment/$', api_requests.payment_delete, name='payment_delete'),
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^courses/$', views.courses_view, name='cspcapp_courses_view'),
    url(r'^teachers/$', views.teachers_view, name='cspcapp_teachers_view'),
    url(r'^', views.students_overview, name='cspcapp_students_overview')
]



# urlpatterns += (
#     # urls for Student
#
#     url(r'^students/$', views.StudentListView, name='CSPCApp_student_list'),
#     url(r'^student/create/$', views.StudentCreateView, name='CSPCApp_student_create'),
#     url(r'^student/detail/(?P<pk>\S+)/$', views.StudentDetailView, name='CSPCApp_student_detail'),
#     url(r'^student/update/(?P<pk>\S+)/$', views.StudentUpdateView, name='CSPCApp_student_update'),
# )
#
# urlpatterns += (
#     # urls for Course
#     url(r'^course/$', views.CourseListView, name='CSPCApp_course_list'),
#     url(r'^course/create/$', views.CourseCreateView.as_view(), name='CSPCApp_course_create'),
#     url(r'^course/detail/(?P<pk>\S+)/$', views.CourseDetailView, name='CSPCApp_course_detail'),
#     url(r'^course/update/(?P<pk>\S+)/$', views.CourseUpdateView, name='CSPCApp_course_update'),
# )
#
# urlpatterns += (
#     # urls for CourseObject
#     url(r'^courseobject/$', views.CourseObjectListView.as_view(), name='CSPCApp_courseobject_list'),
#     url(r'^courseobject/create/$', views.CourseObjectCreateView, name='CSPCApp_courseobject_create'),
#     url(r'^courseobject/detail/(?P<pk>\S+)/$', views.CourseObjectDetailView.as_view(), name='CSPCApp_courseobject_detail'),
#     url(r'^courseobject/update/(?P<pk>\S+)/$', views.CourseObjectUpdateView.as_view(), name='CSPCApp_courseobject_update'),
# )
#
# urlpatterns += (
#     # urls for ContractEndInfo
#     url(r'^contractendinfo/$', views.ContractEndInfoListView.as_view(), name='CSPCApp_contractendinfo_list'),
#     url(r'^contractendinfo/create/$', views.ContractEndInfoCreateView.as_view(), name='CSPCApp_contractendinfo_create'),
#     url(r'^contractendinfo/detail/(?P<pk>\S+)/$', views.ContractEndInfoDetailView.as_view(), name='CSPCApp_contractendinfo_detail'),
#     url(r'^contractendinfo/update/(?P<pk>\S+)/$', views.ContractEndInfoUpdateView.as_view(), name='CSPCApp_contractendinfo_update'),
# )
#
# urlpatterns += (
#     url(r'^contractPrintPage/(?P<contrid>\S+)/(?P<stid>\S+)/(?P<relid>\S+)/$', views.contractPrintPage, name='CSPCApp_contractPrintPage'),
#     url(r'^xls/$', views.xlsFileGet, name='CSPCApp_xlsFileGet'),
#     url(r'^student_full_list/$', views.StudentFullList, name='CSPCApp_student_full_list'),
#     url(r'^ajaxStudentPersonUpdate/$', views.ajaxStudentPersonUpdate, name='ajaxStudentPersonUpdate'),
#
#     url(r'^saveStudentPersonData/$', views.saveStudentPersonData, name='saveStudentPersonData'),
#     url(r'^saveRelativePersonData/$', views.saveRelativePersonData, name='saveRelativePersonData'),
#     url(r'^saveCourseObjectData/$', views.saveCourseObjectData, name='saveCourseObjectData'),
#     url(r'^saveCourseData/$', views.saveCourseData, name='saveCourseData'),
#     # url(r'^addCourse/$', views.addCourse, name='addCourse'),
#
#     url(r'^', views.mainPage, name='mainPage'),
# )
