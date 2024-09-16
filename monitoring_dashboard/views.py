from django.shortcuts import render, redirect
from django.apps import apps
# Create your views here.
from .models import ProductionSchedule, InventoryItem, FinishedProduct, DeliveredProduct, Material, Schedule, ProductionPlanBT, ProductionPlanTBS, ProductionPlanOVK
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from .models import Material
import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from django.core.mail import send_mail
from .forms import UserRegistrationForm
# from .forms import CustomUserCreationForm
from .models import Profile
from django.db import IntegrityError, connection
from monitoring_dashboard.models import Profile, CustomUser
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import AnonymousUser

from .opcua_client import read_cnc_status
from .mqtt_publisher import publish_status
import logging
import os

logger = logging.getLogger(__name__)

def update_cnc_status(request):
    if request.method == 'POST':
        # Process the request and get data
        cnc104_status = request.POST.get('cnc104_status', 'Active')
        cnc104_details = request.POST.get('cnc104_details', 'N/A')
        cnc104_time = request.POST.get('cnc104_time', 'N/A')
        cnc104_percent = request.POST.get('cnc104_percent', '50')
        cnc104_parts = request.POST.get('cnc104_parts', '27')
        
        cnc105_status = request.POST.get('cnc105_status', 'Idle')
        cnc105_details = request.POST.get('cnc105_details', 'N/A')
        cnc105_time = request.POST.get('cnc105_time', 'N/A')
        cnc105_percent = request.POST.get('cnc105_percent', '93')
        cnc105_parts = request.POST.get('cnc105_parts', '213')
        
        # Construct JSON response
        data = {
            'cnc104_status': cnc104_status,
            'cnc104_details': cnc104_details,
            'cnc104_time': cnc104_time,
            'cnc104_percent': cnc104_percent,
            'cnc104_parts': cnc104_parts,
            'cnc105_status': cnc105_status,
            'cnc105_details': cnc105_details,
            'cnc105_time': cnc105_time,
            'cnc105_percent': cnc105_percent,
            'cnc105_parts': cnc105_parts,
            # Add more variables as needed for additional CNC cards
        }
        
        # Return JSON response
        return JsonResponse(data)
    
    # Handle invalid requests
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def logout_view(request):
    logout(request)
    return redirect('landing')

def get_schedule(request):
    # Assuming we want to get all schedule details
    # schedules = Schedule.objects.all()
    schedules = Schedule.objects.all().select_related('cnc_machine').prefetch_related('files')
    
    data = [{
        'id': schedule.id,
        'startDate': schedule.start_date,
        'endDate': schedule.end_date,
        'productType': schedule.product_type,
        'quantity': schedule.quantity,
        'operatorName': schedule.operator_name,
        'cncMachine': {
            'id': schedule.cnc_machine.id,
            'name': schedule.cnc_machine.name,
            'manufacturer': schedule.cnc_machine.manufacturer,
            'maintenanceCompany': schedule.cnc_machine.maintenance_company,
            'location': schedule.cnc_machine.location
        },
        'files': [{'id': f.id, 'name': os.path.basename(f.file.name), 'url': f.file.url} for f in schedule.files.all()],  # Include file names
        # ========> Added the urgent for the sorting urgent schedules in the modal form when clicked in calendar cells <==============
        'urgent': schedule.urgent,  # Include urgent field
        'comments': schedule.comments,
        'startTime': schedule.start_time,
        'endTime': schedule.end_time,
        # 'timeTaken': schedule.time_taken,
        'completed': schedule.is_completed,
        'orderNum': schedule.order_num,
        'limtz': schedule.limtz,
        'is_paused': schedule.is_paused,
        'last_paused_time': schedule.last_pause_time,
        'timeTaken': schedule.elapsed_time,
        'details_quantity': schedule.details_quantity,
        'details_time': schedule.details_time,
        'planner_comment': schedule.planner_comment,

        
    } for schedule in schedules]
    return JsonResponse(data, safe=False)


# ========> This I wrote only for the cnc modal with pause/resume and timer functionality <========
def get_schedule_by_id(request, schedule_id):
    try:
        schedule = Schedule.objects.get(id=schedule_id)
        data = {
            'id': schedule.id,
            'startDate': schedule.start_date,
            'endDate': schedule.end_date,
            'productType': schedule.product_type,
            'quantity': schedule.quantity,
            'operatorName': schedule.operator_name,
            'cncMachine': {
                'id': schedule.cnc_machine.id,
                'name': schedule.cnc_machine.name,
                'manufacturer': schedule.cnc_machine.manufacturer,
                'maintenanceCompany': schedule.cnc_machine.maintenance_company,
                'location': schedule.cnc_machine.location
            },
            'files': [{'id': f.id, 'name': os.path.basename(f.file.name)} for f in schedule.files.all()],
            'urgent': schedule.urgent,
            'comments': schedule.comments,
            'startTime': schedule.start_time,
            'endTime': schedule.end_time,
            'timeTaken': schedule.time_taken,
            'completed': schedule.is_completed,
            'orderNum': schedule.order_num,
            'limtz': schedule.limtz,
            'is_paused': schedule.is_paused,
            'last_paused_time': schedule.last_pause_time,
            'total_elapsed_time': schedule.elapsed_time,
        }
        return JsonResponse(data)
    except Schedule.DoesNotExist:
        return JsonResponse({'error': 'Schedule not found'}, status=404)

@csrf_exempt
def planning(request):
    if request.user.role == 'operator':
        return redirect('unauthorized')
    production_schedule = Schedule.objects.all()
    production_plan_bt = ProductionPlanBT.objects.all()

    context = {
        'production_schedule': production_schedule,
        'production_plan_bt': production_plan_bt,
        'user': request.user
    }

    return render(request, 'monitoring_dashboard/planning.html', context)

@csrf_exempt
def shifts_page(request):
    # if request.user.role == 'operator' or request.user.role == 'regular_user':
    #     return redirect('unauthorized')
    position = getattr(request.user, 'position', 'Not Provided')
    production_schedule = Schedule.objects.all()
    production_plan_bt = ProductionPlanBT.objects.all()
    context = {
        'production_schedule': production_schedule,
        'production_plan_bt': production_plan_bt,
        'user': request.user,
        'user_position': position,
    }

    return render(request, 'monitoring_dashboard/shifts.html', context)

