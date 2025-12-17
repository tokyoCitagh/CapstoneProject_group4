from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.conf import settings
from store.models import Product


class ProductSitemap(Sitemap):
    """Sitemap for all product pages"""
    changefreq = "weekly"
    priority = 0.8
    protocol = "https"

    def items(self):
        return Product.objects.all().order_by('-id')

    def location(self, item):
        return reverse('store:product_detail', args=[item.pk])

    def get_urls(self, page=1, site=None, protocol=None):
        """Override to use production domain"""
        if protocol is None:
            protocol = self.protocol
        urls = []
        for item in self.paginator.page(page).object_list:
            url = f"{protocol}://www.imageelectronics.org{self.location(item)}"
            urls.append({
                'item': item,
                'location': url,
                'lastmod': getattr(item, 'lastmod', None),
                'changefreq': self.changefreq,
                'priority': self.priority,
                'alternates': [],
            })
        return urls


class StaticSitemap(Sitemap):
    """Sitemap for static pages"""
    changefreq = "monthly"
    priority = 1.0
    protocol = "https"

    def items(self):
        return ['store:store', 'store:about_us', 'store:privacy_policy', 'store:terms_conditions', 'store:shipping_info']

    def location(self, item):
        return reverse(item)

    def get_urls(self, page=1, site=None, protocol=None):
        """Override to use production domain"""
        if protocol is None:
            protocol = self.protocol
        urls = []
        for item in self.items():
            url = f"{protocol}://www.imageelectronics.org{self.location(item)}"
            urls.append({
                'item': item,
                'location': url,
                'lastmod': None,
                'changefreq': self.changefreq,
                'priority': self.priority,
                'alternates': [],
            })
        return urls
