from __future__ import annotations

import datetime
import secrets
import string
from typing import TYPE_CHECKING

from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView
from django.views.generic import FormView
from django.views.generic import RedirectView
from django.views.generic import UpdateView

from project_rokto.users.forms import NIDSubmissionForm
from project_rokto.users.forms import OTPVerifyForm
from project_rokto.users.forms import PhoneAddForm
from project_rokto.users.forms import PhoneLoginForm
from project_rokto.users.forms import UserInfoForm
from project_rokto.users.forms import UserUpdateForm
from project_rokto.users.models import NIDVerification
from project_rokto.users.models import OTPRequest
from project_rokto.users.models import User

if TYPE_CHECKING:
    from django.db.models import QuerySet


from django.core.exceptions import PermissionDenied


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    slug_field = "username"
    slug_url_kwarg = "username"

    def get_object(self, queryset: QuerySet | None = None) -> User:
        obj = super().get_object(queryset)
        if obj != self.request.user:
            raise PermissionDenied(
                _("You do not have permission to view this profile."),
            )
        return obj


user_detail_view = UserDetailView.as_view()


class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    success_message = _("Information successfully updated")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get unique values for autocomplete
        # Flatten ArrayField values and get unique ones
        existing_allergies = set()
        existing_conditions = set()

        for user in User.objects.all():
            if user.allergies:
                existing_allergies.update(user.allergies)
            if user.health_conditions:
                existing_conditions.update(user.health_conditions)

        context["existing_allergies"] = sorted(existing_allergies)
        context["existing_conditions"] = sorted(existing_conditions)
        return context

    def get_success_url(self) -> str:
        assert self.request.user.is_authenticated  # type guard
        return self.request.user.get_absolute_url()

    def get_object(self, queryset: QuerySet | None = None) -> User:
        assert self.request.user.is_authenticated  # type guard
        return self.request.user


user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self) -> str:
        return reverse("users:detail", kwargs={"username": self.request.user.username})


user_redirect_view = UserRedirectView.as_view()


class PhoneLoginView(FormView):
    template_name = "users/phone_login.html"
    form_class = PhoneLoginForm

    def form_valid(self, form):
        phone_number = form.cleaned_data["phone_number"]
        otp_code = "".join(secrets.choice(string.digits) for _ in range(6))

        OTPRequest.objects.create(
            phone_number=phone_number,
            otp_code=otp_code,
            expires_at=timezone.now() + datetime.timedelta(minutes=5),
        )

        self.request.session["phone_number"] = phone_number
        return redirect("users:otp_verify")


phone_login_view = PhoneLoginView.as_view()


class OTPVerifyView(FormView):
    template_name = "users/otp_verify.html"
    form_class = OTPVerifyForm

    def form_valid(self, form):
        phone_number = self.request.session.get("phone_number")
        otp_code = form.cleaned_data["otp_code"]

        try:
            otp_request = OTPRequest.objects.filter(
                phone_number=phone_number,
                otp_code=otp_code,
                is_used=False,
            ).latest("created_at")

            if otp_request.is_valid():
                otp_request.is_used = True
                otp_request.save()
                # Delete the OTP request after use for security
                otp_request.delete()

                user = User.objects.filter(phone_number=phone_number).first()
                if user:
                    if not user.is_phone_verified:
                        user.is_phone_verified = True
                        user.save()
                    login(
                        self.request,
                        user,
                        backend="project_rokto.users.backends.PhoneOTPBackend",
                    )
                    if "phone_number" in self.request.session:
                        del self.request.session["phone_number"]
                    return redirect("users:redirect")
                # New user flow: store verified phone and redirect to info collection
                self.request.session["verified_phone_number"] = phone_number
                return redirect("users:signup_info")
        except OTPRequest.DoesNotExist:
            pass

        form.add_error("otp_code", _("Invalid or expired OTP."))
        return self.form_invalid(form)


otp_verify_view = OTPVerifyView.as_view()


class SignupInfoView(FormView):
    template_name = "users/signup_info.html"
    form_class = UserInfoForm

    def dispatch(self, request, *args, **kwargs):
        if "verified_phone_number" not in request.session:
            return redirect("users:phone_login")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        phone_number = self.request.session.pop("verified_phone_number")
        user = form.save(commit=False)
        user.phone_number = phone_number
        user.username = phone_number  # Phone number as username
        user.is_phone_verified = True
        user.set_unusable_password()
        user.save()
        login(
            self.request,
            user,
            backend="project_rokto.users.backends.PhoneOTPBackend",
        )
        return redirect("users:redirect")


