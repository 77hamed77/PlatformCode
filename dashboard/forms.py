# dashboard/forms.py

from django import forms
from .models import Note, Task

# =================================================================
# Reusable Mixins
# =================================================================

class TitleValidationMixin:
    """
    1. REFACTORING FIX: A mixin to provide reusable title validation.
    This ensures that any form needing this validation will have the exact
    same logic, adhering to the DRY principle.
    """
    def clean_title(self):
        """
        Ensures the title is not just whitespace.
        """
        title = self.cleaned_data.get('title')
        if title and not title.strip():
            # 2. BEST PRACTICE: Centralized error messages
            raise forms.ValidationError("لا يمكن أن يتكون العنوان من مسافات فقط.")
        return title


# =================================================================
# Task Form
# =================================================================

class TaskForm(TitleValidationMixin, forms.ModelForm):
    """
    A form for creating and updating tasks.
    Inherits title validation logic from TitleValidationMixin.
    """
    class Meta:
        model = Task
        fields = ['title']
        labels = {
            'title': '', # Hide the label for a cleaner UI
        }


# =================================================================
# Note Form
# =================================================================

class NoteForm(TitleValidationMixin, forms.ModelForm):
    """

    A form for creating and updating notes with Markdown support.
    Inherits title validation logic from TitleValidationMixin.
    """
    class Meta:
        model = Note
        fields = ['title', 'content']

    def clean_content(self):
        """Example of another validation, e.g., for content length."""
        content = self.cleaned_data.get('content')
        if len(content) < 10:
            raise forms.ValidationError("محتوى المذكرة قصير جدًا. يجب أن يكون 10 أحرف على الأقل.")
        return content