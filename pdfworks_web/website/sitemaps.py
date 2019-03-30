from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class PdfworksSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.9

    def items(self):
        return ['website:homepage', 'website:merge', 'website:split']

    def location(self, item):
        return reverse(item)
