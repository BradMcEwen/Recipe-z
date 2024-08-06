from django.shortcuts import shortcuts
from django.shortcuts import redirect, render
import requests
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User
from core.models import UserProfile  # Assuming you have a UserProfile model to store additional user info
from guest_user.models import GuestUser
from guest_user.decorators import allow_guest_user
from django.contrib.messages import messages

# Create your views here.

def custom_lockout_response(request):
    context = {
        'message': 'Your account has been locked due to too many failed login attempts. Please try again later.'
    }
    return render(request, 'core/lockout.html', context)

def facebook_callback(request):
    code = request.GET.get('code')
    # ... rest of your Facebook callback logic ...

    # Handle user info (create or log in the user)
    email = user_info.get('email')
    name = user_info.get('name')

    # Create or get the user
    user, created = User.objects.get_or_create(email=email, defaults={'username': email.split('@')[0]})
    
    if created:
        user.first_name = name.split()[0]  # Assuming the first part of the name is the first name
        user.last_name = ' '.join(name.split()[1:])  # The rest is the last name
        user.save()
    
    # Log in the user
    login(request, user)

    return redirect('home')  # Redirect to your desired page

def google_callback(request):
    code = request.GET.get('code')
    # ... rest of your Google callback logic ...

    # Handle user info (create or log in the user)
    email = user_info.get('email')
    name = user_info.get('name')

    # Create or get the user
    user, created = User.objects.get_or_create(email=email, defaults={'username': email.split('@')[0]})

    if created:
        user.first_name = name.split()[0]  # Assuming the first part of the name is the first name
        user.last_name = ' '.join(name.split()[1:])  # The rest is the last name
        user.save()

    # Log in the user
    login(request, user)

    return redirect('home')  # Redirect to your desired page

# Example view using the allow_guest_user decorator
@allow_guest_user
def some_view(request):
    """
    Example view demonstrating guest user and registered user handling.
    """
    user = request.user

    if isinstance(user, GuestUser):
        # Handle guest user logic
        messages.info(request, 'Limited features available. Please create an account for full access.')

        # Retrieve saved recipes for guest user (using session for simplicity)
        saved_recipes = request.session.get('saved_recipes', [])
        saved_recipes = [Recipe.objects.get(id=recipe_id) for recipe_id in saved_recipes]

        # Prompt user to create an account
        messages.info(request, 'Create an account to save recipes permanently and unlock more features.')
    else:
        # Handle registered user logic
        # Access full features (not implemented here)
        pass

    context = {'saved_recipes': saved_recipes}
    return render(request, 'your_template.html', context)

def save_recipe(request, recipe_id):
    """
    Handles saving a recipe for both guest and registered users.
    """
    user = request.user
    recipe = Recipe.objects.get(id=recipe_id)

    if isinstance(user, GuestUser):
        # Handle guest user logic
        guest_user_id = user.id
        # Store saved recipe in session (replace with database storage if needed)
        if 'saved_recipes' not in request.session:
            request.session['saved_recipes'] = []
        request.session['saved_recipes'].append(recipe_id)
        request.session.modified = True
        messages.success(request, 'Recipe saved for later viewing.')
    else:
        # Handle registered user logic
        SavedRecipe.objects.create(user=user, recipe=recipe)
        messages.success(request, 'Recipe saved successfully!')

    return redirect('recipe_detail', recipe_id=recipe_id)