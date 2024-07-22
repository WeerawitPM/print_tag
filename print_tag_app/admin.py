from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Tag, RefTag

class TagAdmin(admin.ModelAdmin):
    list_display = ('qr_code', 'po_no', 'cust_sup', 'part_name', 'part_no', 'lot_mat', 'lot_prod', 'model', 'mc', 'date', 'qty', 'ref_tag_link')  # Updated field names
    search_fields = ('qr_code', 'po_no', 'cust_sup', 'part_name', 'part_no', 'lot_mat', 'lot_prod', 'model', 'mc')
    list_filter = ('date', 'model', 'mc')
    ordering = ('date',)
    
    def ref_tag_link(self, obj):
        if obj.ref_tag:
            url = reverse('admin:%s_%s_change' % (obj.ref_tag._meta.app_label, obj.ref_tag._meta.model_name), args=[obj.ref_tag.pk])
            return format_html('<a href="{}">{}</a>', url, obj.ref_tag)
        return "-"
    ref_tag_link.short_description = 'Ref Tag'

class RefTagAdmin(admin.ModelAdmin):
    list_display = ('ref_id',)
    search_fields = ('ref_id',)

admin.site.register(Tag, TagAdmin)
admin.site.register(RefTag, RefTagAdmin)
