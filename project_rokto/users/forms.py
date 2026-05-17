from allauth.account.forms import SignupForm
from allauth.socialaccount.forms import SignupForm as SocialSignupForm
from django import forms
from django.contrib.auth import forms as admin_forms
from django.utils.translation import gettext_lazy as _

from project_rokto.donors.models import Donor
from project_rokto.locations.models import Location

from .models import NIDVerification
from .models import NotificationPreference
from .models import User
from .models import phone_validator


class UserUpdateForm(forms.ModelForm):
    # Donor fields
    blood_group = forms.ChoiceField(
        choices=Donor.BloodGroup.choices,
        required=False,
        label=_("Blood Group"),
    )
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
        label=_("Date of Birth"),
    )
    last_donation_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
        label=_("Last Blood Donation Date"),
    )
    resume_donation_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
        label=_("Date to Resume Donation"),
    )
    is_available_to_donate = forms.BooleanField(
        required=False,
        label=_("Available to Donate"),
    )
    allergies = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "tag-input", "placeholder": _("Add allergies...")},
        ),
        label=_("Allergies"),
    )
    health_conditions = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "tag-input",
                "placeholder": _("Add health conditions..."),
            },
        ),
        label=_("Known Health Conditions"),
    )
    preferred_locations = forms.ModelMultipleChoiceField(
        queryset=Location.objects.none(),
        required=False,
        widget=forms.SelectMultiple(
            attrs={
                "class": "location-select",
                "placeholder": _("Add locations..."),
            },
        ),
        label=_("Preferred Blood Donation Locations"),
    )

    class Meta:
        model = User
        fields = ["name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            donor = getattr(self.instance, "donor_profile", None)
            if donor:
                self.initial["blood_group"] = donor.blood_group
                self.initial["date_of_birth"] = donor.date_of_birth
                self.initial["last_donation_date"] = donor.last_donation_date
                self.initial["resume_donation_date"] = donor.resume_donation_date
                self.initial["is_available_to_donate"] = donor.is_available_to_donate
                if donor.allergies:
                    self.initial["allergies"] = ",".join(donor.allergies)
                if donor.health_conditions:
                    self.initial["health_conditions"] = ",".join(
                        donor.health_conditions,
                    )

                # Base queryset: already selected locations

                qs = donor.preferred_locations.all()
            else:
                qs = Location.objects.none()

            # If form is submitted, include newly selected IDs in the queryset
            if self.is_bound:
                if hasattr(self.data, "getlist"):
                    selected_ids = self.data.getlist("preferred_locations")
                else:
                    val = self.data.get("preferred_locations")
                    selected_ids = (
                        val if isinstance(val, list) else [val] if val else []
                    )

                if selected_ids:
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

    def save(self, commit: bool = True):  # noqa: FBT001, FBT002
        user = super().save(commit=commit)
        donor, _ = Donor.objects.get_or_create(user=user)

        donor.blood_group = self.cleaned_data.get("blood_group") or ""
        donor.date_of_birth = self.cleaned_data.get("date_of_birth")
        donor.last_donation_date = self.cleaned_data.get("last_donation_date")
        donor.resume_donation_date = self.cleaned_data.get("resume_donation_date")
        donor.is_available_to_donate = bool(
            self.cleaned_data.get("is_available_to_donate")
        )
        donor.allergies = self.cleaned_data.get("allergies") or []
        donor.health_conditions = self.cleaned_data.get("health_conditions") or []

        if commit:
            donor.save()
            pref_locations = self.cleaned_data.get("preferred_locations")
            if pref_locations is not None:
                donor.preferred_locations.set(pref_locations)

        return user


class UserAdminCreationForm(admin_forms.AdminUserCreationForm):
    """
    Form for User Creation in the Admin Area.
    To change user signup, see UserSignupForm and UserSocialSignupForm.
    """

    class Meta(admin_forms.AdminUserCreationForm.Meta):
        model = User
        error_messages = {
            "username": {"unique": _("This username has already been taken.")},
        }


class UserAdminChangeForm(admin_forms.UserChangeForm):
    class Meta(admin_forms.UserChangeForm.Meta):
        model = User


class UserSignupForm(SignupForm):
    """
    Form that will be rendered on a signup page.
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
        widget=forms.TextInput(
            attrs={"placeholder": _("Phone Number"), "class": "form-control"},
        ),
    )


class OTPVerifyForm(forms.Form):
    otp_code = forms.CharField(
        max_length=6,
        widget=forms.TextInput(
            attrs={"placeholder": _("OTP Code"), "class": "form-control"},
        ),
    )


class PhoneAddForm(forms.Form):
    phone_number = forms.CharField(
        max_length=15,
        validators=[phone_validator],
        widget=forms.TextInput(
            attrs={"placeholder": _("Phone Number"), "class": "form-control"},
        ),
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        qs = User.objects.filter(phone_number=phone_number)
        if self.user:
            qs = qs.exclude(pk=self.user.pk)
        if qs.exists():
            raise forms.ValidationError(_("This phone number is already in use."))
        return phone_number


class UserInfoForm(forms.ModelForm):
    email = forms.EmailField(
        required=False,
        label=_("Email (optional)"),
    )

    class Meta:
        model = User
        fields = ["name", "email"]


class NIDSubmissionForm(forms.ModelForm):
    class Meta:
        model = NIDVerification
        fields = ["front_image", "back_image"]


class NotificationPreferenceForm(forms.ModelForm):
    class Meta:
        model = NotificationPreference
        fields = [
            "email_enabled",
            "sms_enabled",
            "web_push_enabled",
            "emergency_alerts",
            "org_invites",
            "reminders",
        ]
