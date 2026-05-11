from django.urls import path

from .views import nid_submission_view
from .views import otp_verify_view
from .views import phone_login_view
from .views import phone_manage_view
from .views import phone_verify_otp_view
from .views import signup_info_view
from .views import user_detail_view
from .views import user_redirect_view
from .views import user_update_view

app_name = "users"
urlpatterns = [
    path("~redirect/", view=user_redirect_view, name="redirect"),
    path("~update/", view=user_update_view, name="update"),
    path("login/phone/", view=phone_login_view, name="phone_login"),
    path("login/otp/", view=otp_verify_view, name="otp_verify"),
    path("login/phone/signup/", view=signup_info_view, name="signup_info"),
    path("verify/nid/", view=nid_submission_view, name="nid_submission"),
    path("verify/phone/", view=phone_manage_view, name="phone_add"),
    path("verify/phone/manage/", view=phone_manage_view, name="phone_manage"),
    path("verify/phone/otp/", view=phone_verify_otp_view, name="phone_verify_otp"),
    path("<str:username>/", view=user_detail_view, name="detail"),
]
