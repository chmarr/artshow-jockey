from django.conf.urls import patterns, url
from tinyreg.forms import CaptchaPasswordResetForm

urlpatterns = patterns('',
                       url(r'login/$', 'django.contrib.auth.views.login', {'template_name': 'accounts/login.html'},
                           name="login"),
                       url(r'logout/$', 'django.contrib.auth.views.logout',
                           {'template_name': 'accounts/logged_out.html'}, name="logout"),
                       url(r'password_change/$', 'django.contrib.auth.views.password_change',
                           {'template_name': 'accounts/password_change_form.html'}, name="password_change"),
                       url(r'password_change/done/$', 'django.contrib.auth.views.password_change_done',
                           {'template_name': 'accounts/password_change_done.html'}, name="password_change_done"),
                       url(r'password_reset/$', 'django.contrib.auth.views.password_reset',
                           {
                               'template_name': 'accounts/password_reset_form.html',
                               'email_template_name': 'accounts/password_reset_email.html',
                               'subject_template_name': 'accounts/password_reset_subject.txt',
                               'password_reset_form': CaptchaPasswordResetForm,
                           },
                           name="password_reset"),
                       url(r'password_reset/done/$', 'django.contrib.auth.views.password_reset_done',
                           {'template_name': 'accounts/password_reset_done.html'}, name="password_reset_done"),
                       url(r'reset/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
                           'django.contrib.auth.views.password_reset_confirm',
                           {'template_name': 'accounts/password_reset_confirm.html'}, name="password_reset_confirm"),
                       url(r'password_reset/complete/$', 'django.contrib.auth.views.password_reset_complete',
                           {'template_name': 'accounts/password_reset_complete.html'}, name="password_reset_complete"),
                       )
