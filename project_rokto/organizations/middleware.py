from allauth.mfa.models import Authenticator
from django.shortcuts import redirect
from django.urls import reverse


class OrgManagerMFAMiddleware:
    """
    Enforce MFA for organization admins and managers.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and request.user.is_org_manager:
            # Check if user has MFA enabled in allauth
            has_mfa = Authenticator.objects.filter(user=request.user).exists()

            # If they are trying to access org-admin or other sensitive areas
            # and they are not on the MFA page or logging out
            exempt_urls = [reverse("mfa_index"), reverse("account_logout")]
            if request.path.startswith("/org-admin/") and not has_mfa:
                if request.path not in exempt_urls:
                    return redirect(reverse("mfa_index"))

        return self.get_response(request)
