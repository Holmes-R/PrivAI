from django import forms
from .models import Document


class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ["title", "file", "file_type"]
        widgets = {
            "file_type": forms.Select(choices=Document.FILE_TYPE_CHOICES[:3]),  # local only
        }

    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get("file")
        file_type = cleaned_data.get("file_type")

        if file_type in ["pdf", "txt", "docx"] and not file:
            raise forms.ValidationError("A local file is required for this type.")
        return cleaned_data