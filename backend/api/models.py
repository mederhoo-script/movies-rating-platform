from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Movie(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    release_year = models.IntegerField()
    genre = models.CharField(max_length=100)
    director = models.CharField(max_length=255)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='movies')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # IMDB and extended fields (all optional)
    imdb_id = models.CharField(max_length=20, blank=True, null=True, help_text="IMDB ID (e.g., tt1234567)")
    imdb_rank = models.FloatField(blank=True, null=True, help_text="IMDB ranking")
    actors = models.TextField(blank=True, null=True, help_text="Comma-separated list of actors")
    aka = models.CharField(max_length=500, blank=True, null=True, help_text="Also Known As (alternative titles)")
    imdb_url = models.URLField(blank=True, null=True, help_text="IMDB URL")
    imdb_iv = models.CharField(max_length=50, blank=True, null=True, help_text="IMDB IV identifier")
    poster_url = models.URLField(blank=True, null=True, help_text="External poster image URL")
    poster_image = models.ImageField(upload_to='posters/', blank=True, null=True, help_text="Uploaded poster image")
    photo_width = models.IntegerField(blank=True, null=True, help_text="Poster image width in pixels")
    photo_height = models.IntegerField(blank=True, null=True, help_text="Poster image height in pixels")

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def average_rating(self):
        ratings = self.ratings.all()
        if ratings:
            return sum(r.score for r in ratings) / len(ratings)
        return 0

    @property
    def ratings_count(self):
        return self.ratings.count()


class Rating(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    score = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['movie', 'user']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.movie.title}: {self.score}"

