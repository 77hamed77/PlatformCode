# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    # أضف الحقول الجديدة هنا لتظهر في لوحة التحكم
    list_display = ['username', 'email', 'academic_year', 'path', 'score', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ('المعلومات الأكاديمية', {'fields': ('academic_year', 'path')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)

