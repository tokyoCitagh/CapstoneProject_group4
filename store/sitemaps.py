from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from store.models import Product


class ProductSitemap(Sitemap):
    """Sitemap for all product pages"""
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Product.objects.filter(is_active=True).order_by('-created_at')

    def location(self, item):
        return reverse('store:product_detail', args=[item.pk])

    def lastmod(self, item):
        return item.updated_at


class StaticSitemap(Sitemap):
    """Sitemap for static pages"""
    changefreq = "monthly"
    priority = 1.0

    def items(self):
        return ['store', 'store:about_us', 'store:privacy_policy', 'store:terms_conditions', 'store:shipping_info']

    def location(self, item):
        return reverse(item)
