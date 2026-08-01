
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from notifications.models import NotificationSettings  


# ---------- CORE EMAIL SENDER WITH SETTINGS CHECK ----------
def send_email_notification_for_user(user, subject, message, html_message=None):
    """
    Send an email to a single user if they have email notifications enabled.
    Returns True if sent, False otherwise.
    """
    # Check if the user has notification settings and if email is enabled
    try:
        settings_obj = user.notification_settings
        if not settings_obj.email_notifications:
            print(f"🔕 Email notifications disabled for {user.email}")
            return False
    except NotificationSettings.DoesNotExist:
        # If settings don't exist, default to sending (or create them)
        pass

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        print(f"📧 Email sent to {user.email}")
        return True
    except Exception as e:
        print(f"❌ Email sending failed for {user.email}: {e}")
        return False


# ---------- LEGACY WRAPPER (kept for backward compatibility) ----------
def send_email_notification(subject, message, recipient_list, html_message=None):
    """
    Legacy function – kept for compatibility.
    Use send_email_notification_for_user for user-specific checks.
    """
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False


# ---------- SPECIFIC EMAIL FUNCTIONS ----------
def send_welcome_email(user):
    """
    Send welcome email to a newly registered user.
    """
    subject = "Welcome to Student Guidance System! 🎓"
    message = f"""
    Dear {user.first_name or user.username},

    Welcome to the Student Guidance System!

    Your account has been successfully created.
    You can now log in and explore your dashboard.

    Login credentials:
    Email: {user.email}
    Password: (the one you set during registration)

    If you have any questions, please contact support.

    Best regards,
    Student Guidance Team
    """
    
    html_message = f"""
    <html>
    <body style="font-family: Arial, sans-serif;">
        <h2>Welcome to Student Guidance System! 🎓</h2>
        <p>Dear <strong>{user.first_name or user.username}</strong>,</p>
        <p>Your account has been successfully created.</p>
        <p>You can now log in and explore your dashboard:</p>
        <p><a href="http://localhost:9007/dashboard/">Click here to login</a></p>
        <hr>
        <p><strong>Login credentials:</strong></p>
        <ul>
            <li><strong>Email:</strong> {user.email}</li>
            <li><strong>Password:</strong> (the one you set during registration)</li>
        </ul>
        <p>If you have any questions, please contact support.</p>
        <p>Best regards,<br>Student Guidance Team</p>
    </body>
    </html>
    """
    
    return send_email_notification_for_user(user, subject, message, html_message)


def send_enrollment_confirmation(student, batch):
    """
    Send enrollment confirmation email.
    student: Student model instance (from students app)
    batch: CourseBatch instance
    """
    user = student.user  # Student has a OneToOneField to User
    subject = f"Enrollment Confirmed: {batch.course.title} 🎉"
    message = f"""
    Dear {student.name},

    Your enrollment has been confirmed!

    Course: {batch.course.title}
    Batch: {batch.batch_name}
    Start Date: {batch.start_date}
    End Date: {batch.end_date}

    You can view your enrollment details in your dashboard.

    Best regards,
    Student Guidance Team
    """
    
    html_message = f"""
    <html>
    <body style="font-family: Arial, sans-serif;">
        <h2>Enrollment Confirmed! 🎉</h2>
        <p>Dear <strong>{student.name}</strong>,</p>
        <p>Your enrollment has been confirmed!</p>
        <table style="border-collapse: collapse; width: 100%;">
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;"><strong>Course</strong></td>
                <td style="padding: 8px; border: 1px solid #ddd;">{batch.course.title}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;"><strong>Batch</strong></td>
                <td style="padding: 8px; border: 1px solid #ddd;">{batch.batch_name}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;"><strong>Start Date</strong></td>
                <td style="padding: 8px; border: 1px solid #ddd;">{batch.start_date}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;"><strong>End Date</strong></td>
                <td style="padding: 8px; border: 1px solid #ddd;">{batch.end_date}</td>
            </tr>
        </table>
        <p><a href="http://localhost:9007/dashboard/">View your dashboard</a></p>
        <p>Best regards,<br>Student Guidance Team</p>
    </body>
    </html>
    """
    
    return send_email_notification_for_user(user, subject, message, html_message)


def send_appointment_confirmation(student_profile, appointment):
    """
    Send appointment confirmation email.
    student_profile: profiles.models.StudentProfile instance
    appointment: appointments.models.Appointment instance
    """
    user = student_profile.user
    subject = f"Appointment Confirmed – {appointment.scheduled_time}"
    message = f"""
    Dear {student_profile.user.first_name or student_profile.user.username},

    Your appointment has been confirmed.

    Date & Time: {appointment.scheduled_time}
    Advisor: {appointment.advisor.user.email if appointment.advisor else 'N/A'}

    Please arrive on time.

    Regards,
    Student Guidance Team
    """
    return send_email_notification_for_user(user, subject, message)


def send_assessment_result(student, assessment):
    """
    Send assessment result email to the student.
    student: Student model instance (from students app)
    assessment: AssessmentResult instance
    """
    user = student.user
    subject = f"Assessment Result: {assessment.title}"
    message = f"""
    Dear {student.name},

    You have completed the assessment "{assessment.title}".

    Score: {assessment.score} / {assessment.max_score}
    Percentage: {assessment.percentage}%

    Keep up the good work!

    Regards,
    Student Guidance Team
    """
    return send_email_notification_for_user(user, subject, message)