@csrf_exempt
def get_schedule_details(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        schedule_id = data.get('id')
        try:
            schedule = Schedule.objects.get(id=schedule_id)
            schedule_details = {
                'ID': schedule.id,
                'startDate': schedule.start_date,
                'endDate': schedule.end_date,
                'productType': schedule.product_type,
                'quantity': schedule.quantity,
                'operatorName': schedule.operator_name,
                'cncMachine': {
                    'id': schedule.cnc_machine.id,
                    'name': schedule.cnc_machine.name,
                },
                'orderNum': schedule.order_num,
                'limtz': schedule.limtz,

            }
            return JsonResponse({'success': True, 'schedule': schedule_details})
        except Schedule.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Schedule not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
def get_schedule_details_Timer_elapsed(request, schedule_id):
    if request.method == "GET":
        try:
            schedule = Schedule.objects.get(id=schedule_id)
            response_data = {
                'success': True,
                'elapsed_time': schedule.elapsed_time,  # Assuming this is in minutes
            }
            return JsonResponse(response_data)
        except Schedule.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Schedule not found'})
    return JsonResponse({'success': False})

@csrf_exempt
def get_schedule_calendarcell_urgent(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            ids = data.get('schedule_ids')
            print('here is the id from JS')
            print(ids)
            if not ids:
                return JsonResponse({'error': 'No IDs provided'}, status=400)

            schedules = Schedule.objects.filter(id__in=ids)
            data = [{
                'ID': schedule.id,
                'startDate': schedule.start_date,
                'endDate': schedule.end_date,
                'productType': schedule.product_type,
                'quantity': schedule.quantity,
                'operatorName': schedule.operator_name,
                'cncMachine': {
                    'id': schedule.cnc_machine.id,
                    'name': schedule.cnc_machine.name,
                },
                'urgent': schedule.urgent,  # Include urgent field
                'orderNum': schedule.order_num,
                'limtz': schedule.limtz,
            } for schedule in schedules]
            
            print("here is the data for urgent calendar cell")
            print(data)
            
            return JsonResponse(data, safe=False)
        except Schedule.DoesNotExist:
            return JsonResponse({'error': 'Schedule not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

# ====> This is for deleting from the table that shows the production schedule
@csrf_exempt
def delete_schedule_table(request, id):
    try:
        schedule = Schedule.objects.get(id=id)
        schedule.delete()
        return JsonResponse({'success': True})
    except Schedule.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Schedule not found'})

# ====> This is for deleting from the calendar that shows the production schedule
@csrf_exempt
def delete_schedule(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        schedule_id = data.get('id')
        try:
            schedule = Schedule.objects.get(id=schedule_id)
            schedule.delete()
            return JsonResponse({'success': True})
        except Schedule.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Schedule not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

import logging

logger = logging.getLogger(__name__)

@csrf_exempt
def update_schedule(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        print(f"Received data for updating schedule: {data}")
        try:
            schedule = Schedule.objects.get(id=data['id'])
            schedule.start_date = data['startDate']
            schedule.end_date = data['endDate']
            schedule.product_type = data['productType']
            schedule.quantity = data['quantity']
            schedule.operator_name = data['operatorName']
            schedule.order_num = data['orderNum']  # Order number
            schedule.limtz = data['limtz']  # limtz
            schedule.comments = data['comments']  # Comments
            if 'cncMachineId' in data:
                schedule.cnc_machine_id = data['cncMachineId']  # Use cncMachineId instead of name
            else:
                print("cncMachineId is missing from the data")
                return JsonResponse({'success': False, 'error': 'cncMachineId is missing'})
            schedule.urgent = data['urgent']
            schedule.save()


            # # Handle file uploads (if any)
            # files = request.FILES.getlist('files')
            # if files:
            #     uploaded_files = []
            #     for file in files:
            #         uploaded_file = UploadedFile.objects.create(file=file, schedule=schedule)
            #         uploaded_file.save()
            #         uploaded_files.append(uploaded_file)

            #     # Associate new files with the schedule
            #     schedule.files.set(uploaded_files)

            #     return JsonResponse({'success': True})
            

            return JsonResponse({'success': True})
        except Schedule.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Schedule not found'})
        except Exception as e:
            print(f"Exception while updating schedule: {e}")
            return JsonResponse({'success': False, 'error': str(e)})
        
@csrf_exempt
def upload_files(request):
    if request.method == 'POST':
        schedule_id = request.POST.get('id')
        try:
            # Get the schedule object
            schedule = Schedule.objects.get(id=schedule_id)
            
            # Get the already uploaded files for the schedule
            existing_files = schedule.files.all()

            # Print the list of already uploaded files in the console
            print("Already uploaded files for the schedule:")
            for file in existing_files:
                print(f"File Name: {file.file.name}, File URL: {file.file.url}")

            # Now, handle the new files being uploaded
            new_files = request.FILES.getlist('files')

            if new_files:
                uploaded_files = []
                for file in new_files:
                    uploaded_file = UploadedFile(file=file, schedule=schedule)
                    uploaded_file.save()
                    uploaded_files.append(uploaded_file)

                # Append the newly uploaded files to the schedule's existing files
                schedule.files.add(*uploaded_files)
                schedule.save()

            return JsonResponse({'success': True, 'message': 'Files uploaded successfully'})
        
        except Schedule.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Schedule not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def delete_file(request, file_id):
    if request.method == 'DELETE':
        try:
            file = UploadedFile.objects.get(id=file_id)
            file.delete()
            return JsonResponse({'success': True, 'message': 'File deleted successfully'})
        except UploadedFile.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'File not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.files.storage import default_storage
from .models import Schedule, CNCMachine, UploadedFile

@csrf_exempt
def add_schedule(request):
    if request.method == 'POST':
        start_date = request.POST.get('startDate')
        end_date = request.POST.get('endDate')
        product_type = request.POST.get('productType')
        quantity = request.POST.get('quantity')
        operator_name = request.POST.get('operatorName')
        cnc_machine_id = request.POST.get('cncMachine')
        urgent = request.POST.get('urgent') == 'on'
        order_num = request.POST.get('orderNum')
        limtz = request.POST.get('limtz')
        files = request.FILES.getlist('files')
        comments = request.POST.get('comment')

        try:
            cnc_machine = CNCMachine.objects.get(id=cnc_machine_id)
            schedule = Schedule(
                start_date=start_date,
                end_date=end_date,
                product_type=product_type,
                quantity=quantity,
                operator_name=operator_name,
                cnc_machine=cnc_machine,
                urgent=urgent,
                order_num=order_num,
                limtz=limtz,
                comments = comments
            )
            schedule.save()

            uploaded_files = []
            for file in files:
                uploaded_file = UploadedFile(file=file, schedule=schedule)
                uploaded_file.save()
                uploaded_files.append(uploaded_file)

            schedule.files.set(uploaded_files)
            schedule.save()

            # Create notifications for each operator
            operators = CustomUser.objects.filter(role='operator')
            for operator in operators:
                message = f'Добавлено новое График: {product_type} с {start_date} по {end_date}'
                if urgent:
                    message = 'СРОЧНО: ' + message
                notification = Notification(user=operator, schedule=schedule, message=message)
                notification.save()

            return JsonResponse({'success': True})
        
        except CNCMachine.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'CNC Machine not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})



# # ==================> Added this to employ each plan goes to responsible operator <========
from django.http import JsonResponse
from .models import CustomUser

def get_operators(request):
    operators = CustomUser.objects.filter(role='operator').values('username', 'first_name', 'last_name')
    operators_list = [{'username': operator['username'], 'full_name': f"{operator['first_name']} {operator['last_name']}"} for operator in operators]
    return JsonResponse({'operators': operators_list})


@csrf_exempt
def landing(request):
    return render(request, 'monitoring_dashboard/landing.html')

@login_required
def inventory(request):
    if request.user.role == 'operator':
        return redirect('unauthorized')
    return render(request, 'monitoring_dashboard/inventory.html')

# ===========> Added to include the role in the view <===============
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            first_name = form.cleaned_data['first_name']
            middle_name = form.cleaned_data['middle_name']
            last_name = form.cleaned_data['last_name']
            position = form.cleaned_data['position']
            role = form.cleaned_data['role']

            try:
                # Create and save the CustomUser instance
                user = CustomUser.objects.create_user(username=username, email=email, password=password)
                user.first_name = first_name
                user.middle_name = middle_name
                user.last_name = last_name
                user.position = position
                user.role = role  # Assign the selected role
                user.save()

                # Optionally create a profile
                Profile.objects.create(
                    user=user,
                    first_name=first_name,
                    middle_name=middle_name,
                    last_name=last_name,
                    position=position,
                    email=email,
                )

                # Log the user in and redirect to dashboard
                login(request, user)
                return redirect('inventory')

            except IntegrityError:
                return render(request, 'monitoring_dashboard/register.html', {
                    'form': form,
                    'error': 'Username or email already taken.'
                })
        else:
            return render(request, 'monitoring_dashboard/register.html', {
                'form': form,
                'error': 'Form is not valid. Please check the information provided.'
            })
    else:
        form = UserRegistrationForm()
    
    return render(request, 'monitoring_dashboard/register.html', {'form': form})


def reset_password_form(request, uid, token):
    if request.method == 'POST':
        print(request.body)  # Log the request body
    print(f"UID: {uid}, Token: {token}")
    return render(request, 'monitoring_dashboard/reset_password_form.html', {'uid': uid, 'token': token})




# signal_handlers.py

from django.conf import settings
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created
from django.dispatch import receiver
from django.core.mail import send_mail

@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    # Extract user details
    user = reset_password_token.user
    first_name = user.first_name
    middle_name = user.middle_name
    last_name = user.last_name
    user_id = user.id  # Get the user id
    token = reset_password_token.key  # Get the token key
    email = user.email  # Get the user's email

    # Construct the reset URL using `reverse` and proper URL parameters
    reset_url = f"{settings.DJANGO_REST_PASSWORDRESET_PROTOCOL}://{settings.DJANGO_REST_PASSWORDRESET_DOMAIN}{reverse('reset_password_form', kwargs={'uid': user_id, 'token': token})}"

    # Email content
    email_plaintext_message = f"""
    Здравствуйте {first_name} {middle_name} {last_name},

    Вы запросили сброс пароля. Пожалуйста, перейдите на следующую страницу и выберите новый пароль:

    {reset_url}

    Если вы не запрашивали это, пожалуйста, проигнорируйте это письмо.

    С уважением;,
    Команда Scope
    """

    # Send the email
    send_mail(
        # Subject
        "Password Reset for Your Account",
        # Message
        email_plaintext_message,
        # From email
        settings.DEFAULT_FROM_EMAIL,
        # To email
        [email]
    )




from django.core.mail import send_mail
from django.http import HttpResponse

def send_test_email(request):
    send_mail(
        'Test Email',
        'This is a test email.',
        'bahrami.a@zaobt.ru',
        ['bahrami.a@zaobt.ru'], #receiver email
        fail_silently=False,
    )
    return HttpResponse("Test email sent.")


from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import reverse_lazy

class CustomPasswordResetView(PasswordResetView):
    template_name = 'registration/password_reset_form.html'
    success_url = reverse_lazy('password_reset_done')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'is_popup': False,
            'is_nav_sidebar_enabled': False,
            'has_permission': True,  # Assuming the user always has permission in this context
            'site_title': 'My Site'
        })
        return context

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'registration/password_reset_done.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'is_popup': False,
            'is_nav_sidebar_enabled': False,
            'has_permission': True,
            'site_title': 'My Site'
        })
        return context

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'registration/password_reset_confirm.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'is_popup': False,
            'is_nav_sidebar_enabled': False,
            'has_permission': True,
            'site_title': 'My Site'
        })
        return context

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'registration/password_reset_complete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'is_popup': False,
            'is_nav_sidebar_enabled': False,
            'has_permission': True,
            'site_title': 'My Site'
        })
        return context


    

