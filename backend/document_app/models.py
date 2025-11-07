from django.db import models
from django.conf import settings
from django.utils import timezone
                                  
User = settings.AUTH_USER_MODEL


class Document(models.Model):
    FILE_TYPE_CHOICES = [
        ("pdf", "PDF"),
        ("txt", "Text"),
        ("docx", "Word"),
        ("gdoc", "Google Doc"),
        ("notion", "Notion Page"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="documents"
    )
    title = models.CharField(max_length=255)
    file = models.FileField(
        upload_to="documents/%Y/%m/%d/",
        blank=True,
        null=True,
        help_text="Local file (pdf/txt/docx). Leave empty for remote sync."
    )
    file_type = models.CharField(max_length=10, choices=FILE_TYPE_CHOICES)
    remote_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Google Drive file ID or Notion page ID"
    )
    remote_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "documents"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.get_file_type_display()})"