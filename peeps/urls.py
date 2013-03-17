from django.conf.urls import patterns, url
from django.views.generic import DetailView
from models import Person

urlpatterns = patterns('peeps',
                       url(
                           r'^mailing_label/(?P<pk>\d+)/$',
                           DetailView.as_view(model=Person, template_name="peeps/mailing-label.html",
                                              context_object_name="person"),
                           name="person-mailing-label"),
                       )
