from . import views
from django.urls import path


urlpatterns = [
    path("register/", views.register),
    path("login/", views.login),
    path("get_role/", views.get_role),
    path("unverified_list/", views.unverified_list),
    path("admin_check/", views.admin_check),
    path("plugin_switch_share/", views.plugin_switch_share),
    path("template_switch_share/", views.template_switch_share),
    path("gen_token/", views.gen_token),
    path("logout/", views.logout),
    path("get/", views.get), ### only test not use
    path("service_plygin_list/", views.service_plygin_list), ### only test not use
    path("generic_list/", views.generic_list), ### only test not use
    path("slice_list/", views.slice_list), ### only test not use
    path("switch_share_gen/", views.switch_share_gen), ### only test not use
]
