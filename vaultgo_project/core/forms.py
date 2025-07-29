from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.validators import RegexValidator

from .models import CloudFile, Folder


class CloudFileForm(forms.ModelForm):
    class Meta:
        model = CloudFile
        fields = ["file"]


class FolderForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = ["name"]


class RenameFileForm(forms.ModelForm):
    class Meta:
        model = CloudFile
        fields = ["display_name"]


class RenameFolderForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = ["name"]


username_validator = RegexValidator(
    r"^[A-Za-z0-9._]+$",
    "Username may contain letters, numbers, dots and underscores only.",
)


class SignUpForm(UserCreationForm):
    """User creation form with Instagram-like username rules."""

    username = forms.CharField(
        max_length=30,
        min_length=3,
        validators=[username_validator],
        widget=forms.TextInput(attrs={"class": "auth-input"}),
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "auth-input"})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "auth-input"})
    )


class StyledAuthenticationForm(AuthenticationForm):
    """Login form using the same styling as SignUpForm."""

    username = forms.CharField(
        max_length=30, widget=forms.TextInput(attrs={"class": "auth-input"})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "auth-input"})
    )
