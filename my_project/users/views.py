import logging
from rest_framework import status, permissions, pagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import User, Recipe, Ingredient, Instruction, MyPlate, Token, Media, IngredientAmount, SocialLogin
from .serializers import UserSerializer
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.utils.dateparse import parse_datetime
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime, timezone
from .GridFS import MediaFile
from social_django.utils import load_strategy, load_backend
from social_core.backends.google import GoogleOAuth2
from social_core.backends.facebook import FacebookOAuth2
from social_core.exceptions import AuthException
from django.contrib.auth import login
import requests
from dotenv import load_dotenv

load_dotenv()



# GridFS centralized configuration
fs = settings.GRIDFS_FS

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Custom 404 view
def custom_404_view(request, exception):
    return render(request, '404.html', status=404)

# Custom Token Authentication
class CookieTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token_key = request.COOKIES.get('auth_token')  # Get the token from the cookie
        if not token_key:
            return None  # No token, no authentication

        try:
            token = Token.objects.get(key=token_key)  # Fetch the token from the database
        except Token.DoesNotExist:
            raise AuthenticationFailed('Invalid token.')

        return (token.user, token)  # Return the user and token

def home(request):
    return HttpResponse("Welcome to the Recipe-z Project!")

class UserRegister(APIView):
    permission_classes = [permissions.AllowAny]  # Allow any user to register

    def get(self, request):
        return render(request, 'registration/register.html')

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()

            # Send confirmation email
            send_mail(
                'Confirm your account',
                'Click the link to confirm your account: <link>',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            return Response({"message": "User registered successfully! Check your email to confirm your account."}, 
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDeleteView(APIView):
    authentication_classes = [CookieTokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return render(request, 'delete/delete_user.html', {'error_message': None})

    def post(self, request):
        user_id = request.data.get('user_id')

        if not self.is_valid_object_id(user_id):
            return render(request, 'delete/delete_user.html', {
                'error_message': "Please enter a valid user ID."
            })

        try:
            user = User.objects.get(id=ObjectId(user_id))
            user.delete()
            logger.info(f"User deleted: {user_id}")
            return render(request, 'delete/delete_user.html', {
                'success_message': "User deleted successfully."
            })
        except User.DoesNotExist:
            logger.error(f"User with ID {user_id} does not exist.")
            return render(request, 'delete/delete_user.html', {
                'error_message': "User with the given ID does not exist. Please try again."
            })
        except Exception as e:
            logger.error(f"An error occurred while deleting user {user_id}: {str(e)}")
            return render(request, 'delete/delete_user.html', {
                'error_message': f"An error occurred: {str(e)}"
            })

    def is_valid_object_id(self, user_id):
        return ObjectId.is_valid(user_id)

class FacebookLogin(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        code = request.GET.get('code')
        if not code:
            return Response({'error': 'No code provided'}, status=status.HTTP_400_BAD_REQUEST)


        # Step 1: Exchange code for access token
        token_url = "https://graph.facebook.com/v10.0/oauth/access_token"
        token_params = {
            'client_id': settings.SOCIAL_AUTH_FACEBOOK_KEY,
            'client_secret': settings.SOCIAL_AUTH_FACEBOOK_SECRET,
            'redirect_uri': settings.FACEBOOK_REDIRECT_URI,
            'code': code
        }

        token_response = requests.get(token_url, params=token_params)
        token_json = token_response.json()

        if 'access_token' not in token_json:
            return Response({'error': 'Failed to retrieve access token'}, status=status.HTTP_400_BAD_REQUEST)
        
        access_token = token_json['access_token']

        # Step 2: Fetch user info using the access token
        user_info_url = "https://graph.facebook.com/me"
        user_info_params = {
            'fields': 'id,name,email',
            'access_token': access_token
        }
        
        user_info_response = requests.get(user_info_url, params=user_info_params)
        user_info = user_info_response.json()

        if 'email' not in user_info:
            return Response({'error': 'Failed to retrieve user information'}, status=status.HTTP_400_BAD_REQUEST)

        email = user_info.get('email')
        name = user_info.get('name')
        facebook_id = user_info.get('id')

        # Check if user exists or create a new one
        user, created = User.objects.get_or_create(email=email, defaults={'name': name})

        if created:
            # Add social login information
            user.social_logins = SocialLogin(facebookId=facebook_id)
            user.save()
        else:
            # Update social login information if already exists
            user.social_logins.facebookId = facebook_id
            user.save()

        # Log in the user
        login(request, user)

        return redirect('home')  # Redirect to a home or dashboard page

class GoogleLogin(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        code = request.GET.get('code')
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            'client_id': settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
            'client_secret': settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET,
            'redirect_uri': settings.GOOGLE_REDIRECT_URI,
            'grant_type': 'authorization_code',
            'code': code,
        }

        token_response = requests.post(token_url, data=token_data)
        token_json = token_response.json()

        if 'access_token' not in token_json:
            return Response({'error': 'Failed to retrieve access token'}, status=status.HTTP_400_BAD_REQUEST)

        access_token = token_json['access_token']
        user_info_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        user_info_response = requests.get(user_info_url, headers={'Authorization': f'Bearer {access_token}'})
        user_info = user_info_response.json()

        email = user_info.get('email')
        name = user_info.get('name')
        uid = user_info.get('id')

        # Check if user exists or create a new one
        user, created = User.objects.get_or_create(email=email, defaults={'name': name})

        if created:
            user.social_logins = SocialLogin(googleId=uid)
            user.save()
        else:
            # Update social login information if already exists
            user.social_logins.googleId = uid
            user.save()

        login(request, user)

        return redirect('home')

class UserLogin(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return render(request, 'login/login_user.html')
    
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({
                'error': "Email and password are required."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the user using MongoEngine
        user = User.objects(email=email).first()
        if not user:
            logger.error(f"Login failed for email: {email} (user not found)")
            return Response({
                'error': "Invalid email or password."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check the password
        if not check_password(password, user.password_hash):
            logger.error(f"Login failed for email: {email} (incorrect password)")
            return Response({
                'error': "Invalid email or password."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Generate or retrieve the token
        token = Token.generate_token(user)  # Ensure this method is correctly implemented
        token_key = token.key  # Retrieve the key from the token

        response = Response({
            "message": "Login successful!",
            "user": {
                "id": str(user.id),
                "name": user.name,
                "email": user.email
            }
        }, status=status.HTTP_200_OK)

        # Set the authentication token in the cookie
        response.set_cookie(
            key='auth_token',
            value=token_key,
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite='Strict'
        )

        logger.info(f"Login successful for user: {user.email}")
        return response

# Recipe Views

class RecipeListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    authentication_classes = [CookieTokenAuthentication]

    def get(self, request):
        recipes = Recipe.objects.all()
        data = []
        for recipe in recipes:
            data.append({
                'title': recipe.title,
                'description': recipe.description,
                'keywords': recipe.keywords,
                'servings': recipe.servings,
                'cook_time': recipe.cook_time,
                'ingredients': [
                    {
                        'name': ingredient.name,
                        'amount': {
                            'value': ingredient.amount.value if ingredient.amount else None,
                            'unit': ingredient.amount.unit if ingredient.amount else None,
                            'us_value': ingredient.amount.us_value if ingredient.amount else None,
                            'us_unit': ingredient.amount.us_unit if ingredient.amount else None,
                            'metric_value': ingredient.amount.metric_value if ingredient.amount else None,
                            'metric_unit': ingredient.amount.metric_unit if ingredient.amount else None,
                        },
                        'spoonacular_id': ingredient.spoonacular_id,
                        'photo': ingredient.photo,
                        'video': ingredient.video
                    } for ingredient in recipe.ingredients
                ],
                'instructions': [
                    {
                        'step_number': instruction.step_number,
                        'description': instruction.description,
                        'photo': instruction.photo,
                        'video': instruction.video
                    } for instruction in recipe.instructions
                ],
                'media': [{'type': media.type, 'url': media.url, 'file_id': media.file_id} for media in recipe.media],
                'spoonacular_id': recipe.spoonacular_id
            })
        return JsonResponse(data, safe=False)

    def post(self, request):
        logger.info(f"Received POST data: {request.data}")

        title = request.data.get('title')
        description = request.data.get('description')
        keywords = request.data.get('keywords', '')
        servings = request.data.get('servings')
        cook_time = request.data.get('cook_time')
        ingredients_data = request.data.get('ingredients', [])
        instructions_data = request.data.get('instructions', [])
        media_data = request.data.get('media', [])
        
        recipe = Recipe(
            title=title,
            description=description,
            keywords=[keyword.strip() for keyword in keywords.split(',') if keyword.strip()],
            servings=servings,
            cook_time=cook_time,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        recipe.save()

        self.add_ingredients(recipe, ingredients_data)
        self.add_instructions(recipe, instructions_data)
        recipe.media = [self.handle_media(media) for media in media_data]
        recipe.save()

        # Create MyPlate instance and update user's my_plates field
        my_plate = MyPlate(user_id=request.user.id, recipe_id=recipe.id)
        my_plate.save()
        user = User.objects.get(id=request.user.id)
        user.my_plates.append(my_plate)
        user.save()
        recipe.my_plate_id = my_plate.my_plate_id
        recipe.save()

        logger.info(f"Recipe created: {recipe}")
        return JsonResponse({'message': 'Recipe created successfully!'}, status=status.HTTP_201_CREATED)

    def add_ingredients(self, recipe, ingredients_data):
        for ingredient_data in ingredients_data:
            amount_data = ingredient_data.get('amount', None)
            amount = IngredientAmount(
                value=amount_data.get('value') if amount_data else None,
                unit=amount_data.get('unit') if amount_data else None,
                us_value=amount_data.get('us_value') if amount_data else None,
                us_unit=amount_data.get('us_unit') if amount_data else None,
                metric_value=amount_data.get('metric_value') if amount_data else None,
                metric_unit=amount_data.get('metric_unit') if amount_data else None
            ) if amount_data else None
            ingredient = Ingredient(
                name=ingredient_data['name'],
                spoonacular_id=ingredient_data.get('spoonacular_id', None),
                amount=amount,
                photo=self.handle_media(ingredient_data.get('photo')),
                video=self.handle_media(ingredient_data.get('video'))
            )
            recipe.ingredients.append(ingredient)

    def add_instructions(self, recipe, instructions_data):
        for instruction_data in instructions_data:
            instruction = Instruction(
                step_number=instruction_data['step_number'],
                description=instruction_data['description'],
                photo=self.handle_media(instruction_data.get('photo')),
                video=self.handle_media(instruction_data.get('video'))
            )
            recipe.instructions.append(instruction)

    def handle_media(self, media_data):
        if isinstance(media_data, dict):
            file_id = media_data.get('file_id')
            url = media_data.get('url')
            if file_id:
                return Media(type=media_data.get('type'), url=url, file_id=file_id)
            elif url:
                # Use the MediaFile class to handle the download and storage
                media_file = MediaFile.from_url(url, "recipe_image")
                return Media(type=media_data.get('type'), url=url, file_id=media_file.gridfs.grid_id)
        return None


class RecipeRetrieveUpdateDestroyView(APIView):
    authentication_classes = [CookieTokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        logger.info(f"Fetching recipe with ID: {pk}")
        try:
            recipe_id = ObjectId(pk)
            recipe = Recipe.objects.get(id=recipe_id)
        except (InvalidId, Recipe.DoesNotExist):
            logger.error(f"Recipe not found for ID: {pk}")
            return Response(status=status.HTTP_404_NOT_FOUND)

        data = {
            'title': recipe.title,
            'description': recipe.description,
            'keywords': recipe.keywords,
            'servings': recipe.servings,
            'cook_time': recipe.cook_time,
            'ingredients': [
                {
                    'name': ingredient.name,
                    'amount': {
                        'value': ingredient.amount.value if ingredient.amount else None,
                        'unit': ingredient.amount.unit if ingredient.amount else None,
                        'us_value': ingredient.amount.us_value if ingredient.amount else None,
                        'us_unit': ingredient.amount.us_unit if ingredient.amount else None,
                        'metric_value': ingredient.amount.metric_value if ingredient.amount else None,
                        'metric_unit': ingredient.amount.metric_unit if ingredient.amount else None,
                    },
                    'spoonacular_id': ingredient.spoonacular_id,
                    'photo': ingredient.photo,
                    'video': ingredient.video
                } for ingredient in recipe.ingredients
            ],
            'instructions': [
                {
                    'step_number': instruction.step_number,
                    'description': instruction.description,
                    'photo': instruction.photo,
                    'video': instruction.video
                } for instruction in recipe.instructions
            ],
            'media': [{'type': media.type, 'url': media.url, 'file_id': media.file_id} for media in recipe.media],
            'spoonacular_id': recipe.spoonacular_id
        }
        return JsonResponse(data)

    def put(self, request, pk):
        logger.info(f"Updating recipe with ID: {pk}")
        try:
            recipe_id = ObjectId(pk)
            recipe = Recipe.objects.get(id=recipe_id)
        except (InvalidId, Recipe.DoesNotExist):
            logger.error(f"Recipe not found for ID: {pk}")
            return Response(status=status.HTTP_404_NOT_FOUND)

        recipe.title = request.data.get('title', recipe.title)
        recipe.description = request.data.get('description', recipe.description)
        recipe.servings = request.data.get('servings', recipe.servings)
        recipe.cook_time = request.data.get('cook_time', recipe.cook_time)
        recipe.updated_at = datetime.now(timezone.utc)

        ingredients_data = request.data.get('ingredients', [])
        recipe.ingredients = []
        self.add_ingredients(recipe, ingredients_data)

        instructions_data = request.data.get('instructions', [])
        recipe.instructions = []
        self.add_instructions(recipe, instructions_data)

        media_data = request.data.get('media', [])
        recipe.media = [self.handle_media(media) for media in media_data]

        recipe.save()
        logger.info(f"Recipe updated: {recipe}")
        return JsonResponse({'message': 'Recipe updated successfully!'})

    def delete(self, request, pk):
        logger.info(f"Deleting recipe with ID: {pk}")
        try:
            recipe_id = ObjectId(pk)
            recipe = Recipe.objects.get(id=recipe_id)
        except (InvalidId, Recipe.DoesNotExist):
            logger.error(f"Recipe not found for ID: {pk}")
            return Response(status=status.HTTP_404_NOT_FOUND)

        recipe.delete()
        logger.info(f"Recipe with ID: {pk} deleted successfully")
        return Response({'message': 'Recipe deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)

    def add_ingredients(self, recipe, ingredients_data):
        for ingredient_data in ingredients_data:
            amount_data = ingredient_data.get('amount', None)
            amount = IngredientAmount(
                value=amount_data.get('value') if amount_data else None,
                unit=amount_data.get('unit') if amount_data else None,
                us_value=amount_data.get('us_value') if amount_data else None,
                us_unit=amount_data.get('us_unit') if amount_data else None,
                metric_value=amount_data.get('metric_value') if amount_data else None,
                metric_unit=amount_data.get('metric_unit') if amount_data else None
            ) if amount_data else None
            ingredient = Ingredient(
                name=ingredient_data['name'],
                spoonacular_id=ingredient_data.get('spoonacular_id', None),
                amount=amount,
                photo=self.handle_media(ingredient_data.get('photo')),
                video=self.handle_media(ingredient_data.get('video'))
            )
            recipe.ingredients.append(ingredient)

    def add_instructions(self, recipe, instructions_data):
        for instruction_data in instructions_data:
            instruction = Instruction(
                step_number=instruction_data['step_number'],
                description=instruction_data['description'],
                photo=self.handle_media(instruction_data.get('photo')),
                video=self.handle_media(instruction_data.get('video'))
            )
            recipe.instructions.append(instruction)

    def handle_media(self, media_data):
        if isinstance(media_data, dict):
            file_id = media_data.get('file_id')
            url = media_data.get('url')
            if file_id:
                return Media(type=media_data.get('type'), url=url, file_id=file_id)
            elif url:
                # Use the MediaFile class to handle the download and storage
                media_file = MediaFile.from_url(url, "recipe_image")
                return Media(type=media_data.get('type'), url=url, file_id=media_file.gridfs.grid_id)
        return None




















































































# # Recipe views
# class RecipePagination(pagination.PageNumberPagination):
#     page_size = 10
#     page_size_query_param = 'page_size'
#     max_page_size = 100


# class RecipeListCreateView(APIView):
#     permission_classes = [permissions.IsAuthenticatedOrReadOnly]

#     def get(self, request):
#         recipes = Recipe.objects.all()
#         serializer = RecipeSerializer(recipes, many=True)
#         return Response(serializer.data)

#     def post(self, request):
#         logger.info(f"Received POST data: {request.data}")

#         # Handle recipe creation as before
#         serializer = RecipeSerializer(data=request.data)
#         if serializer.is_valid():
#             recipe = serializer.save()
#             logger.info(f"Recipe created: {recipe}")
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
        
#         logger.error(f"Recipe creation failed: {serializer.errors}")
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def create_recipe(self, request):
#         serializer = RecipeSerializer(data=request.data)
#         if serializer.is_valid():
#             recipe = serializer.save()

#             # Handle keywords: Parse comma-separated keywords
#             keywords = request.data.get('keywords', '')
#             recipe.keywords = [keyword.strip() for keyword in keywords.split(',') if keyword.strip()]

#             # Create MyPlate instance
#             my_plate = MyPlate(user_id=request.user.id, recipe_id=recipe.id)
#             my_plate.save()  # Automatically generates my_plate_id

#             # Update the User's my_plates field
#             user = User.objects.get(id=request.user.id)
#             user.my_plates.append(my_plate)
#             user.save()

#             # Update recipe with my_plate_id
#             recipe.my_plate_id = my_plate.my_plate_id
#             recipe.save()

#             # Process ingredients
#             self.add_ingredients(recipe, request.data.get('ingredients', []))

#             # Process instructions
#             self.add_instructions(recipe, request.data.get('instructions', []))

#             recipe.save()
#             logger.info(f"Recipe created: {serializer.data}")
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
        
#         logger.error(f"Recipe creation failed: {serializer.errors}")
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def add_ingredients(self, recipe, ingredients_data):
#         # Handle both step-by-step and single block ingredients input
#         if isinstance(ingredients_data, str):  # Single block
#             single_block_ingredients = ingredients_data.split(',')
#             for ingredient in single_block_ingredients:
#                 ingredient = ingredient.strip()
#                 if ingredient:  # Avoid empty strings
#                     recipe.ingredients.append(Ingredient(name=ingredient))
#         else:  # Step-by-step
#             for ingredient_data in ingredients_data:
#                 # Handling dual-unit and single-unit measurements
#                 if 'amount' in ingredient_data:
#                     amount_data = ingredient_data['amount']
#                     amount = IngredientAmount(
#                         value=amount_data.get('value'),
#                         unit=amount_data.get('unit'),
#                         us_value=amount_data.get('us', {}).get('value'),
#                         us_unit=amount_data.get('us', {}).get('unit'),
#                         metric_value=amount_data.get('metric', {}).get('value'),
#                         metric_unit=amount_data.get('metric', {}).get('unit')
#                     )
#                 else:
#                     amount = None

#                 ingredient = Ingredient(
#                     name=ingredient_data['name'],
#                     spoonacular_id=ingredient_data.get('spoonacular_id', None),
#                     amount=amount
#                 )
#                 recipe.ingredients.append(ingredient)

#     def add_instructions(self, recipe, instructions_data):
#         # Handle both step-by-step and single block instructions input
#         if isinstance(instructions_data, str):  # Single block
#             recipe.instructions.append(Instruction(description=instructions_data))
#         else:  # Step-by-step
#             for instruction_data in instructions_data:
#                 instruction = Instruction(
#                     step_number=instruction_data['step_number'],
#                     description=instruction_data['description'],
#                     photo=instruction_data.get('photo', None),
#                     video=instruction_data.get('video', None)
#                 )
#                 recipe.instructions.append(instruction)


# class RecipeRetrieveUpdateDestroyView(APIView):
#     authentication_classes = [CookieTokenAuthentication]
#     permission_classes = [permissions.IsAuthenticated]

#     def get(self, request, pk):
#         logger.info(f"Fetching recipe with ID: {pk}")
#         try:
#             recipe_id = ObjectId(pk)
#             recipe = Recipe.objects.get(id=recipe_id)  # Use ObjectId with MongoEngine
#         except (InvalidId, Recipe.DoesNotExist):
#             logger.error(f"Recipe not found for ID: {pk}")
#             return Response(status=status.HTTP_404_NOT_FOUND)

#         serializer = RecipeSerializer(recipe)
#         return Response(serializer.data)

#     def put(self, request, pk):
#         logger.info(f"Updating recipe with ID: {pk}")
#         try:
#             recipe_id = ObjectId(pk)
#             recipe = Recipe.objects.get(id=recipe_id)  # Use ObjectId with MongoEngine
#         except (InvalidId, Recipe.DoesNotExist):
#             logger.error(f"Recipe not found for ID: {pk}")
#             return Response(status=status.HTTP_404_NOT_FOUND)

#         serializer = RecipeSerializer(recipe, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             logger.info(f"Recipe updated: {serializer.data}")
#             return Response(serializer.data)
#         logger.error(f"Update failed: {serializer.errors}")
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def delete(self, request, pk):
#         logger.info(f"Deleting recipe with ID: {pk}")
#         try:
#             recipe_id = ObjectId(pk)
#             recipe = Recipe.objects.get(id=recipe_id)  # Use ObjectId with MongoEngine
#             recipe.delete()
#             logger.info(f"Recipe deleted: {pk}")
#             return Response(status=status.HTTP_204_NO_CONTENT)
#         except (ObjectId.InvalidId, Recipe.DoesNotExist):
#             logger.error(f"Recipe not found for ID: {pk}")
#             return Response(status=status.HTTP_404_NOT_FOUND)


# def recipe_form_view(request):
#     # Render the HTML template without needing to process JSON
#     return render(request, 'recipes/recipe_form.html')
