import json
from django.forms.forms import Form
from django.shortcuts import render
from django.contrib.auth.views import LoginView, LogoutView
from django.http import JsonResponse, request, response
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.http import QueryDict

# Create your views here.
class AjaxLoginView(LoginView):
	extra_context = {'button': 'Login'}

	def get(self, request, *args, **kwargs):
		if self.request.user.is_authenticated:
			self.extra_context = {
				'button': 'Logout',
			}
		return super().get(request, *args, **kwargs)

	def post(self, request, *args, **kwargs):
		is_ajax = self.request.headers.get('X-Requested-With') == 'XMLHttpRequest'

		request.POST = json.load(request)
		form = self.get_form()

		if is_ajax and request.POST == {}:
			form = AuthenticationForm()
			logout(request)
			return JsonResponse({
				'form': str(form),
				'button': 'Login',
				'csrftoken': str(self.request.META.get('CSRF_COOKIE')),
			})
		if form.is_valid():
			return self.form_valid(form)
		else:
			return self.form_invalid(form)

	def form_valid(self, form):
		is_ajax = self.request.headers.get('X-Requested-With') == 'XMLHttpRequest'
		if is_ajax:
			login(self.request, form.get_user())
			return JsonResponse({
				'form': str('Logged as ' + self.request.user.username),
				'button': 'Logout',
				'csrftoken': str(self.request.META.get('CSRF_COOKIE')),
			})
		return super().form_valid(form)

	def form_invalid(self, form):
		is_ajax = self.request.headers.get('X-Requested-With') == 'XMLHttpRequest'
		if is_ajax:
			return JsonResponse({
				'form': str(form),
				'button': 'Login',
				'csrftoken': str(self.request.META.get('CSRF_COOKIE')),
			})
		return super().form_invalid(form)

	def render_to_response(self, context, **response_kwargs):
		response_kwargs.setdefault('content_type', self.content_type)
		return self.response_class(
			request=self.request,
			template=self.get_template_names(),
			context=context,
			using=self.template_engine,
			**response_kwargs
		)