signup_info_view = SignupInfoView.as_view()


class NIDSubmissionView(LoginRequiredMixin, SuccessMessageMixin, FormView):
    template_name = "users/nid_submission.html"
    form_class = NIDSubmissionForm
    success_message = _("NID submitted successfully for verification.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        assert self.request.user.is_authenticated
        user = self.request.user

        nid = NIDVerification.objects.filter(user=user).first()
        context["nid"] = nid
        context["attempts_left"] = (
            User.MAX_VERIFICATION_ATTEMPTS - user.verification_attempts
        )
        context["max_attempts"] = User.MAX_VERIFICATION_ATTEMPTS
        return context

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)

        assert request.user.is_authenticated
        user = request.user

        nid = NIDVerification.objects.filter(user=user).first()

        # If already verified, no need to submit again
        if nid and nid.status == NIDVerification.Status.VERIFIED:
            return self.render_to_response(self.get_context_data())

        # If pending, don't allow new submission
        if nid and nid.status == NIDVerification.Status.PENDING:
            return self.render_to_response(self.get_context_data())

        # If max attempts reached and not verified
        if user.verification_attempts >= User.MAX_VERIFICATION_ATTEMPTS:
            return self.render_to_response(self.get_context_data())

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        assert self.request.user.is_authenticated
        user = self.request.user

        # Double check attempts and pending status
        nid = NIDVerification.objects.filter(user=user).first()
        if user.verification_attempts >= User.MAX_VERIFICATION_ATTEMPTS or (
            nid and nid.status == NIDVerification.Status.PENDING
        ):
            return redirect(self.get_success_url())

        if not nid:
            nid = NIDVerification(user=user)

        nid.front_image = form.cleaned_data["front_image"]
        nid.back_image = form.cleaned_data["back_image"]
        nid.status = NIDVerification.Status.PENDING
        nid.save()

        user.verification_attempts += 1
        user.save()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse("users:detail", kwargs={"username": self.request.user.username})


nid_submission_view = NIDSubmissionView.as_view()


class PhoneManageView(LoginRequiredMixin, FormView):
    template_name = "users/phone_manage.html"
    form_class = PhoneAddForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        phone_number = form.cleaned_data["phone_number"]

        assert self.request.user.is_authenticated
        user = self.request.user

        # If number is same and already verified, just stay here
        if user.phone_number == phone_number and user.is_phone_verified:
            return redirect("users:phone_manage")

        otp_code = "".join(secrets.choice(string.digits) for _ in range(6))

        OTPRequest.objects.create(
            phone_number=phone_number,
            otp_code=otp_code,
            expires_at=timezone.now() + datetime.timedelta(minutes=5),
        )
        self.request.session["pending_phone_number"] = phone_number
        return redirect("users:phone_verify_otp")


phone_manage_view = PhoneManageView.as_view()


class PhoneVerifyOTPView(LoginRequiredMixin, FormView):
    template_name = "users/otp_verify.html"
    form_class = OTPVerifyForm

    def form_valid(self, form):
        phone_number = self.request.session.get("pending_phone_number")
        otp_code = form.cleaned_data["otp_code"]

        try:
            otp_request = OTPRequest.objects.filter(
                phone_number=phone_number,
                otp_code=otp_code,
                is_used=False,
            ).latest("created_at")

            if otp_request.is_valid():
                otp_request.is_used = True
                otp_request.save()
                # Delete the OTP request after use for security
                otp_request.delete()

                assert self.request.user.is_authenticated
                user = self.request.user
                user.phone_number = phone_number
                user.is_phone_verified = True
                user.save()

                if "pending_phone_number" in self.request.session:
                    del self.request.session["pending_phone_number"]

                return redirect("users:phone_manage")
        except OTPRequest.DoesNotExist:
            pass

        form.add_error("otp_code", _("Invalid or expired OTP."))
        return self.form_invalid(form)


phone_verify_otp_view = PhoneVerifyOTPView.as_view()
