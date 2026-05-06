from allauth.account.forms import SignupForm
from allauth.socialaccount.forms import SignupForm as SocialSignupForm
from django import forms
from django.contrib.auth import forms as admin_forms
from django.utils.translation import gettext_lazy as _

from project_rokto.locations.models import Location

from .models import NIDVerification
from .models import User
from .models import phone_validator


class UserAdminChangeForm(admin_forms.UserChangeForm):
    class Meta(admin_forms.UserChangeForm.Meta):
        model = User
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
            "last_donation_date": forms.DateInput(attrs={"type": "date"}),
            "resume_donation_date": forms.DateInput(attrs={"type": "date"}),
        }


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "name",
            "date_of_birth",
            "blood_group",
            "last_donation_date",
            "allergies",
            "health_conditions",
            "is_available_to_donate",
            "resume_donation_date",
            "preferred_locations",
        ]
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
            "last_donation_date": forms.DateInput(attrs={"type": "date"}),
            "resume_donation_date": forms.DateInput(attrs={"type": "date"}),
            "allergies": forms.TextInput(
                attrs={"class": "tag-input", "placeholder": _("Add allergies...")},
            ),
            "health_conditions": forms.TextInput(
                attrs={
                    "class": "tag-input",
                    "placeholder": _("Add health conditions..."),
                },
            ),
            "preferred_locations": forms.SelectMultiple(
                attrs={
                    "class": "location-select",
                    "placeholder": _("Add locations..."),
                },
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            if self.instance.allergies:
                self.initial["allergies"] = ",".join(self.instance.allergies)
            if self.instance.health_conditions:
                self.initial["health_conditions"] = ",".join(
                    self.instance.health_conditions,
                )

        # Base queryset: already selected locations
        if self.instance and self.instance.pk:
            qs = self.instance.preferred_locations.all()
        else:
            qs = Location.objects.none()

        # If form is submitted, include newly selected IDs in the queryset
        # so that Django's validation doesn't reject them
        if self.is_bound:
            # self.data is typically a QueryDict which has getlist
            selected_ids = []
            if hasattr(self.data, "getlist"):
                selected_ids = self.data.getlist("preferred_locations")
            else:
                # Fallback for non-QueryDict mappings
                val = self.data.get("preferred_locations")
                if val:
                    selected_ids = val if isinstance(val, list) else [val]

            if selected_ids:
                # Merge current selection with existing selection
                qs = (qs | Location.objects.filter(id__in=selected_ids)).distinct()

        self.fields["preferred_locations"].queryset = qs  # type: ignore[attr-defined]

    def clean_allergies(self):
        data = self.cleaned_data.get("allergies")
        if isinstance(data, str):
            return [x.strip() for x in data.split(",") if x.strip()]
        return data

    def clean_health_conditions(self):
        data = self.cleaned_data.get("health_conditions")
        if isinstance(data, str):
            return [x.strip() for x in data.split(",") if x.strip()]
        return data


class UserAdminCreationForm(admin_forms.AdminUserCreationForm):
    """
    Form for User Creation in the Admin Area.
    To change user signup, see UserSignupForm and UserSocialSignupForm.
    """

    class Meta(admin_forms.UserCreationForm.Meta):
        model = User
        error_messages = {
            "username": {"unique": _("This username has already been taken.")},
        }


class UserSignupForm(SignupForm):
    """
    Form that will be rendered on a user sign up section/screen.
    Default fields will be added automatically.
    Check UserSocialSignupForm for accounts created from social.
    """


class UserSocialSignupForm(SocialSignupForm):
    """
    Renders the form when user has signed up using social accounts.
    Default fields will be added automatically.
    See UserSignupForm otherwise.
    """


class PhoneLoginForm(forms.Form):
    phone_number = forms.CharField(
        max_length=15,
        validators=[phone_validator],
        widget=forms.TextInput(attrs={"placeholder": "01XXXXXXXXX"}),
        label=_("Phone Number"),
    )


class OTPVerifyForm(forms.Form):
    otp_code = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={"placeholder": "123456"}),
        label=_("OTP Code"),
    )


class NIDSubmissionForm(forms.ModelForm):
    class Meta:
        model = NIDVerification
        fields = ["front_image", "back_image"]


class PhoneAddForm(forms.Form):
    phone_number = forms.CharField(
        max_length=15,
        validators=[phone_validator],
        widget=forms.TextInput(attrs={"placeholder": "01XXXXXXXXX"}),
        label=_("Phone Number"),
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        user_qs = User.objects.filter(phone_number=phone_number)
        if self.user and self.user.pk:
            user_qs = user_qs.exclude(pk=self.user.pk)
        if user_qs.exists():
            raise forms.ValidationError(_("This phone number is already in use."))
        return phone_number


class UserInfoForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["name", "email"]
