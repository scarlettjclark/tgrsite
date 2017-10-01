from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic import TemplateView, RedirectView
from . import views

urlpatterns = [
	url(r'^$', TemplateView.as_view(template_name='tgrsite/index.html'), name='homepage'),
	url(r'^admin/', admin.site.urls),
	url(r'^forum/', include('forum.urls')),

	# hard redirect
	# url(r'^signups/(.*)', RedirectView.as_view(url='/events/', permanent=True)),

	# soft direct (/signups links still work but site universally links to /events)
	# url(r'^signups/', include('rpgs.urls')),


	url(r'^events/', include('rpgs.urls'), name='rpgs_root'),
	url(r'^exec/', include('exec.urls')),
	url(r'^', include('users.urls')),
	url(r'^messages/', include('messaging.urls')),
	url(r'^bugs/', include('bugreports.urls')),

	# Pseudo "Static" pages - those with no models or fancy behaviour.
	# e.g. the larp intro page
	url(r'^', include('statics.urls')),

]
