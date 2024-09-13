from django.db import models
from django.contrib.auth.models import User

# Create your models here.
# monitoring_dashboard/dashboard/models.py

# class Profile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     middle_name = models.CharField(max_length=30, blank=True, null=True)
#     position = models.CharField(max_length=30)
#     email = models.EmailField(max_length=254)
#     def __str__(self):
#         return self.user.username

from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils import timezone

# class User(AbstractUser):
#     ROLES = (
#         ('operator', 'Operator'),
#         ('regular', 'Regular'),
#     )
#     role = models.CharField(max_length=10, choices=ROLES, default='regular')
#     user = models.OneToOneField(User, on_delete=models.CASCADE,default="Not Provided")
#     middle_name = models.CharField(max_length=30, blank=True, null=True, default="Not Provided")
#     position = models.CharField(max_length=30, default="Not Provided")
#     email = models.EmailField(max_length=254, default="Not Provided")

#     groups = models.ManyToManyField(Group, related_name='custom_user_set')
#     user_permissions = models.ManyToManyField(Permission, related_name='custom_user_set')

#     def __str__(self):
#         return self.username

# # class User(AbstractUser):
# #     ROLES = (
# #         ('operator', 'Оператор'),
# #         ('manager', 'Руководитель'),
# #         ('regular_user', 'Обычный пользователь'),
# #         ('admin', 'Admin'),
# #     )
# #     role = models.CharField(max_length=20, choices=ROLES, default='regular_user')


# class Profile(models.Model):
#     # user = models.OneToOneField(User, on_delete=models.CASCADE)
#     user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
#     first_name = models.CharField(max_length=30)
#     middle_name = models.CharField(max_length=30, blank=True, null=True)
#     last_name = models.CharField(max_length=30)
#     position = models.CharField(max_length=30)
#     email = models.EmailField()

#     def __str__(self):
#         return self.user.username

# from django.db.models.signals import post_save
# from django.dispatch import receiver

# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)

# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     instance.profile.save()

from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

