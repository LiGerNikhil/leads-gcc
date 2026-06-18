import os
from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm, PasswordResetForm, SetPasswordForm,
)
from django.core.exceptions import ValidationError
from .models import User, LoanApplication, DocumentUpload, INDIAN_STATES


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Email / Employee ID',
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2.5 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 placeholder-slate-400',
            'placeholder': 'Enter your email or employee code',
            'autofocus': True,
        }),
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2.5 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 placeholder-slate-400',
            'placeholder': 'Enter your password',
        }),
    )


class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label='Email', max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-2.5 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 placeholder-slate-400',
            'placeholder': 'Enter your registered email', 'autocomplete': 'email',
        }),
    )


class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2.5 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 placeholder-slate-400',
            'placeholder': 'Enter new password',
        }),
    )
    new_password2 = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2.5 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 placeholder-slate-400',
            'placeholder': 'Confirm new password',
        }),
    )


class UserForm(forms.ModelForm):
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2.5 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 placeholder-slate-400',
            'placeholder': 'Leave blank to keep current password',
        }),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance or not self.instance.pk:
            self.fields['password'].required = True
            self.fields['password'].widget.attrs['placeholder'] = 'Enter a password for the new user'

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'employee_code', 'role', 'state', 'phone', 'is_active']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-4 py-2.5 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500', 'placeholder': 'email@example.com'}),
            'employee_code': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500', 'placeholder': 'EMP-001'}),
            'role': forms.Select(attrs={'class': 'w-full px-4 py-2.5 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'}),
            'state': forms.Select(choices=[('', 'Select State...')] + INDIAN_STATES, attrs={'class': 'w-full px-4 py-2.5 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'}),
            'phone': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500', 'placeholder': '+91 9876543210'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-blue-600 border-slate-300 rounded focus:ring-blue-500'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        employee_code = cleaned_data.get('employee_code')
        role = cleaned_data.get('role')
        state = cleaned_data.get('state')

        if not email and not employee_code:
            raise forms.ValidationError(
                'At least one of Email or Employee Code is required for login.'
            )

        if role in ('STATE_HEAD', 'COORDINATOR') and not state:
            self.add_error('state',
                f'State is required for {dict(User.Role.choices).get(role, role)}.'
            )

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        elif not user.pk:
            password = User.objects.make_random_password()
            user.set_password(password)
        if commit:
            user.save()
        self.generated_password = password if not self.cleaned_data.get('password') else None
        return user


class LoanApplicationForm(forms.ModelForm):
    class Meta:
        model = LoanApplication
        fields = [
            'applicant_name', 'gender', 'date_of_birth',
            'applicant_phone', 'applicant_email',
            'pan_number', 'aadhaar_number',
            'address', 'state', 'district', 'pincode',
            'loan_type', 'loan_amount', 'purpose',
            'tenure_months', 'annual_income', 'existing_loan',
        ]
        widgets = {
            'applicant_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500', 'placeholder': 'Full name as per ID'}),
            'gender': forms.Select(attrs={'class': 'w-full px-4 py-2.5 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-2.5 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'}),
            'applicant_phone': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 validate', 'placeholder': '9876543210', 'pattern': '[6-9]\\d{9}', 'inputmode': 'numeric', 'maxlength': '10', 'title': '10-digit mobile number starting with 6-9'}),
            'applicant_email': forms.EmailInput(attrs={'class': 'w-full px-4 py-2.5 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500', 'placeholder': 'email@example.com'}),
            'pan_number': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 validate', 'placeholder': 'ABCDE1234F', 'style': 'text-transform:uppercase', 'pattern': '[A-Z]{5}[0-9]{4}[A-Z]', 'maxlength': '10', 'title': 'PAN format: 5 letters + 4 digits + 1 letter'}),
            'aadhaar_number': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 validate', 'placeholder': 'XXXX XXXX XXXX', 'pattern': '\\d{4}\\s?\\d{4}\\s?\\d{4}', 'inputmode': 'numeric', 'maxlength': '14', 'title': '12-digit Aadhaar number (with or without spaces)'}),
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-4 py-2.5 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500', 'placeholder': 'Full residential address'}),
            'state': forms.Select(choices=[('', 'Select State...')] + INDIAN_STATES, attrs={'class': 'w-full px-4 py-2.5 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'}),
            'district': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500', 'placeholder': 'e.g. Pune'}),
            'pincode': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 validate', 'placeholder': '6-digit pincode', 'pattern': '\\d{6}', 'inputmode': 'numeric', 'maxlength': '6', 'title': '6-digit pincode'}),
            'loan_type': forms.Select(attrs={'class': 'w-full px-4 py-2.5 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'}),
            'loan_amount': forms.NumberInput(attrs={'class': 'w-full px-4 py-2.5 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500', 'placeholder': '₹ 10,00,000'}),
            'purpose': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-4 py-2.5 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500', 'placeholder': 'Describe the purpose of the loan'}),
            'tenure_months': forms.NumberInput(attrs={'class': 'w-full px-4 py-2.5 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500', 'placeholder': 'e.g. 60'}),
            'annual_income': forms.NumberInput(attrs={'class': 'w-full px-4 py-2.5 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500', 'placeholder': '₹ 5,00,000'}),
            'existing_loan': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-blue-600 border-slate-300 rounded focus:ring-blue-500'}),
        }

    def clean_pan_number(self):
        pan = self.cleaned_data.get('pan_number')
        if pan:
            pan = pan.upper().strip()
        return pan

    def clean_aadhaar_number(self):
        aadhaar = self.cleaned_data.get('aadhaar_number')
        if aadhaar:
            aadhaar = aadhaar.strip()
            if not aadhaar.isdigit() or len(aadhaar) != 12:
                raise forms.ValidationError('Aadhaar number must be 12 digits.')
        return aadhaar


ALLOWED_EXTENSIONS = {'.pdf', '.jpg', '.jpeg', '.png'}
MAX_FILE_SIZE = 5 * 1024 * 1024


class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = DocumentUpload
        fields = ['doc_type', 'file', 'remarks']
        widgets = {
            'doc_type': forms.Select(attrs={'class': 'w-full px-4 py-2.5 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'}),
            'file': forms.FileInput(attrs={'class': 'block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100'}),
            'remarks': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500', 'placeholder': 'Optional remarks'}),
        }

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            ext = os.path.splitext(file.name)[1].lower()
            if ext not in ALLOWED_EXTENSIONS:
                raise ValidationError(f'File type "{ext}" is not supported. Allowed: PDF, JPG, PNG.')
            if file.size > MAX_FILE_SIZE:
                raise ValidationError(f'File size must be under 5 MB. Current: {file.size / 1024 / 1024:.1f} MB.')
        return file


class ApplicationRemarkForm(forms.Form):
    remarks = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 3,
            'class': 'w-full px-4 py-2.5 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
            'placeholder': 'Add your remarks...',
        }),
    )
