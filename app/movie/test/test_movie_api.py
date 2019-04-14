from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Movie

from movie.serializers import MovieSerializer


MOVIES_URL = reverse('movie:movie-list')


def sample_movie(user, **params):
    """Create and return a sample movie"""
    defaults = {
        'title': 'Sample movie',
        'time_minutes': 120,
        'ticket_price_USD': 5.00,
    }
    defaults.update(params)

    return Movie.objects.create(user=user, **defaults)


class PublicMovieApiTests(TestCase):
    """Test unauthenticated movie API access"""

    def setUp(self):
        self.client = APIClient()

    def test_required_auth(self):
        """Test the authenticaiton is required"""
        res = self.client.get(MOVIES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateMovieApiTests(TestCase):
    """Test authenticated movie API access"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@youremail.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_movies(self):
        """Test retrieving list of movies"""
        sample_movie(user=self.user)
        sample_movie(user=self.user)

        res = self.client.get(MOVIES_URL)

        movies = Movie.objects.all().order_by('-id')
        serializer = MovieSerializer(movies, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_movies_limited_to_user(self):
        """Test retrieving movies for user"""
        user2 = get_user_model().objects.create_user(
            'other@youremail.com',
            'pass123'
        )
        sample_movie(user=user2)
        sample_movie(user=self.user)

        res = self.client.get(MOVIES_URL)

        movies = Movie.objects.filter(user=self.user)
        serializer = MovieSerializer(movies, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)