@csrf_exempt
def add_material(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        item = data.get('item')
        net_weight = data.get('netWeight')
        supplier = data.get('supplier')
        manufacturing_date = data.get('manufacturingDate')
        expiration_date = data.get('expirationDate')
        quantity = data.get('quantity')
        location = data.get('location')

        # Determine stock level
        if 500 <= int(quantity) < 900:
            stock_level = 'Mid'
        elif 0 <= int(quantity) < 500:
            stock_level = 'Low'
        else:
            stock_level = 'Full'

        # Insert into the database
        Material.objects.create(
            item=item,
            net_weight=net_weight,
            supplier=supplier,
            manufacturing_date=manufacturing_date,
            expiration_date=expiration_date,
            quantity=quantity,
            location=location,
            stock_level=stock_level
        )

        return JsonResponse({'success': True})
    return JsonResponse({'success': False})


@csrf_exempt
def add_finished_product(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        item = data.get('item')
        net_weight = data.get('netWeight')
        supplier = data.get('supplier')
        manufacturing_date = data.get('manufacturingDate')
        expiration_date = data.get('expirationDate')
        quantity = data.get('quantity')
        location = data.get('location')

        # Determine stock level
        if 500 <= int(quantity) < 900:
            stock_level = 'Mid'
        elif 0 <= int(quantity) < 500:
            stock_level = 'Low'
        else:
            stock_level = 'Full'

        # Insert into the database
        FinishedProduct.objects.create(
            item=item,
            net_weight=net_weight,
            supplier=supplier,
            manufacturing_date=manufacturing_date,
            expiration_date=expiration_date,
            quantity=quantity,
            location=location,
            stock_level=stock_level
        )

        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@csrf_exempt
def add_delivered_product(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        item = data.get('item')
        net_weight = data.get('netWeight')
        supplier = data.get('supplier')
        manufacturing_date = data.get('manufacturingDate')
        expiration_date = data.get('expirationDate')
        quantity = data.get('quantity')
        location = data.get('location')

        # Determine stock level
        if 500 <= int(quantity) < 900:
            stock_level = 'Mid'
        elif 0 <= int(quantity) < 500:
            stock_level = 'Low'
        else:
            stock_level = 'Full'

        # Insert into the database
        DeliveredProduct.objects.create(
            item=item,
            net_weight=net_weight,
            supplier=supplier,
            manufacturing_date=manufacturing_date,
            expiration_date=expiration_date,
            quantity=quantity,
            location=location,
            stock_level=stock_level
        )

        return JsonResponse({'success': True})
    return JsonResponse({'success': False})



def inventory(request):
    if request.user.role == 'operator':
        return redirect('unauthorized')
    materials = Material.objects.all()
    finished_products = FinishedProduct.objects.all()
    delivered_products = DeliveredProduct.objects.all()
    total_materials_count = materials.count()
    total_finished_products = finished_products.count()
    total_delivered_products = delivered_products.count()
    return render(request, 'monitoring_dashboard/inventory.html', {
        'materials': materials,
        'finished_products': finished_products,
        'delivered_products': delivered_products,
        'total_materials' : total_materials_count,
        'total_finished_products' : total_finished_products,
        'total_delivered_products' : total_delivered_products
    })


def get_materials_chart_data(request):
    data = Material.objects.all()
    full = data.filter(quantity__gte=900).count()
    mid = data.filter(quantity__gte=500, quantity__lt=900).count()
    low = data.filter(quantity__lt=500).count()
    return JsonResponse({
        'labels': ['Full', 'Mid', 'Low'],
        'data': [full, mid, low],
    })


# # ========================> The previous view for querying the schedule was not dynamic. So I wrote the next one:

def get_production_schedule_data(request):
    schedule_type = request.GET.get('schedule')
    
    # Convert the schedule_type to a model name
    model_name = ''.join([part.capitalize() for part in schedule_type.split('_')])
    
    try:
        # Dynamically get the model class
        model_class = apps.get_model('monitoring_dashboard', model_name)
        
        # Retrieve data from the model
        data = list(model_class.objects.values())
        
        # Get column names dynamically
        with connection.cursor() as cursor:
            cursor.execute(f'SELECT * FROM {model_class._meta.db_table} LIMIT 1')
            columns = [col[0] for col in cursor.description]
        
        response_data = {
            'columns': columns,
            'rows': data
        }
    except LookupError:
        response_data = {
            'columns': [],
            'rows': []
        }
    
    return JsonResponse(response_data)


#  =============> Added to edit the table entries <==================
# Helper function to get model dynamically
def get_model(schedule):
    model_name = ''.join([part.capitalize() for part in schedule.split('_')])
    try:
        return apps.get_model('monitoring_dashboard', model_name)
    except LookupError:
        return None
    
# View to get data for a specific row
@require_GET
def get_production_schedule_row(request):
    schedule = request.GET.get('schedule')
    row_id = request.GET.get('id')
    model = get_model(schedule)
    if model:
        row = model.objects.filter(id=row_id).values().first()
        if row:
            return JsonResponse(row)
    return JsonResponse({'error': 'Row not found'}, status=404)

# View to update production schedule data

@csrf_exempt
def update_production_schedule_data(request):
    if request.method == 'POST':
        try:
            schedule = request.POST.get('schedule')
            id = request.POST.get('id')

            # Dynamically get the model class
            model_class = apps.get_model('monitoring_dashboard', ''.join([part.capitalize() for part in schedule.split('_')]))

            # Fetch the specific model instance
            instance = get_object_or_404(model_class, id=id)

            # Update instance fields based on POST data
            for key, value in request.POST.items():
                if key != 'schedule' and key != 'id' and hasattr(instance, key):
                    setattr(instance, key, value)

            # Save the updated instance
            instance.save()

            return JsonResponse({"success": True})

        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

    return JsonResponse({"success": False, "message": "Invalid method"})

# View to delete a row
@csrf_exempt
@require_POST
def delete_schedule_entries(request):
    try:
        data = json.loads(request.body)
        ids_to_delete = data['ids']
        schedule = data['schedule']
        model = get_model(schedule)
        if model:
            model.objects.filter(id__in=ids_to_delete).delete()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'message': 'Invalid schedule'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})
#  =============> Added to edit the table entries <==================

@csrf_exempt
def submit_form(request, schedule):
    if request.method == 'POST':
        data = request.POST
        if schedule == 'production_plan_bt':
            model = ProductionPlanBT
        elif schedule == 'production_plan_tbs':
            model = ProductionPlanTBS
        elif schedule == 'production_plan_ovk':
            model = ProductionPlanOVK
        # elif schedule == 'schedule4':
        #     model = Schedule4
        else:
            return JsonResponse({'success': False, 'error': 'Invalid schedule'})

        new_record = model(**data.dict())
        new_record.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@csrf_exempt
def delete_schedule_entries(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        ids = data.get('ids', [])
        schedule = data.get('schedule', '')

        if not ids or not schedule:
            return JsonResponse({'success': False, 'message': 'Invalid data.'})

        try:
            # Use the schedule to determine which table to delete from
            if schedule == 'production_plan_bt':
                ProductionPlanBT.objects.filter(id__in=ids).delete()
            elif schedule == 'production_plan_tbs':
                ProductionPlanTBS.objects.filter(id__in=ids).delete()
            elif schedule == 'production_plan_ovk':
                ProductionPlanOVK.objects.filter(id__in=ids).delete()
            elif schedule == 'schedule4':
                Schedule4.objects.filter(id__in=ids).delete()
            else:
                return JsonResponse({'success': False, 'message': 'Invalid schedule.'})

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})


