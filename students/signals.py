# students/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Student
from .utils import send_welcome_email
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


@receiver(post_save, sender=User)
def create_or_update_student_profile(sender, instance, created, **kwargs):
    """
    Create or update Student profile when User is saved.
    Also send welcome email on new registration.
    """
    # Get or create the student profile
    student, is_new = Student.objects.get_or_create(user=instance)
    
    # ---------- Sync fields from User to Student ----------
    updated = False
    
    # Sync name – use full name if available, else username
    full_name = instance.get_full_name().strip()
    new_name = full_name if full_name else instance.username
    
    if student.name != new_name:
        student.name = new_name
        updated = True
    
    # Sync email
    if student.email != instance.email:
        student.email = instance.email
        updated = True
    
    # Save only if something changed
    if updated:
        student.save(update_fields=['name', 'email'])
        logger.info(f"🔄 Student profile updated for {instance.email}")
    
    # ---------- Send welcome email on new user creation ----------
    if created:
        try:
            send_welcome_email(instance)
            logger.info(f"✅ Welcome email sent to {instance.email}")
        except Exception as e:
            # Log the error but don't break the user creation
            logger.error(f"❌ Failed to send welcome email to {instance.email}: {e}")
            print(f"⚠️ Welcome email failed: {e}")