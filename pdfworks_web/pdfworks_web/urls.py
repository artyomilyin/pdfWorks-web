from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include
from website.sitemaps import PdfworksSitemap

sitemaps = {
    'pdfworks': PdfworksSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('website.urls', namespace='website')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]
