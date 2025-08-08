# accounts/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

# =================================================================
# Form for User Registration (Signup)
# =================================================================

class CustomUserCreationForm(UserCreationForm):
    """
    A form for creating new users. Includes all the required fields, plus a
    repeated password.
    """
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'academic_year', 'path')


# =================================================================
# Form for the Django Admin Panel
# =================================================================

class CustomUserChangeForm(UserChangeForm):
    """
    A form for updating users in the admin panel.
    It allows changing all user fields.
    """
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 
                  'is_staff', 'is_moderator', 'is_active',
                  'academic_year', 'path', 'score', 'avatar')


# =================================================================
# Form for the User-Facing Profile Page
# =================================================================

class ProfileUpdateForm(forms.ModelForm):
    """
    A form for users to update their own profile information from the frontend.
    This form is more limited than the admin form for security.
    """
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'avatar']
        
        widgets = {
            'avatar': forms.RadioSelect,
        }

        labels = {
            'first_name': 'الاسم الأول',
            'last_name': 'اسم العائلة',
            'email': 'البريد الإلكتروني',
            'avatar': 'اختر صورتك الرمزية',
        }

    def clean_email(self):
        """
        Ensures that the new email address is unique among other users.
        """
        email = self.cleaned_data.get('email')
        if self.instance and CustomUser.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("هذا البريد الإلكتروني مسجل بالفعل.")
        return email