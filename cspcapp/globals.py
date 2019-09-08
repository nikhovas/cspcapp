from .models import Course, CourseElement, AuthUserXPerson

courses = Course.objects.all()
course_elements = CourseElement.objects.all()
teachers: AuthUserXPerson.objects.all()