def create_schedule(request):
    if request.method == 'POST':
        schedule_name = request.POST.get('schedule_name')
        columns = request.POST.getlist('columns[]')

        if not schedule_name or not columns:
            return JsonResponse({'success': False, 'message': 'Invalid data.'})

        try:
            with connection.cursor() as cursor:
                # Create new table with the given columns
                column_definitions = ', '.join([f"{column} VARCHAR(255)" for column in columns])
                create_table_sql = f"CREATE TABLE {schedule_name} (id INT AUTO_INCREMENT PRIMARY KEY, {column_definitions})"
                cursor.execute(create_table_sql)

            return JsonResponse({'success': True, 'schedule': schedule_name, 'schedule_name': schedule_name.replace('_', ' ')})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

def get_inventory_chart_data(request):
    data = FinishedProduct.objects.all()
    full = data.filter(quantity__gte=900).count()
    mid = data.filter(quantity__gte=500, quantity__lt=900).count()
    low = data.filter(quantity__lt=500).count()
    return JsonResponse({
        'labels': ['Full', 'Mid', 'Low'],
        'data': [full, mid, low],
    })

def get_deliveries_chart_data(request):
    data = DeliveredProduct.objects.all()
    full = data.filter(quantity__gte=900).count()
    mid = data.filter(quantity__gte=500, quantity__lt=900).count()
    low = data.filter(quantity__lt=500).count()
    return JsonResponse({
        'labels': ['Full', 'Mid', 'Low'],
        'data': [full, mid, low],
    })


#  =====> Added for the QR code login mechanism

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import CustomUser  # Adjust according to your actual model setup

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('admin')
            elif user.role == 'operator':
                return redirect('cnc_planning')  # Redirect to CNC planning for operators
            else:
                return redirect('inventory')  # Redirect to dashboard for other users
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'monitoring_dashboard/login.html')


@csrf_exempt
def get_cnc_machines(request):
    cnc_machines = CNCMachine.objects.all().values('id', 'name')
    return JsonResponse(list(cnc_machines), safe=False)


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import CustomUser, Schedule  # Adjust according to your actual model setup
from datetime import date
from django.utils import timezone
from .models import Schedule, CNCMachine

# This is for sending all the schedules for each cnc machine assigned to each operator when they log in.
# The filtering now is for all the schedules for today, as well as all the schedules which were not completed in their timespan
@login_required
def cnc_planning(request):
    today = timezone.now().date()
    user = request.user
    user_schedules = []

    # Assuming you have a way to check if the user is an operator
    if user.role == 'operator':  # Adjust this condition based on your user model
        # Get schedules for the logged-in operator for today
        # user_schedules = Schedule.objects.filter(
        #     operator_name=user.username,
        #     start_date__lte=today,
        #     end_date__gte=today
        # )
        user_schedules = Schedule.objects.filter(
            operator_name=user.username,
        ).filter(
            (Q(start_date__lte=today) & Q(end_date__gte=today)) | Q(is_completed=False)
        )
        
    else:
        # Get all schedules for today

        user_schedules = Schedule.objects.filter(
            (Q(start_date__lte=today) & Q(end_date__gte=today)) | Q(is_completed=False)
        )

    # Get the unique CNC machines assigned
    cnc_machines = list(set(schedule.cnc_machine for schedule in user_schedules))

    # Create a dictionary of CNC machines to pass to the template
    context = {
        'cnc_machines': cnc_machines
    }
    return render(request, 'monitoring_dashboard/cnc.html', context)

def monitoring(request):
    if request.user.role == 'operator':
        return redirect('unauthorized')

    cnc_machines = CNCMachine.objects.all()

    # Get the unique CNC machines assigned
    # cnc_machines = list(set(schedule.cnc_machine for schedule in user_schedules))
    # cnc_machines = list(set(schedule.cnc_machine for schedule in user_schedules))

    # Create a dictionary of CNC machines to pass to the template
    context = {
        'cnc_machines': cnc_machines
    }
    return render(request, 'monitoring_dashboard/monitoring.html', context)

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import CustomUser  # Adjust according to your actual model setup

def qr_login_view(request):
    if request.method == 'POST':
        qr_code = request.POST.get('qr_code')

        # Validate QR code logic here
        try:
            operator = CustomUser.objects.get(national_id=qr_code, role='operator')
            login(request, operator)
            return redirect('cnc')  # Redirect to CNC page upon successful login
        except CustomUser.DoesNotExist:
            messages.error(request, 'Invalid QR code or operator not found.')
            return redirect('login')  # Redirect back to login page if QR code is invalid

    return render(request, 'monitoring_dashboard/login.html')

def unauthorized_view(request):
    return render(request, 'monitoring_dashboard/unauthorized.html')


from django.http import JsonResponse
from .models import Schedule

#  For showing CNC schedule details in the modal form
def get_schedule_details_cnc_modal(request, machine_id):
    schedules = Schedule.objects.filter(cnc_machine_id=machine_id)
    data = [{
        'id': schedule.id,
        'startDate': schedule.start_date,
        'endDate': schedule.end_date,
        'productType': schedule.product_type,
        'quantity': schedule.quantity,
        'operatorName': schedule.operator_name,
        'cncMachine': schedule.cnc_machine.name if schedule.cnc_machine else 'Unknown',
        'orderNum': schedule.order_num,
        'limtz': schedule.limtz,
    } for schedule in schedules]

    return JsonResponse(data, safe=False)

