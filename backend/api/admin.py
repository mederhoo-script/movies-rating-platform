from django.contrib import admin
from django.utils.html import format_html
from .models import Movie, Rating


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'release_year', 'genre', 'director', 'imdb_id', 'created_by', 'poster_preview')
    list_filter = ('release_year', 'genre', 'created_at')
    search_fields = ('title', 'director', 'imdb_id', 'actors')
    readonly_fields = ('created_at', 'updated_at', 'poster_preview_large')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'release_year', 'genre', 'director', 'created_by')
        }),
        ('IMDB Information', {
            'fields': ('imdb_id', 'imdb_rank', 'imdb_url', 'imdb_iv', 'actors', 'aka'),
            'classes': ('collapse',)
        }),
        ('Poster Images', {
            'fields': ('poster_image', 'poster_url', 'photo_width', 'photo_height', 'poster_preview_large')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def poster_preview(self, obj):
        """Show small thumbnail in list view"""
        if obj.poster_image:
            return format_html('<img src="{}" style="max-width: 50px; max-height: 75px;" />', obj.poster_image.url)
        elif obj.poster_url:
            return format_html('<img src="{}" style="max-width: 50px; max-height: 75px;" />', obj.poster_url)
        return "No poster"
    poster_preview.short_description = 'Poster'
    
    def poster_preview_large(self, obj):
        """Show larger preview in detail view"""
        if obj.poster_image:
            return format_html('<img src="{}" style="max-width: 300px; max-height: 450px;" />', obj.poster_image.url)
        elif obj.poster_url:
            return format_html('<img src="{}" style="max-width: 300px; max-height: 450px;" />', obj.poster_url)
        return "No poster available"
    poster_preview_large.short_description = 'Poster Preview'


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('movie', 'user', 'score', 'created_at')
    list_filter = ('score', 'created_at')
    search_fields = ('movie__title', 'user__username', 'comment')
    readonly_fields = ('created_at', 'updated_at')

