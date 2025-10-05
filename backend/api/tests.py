from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import Movie, Rating
from PIL import Image
import io


class UserAuthenticationTestCase(APITestCase):
    """Test user registration and login"""

    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/auth/register/'
        self.login_url = '/api/auth/login/'

    def test_user_registration(self):
        """Test user can register with valid credentials"""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password2': 'testpass123'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        self.assertIn('tokens', response.data)
        self.assertEqual(response.data['user']['username'], 'testuser')

    def test_user_registration_password_mismatch(self):
        """Test registration fails with mismatched passwords"""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password2': 'differentpass'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_login(self):
        """Test user can login with valid credentials"""
        # First create a user
        user = User.objects.create_user(username='testuser', password='testpass123')

        # Try to login
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        self.assertIn('user', response.data)

    def test_user_login_invalid_credentials(self):
        """Test login fails with invalid credentials"""
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class MovieTestCase(APITestCase):
    """Test movie CRUD operations"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.movies_url = '/api/movies/'

    def test_create_movie_authenticated(self):
        """Test authenticated user can create a movie"""
        self.client.force_authenticate(user=self.user)
        data = {
            'title': 'Test Movie',
            'description': 'A test movie description',
            'release_year': 2023,
            'genre': 'Action',
            'director': 'Test Director'
        }
        response = self.client.post(self.movies_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Test Movie')

    def test_create_movie_unauthenticated(self):
        """Test unauthenticated user cannot create a movie"""
        data = {
            'title': 'Test Movie',
            'description': 'A test movie description',
            'release_year': 2023,
            'genre': 'Action',
            'director': 'Test Director'
        }
        response = self.client.post(self.movies_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_movies(self):
        """Test anyone can list movies"""
        Movie.objects.create(
            title='Test Movie',
            description='Description',
            release_year=2023,
            genre='Action',
            director='Director',
            created_by=self.user
        )
        response = self.client.get(self.movies_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_get_movie_detail(self):
        """Test anyone can view movie details"""
        movie = Movie.objects.create(
            title='Test Movie',
            description='Description',
            release_year=2023,
            genre='Action',
            director='Director',
            created_by=self.user
        )
        response = self.client.get(f'/api/movies/{movie.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Movie')

    def test_create_movie_with_imdb_fields(self):
        """Test creating a movie with optional IMDB fields"""
        self.client.force_authenticate(user=self.user)
        data = {
            'title': 'Test Movie with IMDB',
            'description': 'A test movie with IMDB data',
            'release_year': 2023,
            'genre': 'Action',
            'director': 'Test Director',
            'imdb_id': 'tt1234567',
            'imdb_rank': 8.5,
            'actors': 'Actor 1, Actor 2, Actor 3',
            'aka': 'Alternative Title',
            'imdb_url': 'https://www.imdb.com/title/tt1234567/',
            'poster_url': 'https://example.com/poster.jpg',
            'photo_width': 300,
            'photo_height': 450
        }
        response = self.client.post(self.movies_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Test Movie with IMDB')
        self.assertEqual(response.data['imdb_id'], 'tt1234567')
        self.assertEqual(response.data['imdb_rank'], 8.5)
        self.assertEqual(response.data['actors'], 'Actor 1, Actor 2, Actor 3')
        self.assertEqual(response.data['poster_url'], 'https://example.com/poster.jpg')

    def test_create_movie_without_optional_fields(self):
        """Test creating a movie without optional fields still works"""
        self.client.force_authenticate(user=self.user)
        data = {
            'title': 'Test Movie Basic',
            'description': 'A basic test movie',
            'release_year': 2023,
            'genre': 'Drama',
            'director': 'Test Director'
        }
        response = self.client.post(self.movies_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Test Movie Basic')
        # Check that optional fields are null/None
        self.assertIsNone(response.data.get('imdb_id'))
        self.assertIsNone(response.data.get('imdb_rank'))
        self.assertIsNone(response.data.get('actors'))


class RatingTestCase(APITestCase):
    """Test rating operations"""

    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(username='user1', password='pass123')
        self.user2 = User.objects.create_user(username='user2', password='pass123')
        self.movie = Movie.objects.create(
            title='Test Movie',
            description='Description',
            release_year=2023,
            genre='Action',
            director='Director',
            created_by=self.user1
        )
        self.rating_url = f'/api/movies/{self.movie.id}/ratings/'

    def test_create_rating_authenticated(self):
        """Test authenticated user can rate a movie"""
        self.client.force_authenticate(user=self.user1)
        data = {
            'score': 5,
            'comment': 'Great movie!'
        }
        response = self.client.post(self.rating_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['score'], 5)

    def test_create_rating_unauthenticated(self):
        """Test unauthenticated user cannot rate a movie"""
        data = {
            'score': 5,
            'comment': 'Great movie!'
        }
        response = self.client.post(self.rating_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_rating(self):
        """Test user can update their own rating"""
        self.client.force_authenticate(user=self.user1)

        # Create initial rating
        data = {
            'score': 3,
            'comment': 'OK movie'
        }
        response = self.client.post(self.rating_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Update rating
        data = {
            'score': 5,
            'comment': 'Actually great!'
        }
        response = self.client.post(self.rating_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['score'], 5)

    def test_one_rating_per_user_per_movie(self):
        """Test user can only have one rating per movie"""
        self.client.force_authenticate(user=self.user1)

        # Create rating
        Rating.objects.create(movie=self.movie, user=self.user1, score=3)

        # Try to create another rating - should update instead
        data = {
            'score': 5,
            'comment': 'Updated rating'
        }
        response = self.client.post(self.rating_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify only one rating exists
        ratings_count = Rating.objects.filter(movie=self.movie, user=self.user1).count()
        self.assertEqual(ratings_count, 1)

    def test_list_movie_ratings(self):
        """Test anyone can list movie ratings"""
        Rating.objects.create(movie=self.movie, user=self.user1, score=5)
        Rating.objects.create(movie=self.movie, user=self.user2, score=4)

        response = self.client.get(self.rating_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_user_ratings(self):
        """Test anyone can list a user's ratings"""
        Rating.objects.create(movie=self.movie, user=self.user1, score=5)

        response = self.client.get(f'/api/users/{self.user1.id}/ratings/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check if response is paginated
        if 'results' in response.data:
            self.assertEqual(len(response.data['results']), 1)
        else:
            self.assertEqual(len(response.data), 1)


class MovieImageUploadTestCase(APITestCase):
    """Test movie poster image upload"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.movies_url = '/api/movies/'
        
    def create_test_image(self):
        """Create a simple test image"""
        file = io.BytesIO()
        image = Image.new('RGB', (100, 100), color='red')
        image.save(file, 'PNG')
        file.seek(0)
        return SimpleUploadedFile("test_poster.png", file.read(), content_type="image/png")

    def test_create_movie_with_image_upload(self):
        """Test creating a movie with an uploaded poster image"""
        self.client.force_authenticate(user=self.user)
        
        image = self.create_test_image()
        
        data = {
            'title': 'Test Movie with Image',
            'description': 'A test movie with uploaded image',
            'release_year': 2023,
            'genre': 'Action',
            'director': 'Test Director',
            'poster_image': image,
            'photo_width': 100,
            'photo_height': 100
        }
        
        response = self.client.post(self.movies_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Test Movie with Image')
        self.assertIsNotNone(response.data.get('poster_image'))
        self.assertTrue('posters/' in response.data['poster_image'])

