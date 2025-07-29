import os
import shutil
from io import BytesIO

from cryptography.fernet import Fernet
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files import File
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.db import models


class EncryptedFileSystemStorage(FileSystemStorage):
    """File storage that encrypts data at rest using Fernet."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        key = settings.FILE_ENCRYPTION_KEY
        if isinstance(key, str):
            key = key.encode()
        self.fernet = Fernet(key)

    def _save(self, name, content):
        data = content.read()
        encrypted = self.fernet.encrypt(data)
        return super()._save(name, ContentFile(encrypted))

    def _open(self, name, mode="rb"):
        f = super()._open(name, mode)
        data = f.read()
        f.close()
        decrypted = self.fernet.decrypt(data)
        return File(BytesIO(decrypted), name)


encrypted_storage = EncryptedFileSystemStorage()


def _user_root(user_id: int) -> str:
    """Return the relative storage path for a user's root directory."""
    return os.path.join("users", f"user_{user_id}")


class Folder(models.Model):
    """A simple folder owned by a user. Folders can be nested."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subfolders",
    )

    class Meta:
        unique_together = ("user", "parent", "name")

    def __str__(self):
        return self.name

    def _path_segments(self):
        segments = []
        if self.parent:
            segments.extend(self.parent._path_segments())
        segments.append(f"folder_{self.pk}")
        return segments

    def relative_path(self) -> str:
        """Return the folder's directory relative to MEDIA_ROOT."""
        return os.path.join(_user_root(self.user_id), *self._path_segments())

    def absolute_path(self) -> str:
        return os.path.join(settings.MEDIA_ROOT, self.relative_path())

    def move_to(self, parent):
        """Move this folder (and its contents) to a new parent."""
        old_path = self.absolute_path()
        self.parent = parent
        new_path = self.absolute_path()
        os.makedirs(os.path.dirname(new_path), exist_ok=True)
        if os.path.exists(old_path):
            shutil.move(old_path, new_path)
        self.save()


class CloudFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def upload_to(instance, filename):
        base = _user_root(instance.user_id)
        if instance.folder:
            base = os.path.join(base, *instance.folder._path_segments())
        return os.path.join(base, filename)

    file = models.FileField(upload_to=upload_to, storage=encrypted_storage)
    folder = models.ForeignKey(
        Folder, on_delete=models.CASCADE, null=True, blank=True, related_name="files"
    )
    display_name = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.display_name:
            self.display_name = self.filename
        super().save(*args, **kwargs)

    def __str__(self):
        return self.display_name or self.filename

    @property
    def filename(self):
        return os.path.basename(self.file.name)

    @property
    def is_image(self):
        ext = os.path.splitext(self.filename)[1].lower()
        return ext in [".png", ".jpg", ".jpeg", ".gif"]

    def get_view_url(self):
        from django.urls import reverse

        return reverse("view_file", args=[self.pk])

    def move_to(self, folder):
        """Move this file to a new folder on disk and update its path."""
        old_path = self.file.path
        self.folder = folder
        new_rel = CloudFile.upload_to(self, os.path.basename(self.file.name))
        new_abs = os.path.join(settings.MEDIA_ROOT, new_rel)
        os.makedirs(os.path.dirname(new_abs), exist_ok=True)
        if os.path.exists(old_path):
            shutil.move(old_path, new_abs)
        self.file.name = new_rel
        self.save()
