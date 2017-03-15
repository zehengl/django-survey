
from django.conf.urls import url

from .views import ConfirmView, IndexView, SurveyCompleted, SurveyDetail

urlpatterns = [
       url(r'^$', IndexView.as_view(), name='survey-list'),
       url(r'^(?P<id>\d+)/', SurveyDetail.as_view(), name='survey-detail'),
       url(r'^(?P<id>\d+)/completed/', SurveyCompleted.as_view(),
           name='survey-completed'),
       url(r'^(?P<id>\d+)-(?P<step>\d+)/', SurveyDetail.as_view(),
           name='survey-detail-step'),
       url(r'^confirm/(?P<uuid>\w+)/', ConfirmView.as_view(),
           name='survey-confirmation'),
]
