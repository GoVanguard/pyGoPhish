from django.contrib import admin
from django.contrib.sites.models import Site
from pondering.models import Domain, PhishingTrip, PhishingTripInstance

# Register your models here.
admin.site.unregister(Site)
class SiteAdmin(admin.ModelAdmin):
    fields = ('id', 'name', 'domain')
    readonly_fields = ('id',)
    list_display = ('id', 'name', 'domain')
    list_display_links = ('name',)
    search_fields = ('name', 'domain')
admin.site.register(Site, SiteAdmin)
admin.site.register(Domain)
admin.site.register(PhishingTrip)
admin.site.register(PhishingTripInstance)

def admin(request):
    context = initializeContext(request)
    if request.user.is_authenticated:
        return render(request, '%s?next=%s' %(settings.LOGIN_URL, request.path), context)

