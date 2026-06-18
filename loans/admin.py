from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, LoanApplication, DocumentUpload, ApplicationHistory


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'get_full_name', 'role', 'employee_code', 'state', 'is_active')
    list_filter = ('role', 'is_active', 'state')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'employee_code')
    ordering = ('-date_joined',)

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role & Profile', {
            'fields': ('role', 'employee_code', 'state', 'phone'),
        }),
    )


class DocumentUploadInline(admin.TabularInline):
    model = DocumentUpload
    extra = 0
    readonly_fields = ('uploaded_at', 'uploaded_by')
    fields = ('doc_type', 'file', 'remarks', 'uploaded_by', 'uploaded_at')


class ApplicationHistoryInline(admin.TabularInline):
    model = ApplicationHistory
    extra = 0
    readonly_fields = ('created_at',)
    fields = ('from_status', 'to_status', 'remarks', 'changed_by', 'created_at')


@admin.register(LoanApplication)
class LoanApplicationAdmin(admin.ModelAdmin):
    list_display = (
        'application_id', 'applicant_name', 'loan_type',
        'loan_amount', 'status', 'state', 'assigned_to',
        'created_at',
    )
    list_filter = ('status', 'loan_type', 'state', 'created_at')
    search_fields = (
        'application_id', 'applicant_name', 'applicant_email',
        'pan_number', 'aadhaar_number',
    )
    readonly_fields = ('application_id', 'created_at', 'updated_at', 'submitted_at')
    inlines = [DocumentUploadInline, ApplicationHistoryInline]

    fieldsets = (
        ('Applicant Information', {
            'fields': (
                'applicant_name', 'applicant_email', 'applicant_phone',
                'pan_number', 'aadhaar_number',
            ),
        }),
        ('Address Details', {
            'fields': ('address', 'state', 'district', 'pincode'),
        }),
        ('Loan Details', {
            'fields': (
                'loan_type', 'loan_amount', 'purpose',
                'tenure_months', 'annual_income',
            ),
        }),
        ('Status & Tracking', {
            'fields': (
                'status', 'application_id', 'created_by',
                'assigned_to', 'submitted_at',
            ),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
        }),
    )


@admin.register(DocumentUpload)
class DocumentUploadAdmin(admin.ModelAdmin):
    list_display = ('application', 'doc_type', 'uploaded_by', 'uploaded_at')
    list_filter = ('doc_type', 'uploaded_at')
    search_fields = ('application__application_id', 'original_filename')


@admin.register(ApplicationHistory)
class ApplicationHistoryAdmin(admin.ModelAdmin):
    list_display = ('application', 'from_status', 'to_status', 'changed_by', 'created_at')
    list_filter = ('to_status', 'created_at')
    search_fields = ('application__application_id', 'remarks')