def get_schedule_files(request, schedule_id):
    schedule = Schedule.objects.get(id=schedule_id)
    files = schedule.files.all()
    file_data = [{'url': file.file.url, 'name': file.file.name, 'description': file.description} for file in files]
    return JsonResponse({'files': file_data})


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Schedule, CNCMachine, UploadedFile
from .forms import ScheduleForm
from django.utils.timezone import localdate
import json
from django.db.models import Q
# from .models import CNCMachine, Schedule, TimerState, CustomUser
@csrf_exempt
def get_schedules_for_machine(request, machine_id):
    try:
        cnc_machine = CNCMachine.objects.get(id=machine_id)
        today = localdate()
        
        # Filtering schedules that include today in their range
        schedules = Schedule.objects.filter(
            cnc_machine=cnc_machine
        ).filter(
            (Q(start_date__lte=today) & Q(end_date__gte=today)) | Q(is_completed=False) # added the " | Q(is_completed=False)" to show the schedules for the operators which they did not complete

  
        )
        print("here is the schedules with filters:")
        print(schedules)

        schedule_data = []

        for schedule in schedules:
            files = schedule.files.all()
            file_data = [{'url': file.file.url, 'name': file.file.name, 'description': file.description} for file in files]
            
            # Retrieve operator details
            try:
                operator = CustomUser.objects.get(username=schedule.operator_name)
                operator_full_name = f"{operator.username} - {operator.first_name} {operator.middle_name} {operator.last_name}"
            except CustomUser.DoesNotExist:
                operator_full_name = schedule.operator_name  # Fallback to the username if user not found

            schedule_data.append({
                'id': schedule.id,
                'startDate': schedule.start_date,
                'endDate': schedule.end_date,
                'productType': schedule.product_type,
                'quantity': schedule.quantity,
                'operatorName': operator_full_name,
                'cncMachineId': cnc_machine.id,
                'cncMachine': cnc_machine.name,
                'urgent': schedule.urgent,  # Include the urgent status
                'files': file_data,
                'finished': schedule.is_completed,  # Include the finished status
                'orderNum': schedule.order_num,
                'limtz': schedule.limtz,
                'paused': schedule.is_paused,
            })

        return JsonResponse({'success': True, 'schedules': schedule_data})
    except CNCMachine.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'CNC Machine not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
def get_schedules_for_machine_forMonitoring(request, machine_id):
    try:
        cnc_machine = CNCMachine.objects.get(id=machine_id)
        today = localdate()
        
        # Filtering schedules that include today in their range
        schedules = Schedule.objects.filter(
            cnc_machine=cnc_machine
        )
        print("here is the schedules with filters:")
        print(schedules)

        schedule_data = []

        for schedule in schedules:
            files = schedule.files.all()
            file_data = [{'url': file.file.url, 'name': file.file.name, 'description': file.description} for file in files]
            
            # Retrieve operator details
            try:
                operator = CustomUser.objects.get(username=schedule.operator_name)
                operator_full_name = f"{operator.username} - {operator.first_name} {operator.middle_name} {operator.last_name}"
            except CustomUser.DoesNotExist:
                operator_full_name = schedule.operator_name  # Fallback to the username if user not found

            schedule_data.append({
                'id': schedule.id,
                'startDate': schedule.start_date,
                'endDate': schedule.end_date,
                'productType': schedule.product_type,
                'quantity': schedule.quantity,
                'operatorName': operator_full_name,
                'cncMachineId': cnc_machine.id,
                'cncMachine': cnc_machine.name,
                'urgent': schedule.urgent,  # Include the urgent status
                'files': file_data,
                'finished': schedule.is_completed,  # Include the finished status
                'orderNum': schedule.order_num,
                'limtz': schedule.limtz,
                'paused': schedule.is_paused,
            })

        return JsonResponse({'success': True, 'schedules': schedule_data})
    except CNCMachine.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'CNC Machine not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# =======> This is for registering the time spent each time we click on the pause/resume button
@csrf_exempt
def save_timer_state(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        schedule_id = data.get('scheduleId')
        state = data.get('state')
        elapsed_time = data.get('elapsedTime')

        try:
            schedule = Schedule.objects.get(id=schedule_id)
            timer_state, created = TimerState.objects.get_or_create(schedule=schedule)
            timer_state.state = state
            timer_state.elapsed_time = elapsed_time
            timer_state.save()
            return JsonResponse({'success': True})
        except Schedule.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Schedule not found'})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})

    

# =========> Added the Start work and Finish Work to calculate the work time of the operators.
# =========> Also so save the comments
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Schedule
from django.utils import timezone
from django.utils.timezone import now

@csrf_exempt
def start_work(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        schedule_id = data.get('schedule_id')
        schedule = get_object_or_404(Schedule, id=schedule_id)
        
        if not schedule.start_time:
            schedule.start_time = timezone.localtime(timezone.now())
            schedule.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'message': 'Work already started'}, status=400)

    return JsonResponse({'success': False}, status=400)



@csrf_exempt
def finish_work(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            schedule_id = data.get('schedule_id')
            comments = data.get('comments')
            elapsed_time = data.get('elapsed_time')

            # Validate input
            if not schedule_id:
                return JsonResponse({'success': False, 'message': 'Invalid input'}, status=400)

            # Retrieve the schedule object
            schedule = Schedule.objects.get(id=schedule_id)
            # schedule.end_time = now()  # Save the end time
            schedule.end_time = timezone.localtime(timezone.now())
            schedule.time_taken = elapsed_time
            schedule.is_completed = True  # Mark as finished
            schedule.comments = comments
            schedule.save()

            return JsonResponse({'success': True, 'message': 'Work finished successfully'})
        except Schedule.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Schedule not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON'}, status=400)
    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)

    
@csrf_exempt
def end_shift(request):
    if request.method == "POST":
        data = json.loads(request.body)
        schedule_id = data.get('schedule_id')
        elapsed_time = data.get('elapsed_time')

        schedule = Schedule.objects.get(id=schedule_id)
        schedule.elapsed_time = elapsed_time
        schedule.last_pause_time = timezone.now()
        schedule.is_paused = True
        schedule.save()

        return JsonResponse({'success': True})

    return JsonResponse({'success': False})

@csrf_exempt
def resume_work(request):
    if request.method == "POST":
        data = json.loads(request.body)
        schedule_id = data.get('schedule_id')

        schedule = Schedule.objects.get(id=schedule_id)
        schedule.is_paused = False
        schedule.save()

        return JsonResponse({'success': True})

    return JsonResponse({'success': False})


@csrf_exempt
def save_comment(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            schedule_id = data.get('schedule_id')
            comment = data.get('comment')

            if not schedule_id or comment is None:
                return JsonResponse({'success': False, 'message': 'Invalid input'}, status=400)

            schedule = Schedule.objects.get(id=schedule_id)
            schedule.comments = comment
            schedule.save()

            return JsonResponse({'success': True, 'message': 'Comment saved successfully'})
        except Schedule.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Schedule not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON'}, status=400)
    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)




from django.http import JsonResponse
from .models import Notification


def mark_notifications_read(request):
    if request.method == 'POST' and request.user.is_authenticated:
        Notification.objects.filter(user=request.user, read=False).update(read=True)
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request or user not authenticated'})

def get_notifications(request):
    user_id = request.user.id
    now = timezone.now()
    notifications = Notification.objects.filter(user_id=user_id, schedule__end_date__gte=now)
    
    unread_count = notifications.filter(read=False).count()
    
    notification_data = [
        {
            'id': notif.id,
            'message': notif.message,
            'urgent': notif.schedule.urgent,
            'schedule': {
                'productType': notif.schedule.product_type,
                'endDate': notif.schedule.end_date.strftime('%Y-%m-%d')
            }
        }
        for notif in notifications
    ]
    
    return JsonResponse({'success': True, 'notifications': notification_data, 'unreadCount': unread_count})


