from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import TemplateView
from registration import views
from registration.views import *
from registration.models import *
from django.contrib.auth.decorators import login_required

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='register/register.html')),
    url(r'^event/$', EventSearchView.as_view(), name="event_search"),
    url(r'^event/review/(?P<module_id>\d+)/$', EventModuleReviewUpdateView.as_view(), name="review_module"),
    url(r'^event/review/success/$', TemplateView.as_view(template_name='event/module_review_update_success.html')),
    url(r'^user/$', UserRegistrationView.as_view(), name='register_user'),
    url(r'^user/success/', TemplateView.as_view(template_name='register/user/success.html'),
        name='user_registration_success'),
    url(r'^user/profile/$', UserProfileView.as_view(), name='user_profile'),
    url(r'^user/profile/view_public/(?P<user_id>\d+)/$', UserProfileCommonView.as_view(), name='user_profile_public'),
    url(r'^user/profile/edit/$', UserProfileUpdateView.as_view(), name='user_profile_update'),
    url(r'^user/profile/edit/success/$',
        TemplateView.as_view(template_name='registration/user_update_success.html'),
        name='user_profile_update_success'),

]
