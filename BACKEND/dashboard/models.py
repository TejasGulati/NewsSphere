from django.db import models
from django.conf import settings

class Article(models.Model):
    CATEGORY_CHOICES = (
        ('technology', 'Technology'),
        ('sports', 'Sports'),
        ('entertainment', 'Entertainment'),
        ('politics', 'Politics'),
        ('science', 'Science'),
    )

    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.CharField(max_length=255, null=True, blank=True)
    source_url = models.URLField(max_length=500, unique=True)
    media_url = models.URLField(max_length=500, null=True, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)

    def __str__(self):
        return self.title

class Bookmark(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} bookmarked {self.article.title}"

class UserArticleView(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} viewed {self.article.title}"