def employee_list(request):
    employees = CustomUser.objects.filter(role__in=['operator', 'manager', 'regular_user']).values('id', 'first_name', 'middle_name', 'last_name', 'role')
    employee_data = [
        {
            "id": emp['id'],  # Include the id in the response
            "name": f"{emp['first_name']} {emp['middle_name']} {emp['last_name']}",
            'role': f"{emp['role']}"
        }
        for emp in employees
    ]
    return JsonResponse(employee_data, safe=False)

from .models import Shift, CustomUser


@csrf_exempt
@require_POST
def save_shift(request):
    try:
        data = json.loads(request.body)
        print("Received data:", data)  # Debugging line

        user = CustomUser.objects.get(id=data['user_id'])
        shift_type = data['shift_type']
        date = data['date']
        start_time = data['start_time']
        end_time = data['end_time']
        notes = data['notes']
        
        # Handling overtime shifts
        overtime_start_time = data.get('overtime_start_time', None)
        overtime_end_time = data.get('overtime_end_time', None)

        # Update or create the shift entry in the database
        shift, created = Shift.objects.update_or_create(
            user=user,
            shift_type=shift_type,
            date=date,
            defaults={
                'start_time': start_time,
                'end_time': end_time,
                'notes': notes,
                'overtime_start_time': overtime_start_time,
                'overtime_end_time': overtime_end_time
            }
        )

        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})
    

from django.http import JsonResponse
from .models import Shift


def shift_list(request, year, month):
    shifts = Shift.objects.filter(date__year=year, date__month=month).values(
        'user_id', 
        'shift_type', 
        'date', 
        'start_time', 
        'end_time', 
        'overtime_start_time', 
        'overtime_end_time', 
        'notes'
    )
    shift_data = list(shifts)  # Convert QuerySet to a list
    return JsonResponse(shift_data, safe=False)



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def get_classifier_choices(request, model_name):
    models = {
        'threadring': ThreadRing,
        'threadplug': ThreadPlug,
        'smoothgauge': SmoothGauge
    }

    model = models.get(model_name)
    if model:
        choices = model.CLASSIFIER_CHOICES
        return JsonResponse({'choices': choices})
    return JsonResponse({'error': 'Invalid model name'}, status=400)

from django.shortcuts import render, get_object_or_404, redirect
from .models import Instrument, ThreadRing, ThreadPlug, SmoothGauge
from .forms import InstrumentForm, ThreadRingForm, ThreadPlugForm, SmoothGaugeForm

def get_instruments(request):
    instruments = Instrument.objects.all().values()
    return JsonResponse(list(instruments), safe=False)

def get_threadrings(request):
    threadrings = ThreadRing.objects.all().values()
    print(threadrings)
    return JsonResponse(list(threadrings), safe=False)

def get_threadplugs(request):
    threadplugs = ThreadPlug.objects.all().values()
    return JsonResponse(list(threadplugs), safe=False)

def get_smoothgauges(request):
    smoothgauges = SmoothGauge.objects.all().values()
    return JsonResponse(list(smoothgauges), safe=False)


from django.http import JsonResponse
from .models import Instrument

def instrument_detail(request, id):
    try:
        instrument = Instrument.objects.get(id=id)
        data = {
            'name': instrument.name,
            'range': instrument.range,
            'serial_number': instrument.serial_number,
            'calibration_date': instrument.calibration_date,
            'storage': instrument.storage,
            'note': instrument.note,
        }
        return JsonResponse(data)
    except Instrument.DoesNotExist:
        return JsonResponse({'error': 'Instrument not found'}, status=404)


from django.http import JsonResponse
from .models import ThreadRing

def threadring_detail(request, id):
    try:
        threadring = ThreadRing.objects.get(id=id)
        data = {
            'name': threadring.name,
            'pr': threadring.pr,
            'ne': threadring.ne,
            'location': threadring.location,
            'calibration_date': threadring.calibration_date,
            'passport': threadring.passport,
            'classifier': threadring.classifier,
        }
        return JsonResponse(data)
    except ThreadRing.DoesNotExist:
        return JsonResponse({'error': 'ThreadRing not found'}, status=404)

from django.http import JsonResponse
from .models import ThreadPlug

def threadplug_detail(request, id):
    try:
        threadplug = ThreadPlug.objects.get(id=id)
        data = {
            'name': threadplug.name,
            'pr': threadplug.pr,
            'ne': threadplug.ne,
            'location': threadplug.location,
            'calibration_date': threadplug.calibration_date,
            'passport': threadplug.passport,
            'classifier': threadplug.classifier,
        }
        return JsonResponse(data)
    except ThreadPlug.DoesNotExist:
        return JsonResponse({'error': 'ThreadPlug not found'}, status=404)


from django.http import JsonResponse
from .models import SmoothGauge

def smoothgauge_detail(request, id):
    try:
        smoothgauge = SmoothGauge.objects.get(id=id)
        data = {
            'name': smoothgauge.name,
            'pr': smoothgauge.pr,
            'ne': smoothgauge.ne,
            'location': smoothgauge.location,
            'calibration_date': smoothgauge.calibration_date,
            'passport': smoothgauge.passport,
            'classifier': smoothgauge.classifier,
        }
        return JsonResponse(data)
    except SmoothGauge.DoesNotExist:
        return JsonResponse({'error': 'SmoothGauge not found'}, status=404)



from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest
from .models import Instrument, ThreadRing, ThreadPlug, SmoothGauge
from django.forms.models import model_to_dict
import json

# Instrument views
@csrf_exempt
def create_or_update_instrument(request):
    try:
        data = json.loads(request.body)
        instrument_id = data.get('id')

        if request.method == 'POST':
            # Create a new record
            instrument = Instrument(
                name=data.get('name'),
                range=data.get('range'),
                serial_number=data.get('serial_number'),
                calibration_date=data.get('calibration_date'),
                storage=data.get('storage'),
                note=data.get('note')
            )
            instrument.save()
            return JsonResponse(model_to_dict(instrument), status=201)
        
        elif request.method == 'PUT' and instrument_id:
            # Update an existing record
            try:
                instrument = Instrument.objects.get(id=instrument_id)
                instrument.name = data.get('name')
                instrument.range = data.get('range')
                instrument.serial_number = data.get('serial_number')
                instrument.calibration_date = data.get('calibration_date')
                instrument.storage = data.get('storage')
                instrument.note = data.get('note')
                instrument.save()
                return JsonResponse(model_to_dict(instrument), status=200)
            except Instrument.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Instrument not found'}, status=404)

        else:
            return HttpResponseBadRequest("Invalid request method")
    
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON data")
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
def delete_instrument(request, instrument_id):
    if request.method == "DELETE":
        try:
            instrument = Instrument.objects.get(id=instrument_id)
            instrument.delete()
            return JsonResponse({'status': 'success'}, status=204)
        except Instrument.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Instrument not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return HttpResponseBadRequest("Invalid request method")


# ThreadRing views
@csrf_exempt
def create_or_update_threadring(request):
    try:
        data = json.loads(request.body)
        threadring_id = data.get('id')

        if request.method == 'POST':
            # Create a new record
            threadring = ThreadRing(
                name=data.get('name'),
                pr=data.get('pr'),
                ne=data.get('ne'),
                location=data.get('location'),
                calibration_date=data.get('calibration_date'),
                passport=data.get('passport'),
                classifier=data.get('classifier')
            )
            threadring.save()
            return JsonResponse(model_to_dict(threadring), status=201)
        
        elif request.method == 'PUT' and threadring_id:
            # Update an existing record
            try:
                threadring = ThreadRing.objects.get(id=threadring_id)
                threadring.name = data.get('name')
                threadring.pr = data.get('pr')
                threadring.ne = data.get('ne')
                threadring.location = data.get('location')
                threadring.calibration_date = data.get('calibration_date')
                threadring.passport = data.get('passport')
                threadring.classifier = data.get('classifier')
                threadring.save()
                return JsonResponse(model_to_dict(threadring), status=200)
            except ThreadRing.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'ThreadRing not found'}, status=404)

        else:
            return HttpResponseBadRequest("Invalid request method")
    
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON data")
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
def delete_threadring(request, threadring_id):
    if request.method == "DELETE":
        try:
            threadring = ThreadRing.objects.get(id=threadring_id)
            threadring.delete()
            return JsonResponse({'status': 'success'}, status=204)
        except ThreadRing.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'ThreadRing not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return HttpResponseBadRequest("Invalid request method")


