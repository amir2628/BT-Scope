from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth.models import User
from monitoring_dashboard.models import OperatorProfile
from django.utils.crypto import get_random_string
import os
import qrcode

class Command(BaseCommand):
    help = 'Generate QR codes for all operators'

    def handle(self, *args, **kwargs):
        qr_codes_dir = os.path.join(settings.BASE_DIR, 'qrcodes')
        os.makedirs(qr_codes_dir, exist_ok=True)

        for user in User.objects.filter(groups__name='Operators'):
            profile, created = OperatorProfile.objects.get_or_create(user=user)
            if not profile.qr_token:
                profile.qr_token = get_random_string(length=32)
                profile.save()

            url = f"{settings.SITE_URL}/qr_login/?operator_id={profile.qr_token}"
            qr = qrcode.make(url)
            qr_path = os.path.join(qr_codes_dir, f"{user.username}.png")
            qr.save(qr_path)

            self.stdout.write(self.style.SUCCESS(f'Generated QR code for {user.username}'))
