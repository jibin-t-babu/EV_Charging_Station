from django.contrib import admin
from .models import *
from django.utils.html import format_html
# Register your models here.
admin.site.register(Station)
admin.site.register(Booking)
admin.site.register(Contact)
admin.site.register(Vehicle)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('colored_message', 'created_at', 'is_read')

    def colored_message(self, obj):
        color = "red" if not obj.is_read else "gray"
        return format_html(f"<b style='color:{color};'>{obj.message}</b>")

    colored_message.short_description = "Notification"
