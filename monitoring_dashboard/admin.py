from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Profile
from .models import Instrument, ThreadRing, ThreadPlug, SmoothGauge

# Register your models here.

# #  =====> Added to generate the QR codes for the operators <=======
# from django.contrib import admin
# from django.utils.safestring import mark_safe
# import qrcode
# from io import BytesIO
# from django.core.files.uploadedfile import InMemoryUploadedFile
# from .models import OperatorProfile

# class OperatorProfileAdmin(admin.ModelAdmin):
#     list_display = ('user', 'qr_token', 'qr_code_image')

#     def qr_code_image(self, obj):
#         qr = qrcode.make(obj.qr_token)
#         stream = BytesIO()
#         qr.save(stream)
#         qr_code = InMemoryUploadedFile(
#             stream, 'ImageField', f'{obj.user.username}.png', 'image/png', stream.getbuffer().nbytes, None
#         )
#         return mark_safe(f'<img src="data:image/png;base64,{qr_code.read().decode("utf-8")}" width="100" height="100" />')

# admin.site.register(OperatorProfile, OperatorProfileAdmin)


# ========> To register the users with roles in the admin page <==========

# class CustomUserAdmin(UserAdmin):
#     # Fields to be displayed in the user detail page in the admin
#     fieldsets = UserAdmin.fieldsets + (
#         (None, {'fields': ('role', 'middle_name', 'position', 'email')}),
#     )
    
#     # Fields to be displayed in the add user page in the admin
#     add_fieldsets = UserAdmin.add_fieldsets + (
#         (None, {'fields': ('username', 'password1', 'password2', 'role', 'middle_name', 'position', 'email')}),
#     )
    
#     # Fields to be displayed in the user list in the admin
#     list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')

#     # Fields to be used for filtering in the user list in the admin
#     search_fields = ('username', 'first_name', 'last_name', 'email')

# admin.site.register(CustomUser, CustomUserAdmin)
# admin.site.register(Profile)


# class CustomUserAdmin(UserAdmin):
#     # Fields to be displayed in the user detail page in the admin
#     fieldsets = (
#         (None, {'fields': ('username', 'password')}),
#         ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
#         ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser',
#                                     'groups', 'user_permissions')}),
#         ('Important dates', {'fields': ('last_login', 'date_joined')}),
#         ('Additional info', {'fields': ('role', 'middle_name', 'position')}),
#     )
    
#     # Fields to be displayed in the add user page in the admin
#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': ('username', 'password1', 'password2', 'role', 'first_name', 'last_name', 'middle_name', 'position', 'email'),
#         }),
#     )
    
#     # Fields to be displayed in the user list in the admin
#     list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')

#     # Fields to be used for filtering in the user list in the admin
#     search_fields = ('username', 'first_name', 'last_name', 'email')

# admin.site.register(CustomUser, CustomUserAdmin)
# admin.site.register(Profile)

class CustomUserAdmin(UserAdmin):
    # Fields to be displayed in the user detail page in the admin
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),  # Remove 'groups' and 'user_permissions'
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Additional info', {'fields': ('role', 'middle_name', 'position')}),
    )

    # Fields to be displayed in the add user page in the admin
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'role', 'first_name', 'last_name', 'middle_name', 'position', 'email'),
        }),
    )

    # Fields to be displayed in the user list in the admin
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')

    # Fields to be used for filtering in the user list in the admin
    search_fields = ('username', 'first_name', 'last_name', 'email')

admin.site.register(CustomUser, CustomUserAdmin)


admin.site.register(Instrument)
admin.site.register(ThreadRing)
admin.site.register(ThreadPlug)
admin.site.register(SmoothGauge)


from .models import CNCMachine

@admin.register(CNCMachine)
class CNCMachineAdmin(admin.ModelAdmin):
    list_display = ('name', 'manufacturer', 'maintenance_company', 'location', 'image')
    search_fields = ('name', 'manufacturer', 'maintenance_company', 'location')