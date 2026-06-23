from rest_framework import serializers
from .models import Document
from .vector_store import get_user_collection


IMAGE_SIGNATURES = {
    b"\x89PNG": "PNG image",
    b"\xff\xd8\xff": "JPEG image",
    b"GIF": "GIF image",
    b"BM": "BMP image",
    b"RIFF": "WebP/RIFF image",
}


def _check_file_signature(file_obj, expected_type: str) -> tuple:
    """Verify the uploaded file's magic bytes match the declared type and reject images."""
    magic = file_obj.read(8)
    file_obj.seek(0)

    for sig, label in IMAGE_SIGNATURES.items():
        if magic.startswith(sig):
            return False, f"{label} detected — only PDF, DOCX, and TXT files are supported."

    if expected_type == "pdf":
        if magic[:5] != b"%PDF-":
            return False, "File does not have a PDF signature (must start with %PDF-)."
    elif expected_type == "docx":
        if magic[:2] != b"PK":
            return False, "File is not a valid DOCX (must be a ZIP archive starting with PK)."
    elif expected_type == "txt":
        if b"\x00" in magic:
            return False, "File contains null bytes — not a valid text file."

    return True, ""


class DocumentSerializer(serializers.ModelSerializer):
    chunk_count = serializers.SerializerMethodField()

    file_type = serializers.ChoiceField(
        choices=[
            ("pdf", "PDF"),
            ("txt", "Text"),
            ("docx", "Word"),
        ]
    )

    class Meta:
        model = Document
        fields = [
            "id", "title", "file_type", "file",
            "remote_id", "remote_url", "created_at", "updated_at",
            "chunk_count",
        ]
        read_only_fields = [
            "id", "remote_id", "remote_url", "created_at", "updated_at", "chunk_count",
        ]

    def get_chunk_count(self, obj):
        try:
            collection = get_user_collection(obj.user_id)
            ids = collection.get(where={"document_id": obj.id}).get("ids", [])
            return len(ids)
        except Exception:
            return 0

    def validate(self, attrs):
        file_type = attrs.get("file_type")
        file_obj = attrs.get("file")
        if file_type and not file_obj:
            raise serializers.ValidationError(
                "A file is required for local upload (pdf/txt/docx)."
            )
        if file_type and file_obj:
            valid, err_msg = _check_file_signature(file_obj, file_type)
            if not valid:
                raise serializers.ValidationError(
                    {"file": f"Type mismatch: selected '{file_type}' but {err_msg}"}
                )
        return attrs

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)
