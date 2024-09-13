from django.core.mail import send_mail
from django.dispatch import receiver
from rest_passwordreset.signals import reset_password_token_created
from django.conf import settings

import logging

logger = logging.getLogger(__name__)

# @receiver(reset_password_token_created)
# def send_password_reset_email(sender, instance, **kwargs):
#     user = instance.user
#     token = instance.key
#     domain = kwargs.get('domain', 'localhost')
#     protocol = kwargs.get('protocol', 'http')
    
#     subject = 'Password Reset Requested'
#     message = f"""
#     Hi {user.get_username()},
    
#     Please use the following link to reset your password:
#     {protocol}://{domain}/api/auth/password/reset/confirm/?token={token}
    
#     If you did not request a password reset, please ignore this email.
#     """
    
#     try:
#         send_mail(
#             subject,
#             message,
#             settings.DEFAULT_FROM_EMAIL,
#             [user.email],
#             fail_silently=False,
#         )
#         logger.info(f"Password reset email sent to {user.email}")
#     except Exception as e:
#         logger.error(f"Failed to send password reset email: {e}")


# from django.core.mail import send_mail
# from django.dispatch import receiver
# from rest_passwordreset.signals import reset_password_token_created
# from django.conf import settings

# @receiver(reset_password_token_created)
# def send_password_reset_email(sender, instance, **kwargs):
#     user = instance.user
#     token = instance.key
#     domain = kwargs.get('domain', 'localhost')
#     protocol = kwargs.get('protocol', 'http')
    
#     subject = 'Password Reset Requested'
#     message = f"""
#     Hi {user.get_username()},
    
#     Please use the following link to reset your password:
#     {protocol}://{domain}/api/password_reset/confirm/?token={token}
    
#     If you did not request a password reset, please ignore this email.
#     """
    
#     try:
#         send_mail(
#             subject,
#             message,
#             settings.DEFAULT_FROM_EMAIL,
#             [user.email],
#             fail_silently=False,
#         )
#         print(f"Password reset email sent to {user.email}")
#     except Exception as e:
#         print(f"Failed to send password reset email: {e}")
