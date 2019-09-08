from django import template
from .models import StudentPerson, Person, CourseElement
register = template.Library()


@register.filter
def has_contract_with_teacher(obj: StudentPerson, teacher_user: Person):
    return len(CourseElement.objects.filter(contract__student_person=obj, teacher_person=teacher_user)) != 0

#
# @register.filter
# def (obj: StudentPerson, teacher_user: Person):
#     return len(CourseElement.objects.filter(contract__student_person=obj, teacher_person=teacher_user)) != 0
