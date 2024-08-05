from django.contrib import admin
from .models import User, SocialAccount, DietaryRestriction, Allergy, Cuisine, UserProfile, SavedRecipe

# Register your models here.
admin.site.register(User)
admin.site.register(SocialAccount)
admin.site.register(DietaryRestriction)
admin.site.register(Allergy)
admin.site.register(Cuisine)
admin.site.register(UserProfile)
admin.site.register(SavedRecipe)
