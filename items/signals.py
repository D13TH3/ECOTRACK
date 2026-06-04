from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import Notification, UserProfile
from django.contrib.auth.signals import user_logged_out
from django.contrib.auth.models import User


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Auto-create a UserProfile whenever a new User is created."""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the UserProfile whenever the User is saved."""
    if hasattr(instance, 'profile'):
        instance.profile.save()


@receiver(user_logged_out)
def handle_user_logged_out(sender, request, user, **kwargs):
    # Mark the session so middleware can write the 'last_state' cookie to 'items'
    if request is not None and hasattr(request, 'session'):
        try:
            request.session['just_logged_out'] = True
        except Exception:
            pass

@receiver(post_save, sender=Notification)
def send_notification_email(sender, instance, created, **kwargs):
    if not created:
        return

    recipient_email = instance.recipient.email
    if not recipient_email:
        return

    subject = ""
    template_name = ""
    context = {
        'recipient_name': instance.recipient.username,
        'actor_name': instance.actor.username,
        'item_title': instance.item.title,
        'item_id': instance.item.id,
        'domain': settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'localhost:8000',
    }

    if instance.notification_type == 'ITEM_CLAIMED':
        subject = f"📌 {instance.actor.username} claimed your item: {instance.item.title}"
        template_name = 'emails/item_claimed.txt'
    elif instance.notification_type == 'CLAIM_APPROVED':
        subject = f"✅ Your claim for {instance.item.title} was approved!"
        template_name = 'emails/claim_approved.txt'
    elif instance.notification_type == 'CLAIM_REJECTED':
        subject = f"❌ Your claim for {instance.item.title} was rejected"
        template_name = 'emails/claim_rejected.txt'

    try:
        message = render_to_string(template_name, context)
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient_email])
    except Exception as e:
        print(f"Error sending email: {e}")
