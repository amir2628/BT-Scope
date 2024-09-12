"""
URL configuration for monitoring project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from monitoring_dashboard import views
from django.contrib.auth import views as auth_views


# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('', views.dashboard, name='dashboard'),
# ]

# from django.urls import path
# from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.landing, name='landing'),
    path('inventory/', views.inventory, name='inventory'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('planning/', views.planning, name='planning'),
    path('shifts-planning/', views.shifts_page, name='shifts_page'),
    path('add-material/', views.add_material, name='add_material'),
    path('add-schedule/', views.add_schedule, name='add_schedule'),
    path('get-schedule/', views.get_schedule, name='get_schedule'),
    path('get-schedule-details/', views.get_schedule_details, name='get_schedule_details'),
    path('delete-schedule/', views.delete_schedule, name='delete_schedule'),
    
    path('delete-schedule-table/<int:id>/', views.delete_schedule_table, name='delete_schedule_table'),
    path('update-schedule/', views.update_schedule, name='update_schedule'),
    path('add-finished-product/', views.add_finished_product, name='add_finished_product'),
    path('add-delivered-product/', views.add_delivered_product, name='add_delivered_product'),
    path('get-materials-chart-data/', views.get_materials_chart_data, name='get_materials_chart_data'),
    path('get-inventory-chart-data/', views.get_inventory_chart_data, name='get_inventory_chart_data'),
    path('get-deliveries-chart-data/', views.get_deliveries_chart_data, name='get_deliveries_chart_data'),
    path('get_production_schedule_data/', views.get_production_schedule_data, name='get_production_schedule_data'),
    path('submit_form/<str:schedule>/', views.submit_form, name='submit_form'),
    path('delete_schedule_entries/', views.delete_schedule_entries, name='delete_schedule_entries'),
    path('create_schedule/', views.create_schedule, name='create_schedule'),

    # =======================> Added to be able to edit table entries <==========================
    path('get_production_schedule_row/', views.get_production_schedule_row, name='get_production_schedule_row'),
    path('update_production_schedule_data/', views.update_production_schedule_data, name='update_production_schedule_data'),
    path('delete_schedule_entries/', views.delete_schedule_entries, name='delete_schedule_entries'),
    # =======================> Added to be able to edit table entries <==========================

    path('update_cnc_status/', views.update_cnc_status, name='update_cnc_status'), #added for CNC status opcua

    # Added for the new page for CNC planning
    path('cnc-planning/', views.cnc_planning, name='cnc_planning'), #added for CNC status opcua

    # =======> Added for the QR code functionality <===========
    path('qr_login/', views.qr_login_view, name='qr_login'),
    path('cnc/', views.cnc_planning, name='cnc_planning'),
    path('unauthorized/', views.unauthorized_view, name='unauthorized'),

    path('api/password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
    path('reset-password-form/<str:uid>/<str:token>/', views.reset_password_form, name='reset_password_form'),

    path('send_test_email/', views.send_test_email),
    path('start-work/', views.start_work, name='start_work'),
    path('finish-work/', views.finish_work, name='finish_work'),
    path('end-shift/', views.end_shift, name='end_shift'),
    path('resume-work/', views.resume_work, name='resume_work'),
    path('get-schedule-details-Timer-elapsed/<int:schedule_id>/', views.get_schedule_details_Timer_elapsed, name='get_schedule_details_Timer_elapsed'),
    
    # ========> Added for fetching the users (employees) names for the planning of their shifts, based on the table
    path('api/employees/', views.employee_list, name='employee_list'),
    path('api/save_shift/', views.save_shift, name='save_shift'),
    path('api/shifts/<int:year>/<int:month>/', views.shift_list, name='shift_list'),

    path('instruments/data/', views.get_instruments, name='get_instruments'),
    path('instruments/save/', views.create_or_update_instrument, name='create_or_update_instrument'),
    path('instruments/delete/<int:instrument_id>/', views.delete_instrument, name='delete_instrument'),

    path('threadrings/data/', views.get_threadrings, name='get_threadrings'),
    path('threadrings/save/', views.create_or_update_threadring, name='create_or_update_threadring'),
    path('threadrings/delete/<int:threadring_id>/', views.delete_threadring, name='delete_threadring'),

    path('threadplugs/data/', views.get_threadplugs, name='get_threadplugs'),
    path('threadplugs/save/', views.create_or_update_threadplug, name='create_or_update_threadplug'),
    path('threadplugs/delete/<int:threadplug_id>/', views.delete_threadplug, name='delete_threadplug'),

    path('smoothgauges/data/', views.get_smoothgauges, name='get_smoothgauges'),
    path('smoothgauges/save/', views.create_or_update_smoothgauge, name='create_or_update_smoothgauge'),
    path('smoothgauges/delete/<int:smoothgauge_id>/', views.delete_smoothgauge, name='delete_smoothgauge'),

    path('classifier/choices/<str:model_name>/', views.get_classifier_choices, name='get_classifier_choices'),


    path('instruments/data/<int:id>/', views.instrument_detail, name='instrument-detail'),
    path('threadrings/data/<int:id>/', views.threadring_detail, name='threadring-detail'),
    path('threadplugs/data/<int:id>/', views.threadplug_detail, name='threadplug-detail'),
    path('smoothgauges/data/<int:id>/', views.smoothgauge_detail, name='smoothgauge-detail'),

    path('calibration-status/', views.get_calibration_status, name='calibration_status'),

    # ===========> Added this to employ each plan goes to responsible operator <========
    path('get-operators/', views.get_operators, name='get_operators'),
    path('add-schedule/', views.add_schedule, name='add_schedule'),
    path('get_cnc_machines/', views.get_cnc_machines, name='get_cnc_machines'),
    # ======> To show the schedule details of each task in the modal form <========
    path('get-schedule-details-cnc-modal/<int:machine_id>/', views.get_schedule_details_cnc_modal, name='get_schedule_details_cnc_modal'),

    # =======> Added when I wanted to implement upload files and show then in the modal form in cnc.html <========
    path('get-schedule-files/<int:schedule_id>/', views.get_schedule_files, name='get_schedule_files'),
    path('get-schedules-for-machine/<int:machine_id>/', views.get_schedules_for_machine, name='get_schedules_for_machine'),
    path('upload-files/', views.upload_files, name='upload_files'),
    path('delete-file/<int:file_id>/', views.delete_file, name='delete_file'),

    # =========> Added for start and finish work and comments from operator <==========
    path('start-work/', views.start_work, name='start_work'),
    path('finish-work/', views.finish_work, name='finish_work'),
    path('save-comment/', views.save_comment, name='save_comment'),


    # ========> For notifications functionality <===========
    path('get-notifications/', views.get_notifications, name='get_notifications'),
    path('mark-notifications-read/', views.mark_notifications_read, name='mark_notifications_read'),

    # =======> Added to classify urgent details in the calendar cell <========
    path('get-schedule-calendarcell-urgent/', views.get_schedule_calendarcell_urgent, name='get_schedule_calendarcell_urgent'),


    # # to see the data from the machines connected to the local network
    # path('mtconnect/', views.mtconnect_view, name='mtconnect_view'),
    path('get-machine-status/<str:machine_id>/', views.get_machine_status, name='get_machine_status'),

]



from django.conf import settings
from django.conf.urls.static import static
# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)