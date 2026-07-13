from django.urls import path

from .views import ContactView, HomeView, NewsletterSubscribeView

app_name = "home"

urlpatterns = [
    path("", HomeView.as_view(), name="index"),
    path("contact/", ContactView.as_view(), name="contact"),
    path(
        "newsletter/",
        NewsletterSubscribeView.as_view(),
        name="newsletter",
    ),
]
