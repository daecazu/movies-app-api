from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Movie

from movie import serializers


class BaseMovieAttrViewSet(viewsets.GenericViewSet,
                           mixins.ListModelMixin,
                           mixins.CreateModelMixin):
    """Base viewset for user own attributes"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """Crete a new object"""
        serializer.save(user=self.request.user)


class TagViewSet(BaseMovieAttrViewSet):
    """Manage tags in the database"""

    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class MovieViewSet(viewsets.ModelViewSet):
    """Manage movies in the database"""
    serializer_class = serializers.MovieSerializer
    queryset = Movie.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Retrieve the movies for the authenticated user"""
        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'retrieve':
            return serializers.MovieDetailSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new movie"""
        serializer.save(user=self.request.user)