# ThreadPlug views
@csrf_exempt
def create_or_update_threadplug(request):
    try:
        data = json.loads(request.body)
        threadplug_id = data.get('id')

        if request.method == 'POST':
            # Create a new record
            threadplug = ThreadPlug(
                name=data.get('name'),
                pr=data.get('pr'),
                ne=data.get('ne'),
                location=data.get('location'),
                calibration_date=data.get('calibration_date'),
                passport=data.get('passport'),
                classifier=data.get('classifier')
            )
            threadplug.save()
            return JsonResponse(model_to_dict(threadplug), status=201)
        
        elif request.method == 'PUT' and threadplug_id:
            # Update an existing record
            try:
                threadplug = ThreadPlug.objects.get(id=threadplug_id)
                threadplug.name = data.get('name')
                threadplug.pr = data.get('pr')
                threadplug.ne = data.get('ne')
                threadplug.location = data.get('location')
                threadplug.calibration_date = data.get('calibration_date')
                threadplug.passport = data.get('passport')
                threadplug.classifier = data.get('classifier')
                threadplug.save()
                return JsonResponse(model_to_dict(threadplug), status=200)
            except ThreadPlug.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'ThreadPlug not found'}, status=404)

        else:
            return HttpResponseBadRequest("Invalid request method")
    
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON data")
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
def delete_threadplug(request, threadplug_id):
    if request.method == "DELETE":
        try:
            threadplug = ThreadPlug.objects.get(id=threadplug_id)
            threadplug.delete()
            return JsonResponse({'status': 'success'}, status=204)
        except ThreadPlug.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'ThreadPlug not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return HttpResponseBadRequest("Invalid request method")


# SmoothGauge views
@csrf_exempt
def create_or_update_smoothgauge(request):
    try:
        data = json.loads(request.body)
        smoothgauge_id = data.get('id')

        if request.method == 'POST':
            # Create a new record
            smoothgauge = SmoothGauge(
                name=data.get('name'),
                pr=data.get('pr'),
                ne=data.get('ne'),
                location=data.get('location'),
                calibration_date=data.get('calibration_date'),
                passport=data.get('passport'),
                classifier=data.get('classifier')
            )
            smoothgauge.save()
            return JsonResponse(model_to_dict(smoothgauge), status=201)
        
        elif request.method == 'PUT' and smoothgauge_id:
            # Update an existing record
            try:
                smoothgauge = SmoothGauge.objects.get(id=smoothgauge_id)
                smoothgauge.name = data.get('name')
                smoothgauge.pr = data.get('pr')
                smoothgauge.ne = data.get('ne')
                smoothgauge.location = data.get('location')
                smoothgauge.calibration_date = data.get('calibration_date')
                smoothgauge.passport = data.get('passport')
                smoothgauge.classifier = data.get('classifier')
                smoothgauge.save()
                return JsonResponse(model_to_dict(smoothgauge), status=200)
            except SmoothGauge.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'SmoothGauge not found'}, status=404)

        else:
            return HttpResponseBadRequest("Invalid request method")
    
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON data")
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
def delete_smoothgauge(request, smoothgauge_id):
    if request.method == "DELETE":
        try:
            smoothgauge = SmoothGauge.objects.get(id=smoothgauge_id)
            smoothgauge.delete()
            return JsonResponse({'status': 'success'}, status=204)
        except SmoothGauge.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'SmoothGauge not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return HttpResponseBadRequest("Invalid request method")





from django.http import JsonResponse
from datetime import datetime, timedelta
from .models import Instrument, ThreadRing, ThreadPlug, SmoothGauge

def get_calibration_status(request):
    def check_calibration_status(items, recent_interval_months, soon_interval_months):
        status = {
            'Недавно Калиброванный': 0,
            'Скоро потребуется калибровка': 0,
            'Требуется выполнить калибровку': 0
        }
        now = datetime.now().date()
        for item in items:
            calibration_date = item.get('calibration_date')
            if calibration_date:
                if isinstance(calibration_date, str):
                    try:
                        calibration_date = datetime.strptime(calibration_date, '%Y-%m-%d').date()
                    except ValueError:
                        continue
                elif isinstance(calibration_date, datetime):
                    calibration_date = calibration_date.date()

                days_since_calibration = (now - calibration_date).days
                if days_since_calibration <= recent_interval_months * 30:
                    status['Недавно Калиброванный'] += 1
                elif days_since_calibration <= soon_interval_months * 30:
                    status['Скоро потребуется калибровка'] += 1
                else:
                    status['Требуется выполнить калибровку'] += 1
        return status
    
    recent_interval_months = 10
    soon_interval_months = 11

    instruments = Instrument.objects.all().values('calibration_date')
    threadrings = ThreadRing.objects.all().values('calibration_date')
    threadplugs = ThreadPlug.objects.all().values('calibration_date')
    smoothgauges = SmoothGauge.objects.all().values('calibration_date')

    data = {
        'Инструменты': check_calibration_status(instruments, recent_interval_months, soon_interval_months),
        'Кольца резьбовые': check_calibration_status(threadrings, recent_interval_months, soon_interval_months),
        'Резьбовые пробки': check_calibration_status(threadplugs, recent_interval_months, soon_interval_months),
        'Гладкие калибры': check_calibration_status(smoothgauges, recent_interval_months, soon_interval_months),
    }

    print(data)
    
    return JsonResponse(data)


















# # MT connect and machine data
# import requests
# from django.http import HttpResponse

# def fetch_mtconnect_data():
#     url = "http://localhost:5000/current"  # MTConnect agent URL
#     try:
#         response = requests.get(url)
#         response.raise_for_status()  # Raise an exception for HTTP errors
#         return response.text  # Return the raw XML content as a string
#     except requests.RequestException as e:
#         print(f"Error fetching MTConnect data: {e}")
#         return None

# def mtconnect_view(request):
#     xml_data = fetch_mtconnect_data()
#     if xml_data:
#         print("MTConnect Data:")
#         print(xml_data)
#     else:
#         print("Failed to fetch MTConnect data.")
    
#     return HttpResponse("Check the console for MTConnect data.")

# from django.http import JsonResponse
# import xml.etree.ElementTree as ET
# import requests

# def fetch_mtconnect_data():
#     url = "http://localhost:5000/current"  # MTConnect agent URL
#     try:
#         response = requests.get(url)
#         response.raise_for_status()  # Raise an exception for HTTP errors
        
#         # Return the response content (assuming it should be XML)
#         return response.content  # Return raw content instead of .text to handle bytes properly
#     except requests.RequestException as e:
#         print(f"Error fetching MTConnect data: {e}")
#         return None

# def get_machine_status(request, machine_id):
#     xml_data = fetch_mtconnect_data()
#     if xml_data and machine_id == '7':
#         try:
#             print("Raw XML Data:")
#             print(xml_data)  # Print the raw XML data

#             # Parse the XML data
#             root = ET.fromstring(xml_data)  # root will be an XML Element
            
#             # Attempt to find the 'f_sim_p1_ctl_exec' element
#             f_sim_p1_ctl_exec_element = root.find(".//DataItem[@id='f_sim_p1_ctl_exec']")
            