class CustomUser(AbstractUser):
    ROLES = (
        ('operator', 'Оператор'),
        ('manager', 'Руководитель'),
        ('regular_user', 'Обычный пользователь'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=20, choices=ROLES, default='regular_user')
    middle_name = models.CharField(max_length=30, blank=True, null=True, default="Not Provided")
    position = models.CharField(max_length=30, default="Not Provided")
    email = models.EmailField(max_length=254, default="Not Provided")

    groups = models.ManyToManyField(Group, related_name='custom_user_set')
    user_permissions = models.ManyToManyField(Permission, related_name='custom_user_set')

    def __str__(self):
        return self.username

# class Shift(models.Model):
#     DAY_SHIFT = 'day'
#     NIGHT_SHIFT = 'night'
#     SHIFT_CHOICES = (
#         (DAY_SHIFT, 'Day Shift'),
#         (NIGHT_SHIFT, 'Night Shift'),
#     )

#     user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='shifts')
#     shift_type = models.CharField(max_length=5, choices=SHIFT_CHOICES, default=DAY_SHIFT)
#     date = models.DateField()
#     start_time = models.TimeField()
#     end_time = models.TimeField()
#     notes = models.TextField(blank=True, null=True)

#     def __str__(self):
#         return f'{self.user.username} - {self.date} - {self.get_shift_type_display()}'

#     # def get_duration(self):
#     #     start = datetime.combine(self.date, self.start_time)
#     #     end = datetime.combine(self.date, self.end_time)
#     #     duration = (end - start).seconds / 3600  # duration in hours
#     #     return duration
#     def get_duration(self):
#         start = datetime.combine(self.date, self.start_time)
#         end = datetime.combine(self.date, self.end_time)
#         duration = (end - start).total_seconds()  # duration in seconds
#         return duration



#     # @classmethod
#     # def total_hours_for_user(cls, user, month, year):
#     #     shifts = cls.objects.filter(user=user, date__month=month, date__year=year)
#     #     total_hours = sum(shift.get_duration() for shift in shifts)
#     #     return total_hours
#     @classmethod
#     def total_hours_for_user(cls, user, month, year):
#         shifts = cls.objects.filter(user=user, date__month=month, date__year=year)
#         total_seconds = sum(shift.get_duration() for shift in shifts)
        
#         hours = total_seconds // 3600
#         seconds = total_seconds % 3600
#         minutes = seconds // 60
#         seconds = seconds % 60
        
#         return f"{int(hours)} hours and {int(minutes)} minutes and {int(seconds)} seconds"

class Shift(models.Model):
    DAY_SHIFT = 'day'
    NIGHT_SHIFT = 'night'
    SHIFT_CHOICES = (
        (DAY_SHIFT, 'Day Shift'),
        (NIGHT_SHIFT, 'Night Shift'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='shifts')
    shift_type = models.CharField(max_length=5, choices=SHIFT_CHOICES, default=DAY_SHIFT)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    overtime_start_time = models.TimeField(null=True, blank=True)
    overtime_end_time = models.TimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} - {self.date} - {self.get_shift_type_display()}'

    def get_duration(self):
        start = datetime.combine(self.date, self.start_time)
        end = datetime.combine(self.date, self.end_time)
        duration = (end - start).total_seconds()  # duration in seconds
        return duration

    def get_overtime_duration(self):
        if self.overtime_start_time and self.overtime_end_time:
            overtime_start = datetime.combine(self.date, self.overtime_start_time)
            overtime_end = datetime.combine(self.date, self.overtime_end_time)
            overtime_duration = (overtime_end - overtime_start).total_seconds()  # duration in seconds
            return overtime_duration
        return 0

    @classmethod
    def total_hours_for_user(cls, user, month, year):
        shifts = cls.objects.filter(user=user, date__month=month, date__year=year)
        total_shift_seconds = sum(shift.get_duration() for shift in shifts)
        total_overtime_seconds = sum(shift.get_overtime_duration() for shift in shifts)
        
        # Calculate total shift hours
        shift_hours = total_shift_seconds // 3600
        shift_minutes = (total_shift_seconds % 3600) // 60
        shift_seconds = total_shift_seconds % 60
        
        # Calculate total overtime hours
        overtime_hours = total_overtime_seconds // 3600
        overtime_minutes = (total_overtime_seconds % 3600) // 60
        overtime_seconds = total_overtime_seconds % 60
        
        return {
            "shift_hours": f"{int(shift_hours)} hours and {int(shift_minutes)} minutes and {int(shift_seconds)} seconds",
            "overtime_hours": f"{int(overtime_hours)} hours and {int(overtime_minutes)} minutes and {int(overtime_seconds)} seconds"
        }




class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    first_name = models.CharField(max_length=30)
    middle_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30)
    position = models.CharField(max_length=30)
    email = models.EmailField()

    def __str__(self):
        return self.user.username

from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


# # =====> Added to implement the QR code for CNC cards <======
# from django.contrib.auth.models import User
# from django.db import models
# import uuid

# class OperatorProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     qr_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

# # Signal to create or update profile
# from django.db.models.signals import post_save
# from django.dispatch import receiver

# @receiver(post_save, sender=User)
# def create_or_update_operator_profile(sender, instance, created, **kwargs):
#     if created:
#         OperatorProfile.objects.create(user=instance)
#     instance.operatorprofile.save()



class ProductionSchedule(models.Model):
    date = models.DateField()
    product_type = models.CharField(max_length=100)
    quantity = models.IntegerField()

class CNCMachine(models.Model):
    name = models.CharField(max_length=255)
    manufacturer = models.CharField(max_length=255)
    maintenance_company = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    image = models.ImageField(upload_to='cnc_machines/', null=True, blank=True)

    def __str__(self):
        return self.name

# class Schedule(models.Model):
#     date = models.DateField()
#     product_type = models.CharField(max_length=100)
#     quantity = models.PositiveIntegerField()
#     operator_name = models.CharField(max_length=200)
#     cnc_machine = models.CharField(max_length=100)
#     # def __str__(self):
#     #     return f"{self.date} - {self.product_type} - {self.operator} - {self.cnc_machine}"

