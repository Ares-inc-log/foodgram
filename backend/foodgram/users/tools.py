import base64
import os

from django.core.files.base import ContentFile
from rest_framework.serializers import ImageField


def normalize_avatar_path(instance, filename):
    base_name, ext = os.path.splitext(filename)

    if ext.lower() in [".jpeg", ".jpg"]:
        ext = ".jpg"

    return f"avatars/user_{instance.id}{ext}"


class Base64ImageField(ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            header, imgstr = data.split(";base64,")
            ext = header.split("/")[-1]

            if ext.lower() in ["jpeg", "jpg"]:
                ext = "jpg"

            data = ContentFile(base64.b64decode(imgstr), name=f"avatar.{ext}")

        return super().to_internal_value(data)