#             if f_sim_p1_ctl_exec_element is not None and f_sim_p1_ctl_exec_element.text is not None:
#                 f_sim_p1_ctl_exec = f_sim_p1_ctl_exec_element.text
#                 return JsonResponse({'f_sim_p1_ctl_exec': f_sim_p1_ctl_exec})
#             else:
#                 error_message = "DataItem with id 'f_sim_p1_ctl_exec' not found or has no text."
#                 print(error_message)
#                 return JsonResponse({'error': error_message}, status=400)
            
#         except ET.ParseError as e:
#             print(f"Error parsing XML data: {e}")
#             return JsonResponse({'error': 'Failed to parse MTConnect data'}, status=500)

#     else:
#         return JsonResponse({'error': 'Failed to fetch MTConnect data or machine ID not 7'}, status=400)
# from django.http import JsonResponse
# import xml.etree.ElementTree as ET
# import requests

# def fetch_execution_data():
#     # url = "http://localhost:5000/current?path=//DataItem[@type=%22EXECUTION%22]"  # Specific MTConnect path
#     url = "http://localhost:5000/current"
#     try:
#         response = requests.get(url)
#         response.raise_for_status()  # Raise an exception for HTTP errors
#         return response.content  # Return raw content as bytes for XML parsing
#     except requests.RequestException as e:
#         print(f"Error fetching MTConnect data: {e}")
#         return None

# def get_machine_status(request, machine_id):
#     if machine_id == '7':
#         xml_data = fetch_execution_data()  # Fetch data from the specific path
#         if xml_data:
#             try:
#                 # Parse the XML data
#                 root = ET.fromstring(xml_data)
#                 print(f'here is the roor xml data: {root}')

#                 # Locate the Execution element using the provided path
#                 f_sim_p1_ctl_exec_element = root.find(".//Execution[@dataItemId='f_sim_p1_ctl_exec']")

#                 # Check if the element exists and has a text value
#                 if f_sim_p1_ctl_exec_element is not None and f_sim_p1_ctl_exec_element.text is not None:
#                     f_sim_p1_ctl_exec = f_sim_p1_ctl_exec_element.text
#                     return JsonResponse({'f_sim_p1_ctl_exec': f_sim_p1_ctl_exec})
#                 else:
#                     error_message = "DataItem with id 'f_sim_p1_ctl_exec' not found or has no text."
#                     print(error_message)
#                     return JsonResponse({'error': error_message}, status=400)

#             except ET.ParseError as e:
#                 print(f"Error parsing XML data: {e}")
#                 return JsonResponse({'error': 'Failed to parse MTConnect data'}, status=500)
#         else:
#             return JsonResponse({'error': 'Failed to fetch MTConnect data'}, status=400)
#     else:
#         return JsonResponse({'error': 'Machine ID is not 7'}, status=400)


from django.http import JsonResponse
import requests
from bs4 import BeautifulSoup

def fetch_execution_data():
    url = "http://localhost:5000/current"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.content  # Return raw content as bytes for XML parsing
    except requests.RequestException as e:
        print(f"Error fetching MTConnect data: {e}")
        return None

# def get_machine_status(request, machine_id):
#     if machine_id == '7':
#         xml_data = fetch_execution_data()  # Fetch data from the specific path
#         if xml_data:
#             try:
#                 # Parse the XML data using BeautifulSoup
#                 soup = BeautifulSoup(xml_data, 'xml')
#                 # print(f'here is the parsed xml data: {soup.prettify()}')

#                 # Locate the Execution element using the dataItemId attribute 
#                 execution_element = soup.find('Execution', {'dataItemId': 'f_sim_p1_ctl_exec'})
#                 part_count_element = soup.find('PartCount', {'dataItemId': 'f_sim_p1_part_count_complete'})

#                 # Check if the element exists and has a text value
#                 if execution_element is not None and execution_element.text:
#                     f_sim_p1_ctl_exec = execution_element.text.strip()  # Strip any extra whitespace
#                     return JsonResponse({'f_sim_p1_ctl_exec': f_sim_p1_ctl_exec})
#                 else:
#                     error_message = "DataItem with id 'f_sim_p1_ctl_exec' not found or has no text."
#                     print(error_message)
#                     return JsonResponse({'error': error_message}, status=400)


#             except Exception as e:
#                 print(f"Error processing XML data: {e}")
#                 return JsonResponse({'error': 'Failed to process MTConnect data'}, status=500)
#         else:
#             return JsonResponse({'error': 'Failed to fetch MTConnect data'}, status=400)
#     else:
#         return JsonResponse({'error': 'Machine ID is not 7'}, status=400)
def get_machine_status(request, machine_id):
    if machine_id == '7':
        xml_data = fetch_execution_data()  # Fetch data from the specific path
        if xml_data:
            try:
                # Parse the XML data using BeautifulSoup
                soup = BeautifulSoup(xml_data, 'xml')
                # print(f'here is the parsed xml data: {soup.prettify()}')

                # Locate the Execution element using the dataItemId attribute
                execution_element = soup.find('Execution', {'dataItemId': 'f_sim_p1_ctl_exec'})
                controllerMode_element = soup.find('ControllerMode', {'dataItemId': 'f_sim_p1_ctl_mode'})
                toolNumber_element = soup.find('ToolNumber', {'dataItemId': 'f_sim_p1_tool_num'})
                # Locate the PartCount element using the dataItemId attribute
                part_count_element = soup.find('PartCount', {'dataItemId': 'f_sim_p1_part_count_complete'})
                f_sim_p1_alm_all_element = soup.find(attrs={'dataItemId': 'f_sim_p1_alm_all'})

                # Find the Condition element
                condition_element = soup.find('Condition')
                # print(f'here is the condition tag: {condition_element}')

                # alarmm_all_element = soup.find('Condition', {'dataItemId': 'f_sim_p1_alm_all'})
                # f_sim_p1_alm_all_element = condition_element.find('Normal', {'dataItemId': 'f_sim_p1_alm_all'}) if condition_element else None
                # f_sim_p1_alm_all_element = condition_element.find(attrs={'dataItemId': 'f_sim_p1_alm_all'}) if condition_element else None



                # Extract the text content from the elements if they exist
                f_sim_p1_ctl_exec = execution_element.text.strip() if execution_element else None
                f_sim_p1_ctl_mode = controllerMode_element.text.strip() if controllerMode_element else None
                f_sim_p1_tool_num = toolNumber_element.text.strip() if toolNumber_element else None
                f_sim_p1_part_count = part_count_element.text.strip() if part_count_element else None


                # f_sim_p1_alm = alarmm_all_element.text.strip() if alarmm_all_element else None
                # f_sim_p1_alm_all = f_sim_p1_alm_all_element.text.strip() if f_sim_p1_alm_all_element else None
                f_sim_p1_alm_all = f_sim_p1_alm_all_element.name
                # f_sim_p1_alm_all = f_sim_p1_alm_all_element.text

                # Check if the elements were found and have text values
                if f_sim_p1_ctl_exec is not None and f_sim_p1_part_count is not None:
                    return JsonResponse({
                        'f_sim_p1_ctl_exec': f_sim_p1_ctl_exec,
                        'f_sim_p1_ctl_mode': f_sim_p1_ctl_mode,
                        'f_sim_p1_part_count': f_sim_p1_part_count,
                        # 'f_sim_p1_alm': f_sim_p1_alm,
                        'f_sim_p1_alm_all': f_sim_p1_alm_all,
                        'f_sim_p1_tool_num': f_sim_p1_tool_num,
                    })
                else:
                    error_message = "One or more required DataItems not found or have no text."
                    print(error_message)
                    return JsonResponse({'error': error_message}, status=400)

            except Exception as e:
                print(f"Error processing XML data: {e}")
                return JsonResponse({'error': 'Failed to process MTConnect data'}, status=500)
        else:
            return JsonResponse({'error': 'Failed to fetch MTConnect data'}, status=400)
    else:
        return JsonResponse({'error': 'Machine ID is not 7'}, status=400)
