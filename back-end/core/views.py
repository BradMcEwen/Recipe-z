import django.shortcuts as shortcuts
from django.shortcuts import redirect
import requests
from django.conf import settings

# Create your views here.

def custom_lockout_response(request):
    context = {
        'message': 'Your account has been locked due to too many failed login attempts. Please try again later.'
    }
    return render(request, 'core/lockout.html', context)


def facebook_callback(request):
    code = request.GET.get('code')
    token_url = "https://graph.facebook.com/v10.0/oauth/access_token"
    token_data = {
        'client_id': settings.FACEBOOK_CLIENT_ID,
        'client_secret': settings.FACEBOOK_CLIENT_SECRET,
        'redirect_uri': settings.FACEBOOK_REDIRECT_URI,
        'code': code
    }
    token_response = requests.get(token_url, params=token_data)
    token_json = token_response.json()

    access_token = token_json.get('access_token')
    user_info_url = "https://graph.facebook.com/me?fields=id,name,email"
    user_info_response = requests.get(user_info_url, params={'access_token': access_token})
    user_info = user_info_response.json()

    # Handle user info (e.g., create user, log in user, etc.)

    return redirect('home')  # Redirect to your desired page
