from django.urls import path

from . import views

app_name = "builder"

urlpatterns = [
    path("start/", views.start_build, name="start"),
    path("building/<int:job_id>/", views.building, name="building"),
    path("building/<int:job_id>/retry/", views.retry_build, name="retry"),
    path("building/<int:job_id>/status/", views.job_status, name="job_status"),
    path("success/<int:job_id>/", views.success, name="success"),
    path("status/", views.builder_status, name="status"),
]
