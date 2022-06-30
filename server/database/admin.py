from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Personal, Visit


@admin.register(Personal)
class PersonalAdmin(admin.ModelAdmin):
    list_display = ("get_fullname", 'visit_counts', "last_visit", "get_photo_list")
    fields = ("surname", "name", 'visit_counts', "last_visit", "get_photo")
    readonly_fields = ('visit_counts', "last_visit", "get_photo")

    def get_photo_list(self, obj: Personal):
        return self.get_photo(obj, 50)

    def get_photo(self, obj: Personal, width: int = 90):
        if obj.image:
            return mark_safe(f'<img src={obj.image.url} width = "{width}">')
        return ' - '

    def visit_counts(self, obj: Personal):
        return len(Visit.objects.filter(personal_id=obj.id))

    def last_visit(self, obj: Personal):
        return Visit.objects.filter(personal_id=obj.id).order_by('-visit_at')[0] \
            .visit_at.replace(tzinfo=None, microsecond=0)

    get_photo.short_description = 'Photo'
    visit_counts.short_description = 'Visits count'
    last_visit.short_description = 'Last visit'


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ("personal", "visit_at", "get_photo_list")
    fields = ("personal", "visit_at", "get_photo")
    readonly_fields = ("personal", "visit_at")
    search_fields = ("personal__id", "personal__name", "personal__surname")

    def get_photo_list(self, obj: Visit):
        return self.get_photo(obj, 50)

    def get_photo(self, obj: Visit, width: int = 150):
        if obj.personal.image:
            return mark_safe(f'<img src={obj.personal.image.url} width = "{width}">')
        return ' - '

    get_photo.short_description = 'Photo'
