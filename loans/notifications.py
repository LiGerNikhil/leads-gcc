from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse


STATUS_MESSAGES = {
    'SUBMITTED': ('Application Submitted', 'Your loan application {app_id} has been submitted successfully.'),
    'STATE_REVIEW': ('Application Under Review', 'Your application {app_id} is now under State Head review.'),
    'RETURNED_FOR_CORRECTION': ('Application Returned for Correction',
                                'Your application {app_id} has been returned for correction by the State Head. Remarks: {remarks}'),
    'RESUBMITTED': ('Application Resubmitted', 'Application {app_id} has been resubmitted after correction.'),
    'GCC_REVIEW': ('Application Forwarded to GCC',
                   'Your application {app_id} has been forwarded to GCC Noida for final review.'),
    'ADDITIONAL_DOCS_REQUIRED': ('Additional Documents Required',
                                 'Additional documents are required for application {app_id}. Remarks: {remarks}'),
    'APPROVED': ('Application Approved', 'Congratulations! Your loan application {app_id} has been approved.'),
    'REJECTED': ('Application Rejected', 'Your loan application {app_id} has been rejected. Remarks: {remarks}'),
    'DISBURSED': ('Loan Disbursed', 'Your loan for application {app_id} has been disbursed.'),
}


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
    if application.created_by and application.created_by.employee_code:
        pass
    if recipients:
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL or 'noreply@gcc-loans.in', recipients, fail_silently=True)
