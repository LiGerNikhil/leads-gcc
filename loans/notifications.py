from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from .models import Notification


STATUS_MESSAGES = {
    'SUBMITTED': ('Application Submitted', 'Your loan application {app_id} has been submitted successfully.'),
    'STATE_REVIEW': ('Application Under Review', 'Your application {app_id} is now under State Head review.'),
    'RETURNED_FOR_CORRECTION': ('Application Returned',
                                'Your application {app_id} has been returned for correction. Remarks: {remarks}'),
    'RESUBMITTED': ('Application Resubmitted', 'Application {app_id} has been resubmitted after correction.'),
    'GCC_REVIEW': ('Application Forwarded to GCC',
                   'Your application {app_id} has been forwarded to GCC Noida for review.'),
    'ADDITIONAL_DOCS_REQUIRED': ('Additional Documents Required',
                                 'Additional documents are required for {app_id}. Remarks: {remarks}'),
    'APPROVED': ('Application Approved', 'Congratulations! Your loan application {app_id} has been approved.'),
    'REJECTED': ('Application Rejected', 'Your loan application {app_id} has been rejected. Remarks: {remarks}'),
    'DISBURSED': ('Loan Disbursed', 'Your loan for application {app_id} has been disbursed.'),
}


def get_notification_recipients(application):
    """Return list of (user, user_type) tuples who should be notified about this application."""
    recipients = set()
    if application.created_by:
        recipients.add((application.created_by, 'coordinator'))
    state_heads = application.created_by.__class__.objects.filter(
        role='STATE_HEAD', state=application.state, is_active=True
    ) if application.state else []
    for sh in state_heads:
        recipients.add((sh, 'state_head'))
    gcc_users = application.created_by.__class__.objects.filter(
        role='GCC_NOIDA', is_active=True
    ) if application.created_by else []
    for gcc in gcc_users:
        recipients.add((gcc, 'gcc'))
    super_admins = application.created_by.__class__.objects.filter(
        role='SUPER_ADMIN', is_active=True
    ) if application.created_by else []
    for sa in super_admins:
        recipients.add((sa, 'super_admin'))
    return list(recipients)


def create_in_app_notifications(application, to_status, remarks=''):
    if to_status not in STATUS_MESSAGES:
        return
    subject_template, body_template = STATUS_MESSAGES[to_status]
    app_id = application.application_id or 'N/A'
    title = f'[{app_id}] {subject_template}'
    message = body_template.format(app_id=app_id, remarks=remarks)
    recipients = get_notification_recipients(application)
    for user, _ in recipients:
        Notification.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type='STATUS_CHANGE',
            application=application,
        )


def send_status_notification(application, to_status, remarks=''):
    if to_status not in STATUS_MESSAGES:
        return
    subject_template, body_template = STATUS_MESSAGES[to_status]
    app_id = application.application_id or 'N/A'
    subject = f'[GCC Loan Portal] {subject_template}'
    body = body_template.format(app_id=app_id, remarks=remarks)
    body += f'\n\nView application: {settings.BASE_URL or "http://localhost:8000"}{reverse("loan_detail", args=[application.id])}'

    recipients = []
    if application.created_by and application.created_by.email:
        recipients.append(application.created_by.email)
    if recipients:
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL or 'noreply@gcc-loans.in', recipients, fail_silently=True)
