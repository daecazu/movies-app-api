from rest_framework import serializers

from core.models import Tag, Movie


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag object"""

    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_Fields = ('id',)


class MovieSerializer(serializers.ModelSerializer):
    """Serialize a movie"""

    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Movie
        fields = (
            'id', 'title', 'tags', 'time_minutes', 'ticket_price_USD',
            'link',
        )
        read_only_fields = ('id',)


class MovieDetailSerializer(MovieSerializer):
    tags = TagSerializer(many=True, read_only=True)


class MovieImageSerializer(serializers.ModelSerializer):
    """ Serializer for uploading images to movie"""
    class Meta:
        model = Movie
        fields = ('id', 'image')
        read_only_fields = ('id',)
