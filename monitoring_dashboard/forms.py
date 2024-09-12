# # forms.py
# from django import forms
# from django.contrib.auth.models import User

# class UserRegistrationForm(forms.ModelForm):
#     first_name = forms.CharField(max_length=30, required=True, help_text='First Name')
#     middle_name = forms.CharField(max_length=30, required=False, help_text='Middle Name')
#     last_name = forms.CharField(max_length=30, required=True, help_text='Family Name')
#     position = forms.CharField(max_length=30, required=True, help_text='Position')
#     email = forms.EmailField(max_length=254, required=True, help_text='Email')
#     password = forms.CharField(widget=forms.PasswordInput, required=True)

#     class Meta:
#         model = User
#         fields = ['username', 'first_name', 'middle_name', 'last_name', 'position', 'email', 'password']


# ======> Changed to include the role filed in the registration form <=======
# forms.py
from django import forms
from .models import CustomUser, Schedule, CNCMachine
from django.forms import modelformset_factory
from .models import UploadedFile

class UserRegistrationForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True, help_text='First Name')
    middle_name = forms.CharField(max_length=30, required=False, help_text='Middle Name')
    last_name = forms.CharField(max_length=30, required=True, help_text='Family Name')
    position = forms.CharField(max_length=30, required=True, help_text='Position')
    email = forms.EmailField(max_length=254, required=True, help_text='Email')
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    role = forms.ChoiceField(choices=CustomUser.ROLES, required=True, help_text='Role')

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'middle_name', 'last_name', 'position', 'email', 'password', 'role']



class ScheduleForm(forms.ModelForm):
    cnc_machine = forms.ModelChoiceField(queryset=CNCMachine.objects.all(), required=True)
    # files = forms.ClearableFileInput(attrs={'multiple': True})  # Allows multiple file uploads
    # files = forms.ClearableFileInput()
    # files = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required=False)

    class Meta:
        model = Schedule
        fields = ['start_date', 'end_date', 'product_type', 'quantity', 'operator_name', 'cnc_machine', 'urgent']
        widgets = {
            'urgent': forms.CheckboxInput(attrs={'class': 'urgent-checkbox'}),
        }

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['files'].widget.attrs.update({'multiple': True})

# # Create a formset for handling multiple file uploads
# UploadedFileFormSet = modelformset_factory(
#     UploadedFile,
#     fields=('file', 'description'),
#     extra=1,  # You can adjust this number
#     widgets={'file': forms.ClearableFileInput(attrs={'multiple': True})}
# )


# from django import forms
# from django.contrib.auth.forms import PasswordResetForm

# class CustomPasswordResetForm(PasswordResetForm):
#     email = forms.EmailField(max_length=254, widget=forms.EmailInput(attrs={'placeholder': 'Enter your email'}))


from django import forms
from .models import Instrument, ThreadRing, ThreadPlug, SmoothGauge

class InstrumentForm(forms.ModelForm):
    class Meta:
        model = Instrument
        fields = '__all__'

class ThreadRingForm(forms.ModelForm):
    class Meta:
        model = ThreadRing
        fields = '__all__'

# Similar forms for ThreadPlug and SmoothGauge
class ThreadPlugForm(forms.ModelForm):
    class Meta:
        model = ThreadPlug
        fields = '__all__'

class SmoothGaugeForm(forms.ModelForm):
    class Meta:
        model = SmoothGauge
        fields = '__all__'
