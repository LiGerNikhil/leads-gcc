from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


INDIAN_STATES = [
    ('Andhra Pradesh', 'Andhra Pradesh'),
    ('Arunachal Pradesh', 'Arunachal Pradesh'),
    ('Assam', 'Assam'),
    ('Bihar', 'Bihar'),
    ('Chhattisgarh', 'Chhattisgarh'),
    ('Goa', 'Goa'),
    ('Gujarat', 'Gujarat'),
    ('Haryana', 'Haryana'),
    ('Himachal Pradesh', 'Himachal Pradesh'),
    ('Jharkhand', 'Jharkhand'),
    ('Karnataka', 'Karnataka'),
    ('Kerala', 'Kerala'),
    ('Madhya Pradesh', 'Madhya Pradesh'),
    ('Maharashtra', 'Maharashtra'),
    ('Manipur', 'Manipur'),
    ('Meghalaya', 'Meghalaya'),
    ('Mizoram', 'Mizoram'),
    ('Nagaland', 'Nagaland'),
    ('Odisha', 'Odisha'),
    ('Punjab', 'Punjab'),
    ('Rajasthan', 'Rajasthan'),
    ('Sikkim', 'Sikkim'),
    ('Tamil Nadu', 'Tamil Nadu'),
    ('Telangana', 'Telangana'),
    ('Tripura', 'Tripura'),
    ('Uttar Pradesh', 'Uttar Pradesh'),
    ('Uttarakhand', 'Uttarakhand'),
    ('West Bengal', 'West Bengal'),
    ('Andaman and Nicobar Islands', 'Andaman and Nicobar Islands'),
    ('Chandigarh', 'Chandigarh'),
    ('Dadra and Nagar Haveli and Daman and Diu', 'Dadra and Nagar Haveli and Daman and Diu'),
    ('Delhi', 'Delhi'),
    ('Jammu and Kashmir', 'Jammu and Kashmir'),
    ('Ladakh', 'Ladakh'),
    ('Lakshadweep', 'Lakshadweep'),
    ('Puducherry', 'Puducherry'),
]


class User(AbstractUser):
    class Role(models.TextChoices):
        COORDINATOR = 'COORDINATOR', 'Coordinator'
        STATE_HEAD = 'STATE_HEAD', 'State Head'
        GCC_NOIDA = 'GCC_NOIDA', 'GCC Noida Team'
        SUPER_ADMIN = 'SUPER_ADMIN', 'Super Admin'

    role = models.CharField(
        _('Role'),
        max_length=20,
        choices=Role.choices,
        default=Role.COORDINATOR,
    )
    employee_code = models.CharField(
        _('Employee Code'),
        max_length=20,
        unique=True,
        null=True,
        blank=True,
    )
    state = models.CharField(
        _('State'),
        max_length=50,
        choices=INDIAN_STATES,
        null=True,
        blank=True,
        help_text=_('Applicable for State Heads and Coordinators'),
    )
    is_active = models.BooleanField(_('Active'), default=True)
    phone = models.CharField(_('Phone'), max_length=15, null=True, blank=True)

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-date_joined']

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = self.Role.SUPER_ADMIN
        if self.role == self.Role.SUPER_ADMIN:
            self.is_superuser = True
            self.is_staff = True
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.get_full_name() or self.username} ({self.get_role_display()})'


