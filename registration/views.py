from django.shortcuts import redirect
from workshop import settings
from django.views.generic.edit import FormView, UpdateView
from django.core.urlresolvers import reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.edit import DeleteView
from braces.views import LoginRequiredMixin, AnonymousRequiredMixin
from registration.models import *
from registration.forms import *
from django.views.generic import ListView
from django.http import Http404
from django.http import HttpResponse
import simplejson as json
from django.views.generic import TemplateView
from django.shortcuts import render_to_response
from django.core.mail import EmailMessage
from mail_templated import send_mail
import uuid
from string import Template
from django.views.decorators.csrf import csrf_exempt


class CurrentUserMixin(object):
    model = User

    def get_object(self, *args, **kwargs):
        try: obj = super(CurrentUserMixin, self).get_object(*args, **kwargs)
        except AttributeError: obj = self.request.user
        return obj


# Create your views here
def anonymous_required(func):
    def as_view(request, *args, **kwargs):
        redirect_to = kwargs.get('next', settings.LOGIN_REDIRECT_URL )
        if request.user.is_authenticated():
            return redirect(redirect_to)
        response = func(request, *args, **kwargs)
        return response
    return as_view


class HomePageView(ListView):
    template_name="index.html"

    def get_queryset(self):
        return Event.objects.all()


class EventSearchView(ListView):
    template_name = "event/viewevent.html"

    def get_context_data(self, **kwargs):
        eventsearched = self.request.GET.get('search')
        event = Event.objects.get(name=eventsearched)
        context = super(EventSearchView, self).get_context_data(**kwargs)
        context['eventname'] = event.name
        context['eventdescription'] = event.description
        context['eventlocation'] = event.location
        context['start_date'] = event.start_date
        context['end_date'] = event.end_date
        return context

    def get_queryset(self):
        eventsearched = self.request.GET.get('search')
        try:
            event = Event.objects.get(name=eventsearched)
            return EventModules.objects.filter(event=event).order_by('id')
        except Event.DoesNotExist:
            raise Http404("No Match Found. Please try again.")




class EventModuleReviewUpdateView(LoginRequiredMixin, UpdateView):
    model = EventModuleReview
    fields = review_fields
    template_name_suffix = '_update_form'
    success_url = '/register/event/review/success/'

    def get_context_data(self, **kwargs):
        module = self.kwargs['module_id']
        reviewed_module = EventModules.objects.get(pk=module)
        context = super(EventModuleReviewUpdateView, self).get_context_data(**kwargs)
        context['modulename'] = reviewed_module.name
        context['eventname'] = reviewed_module.get_event()
        return context

    def get_object(self, queryset=None):
        user = self.request.user
        module = self.kwargs['module_id']
        reviewed_module = EventModules.objects.get(pk=module)
        try:
            obj = EventModuleReview.objects.get(module=reviewed_module, user=user)
        except self.model.DoesNotExist:
            obj = EventModuleReview.objects.create_review(reviewed_module, user)
        return obj


class UserProfileView(LoginRequiredMixin, CurrentUserMixin, DetailView):
    pass


class UserRegistrationView(AnonymousRequiredMixin, FormView):
    template_name = "register/user/register_user.html"
    authenticated_redirect_url = reverse_lazy(u"home")
    form_class = UserRegistrationForm
    success_url = '/register/user/success/'

    def form_valid(self, form):
        form.save()
        return FormView.form_valid(self, form)



class UserProfileCommonView(DetailView):
    template_name = 'registration/user_detail.html'

    def get_object(self, queryset=None):
            user_id = self.kwargs['user_id']
            obj = User.objects.get(user_id=self.kwargs['user_id'])
            if obj:
                return obj
            else:
                raise Http404("No details Found.")


class UserProfileUpdateView(LoginRequiredMixin, CurrentUserMixin, UpdateView):
    model = User
    fields = user_fields + user_extra_fields
    template_name_suffix = '_update_form'
    success_url = '/register/user/profile/edit/success/'
