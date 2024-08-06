from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    Custom user model with additional fields for email verification, account activation, and timestamps.
    """
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)  # For account activation
    is_verified = models.BooleanField(default=False)  # For email verification
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class SocialAccount(models.Model):
    """
    Model to store information about social logins for users.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='social_accounts')
    provider = models.CharField(max_length=255)
    uid = models.CharField(max_length=255, unique=True)
    extra_data = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class DietaryRestriction(models.Model):
    """
    Model to represent different dietary restrictions.
    """
    name = models.CharField(max_length=50)

class Allergy(models.Model):
    """
    Model to represent different allergies.
    """
    name = models.CharField(max_length=50)

class Cuisine(models.Model):
    """
    Model to represent different cuisines.
    """
    name = models.CharField(max_length=50)

class UserProfile(models.Model):
    """
    Model to store additional user-specific information.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    dietary_restrictions = models.ManyToManyField(DietaryRestriction, blank=True)
    allergies = models.ManyToManyField(Allergy, blank=True)
    preferred_cuisines = models.ManyToManyField(Cuisine, blank=True)

class SavedRecipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    guest_user_id = models.CharField(max_length=128, null=True, blank=True)
    recipe = models.ForeignKey('recipes.Recipe', on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)
    last_viewed = models.DateTimeField(auto_now=True)
    is_favorite = models.BooleanField(default=False)