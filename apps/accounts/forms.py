"""Account forms."""

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class SignupForm(forms.Form):
    first_name = forms.CharField(
        max_length=150,
        label="First name",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Alex",
                "autocomplete": "given-name",
            }
        ),
    )
    last_name = forms.CharField(
        max_length=150,
        label="Last name",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Rivera",
                "autocomplete": "family-name",
            }
        ),
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={
                "placeholder": "name@company.com",
                "autocomplete": "email",
            }
        ),
    )
    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "••••••••",
                "autocomplete": "new-password",
            }
        ),
    )

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        if User.objects.filter(username__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean_password(self):
        password = self.cleaned_data["password"]
        validate_password(password)
        return password

    def save(self):
        email = self.cleaned_data["email"]
        user = User(
            username=email,
            email=email,
            first_name=self.cleaned_data["first_name"].strip(),
            last_name=self.cleaned_data["last_name"].strip(),
        )
        user.set_password(self.cleaned_data["password"])
        user.save()
        return user


class ProfileForm(forms.Form):
    """Customer profile — Settings → Account."""

    name = forms.CharField(
        max_length=255,
        label="Name",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Alex Rivera",
                "autocomplete": "name",
            }
        ),
    )
    username = forms.CharField(
        max_length=150,
        label="Username",
        widget=forms.TextInput(
            attrs={
                "placeholder": "alexrivera",
                "autocomplete": "username",
            }
        ),
    )
    company = forms.CharField(
        max_length=255,
        required=False,
        label="Company (Optional)",
        widget=forms.TextInput(
            attrs={
                "placeholder": "BrandBox Co.",
                "autocomplete": "organization",
            }
        ),
    )
    address = forms.CharField(
        required=False,
        label="Address",
        widget=forms.Textarea(
            attrs={
                "placeholder": "Street, city, country",
                "rows": 3,
                "autocomplete": "street-address",
            }
        ),
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={
                "placeholder": "name@company.com",
                "autocomplete": "email",
            }
        ),
    )
    phone = forms.CharField(
        max_length=64,
        required=False,
        label="Phone",
        widget=forms.TextInput(
            attrs={
                "placeholder": "+1 555 000 0000",
                "autocomplete": "tel",
            }
        ),
    )
    vertical_industry = forms.CharField(
        max_length=255,
        required=False,
        label="Vertical / Industry",
        widget=forms.TextInput(
            attrs={
                "placeholder": "e.g. Beauty, Pets, Home",
            }
        ),
    )
    desired_niche = forms.CharField(
        max_length=255,
        required=False,
        label="Desired Niche",
        widget=forms.TextInput(
            attrs={
                "placeholder": "e.g. Skincare, Outdoor gear",
            }
        ),
    )
    bio = forms.CharField(
        required=False,
        label="Bio",
        widget=forms.Textarea(
            attrs={
                "placeholder": "Short bio about you or your brand",
                "rows": 4,
            }
        ),
    )

    def __init__(self, *args, user=None, profile=None, **kwargs):
        self.user = user
        self.profile = profile
        super().__init__(*args, **kwargs)
        if user is not None and not self.is_bound:
            full = (user.get_full_name() or "").strip()
            self.fields["name"].initial = full or user.first_name or ""
            self.fields["username"].initial = user.username or ""
            self.fields["email"].initial = user.email or ""
        if profile is not None and not self.is_bound:
            self.fields["company"].initial = profile.company
            self.fields["address"].initial = profile.address
            self.fields["phone"].initial = profile.phone
            self.fields["vertical_industry"].initial = profile.vertical_industry
            self.fields["desired_niche"].initial = profile.desired_niche
            self.fields["bio"].initial = profile.bio

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if not username:
            raise forms.ValidationError("Enter a username.")
        qs = User.objects.filter(username__iexact=username)
        if self.user is not None:
            qs = qs.exclude(pk=self.user.pk)
        if qs.exists():
            raise forms.ValidationError("That username is already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        qs = User.objects.filter(email__iexact=email)
        if self.user is not None:
            qs = qs.exclude(pk=self.user.pk)
        if qs.exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def save(self):
        from apps.dashboard.models import MerchantProfile

        user = self.user
        profile = self.profile or MerchantProfile.for_user(user)

        name = self.cleaned_data["name"].strip()
        parts = name.split(None, 1)
        user.first_name = parts[0] if parts else ""
        user.last_name = parts[1] if len(parts) > 1 else ""
        user.username = self.cleaned_data["username"]
        user.email = self.cleaned_data["email"]
        user.save(update_fields=["first_name", "last_name", "username", "email"])

        profile.company = self.cleaned_data.get("company", "").strip()
        profile.address = self.cleaned_data.get("address", "").strip()
        profile.phone = self.cleaned_data.get("phone", "").strip()
        profile.vertical_industry = self.cleaned_data.get("vertical_industry", "").strip()
        profile.desired_niche = self.cleaned_data.get("desired_niche", "").strip()
        profile.bio = self.cleaned_data.get("bio", "").strip()
        profile.save()
        return profile
