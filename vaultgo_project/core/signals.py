import os
import shutil

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import CloudFile, Folder


@receiver(post_save, sender=Folder)
def create_folder_dir(sender, instance, created, **kwargs):
    if created:
        os.makedirs(instance.absolute_path(), exist_ok=True)


@receiver(post_delete, sender=Folder)
def remove_folder_dir(sender, instance, **kwargs):
    path = instance.absolute_path()
    if os.path.exists(path):
        shutil.rmtree(path, ignore_errors=True)


@receiver(post_delete, sender=CloudFile)
def remove_cloud_file(sender, instance, **kwargs):
    if instance.file:
        instance.file.delete(save=False)