import os
from django.utils.timezone import now

# def custom_upload_to(instance, filename):
#     # Extract relevant data from the instance
#     today = now().strftime('%Y/%m/%d')  # Format: Year/Month/Day
#     cnc_machine = instance.cnc_machine.name if instance.cnc_machine else 'default_cnc'
#     product_type = instance.product_type.replace(' ', '_')  # Replace spaces in product_type with underscores

#     # Construct the file path
#     # file_ext = filename.split('.')[-1]  # Get the file extension
#     new_filename = f"{today}/{cnc_machine}/{product_type}/{filename}"
    
#     return os.path.join('uploads/production_files', new_filename)

def custom_upload_to(instance, filename):
    # Ensure we access the Schedule instance attributes correctly
    schedule = instance.schedule
    today = now().strftime('%Y/%m/%d')  # Format: Year/Month/Day
    cnc_machine = schedule.cnc_machine.name if schedule and schedule.cnc_machine else 'default_cnc'
    product_type = schedule.product_type.replace(' ', '_') if schedule else 'default_product'

    # Construct the file path
    new_filename = f"{today}/{cnc_machine}/{product_type}/{filename}"
    
    return os.path.join('uploads/production_files', new_filename)

from datetime import datetime, timedelta
# =====> added this one to also have the end date
class Schedule(models.Model):
    start_date = models.DateField()
    end_date = models.DateField(default=timezone.now)
    product_type = models.CharField(max_length=255)
    quantity = models.IntegerField()
    operator_name = models.CharField(max_length=255)
    planner_comment = models.CharField(max_length=510, null=True, blank=True)
    cnc_machine = models.ForeignKey(CNCMachine, on_delete=models.CASCADE) # Added the foreign key to connect the CNCMachine table with the Schedule table in the DB
    files = models.ManyToManyField('UploadedFile', blank=True, related_name='schedules')
    urgent = models.BooleanField(default=False)  # Added field to indicate urgency
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    comments = models.TextField(null=True, blank=True)
    time_taken = models.FloatField(null=True, blank=True)  # Time in minutes
    is_completed = models.BooleanField(default=False)  # New field for completion status
    order_num = models.CharField(max_length=255, null=True)
    limtz = models.CharField(max_length=255, null=True)
    details_quantity = models.IntegerField(null=True) # the operator defines how many did they produce
    details_time = models.CharField(max_length=255, null=True) # The operator defines how much time they spend per detail produced

    # New fields for tracking pauses and elapsed time
    elapsed_time = models.IntegerField(default=0)  # Total elapsed time in minutes
    last_pause_time = models.DateTimeField(null=True, blank=True)  # Last time the work was paused
    is_paused = models.BooleanField(default=False)  # To track if the schedule is paused


    def __str__(self):
        return f'{self.product_type} scheduled from {self.start_date} to {self.end_date}'
    
# # ======> To register the time operator spends on the schedule (for pause and resume button) <========
# class TimerState(models.Model):
#     schedule = models.OneToOneField(Schedule, on_delete=models.CASCADE)
#     state = models.CharField(max_length=20)
#     elapsed_time = models.BigIntegerField(default=0)

# class UploadedFile(models.Model):
#     file = models.FileField(upload_to=custom_upload_to)
#     description = models.CharField(max_length=255, blank=True)

class UploadedFile(models.Model):
    file = models.FileField(upload_to=custom_upload_to)
    description = models.CharField(max_length=255, blank=True)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='uploaded_files', null=True, blank=True)

    def __str__(self):
        return self.file.name


from django.db import models
from django.utils import timezone

class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']


class InventoryItem(models.Model):
    name = models.CharField(max_length=100)
    net_weight = models.FloatField()
    supplier = models.CharField(max_length=100)
    manufacturing_date = models.DateField()
    expiration_date = models.DateField()
    quantity = models.IntegerField()
    stock_level = models.CharField(max_length=10)

