from django.conf.urls import patterns, include, url

from .views import IndexView, SurveyDetail, ConfirmView, SurveyCompleted

urlpatterns = patterns('',
	# Examples:
	url(r'^survey/$', IndexView.as_view(), name='survey-list'),
	url(r'^survey/(?P<id>[a-zA-Z0-9-]+)/', SurveyDetail.as_view(), name='survey-detail'),
	url(r'^survey/(?P<id>[a-zA-Z0-9-]+)/completed/', SurveyCompleted.as_view(), name='survey-completed'),
	url(r'^survey/(?P<id>[a-zA-Z0-9-]+)-(?P<step>\d+)/', SurveyDetail.as_view(), name='survey-detail-step'),
	url(r'^confirm/(?P<uuid>\w+)/', ConfirmView.as_view(), name='survey-confirmation'),
)
