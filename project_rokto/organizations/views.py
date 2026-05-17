from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views.generic import DetailView
from django.views.generic import ListView

from .models import Organization
from .models import OrganizationMember


class OrganizationDetailView(DetailView):
    model = Organization
    template_name = "organizations/organization_detail.html"
    context_object_name = "organization"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["donor_count"] = self.object.donors.count()
        return context


class CreateOrganizationView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Organization
    fields = ["name", "logo", "banner", "basic_info", "contact_information"]
    template_name = "organizations/organization_form.html"
    success_url = reverse_lazy("organizations:list")

    def test_func(self):
        # User must be fully verified to create an organization
        user = self.request.user
        return user.is_authenticated and user.is_verified

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            # Maybe show a message that they need verification
            return redirect("users:redirect")
        return super().handle_no_permission()

    def form_valid(self, form):
        response = super().form_valid(form)
        # Create OrganizationMember for the creator as ADMIN
        if self.object and self.request.user.is_authenticated:
            OrganizationMember.objects.create(
                organization=self.object,
                user=self.request.user,
                role=OrganizationMember.Role.ADMIN,
            )
        return response


class OrganizationListView(ListView):
    model = Organization
    template_name = "organizations/organization_list.html"
    context_object_name = "organizations"
    queryset = Organization.objects.filter()
