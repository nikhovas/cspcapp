from django.db import models
from django.db import connection
from django.contrib.auth.models import User


class Contract(models.Model):
    contract_id = models.AutoField(primary_key=True)
    contract_dttm = models.DateTimeField()
    student_document = models.ForeignKey('PersonDocument', models.DO_NOTHING, blank=True, null=True,
                                         related_name='student_document')
    student_address = models.ForeignKey('PersonHomeAddress', models.DO_NOTHING, blank=True, null=True,
                                        related_name='student_address')
    student_phone_no = models.CharField(max_length=20, blank=True, null=True)
    payer_document = models.ForeignKey('PersonDocument', models.DO_NOTHING, blank=True, null=True,
                                       related_name='payer_document')
    payer_address = models.ForeignKey('PersonHomeAddress', models.DO_NOTHING, blank=True, null=True,
                                      related_name='payer_address')
    payer_phone_no = models.CharField(max_length=20, blank=True, null=True)
    payer_inn_no = models.CharField(max_length=12)
    course_element = models.ForeignKey('CourseElement', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'contract'


class ContractPayment(models.Model):
    contract_payment_id = models.AutoField(primary_key=True)
    payment_dt = models.DateField()
    payment_amt = models.IntegerField()
    contract = models.ForeignKey(Contract, models.DO_NOTHING, blank=True, null=True)
    payment_type = models.SmallIntegerField()
    voucher_no = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'contract_payment'


class ContractTermination(models.Model):
    contract = models.ForeignKey(Contract, models.DO_NOTHING, primary_key=True)
    termination_dt = models.DateField(blank=True, null=True)
    termination_reason_txt = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'contract_termination'


class Course(models.Model):
    course_id = models.AutoField(primary_key=True)
    sphere_txt = models.CharField(max_length=100, blank=True, null=True)
    direction = models.CharField(max_length=1, blank=True, null=True)
    name_txt = models.CharField(max_length=100)
    short_nm = models.CharField(max_length=20)
    price_per_hour = models.DecimalField(max_digits=65535, decimal_places=65535)
    number_of_hours = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'course'


class CourseClass(models.Model):
    course_class_id = models.AutoField(primary_key=True)
    week_day_txt = models.CharField(max_length=1)
    start_tm = models.TimeField()
    end_tm = models.TimeField()
    course_element = models.ForeignKey('CourseElement', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'course_class'


class CourseElement(models.Model):
    course_element_id = models.AutoField(primary_key=True)
    course = models.ForeignKey(Course, models.DO_NOTHING, blank=True, null=True)
    teacher_person = models.ForeignKey('Person', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'course_element'


class Person(models.Model):
    person_id = models.AutoField(primary_key=True)
    person_surname_txt = models.CharField(max_length=50)
    person_name_txt = models.CharField(max_length=50)
    person_father_name_txt = models.CharField(max_length=50, blank=True, null=True)
    birth_dt = models.DateField()

    class Meta:
        managed = False
        db_table = 'person'


class PersonDocument(models.Model):
    person_document_id = models.AutoField(primary_key=True)
    document_no = models.IntegerField()
    document_series = models.CharField(max_length=10, blank=True, null=True)
    document_type_txt = models.CharField(max_length=20)
    person = models.ForeignKey(Person, models.DO_NOTHING, blank=True, null=True)
    person_surname_txt = models.CharField(max_length=50)
    person_name_txt = models.CharField(max_length=50)
    person_father_name_txt = models.CharField(max_length=50, blank=True, null=True)
    authority_no = models.CharField(max_length=20)
    authority_txt = models.CharField(max_length=150)
    issue_dt = models.DateField()

    class Meta:
        managed = False
        db_table = 'person_document'


class PersonHomeAddress(models.Model):
    person_home_address_id = models.AutoField(primary_key=True)
    person = models.ForeignKey(Person, models.DO_NOTHING, blank=True, null=True)
    region_cd = models.SmallIntegerField()
    city_txt = models.CharField(max_length=50)
    street_txt = models.CharField(max_length=50)
    house_txt = models.CharField(max_length=10)
    building_no = models.CharField(max_length=10, blank=True, null=True)
    structure_no = models.CharField(max_length=10, blank=True, null=True)
    flat_nm = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'person_home_address'


class StudentPerson(models.Model):
    person = models.ForeignKey(Person, models.DO_NOTHING, primary_key=True)
    education_start_year = models.DateField(blank=True, null=True)
    school_name_txt = models.CharField(max_length=50, blank=True, null=True)
    liter = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'student_person'


# view models

class StudentsOverviewView(models.Model):
    person = models.ForeignKey(Person, models.DO_NOTHING, primary_key=True)
    person_surname_txt = models.CharField(max_length=50)
    person_name_txt = models.CharField(max_length=50)
    person_father_name_txt = models.CharField(max_length=50, blank=True, null=True)
    school_name_txt = models.CharField(max_length=50, blank=True, null=True)
    grade = models.SmallIntegerField()
    liter = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'students_overview_view'


class AuthUserXPerson(models.Model):
    auth_user = models.ForeignKey(User, models.DO_NOTHING, primary_key=True)
    person = models.ForeignKey('Person', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_x_person'
        unique_together = (('auth_user', 'person'),)
