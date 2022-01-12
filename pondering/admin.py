from django.contrib import admin
from django.contrib.sites.models import Site
from pondering import models 

# Register your models here.
admin.site.unregister(Site)
class SiteAdmin(admin.ModelAdmin):
    fields = ('id', 'name', 'domain')
    readonly_fields = ('id',)
    list_display = ('id', 'name', 'domain')
    list_display_links = ('name',)
    search_fields = ('name', 'domain')
admin.site.register(Site, SiteAdmin)
admin.site.register(models.PointOfContact)
admin.site.register(models.Company)
admin.site.register(models.Owner)
admin.site.register(models.PhishingWebsite)
admin.site.register(models.TargetWebsite)
admin.site.register(models.CompanyProfile)
admin.site.register(models.PhishingTrip)
admin.site.register(models.Name)
admin.site.register(models.Exclusion)
admin.site.register(models.NameList)
admin.site.register(models.TargetEmailAddress)
admin.site.register(models.PhishingList)
admin.site.register(models.PhishingEmail)
admin.site.register(models.PhishingTripInstance)

def admin(request):
    context = initializeContext(request)
    if request.user.is_authenticated:
        return render(request, '%s?next=%s' %(settings.LOGIN_URL, request.path), context)

