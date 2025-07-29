import os

from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (
    CloudFileForm,
    FolderForm,
    RenameFileForm,
    RenameFolderForm,
    SignUpForm,
    StyledAuthenticationForm,
)
from .models import CloudFile, Folder


def index(request):
    """Render the landing page."""
    return render(request, "index.html")


@login_required
def dashboard(request):
    """Display the contents of the current folder and handle uploads/folder creation."""
    folder_id = request.GET.get("folder")
    current_folder = None
    if folder_id:
        current_folder = get_object_or_404(Folder, pk=folder_id, user=request.user)

    if request.method == "POST":
        if "create_folder" in request.POST:
            fform = FolderForm(request.POST)
            if fform.is_valid():
                folder = fform.save(commit=False)
                folder.user = request.user
                folder.parent = current_folder
                folder.save()
                return redirect(
                    request.path
                    + (f"?folder={current_folder.id}" if current_folder else "")
                )
        else:
            form = CloudFileForm(request.POST, request.FILES)
            if form.is_valid():
                uploaded = request.FILES.get("file") or form.cleaned_data["file"]
                cloud_file = CloudFile(
                    file=uploaded, user=request.user, folder=current_folder
                )
                cloud_file.save()
                return redirect(
                    request.path
                    + (f"?folder={current_folder.id}" if current_folder else "")
                )
    else:
        form = CloudFileForm()
        fform = FolderForm()

    files = CloudFile.objects.filter(user=request.user, folder=current_folder).order_by(
        "-uploaded_at"
    )
    folders = Folder.objects.filter(user=request.user, parent=current_folder).order_by(
        "name"
    )
    return render(
        request,
        "dashboard.html",
        {
            "form": form,
            "folder_form": fform,
            "files": files,
            "folders": folders,
            "current_folder": current_folder,
        },
    )


def signup(request):
    """Register a new user account."""
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = SignUpForm()
    return render(request, "registration/signup.html", {"form": form})


class CustomLoginView(LoginView):
    """Login view using StyledAuthenticationForm."""

    authentication_form = StyledAuthenticationForm


@login_required
def download_file(request, pk):
    """Download a stored file as an attachment."""
    cloud_file = get_object_or_404(CloudFile, pk=pk, user=request.user)
    return FileResponse(
        cloud_file.file.open("rb"),
        as_attachment=True,
        filename=os.path.basename(cloud_file.file.name),
    )


@login_required
def view_file(request, pk):
    """Serve a decrypted file for inline viewing."""
    cloud_file = get_object_or_404(CloudFile, pk=pk, user=request.user)
    return FileResponse(
        cloud_file.file.open("rb"), filename=os.path.basename(cloud_file.file.name)
    )


@login_required
def file_detail(request, pk):
    """Display a preview for a single file with options to rename or delete."""
    cloud_file = get_object_or_404(CloudFile, pk=pk, user=request.user)

    if request.method == "POST":
        if "delete" in request.POST:
            parent_id = cloud_file.folder_id
            cloud_file.file.delete()
            cloud_file.delete()
            redirect_url = (
                f"/dashboard/?folder={parent_id}" if parent_id else "/dashboard/"
            )
            return redirect(redirect_url)
        else:
            form = RenameFileForm(request.POST, instance=cloud_file)
            if form.is_valid():
                form.save()
    else:
        form = RenameFileForm(instance=cloud_file)

    ext = os.path.splitext(cloud_file.filename)[1].lower()
    is_image = ext in [".png", ".jpg", ".jpeg", ".gif"]
    is_pdf = ext == ".pdf"
    return render(
        request,
        "file_detail.html",
        {
            "file": cloud_file,
            "form": form,
            "is_image": is_image,
            "is_pdf": is_pdf,
        },
    )


@login_required
def move_file(request, pk):
    """Handle drag-and-drop move requests for a single file."""
    if request.method == "POST":
        cloud_file = get_object_or_404(CloudFile, pk=pk, user=request.user)
        target_id = request.POST.get("target_folder")
        target_folder = None
        if target_id:
            target_folder = get_object_or_404(Folder, pk=target_id, user=request.user)
        cloud_file.move_to(target_folder)
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            from django.http import JsonResponse

            return JsonResponse({"status": "ok"})
    return redirect("dashboard")


@login_required
def move_folder(request, pk):
    """Handle drag-and-drop move requests for a folder."""
    if request.method == "POST":
        folder = get_object_or_404(Folder, pk=pk, user=request.user)
        target_id = request.POST.get("target_folder")
        target_folder = None
        if target_id:
            target_folder = get_object_or_404(Folder, pk=target_id, user=request.user)
            ancestor = target_folder
            while ancestor:
                if ancestor.pk == folder.pk:
                    if request.headers.get("x-requested-with") == "XMLHttpRequest":
                        from django.http import JsonResponse

                        return JsonResponse({"status": "invalid"}, status=400)
                    return redirect("dashboard")
                ancestor = ancestor.parent
        folder.move_to(target_folder)
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            from django.http import JsonResponse

            return JsonResponse({"status": "ok"})
    return redirect("dashboard")


@login_required
def folder_detail(request, pk):
    """Rename or delete a folder."""
    folder = get_object_or_404(Folder, pk=pk, user=request.user)

    if request.method == "POST":
        if "delete" in request.POST:
            parent_id = folder.parent_id
            folder.delete()
            redirect_url = (
                f"/dashboard/?folder={parent_id}" if parent_id else "/dashboard/"
            )
            return redirect(redirect_url)
        else:
            form = RenameFolderForm(request.POST, instance=folder)
            if form.is_valid():
                form.save()
    else:
        form = RenameFolderForm(instance=folder)
    return render(request, "folder_detail.html", {"folder": folder, "form": form})


def logout_view(request):
    """Log the user out and redirect to ``LOGOUT_REDIRECT_URL``."""
    logout(request)
    redirect_url = getattr(settings, "LOGOUT_REDIRECT_URL", "/") or "/"
    return redirect(redirect_url)


def custom_404(request, exception):
    """Render a friendly 404 page."""
    return render(request, "404.html", status=404)
