from django.urls import path
from .views import AjaxLoginView


urlpatterns = [
	path('', AjaxLoginView.as_view(), name='account'),
]
