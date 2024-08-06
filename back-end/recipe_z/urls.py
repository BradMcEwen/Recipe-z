"""
URL configuration for recipe_z project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from core.views import (  # Assuming your views are in core.views
    custom_lockout_response, facebook_callback, google_callback, some_view, save_recipe, convert_to_user
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # Social Login Callbacks
    path('facebook/callback/', facebook_callback, name='facebook_callback'),
    path('google/callback/', google_callback, name='google_callback'),

    # Custom Login Error Handling (optional)
    path('accounts/lockout/', custom_lockout_response, name='lockout'),

    # Login Redirects (assuming these are in separate views)
    path('login/facebook/', some_view, name='facebook_login'),  # Adjust view name if needed
    path('login/google/', some_view, name='google_login'),  # Adjust view name if needed

    # Guest User and Registered User Views
    path('', some_view, name='home'),  # Assuming this is your home page view
    path('convert-to-user/', convert_to_user, name='convert_to_user'),
    path('recipes/<int:recipe_id>/save/', save_recipe, name='save_recipe'),

    # ... other URL patterns
]
