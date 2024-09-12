from django.apps import AppConfig


class MonitoringDashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'monitoring_dashboard'


# yourapp/apps.py

from django.apps import AppConfig
from django.conf import settings
import subprocess
import atexit

class YourAppConfig(AppConfig):
    name = 'monitoring_dashboard'

    def ready(self):
        # Start the fetch_cnc_data management command
        def start_fetch_cnc_data():
            manual = getattr(settings, 'FETCH_CNC_MANUAL', False)
            cmd = ['python', 'manage.py', 'fetch_cnc_data']
            if manual:
                cmd.append('--manual')
            self.process = subprocess.Popen(cmd)

        start_fetch_cnc_data()

        # Ensure the subprocess is terminated when the main process exits
        def cleanup():
            if hasattr(self, 'process'):
                self.process.terminate()

        atexit.register(cleanup)


# from django.apps import AppConfig

# class MyAppConfig(AppConfig):
#     name = 'myapp'

#     def ready(self):
#         import myapp.signals  # Adjust the import to the path of your signals.py
