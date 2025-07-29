from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("signup/", views.signup, name="signup"),
    path("download/<int:pk>/", views.download_file, name="download_file"),
    path("view/<int:pk>/", views.view_file, name="view_file"),
    path("file/<int:pk>/", views.file_detail, name="file_detail"),
    path("folder/<int:pk>/", views.folder_detail, name="folder_detail"),
    path("move/<int:pk>/", views.move_file, name="move_file"),
    path("move_folder/<int:pk>/", views.move_folder, name="move_folder"),
    path("logout/", views.logout_view, name="logout"),
]
