from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from project_rokto.organizations.services import NotificationDispatcher

from .models import BloodRequest
from .models import BloodRequestDonor
from .serializers import BloodRequestCreateSerializer
from .serializers import BloodRequestDashboardSerializer
from .serializers import BloodRequestDonorDashboardSerializer


class BloodRequestViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for managing blood requests.
    """

    queryset = BloodRequest.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            return BloodRequestCreateSerializer
        return BloodRequestDashboardSerializer

    def get_queryset(self):
        return super().get_queryset().filter(seeker=self.request.user)

    @action(detail=True, methods=["post"])
    def reveal_contact(self, request, pk=None):
        """
        Reveals the donor's contact information to the seeker, or vice-versa.
        """
        entry = get_object_or_404(BloodRequestDonor, pk=pk)
        actor = request.data.get("actor")

        if entry.response_status != BloodRequestDonor.ResponseStatus.ACCEPTED:
            return Response(
                {"detail": _("Donor must be accepted before revealing contact.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if actor == "seeker":
            if entry.blood_request.seeker != request.user:
                return Response(
                    {"detail": _("Unauthorized.")},
                    status=status.HTTP_403_FORBIDDEN,
                )
            entry.seeker_contact_accessed_at = timezone.now()
            entry.save(update_fields=["seeker_contact_accessed_at"])
            return Response({"phone_number": entry.donor.phone_number})

        if actor == "donor":
            if entry.donor != request.user:
                return Response(
                    {"detail": _("Unauthorized.")},
                    status=status.HTTP_403_FORBIDDEN,
                )
            entry.donor_contact_accessed_at = timezone.now()
            entry.save(update_fields=["donor_contact_accessed_at"])
            return Response({"phone_number": entry.blood_request.seeker.phone_number})

        return Response(
            {"detail": _("Invalid actor type.")},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=True, methods=["post"])
    def accept_request(self, request, pk=None):
        """
        Allows a donor to accept a blood request.
        """
        entry = get_object_or_404(BloodRequestDonor, pk=pk, donor=request.user)
        if entry.response_status != BloodRequestDonor.ResponseStatus.PENDING:
            return Response(
                {"detail": _("This request has already been responded to.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        entry.response_status = BloodRequestDonor.ResponseStatus.ACCEPTED
        entry.responded_at = timezone.now()
        entry.save()

        return Response({"status": "accepted"})

    @action(detail=True, methods=["post"])
    def decline_request(self, request, pk=None):
        """
        Allows a donor to decline a blood request.
        """
        entry = get_object_or_404(BloodRequestDonor, pk=pk, donor=request.user)
        if entry.response_status != BloodRequestDonor.ResponseStatus.PENDING:
            return Response(
                {"detail": _("This request has already been responded to.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        entry.response_status = BloodRequestDonor.ResponseStatus.DECLINED
        entry.responded_at = timezone.now()
        entry.save()

        return Response({"status": "declined"})

    @action(detail=True, methods=["post"])
    def confirm_donation(self, request, pk=None):
        """
        Allows a seeker or donor to confirm that a donation actually happened.
        """
        entry = get_object_or_404(BloodRequestDonor, pk=pk)
        confirmation = request.data.get("confirmation")

        if confirmation not in BloodRequestDonor.DonationConfirmation.values:
            return Response(
                {"detail": f"Invalid confirmation value: {confirmation}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if entry.blood_request.seeker == request.user:
            if (
                entry.seeker_confirmation
                != BloodRequestDonor.DonationConfirmation.PENDING
            ):
                return Response(
                    {
                        "detail": (
                            f"You have already confirmed as {entry.seeker_confirmation}"
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            entry.seeker_confirmation = confirmation
            entry.seeker_confirmation_at = timezone.now()
        elif entry.donor == request.user:
            if (
                entry.donor_confirmation
                != BloodRequestDonor.DonationConfirmation.PENDING
            ):
                return Response(
                    {
                        "detail": (
                            f"You have already confirmed as {entry.donor_confirmation}"
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            entry.donor_confirmation = confirmation
            entry.donor_confirmation_at = timezone.now()
        else:
            return Response(
                {"detail": _("You are not authorized to confirm this donation.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        entry.save()

        return Response(
            {
                "status": "confirmed",
                "seeker_confirmation": entry.seeker_confirmation,
                "donor_confirmation": entry.donor_confirmation,
            }
        )

    @action(detail=False, methods=["get"])
    def sent_requests(self, request):
        """
        Returns all blood requests initiated by the current user.
        """
        queryset = BloodRequest.objects.filter(seeker=request.user).order_by(
            "-created_at"
        )
        serializer = BloodRequestDashboardSerializer(
            queryset, many=True, context={"request": request}
        )
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def received_requests(self, request):
        """
        Returns all blood requests received by the current user as a donor.
        """
        queryset = BloodRequestDonor.objects.filter(donor=request.user).order_by(
            "-created_at"
        )
        serializer = BloodRequestDonorDashboardSerializer(
            queryset, many=True, context={"request": request}
        )
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def cancel_request(self, request, pk=None):
        """
        Allows a seeker to cancel their own blood request.
        """
        obj = get_object_or_404(BloodRequest, pk=pk, seeker=request.user)
        obj.delete()
        return Response({"status": "cancelled"})

    def perform_create(self, serializer):
        blood_request = serializer.save()
        self.send_donor_requests(blood_request)

    def send_donor_requests(self, blood_request):
        """
        Sends initial notifications to selected donors.
        """
        for entry in blood_request.donors.all():
            accept_path = reverse(
                "blood_requests:donor_response",
                kwargs={"token": entry.token, "action_type": "accept"},
            )
            decline_path = reverse(
                "blood_requests:donor_response",
                kwargs={"token": entry.token, "action_type": "decline"},
            )
            context = {
                "seeker_name": blood_request.seeker.name
                or blood_request.seeker.username,
                "hospital": blood_request.hospital,
                "bags_needed": blood_request.bags_needed,
                "donation_date": blood_request.donation_date,
                "accept_url": f"{settings.BASE_URL}{accept_path}",
                "decline_url": f"{settings.BASE_URL}{decline_path}",
            }
            NotificationDispatcher.send(entry.donor, "emergency_request", context)


class BloodRequestDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "blood_requests/dashboard.html"


blood_request_dashboard_view = BloodRequestDashboardView.as_view()


def donor_response_view(request, token, action_type):
    """
    Public view for donors to quickly accept or decline a request via email/SMS links.
    """
    entry = get_object_or_404(BloodRequestDonor, token=token)

    if entry.response_status != BloodRequestDonor.ResponseStatus.PENDING:
        message = _("You have already responded to this request.")
        return render(
            request, "blood_requests/response_confirm.html", {"message": message}
        )

    if action_type == "accept":
        entry.response_status = BloodRequestDonor.ResponseStatus.ACCEPTED
        message = _("Thank you for accepting! The seeker will be notified.")
    elif action_type == "decline":
        entry.response_status = BloodRequestDonor.ResponseStatus.DECLINED
        message = _("Thank you for your response. We will look for other donors.")
    else:
        return HttpResponseBadRequest(_("Invalid action."))

    entry.responded_at = timezone.now()
    entry.save()

    return render(request, "blood_requests/response_confirm.html", {"message": message})


def confirm_donation_view(request, token, actor, status_type):
    """
    Public view for seekers/donors to confirm donation via simple links.
    """
    entry = get_object_or_404(BloodRequestDonor, token=token)

    if entry.is_fully_confirmed:
        message = _("This donation has already been fully confirmed.")
        return render(
            request, "blood_requests/response_confirm.html", {"message": message}
        )

    confirmation = (
        BloodRequestDonor.DonationConfirmation.YES
        if status_type == "yes"
        else BloodRequestDonor.DonationConfirmation.NO
    )

    if actor == "seeker":
        if entry.seeker_confirmation != BloodRequestDonor.DonationConfirmation.PENDING:
            message = _("You have already confirmed this donation.")
            return render(
                request, "blood_requests/response_confirm.html", {"message": message}
            )
        entry.seeker_confirmation = confirmation
        entry.seeker_confirmation_at = timezone.now()
    elif actor == "donor":
        if entry.donor_confirmation != BloodRequestDonor.DonationConfirmation.PENDING:
            message = _("You have already confirmed this donation.")
            return render(
                request, "blood_requests/response_confirm.html", {"message": message}
            )
        entry.donor_confirmation = confirmation
        entry.donor_confirmation_at = timezone.now()
    else:
        return HttpResponseBadRequest(_("Invalid actor."))

    entry.save()

    message = _("Thank you for your confirmation. We have updated our records.")
    return render(request, "blood_requests/response_confirm.html", {"message": message})