# class FinishedProduct(models.Model):
#     name = models.CharField(max_length=100)
#     net_weight = models.FloatField()
#     manufacturing_date = models.DateField()
#     expiration_date = models.DateField()
#     quantity = models.IntegerField()
#     stock_level = models.CharField(max_length=10)

# class Material(models.Model):
#     item = models.CharField(max_length=255)
#     net_weight = models.CharField(max_length=255)
#     supplier = models.CharField(max_length=255)
#     manufacturing_date = models.DateField()
#     expiration_date = models.DateField()
#     quantity = models.IntegerField()
#     location = models.CharField(max_length=255)
#     stock_level = models.CharField(max_length=50)

#     def __str__(self):
#         return self.item

# from django.db import models

class Material(models.Model):
    item = models.CharField(max_length=100)
    net_weight = models.DecimalField(max_digits=10, decimal_places=2)
    # net_weight = models.CharField(max_length=255)
    supplier = models.CharField(max_length=100)
    manufacturing_date = models.DateField()
    expiration_date = models.DateField()
    quantity = models.IntegerField()
    location = models.CharField(max_length=100)
    stock_level = models.CharField(max_length=50)

class FinishedProduct(models.Model):
    item = models.CharField(max_length=100)
    net_weight = models.DecimalField(max_digits=10, decimal_places=2)
    # supplier = models.CharField(max_length=100, default="Not Provided")
    supplier = models.CharField(max_length=100)
    manufacturing_date = models.DateField()
    expiration_date = models.DateField()
    quantity = models.IntegerField()
    # location = models.CharField(max_length=100, default="Not Provided")
    location = models.CharField(max_length=100)
    stock_level = models.CharField(max_length=50)

class DeliveredProduct(models.Model):
    item = models.CharField(max_length=100)
    net_weight = models.DecimalField(max_digits=10, decimal_places=2)
    supplier = models.CharField(max_length=100)
    manufacturing_date = models.DateField()
    expiration_date = models.DateField()
    quantity = models.IntegerField()
    location = models.CharField(max_length=100)
    stock_level = models.CharField(max_length=50)

class ProductionPlanBT(models.Model):
    up_num = models.CharField(max_length=20, null=True, blank=True)
    date = models.CharField(max_length=20, null=True, blank=True)
    order = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    limtz = models.CharField(max_length=50, null=True, blank=True)
    order_priority = models.CharField(max_length=100, null=True, blank=True)
    smz_chpu = models.CharField(max_length=50, null=True, blank=True)
    chpu_smz = models.CharField(max_length=50, null=True, blank=True)
    shipment = models.CharField(max_length=100, null=True, blank=True)
    operations = models.CharField(max_length=150, null=True, blank=True)
    time_for_piece = models.CharField(max_length=20, null=True, blank=True)
    time_for_batch = models.CharField(max_length=20, null=True, blank=True)
    planned_date_readiness = models.CharField(max_length=20, null=True, blank=True)
    ovk_manufacturing = models.CharField(max_length=50, null=True, blank=True)
    comments = models.CharField(max_length=255, null=True, blank=True)
    result = models.CharField(max_length=25, choices=[('Готово и отправлено', 'Готово и отправлено'), ('Не готово', 'Не готово')], default='Готово и отправлено')

    # class Meta:
    #     managed = False
    #     db_table = 'monitoring_dashboard_productionplanbt'  # Specify the actual table name in your database

    # def __str__(self):
    #     return f"monitoring_dashboard_productionplanbt id={self.id}"


class ProductionPlanTBS(models.Model):
    company = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    drawing = models.CharField(max_length=100, null=True, blank=True)
    quantity = models.CharField(max_length=30, null=True, blank=True)
    operation = models.CharField(max_length=150, null=True, blank=True)
    time_part = models.CharField(max_length=150, null=True, blank=True)
    time_batch = models.CharField(max_length=150, null=True, blank=True)
    price = models.CharField(max_length=150, null=True, blank=True)
    deadline = models.CharField(max_length=100, null=True, blank=True)
    comments = models.CharField(max_length=255, null=True, blank=True)
    result = models.CharField(max_length=25, choices=[('Готово и отправлено', 'Готово и отправлено'), ('Не готово', 'Не готово')], default='Готово и отправлено')


