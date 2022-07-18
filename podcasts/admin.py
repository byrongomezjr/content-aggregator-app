from django.contrib import admin

from .models import Episode  # .models folder import class


@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ("podcast_name", "title", "pub_date")