class LoanApplication(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        SUBMITTED = 'SUBMITTED', 'Submitted'
        STATE_REVIEW = 'STATE_REVIEW', 'Under State Review'
        RETURNED_FOR_CORRECTION = 'RETURNED_FOR_CORRECTION', 'Returned for Correction'
        RESUBMITTED = 'RESUBMITTED', 'Resubmitted'
        GCC_REVIEW = 'GCC_REVIEW', 'Under GCC Review'
        ADDITIONAL_DOCS_REQUIRED = 'ADDITIONAL_DOCS_REQUIRED', 'Additional Documents Required'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'
        DISBURSED = 'DISBURSED', 'Disbursed'

    class LoanType(models.TextChoices):
        PERSONAL = 'PERSONAL', 'Personal Loan'
        HOME = 'HOME', 'Home Loan'
        EDUCATION = 'EDUCATION', 'Education Loan'
        BUSINESS = 'BUSINESS', 'Business Loan'
        AGRICULTURE = 'AGRICULTURE', 'Agriculture Loan'

    applicant_name = models.CharField(_('Applicant Name'), max_length=255)
    applicant_email = models.EmailField(_('Email'), null=True, blank=True)
    applicant_phone = models.CharField(_('Phone'), max_length=15)
    gender = models.CharField(
        _('Gender'),
        max_length=10,
        choices=[('MALE', 'Male'), ('FEMALE', 'Female'), ('OTHER', 'Other')],
        null=True,
        blank=True,
    )
    date_of_birth = models.DateField(_('Date of Birth'), null=True, blank=True)
    pan_number = models.CharField(_('PAN Number'), max_length=10, null=True, blank=True)
    aadhaar_number = models.CharField(_('Aadhaar Number'), max_length=12, null=True, blank=True)
    address = models.TextField(_('Address'), null=True, blank=True)
    state = models.CharField(_('State'), max_length=50, choices=INDIAN_STATES)
    district = models.CharField(_('District'), max_length=100)
    pincode = models.CharField(_('Pincode'), max_length=6, null=True, blank=True)
    existing_loan = models.BooleanField(_('Existing Loan'), default=False)

    loan_type = models.CharField(
        _('Loan Type'),
        max_length=20,
        choices=LoanType.choices,
        default=LoanType.PERSONAL,
    )
    loan_amount = models.DecimalField(
        _('Loan Amount'),
        max_digits=12,
        decimal_places=2,
    )
    purpose = models.TextField(_('Purpose'), null=True, blank=True)
    tenure_months = models.PositiveIntegerField(_('Tenure (Months)'))
    annual_income = models.DecimalField(
        _('Annual Income'),
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )

    status = models.CharField(
        _('Status'),
        max_length=30,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    application_id = models.CharField(
        _('Application ID'),
        max_length=20,
        unique=True,
        editable=False,
        null=True,
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='applications_created',
        verbose_name=_('Created By'),
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='applications_assigned',
        verbose_name=_('Assigned To'),
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _('Loan Application')
        verbose_name_plural = _('Loan Applications')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.application_id or "N/A"} - {self.applicant_name}'

    def save(self, *args, **kwargs):
        if not self.application_id:
            last_id = LoanApplication.objects.aggregate(
                max_id=models.Max('id')
            )['max_id'] or 0
            self.application_id = f'GCC-{last_id + 1:06d}'
        super().save(*args, **kwargs)


class DocumentUpload(models.Model):
    class DocType(models.TextChoices):
        AADHAAR = 'AADHAAR', 'Aadhaar Card'
        PAN = 'PAN', 'PAN Card'
        INCOME_PROOF = 'INCOME_PROOF', 'Income Proof'
        BANK_STATEMENT = 'BANK_STATEMENT', 'Bank Statement'
        PROPERTY = 'PROPERTY', 'Property Document'
        PHOTO = 'PHOTO', 'Photograph'
        SIGNATURE = 'SIGNATURE', 'Signature'
        OTHER = 'OTHER', 'Other'

    application = models.ForeignKey(
        LoanApplication,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name=_('Application'),
    )
    doc_type = models.CharField(
        _('Document Type'),
        max_length=20,
        choices=DocType.choices,
        default=DocType.OTHER,
    )
    file = models.FileField(
        _('File'),
        upload_to='uploads/documents/%Y/%m/',
    )
    original_filename = models.CharField(
        _('Original Filename'),
        max_length=255,
        null=True,
        blank=True,
    )
    verification_status = models.CharField(
        _('Verification Status'),
        max_length=20,
        choices=[('PENDING', 'Pending'), ('VERIFIED', 'Verified'), ('REJECTED', 'Rejected')],
        default='PENDING',
    )
    verification_remarks = models.TextField(_('Verification Remarks'), null=True, blank=True)
    verified_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='verified_documents', verbose_name=_('Verified By'),
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    remarks = models.TextField(_('Remarks'), null=True, blank=True)
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('Uploaded By'),
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Document Upload')
        verbose_name_plural = _('Document Uploads')
        ordering = ['-uploaded_at']

    def __str__(self):
        return f'{self.get_doc_type_display()} - {self.application.application_id}'


class ApplicationHistory(models.Model):
    application = models.ForeignKey(
        LoanApplication,
        on_delete=models.CASCADE,
        related_name='history',
        verbose_name=_('Application'),
    )
    from_status = models.CharField(
        _('From Status'),
        max_length=30,
        choices=LoanApplication.Status.choices,
        null=True,
        blank=True,
    )
    to_status = models.CharField(
        _('To Status'),
        max_length=30,
        choices=LoanApplication.Status.choices,
    )
    remarks = models.TextField(_('Remarks'), null=True, blank=True)
    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('Changed By'),
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Application History')
        verbose_name_plural = _('Application Histories')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.application.application_id}: {self.from_status or "NEW"} → {self.to_status}'


class AuditLog(models.Model):
    class Action(models.TextChoices):
        LOGIN = 'LOGIN', 'Login'
        LOGOUT = 'LOGOUT', 'Logout'
        CREATE_APPLICATION = 'CREATE_APPLICATION', 'Create Application'
        UPDATE_STATUS = 'UPDATE_STATUS', 'Update Status'
        UPLOAD_DOCUMENT = 'UPLOAD_DOCUMENT', 'Upload Document'
        ADD_REMARK = 'ADD_REMARK', 'Add Remark'
        CREATE_USER = 'CREATE_USER', 'Create User'
        EDIT_USER = 'EDIT_USER', 'Edit User'
        RESET_PASSWORD = 'RESET_PASSWORD', 'Reset Password'
        TOGGLE_USER = 'TOGGLE_USER', 'Toggle User Active'
        VERIFY_DOCUMENT = 'VERIFY_DOCUMENT', 'Verify Document'

    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, verbose_name=_('User'),
    )
    action = models.CharField(_('Action'), max_length=30, choices=Action.choices)
    module = models.CharField(_('Module'), max_length=50, blank=True)
    remarks = models.TextField(_('Remarks'), blank=True)
    ip_address = models.GenericIPAddressField(_('IP Address'), null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Audit Log')
        verbose_name_plural = _('Audit Logs')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} - {self.get_action_display()} ({self.created_at})'