class ProductionPlanOVK(models.Model):
    # request_date = models.DateField(null=True)
    request_date = models.CharField(max_length=15, null=True, blank=True)
    request_num = models.CharField(max_length=100, null=True, blank=True)
    order_mum = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    limtz = models.CharField(max_length=50, null=True, blank=True)
    quantity = models.CharField(max_length=30, null=True, blank=True)
    operation = models.CharField(max_length=150, null=True, blank=True)
    comments = models.CharField(max_length=255, null=True, blank=True)
    result = models.CharField(max_length=25, choices=[('Готово и отправлено', 'Готово и отправлено'), ('Не готово', 'Не готово')], default='Готово и отправлено')



class Instrument(models.Model):
    name = models.CharField(max_length=255, verbose_name="Наименование")
    range = models.CharField(max_length=255, verbose_name="Диапазон")
    serial_number = models.CharField(max_length=255, verbose_name="Зав.номер")
    calibration_date = models.DateField(verbose_name="Дата поверки")
    storage = models.CharField(max_length=255, verbose_name="Хранение")
    note = models.TextField(blank=True, null=True, verbose_name="Примечание")

    def __str__(self):
        return self.name

# Choices for classifier field
CLASSIFIER_CHOICES = [
    ('Метрический', 'Метрический'),
    ('Конический', 'Конический'),
    ('Трубный', 'Трубный'),
    ('Трубная коническая', 'Трубная коническая')
]

class ThreadRing(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название")
    pr = models.CharField(max_length=255, verbose_name="ПР")
    ne = models.CharField(max_length=255, verbose_name="НЕ")
    location = models.CharField(max_length=255, verbose_name="Место")
    calibration_date = models.DateField(verbose_name="Дата поверки")
    passport = models.TextField(blank=True, null=True, verbose_name="Паспорт")
    classifier = models.CharField(max_length=50, choices=CLASSIFIER_CHOICES, verbose_name="Классификатор")


    def __str__(self):
        return self.name

class ThreadPlug(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название")
    pr = models.CharField(max_length=255, verbose_name="ПР")
    ne = models.CharField(max_length=255, verbose_name="НЕ")
    location = models.CharField(max_length=255, verbose_name="Место")
    calibration_date = models.DateField(verbose_name="Дата поверки")
    passport = models.TextField(blank=True, null=True, verbose_name="Паспорт")
    classifier = models.CharField(max_length=50, choices=CLASSIFIER_CHOICES, verbose_name="Классификатор")


    def __str__(self):
        return self.name

class SmoothGauge(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название")
    pr = models.CharField(max_length=255, verbose_name="ПР")
    ne = models.CharField(max_length=255, verbose_name="НЕ")
    location = models.CharField(max_length=255, verbose_name="Место")
    calibration_date = models.DateField(verbose_name="Дата поверки")
    passport = models.TextField(blank=True, null=True, verbose_name="Паспорт")
    classifier = models.CharField(max_length=50, choices=CLASSIFIER_CHOICES, verbose_name="Классификатор")


    def __str__(self):
        return self.name




# from django.dispatch import receiver
# from django.urls import reverse
# from django_rest_passwordreset.signals import reset_password_token_created
# from django.core.mail import send_mail, EmailMessage

# @receiver(reset_password_token_created)
# def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):

#     # the below like concatinates your websites reset password url and the reset email token which will be required at a later stage
#     email_plaintext_message = "Open the link to reset your password" + " " + "{}{}".format(instance.request.build_absolute_uri("http://localhost:3000/login#/reset-password-form/"), reset_password_token.key)
    
#     """
#         this below line is the django default sending email function, 
#         takes up some parameter (title(email title), message(email body), from(email sender), to(recipient(s))
#     """
#     send_mail(
#         # title:
#         "Password Reset for {title}".format(title="Crediation portal account"),
#         # message:
#         email_plaintext_message,
#         # from:
#         "info@yourcompany.com",
#         # to:
#         [reset_password_token.user.email],
#         fail_silently=False,
#     )



