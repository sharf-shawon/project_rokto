from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import BloodRequest
from .models import BloodRequestDonor
from .serializers import BloodRequestCreateSerializer
from .serializers import BloodRequestDashboardSerializer
from .serializers import BloodRequestDonorDashboardSerializer


class BloodRequestViewSet(viewsets.ModelViewSet):
    queryset = BloodRequest.objects.all()
    serializer_class = BloodRequestCreateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        assert self.request.user.is_authenticated
        return self.queryset.filter(seeker=self.request.user)

    @action(detail=False, methods=["get"])
    def sent_requests(self, request):
        """
        List of requests sent by the current user.
        """
        qs = self.get_queryset().prefetch_related(
            "donors",
            "donors__donor",
            "donors__blood_request",
            "donors__blood_request__seeker",
        )
        serializer = BloodRequestDashboardSerializer(
            qs,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def received_requests(self, request):
        """
        List of requests received by the current user as a potential donor.
        """
        qs = (
            BloodRequestDonor.objects.filter(donor=request.user)
            .select_related(
                "blood_request",
                "blood_request__seeker",
                "donor",
            )
            .order_by("-blood_request__created_at")
        )
        serializer = BloodRequestDonorDashboardSerializer(
            qs,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def reveal_contact(self, request, pk=None):
        """
        Reveals the phone number of a donor or seeker and logs the access.
        Expected data body: {"actor": "seeker" | "donor"}.
        """
        entry = get_object_or_404(BloodRequestDonor, pk=pk)
        actor_type = request.data.get("actor")

        if entry.response_status != BloodRequestDonor.ResponseStatus.ACCEPTED:
            return Response(
                {
                    "detail": _(
                        "Request must be accepted before revealing contact info.",
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if actor_type == "seeker":
            # Seeker wants to see donor's number
            if entry.blood_request.seeker != request.user:
                return Response(status=status.HTTP_403_FORBIDDEN)
            if not entry.donor_contact_accessed_at:
                entry.donor_contact_accessed_at = timezone.now()
                entry.save()
            return Response({"phone_number": entry.donor.phone_number})

        if actor_type == "donor":
            # Donor wants to see seeker's number
            if entry.donor != request.user:
                return Response(status=status.HTTP_403_FORBIDDEN)
            if not entry.seeker_contact_accessed_at:
                entry.seeker_contact_accessed_at = timezone.now()
                entry.save()
            return Response({"phone_number": entry.blood_request.seeker.phone_number})

        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def accept_request(self, request, pk=None):
        """
        Allows a donor to accept a pending request.
        """
        entry = get_object_or_404(BloodRequestDonor, pk=pk, donor=request.user)
        if entry.response_status != BloodRequestDonor.ResponseStatus.PENDING:
            return Response(
                {"detail": _("This request has already been responded to.")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        entry.response_status = BloodRequestDonor.ResponseStatus.ACCEPTED
        entry.save()
        return Response({"status": "accepted"})

    @action(detail=True, methods=["post"])
    def decline_request(self, request, pk=None):
        """
        Allows a donor to decline a pending request.
        """
        entry = get_object_or_404(BloodRequestDonor, pk=pk, donor=request.user)
        if entry.response_status != BloodRequestDonor.ResponseStatus.PENDING:
            return Response(
                {"detail": _("This request has already been responded to.")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        entry.response_status = BloodRequestDonor.ResponseStatus.DECLINED
        entry.save()
        return Response({"status": "declined"})

    @action(detail=True, methods=["post"])
    def confirm_donation(self, request, pk=None):
        """
        Handles post-donation confirmation from seeker or donor.
        """
        entry = get_object_or_404(BloodRequestDonor, pk=pk)
        confirmation = request.data.get("confirmation")

        if confirmation not in BloodRequestDonor.DonationConfirmation.values:
            return Response(
                {
                    "detail": _("Invalid confirmation value: {val}").format(
                        val=confirmation,
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if entry.blood_request.seeker == request.user:
            if (
                entry.seeker_confirmation
                != BloodRequestDonor.DonationConfirmation.PENDING
            ):
                return Response(
                    {
                        "detail": _("You have already confirmed as {val}").format(
                            val=entry.seeker_confirmation,
                        ),
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
                        "detail": _("You have already confirmed as {val}").format(
                            val=entry.donor_confirmation,
                        ),
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

        # Only update donor's last donation date if BOTH confirmed YES
        if entry.is_fully_confirmed:
            donor = entry.donor
            request_date = entry.blood_request.donation_date

            if not donor.last_donation_date or request_date >= donor.last_donation_date:
                donor.last_donation_date = request_date
                donor.save()

        return Response(
            {
                "status": "confirmed",
                "seeker_confirmation": entry.seeker_confirmation,
                "donor_confirmation": entry.donor_confirmation,
                "is_fully_confirmed": entry.is_fully_confirmed,
            },
        )

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
        for _entry in blood_request.donors.all():
            # In a real app, send actual email and SMS here.
            pass


class BloodRequestDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "blood_requests/dashboard.html"


blood_request_dashboard_view = BloodRequestDashboardView.as_view()


def donor_response_view(request, token, action_type):
    """
    Public view to handle donor responses from email/SMS links.
    """
    entry = get_object_or_404(BloodRequestDonor, token=token)

    if action_type == "accept":
        entry.response_status = BloodRequestDonor.ResponseStatus.ACCEPTED
        entry.save()

        # Secure contact exchange
        notify_seeker_of_acceptance(entry)
        notify_donor_of_seeker_details(entry)

        message = _(
            "Thank you for accepting! We have sent the seeker's contact details "
            "to your email/phone.",
        )
    elif action_type == "decline":
        entry.response_status = BloodRequestDonor.ResponseStatus.DECLINED
        entry.save()
        message = _("Thank you for your response. We will notify the seeker.")
    else:
        return HttpResponseBadRequest(_("Invalid action type."))

    return render(request, "blood_requests/response_confirm.html", {"message": message})


def notify_seeker_of_acceptance(entry):
    # In a real app, send actual email and SMS.
    pass


def notify_donor_of_seeker_details(entry):
    # In a real app, send actual email and SMS.
    pass


def confirm_donation_view(request, token, actor, status_type):
    """
    Handles post-donation confirmation from seeker or donor.
    """
    entry = get_object_or_404(BloodRequestDonor, token=token)

    if entry.is_fully_confirmed:
        message = _("Donation is already fully confirmed.")
        return render(
            request,
            "blood_requests/response_confirm.html",
            {"message": message},
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
                request,
                "blood_requests/response_confirm.html",
                {"message": message},
            )
        entry.seeker_confirmation = confirmation
        entry.seeker_confirmation_at = timezone.now()
    elif actor == "donor":
        if entry.donor_confirmation != BloodRequestDonor.DonationConfirmation.PENDING:
            message = _("You have already confirmed this donation.")
            return render(
                request,
                "blood_requests/response_confirm.html",
                {"message": message},
            )
        entry.donor_confirmation = confirmation
        entry.donor_confirmation_at = timezone.now()
    else:
        return HttpResponseBadRequest(_("Invalid actor."))

    entry.save()

    # Only update donor's last donation date if BOTH confirmed YES
    if entry.is_fully_confirmed:
        donor = entry.donor
        request_date = entry.blood_request.donation_date

        if not donor.last_donation_date or request_date >= donor.last_donation_date:
            donor.last_donation_date = request_date
            donor.save()

    message = _("Thank you for your confirmation. We have updated our records.")
    return render(request, "blood_requests/response_confirm.html", {"message": message})
