from django.db import models
from django.conf import settings


class ChatHistory(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="chat_history"
    )
    document = models.ForeignKey(
        "document_app.Document", on_delete=models.CASCADE, related_name="chat_history"
    )
    question = models.TextField()
    answer = models.TextField()
    sources = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "chat_history"
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.user.email} - {self.document.title} - {self.question[:50]}"
