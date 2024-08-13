from rest_framework import serializers
from dashboard.models import Article, Bookmark

class ArticleSerializer(serializers.ModelSerializer):
    is_bookmarked = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = '__all__'

    def get_is_bookmarked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Bookmark.objects.filter(user=request.user, article=obj).exists()
        return False

class BookmarkSerializer(serializers.ModelSerializer):
    article_title = serializers.CharField(source='article.title', read_only=True)
    article_url = serializers.URLField(source='article.source_url', read_only=True)
    article_id = serializers.IntegerField(source='article.id', read_only=True)
    article_content = serializers.CharField(source='article.content', read_only=True)
    article_media_url = serializers.URLField(source='article.media_url', read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Bookmark
        fields = '__all__'
