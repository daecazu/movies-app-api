from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Movie, Tag

from movie.serializers import MovieSerializer, MovieDetailSerializer


MOVIES_URL = reverse('movie:movie-list')


def detail_url(movie_id):
    """Return movie detail URL"""
    return reverse('movie:movie-detail', args=[movie_id])


def sample_tag(user, name='sample tag'):
    """Create and return a sample tag"""
    return Tag.objects.create(user=user, name=name)


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

    def test_view_movie_detail(self):
        """Test viewing a movie detail"""
        movie = sample_movie(user=self.user)
        movie.tags.add(sample_tag(user=self.user))

        url = detail_url(movie.id)
        res = self.client.get(url)

        serializer = MovieDetailSerializer(movie)
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_movie(self):
        """Test creating movie"""
        payload = {
            'title': 'Test movie',
            'time_minutes': 30,
            'ticket_price_USD': 10.00,
        }
        res = self.client.post(MOVIES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        movie = Movie.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(movie, key))

    def test_create_movie_with_tags(self):
        """Test creating a movie with tags"""
        tag1 = sample_tag(user=self.user, name='Tag 1')
        tag2 = sample_tag(user=self.user, name='Tag 2')
        payload = {
            'title': 'Test movie with two tags',
            'tags': [tag1.id, tag2.id],
            'time_minutes': 30,
            'ticket_price_USD': 10.00
        }
        res = self.client.post(MOVIES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        movie = Movie.objects.get(id=res.data['id'])
        tags = movie.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)
