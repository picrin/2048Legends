from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'WC2048.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    #url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('website.urls')),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

#from django.contrib import admin
#
#from django.db.models import get_models, get_app
#
#for model in get_models(get_app('website')):
#    admin.site.register(model)

