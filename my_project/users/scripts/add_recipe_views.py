import requests
import os
from dotenv import load_dotenv
from mongoengine import connect
from models import User

# Load environment variables from .env file
load_dotenv()

# Connect to MongoDB using mongoengine
connect(
    db=os.getenv('MONGO_DB_NAME'),
    host=os.getenv('MONGO_DB_HOST')
)

# Sample data for the recipe
recipe_data = {
    "title": "What to make for dinner tonight?? Bruschetta Style Pork & Pasta",
    "photo": "https://img.spoonacular.com/recipes/715538-556x370.jpg",
    "description": "What to make for dinner tonight?? Bruschetta Style Pork & Pasta might be a good recipe to expand your main course recipe box...",
    "servings": 5,
    "cook_time": "35 minutes",
    "ingredients": [
        {
            "name": "Bow Tie Pasta",
            "amount": {
                "us_value": 3.0,
                "us_unit": "cups",
                "metric_value": 180.0,
                "metric_unit": "g"
            }
        },
        {
            "name": "Parmigiano Reggiano",
            "amount": {
                "us_value": 0.5,
                "us_unit": "cup",
                "metric_value": 50.0,
                "metric_unit": "g"
            }
        },
        {
            "name": "Kraft Recipe Makers Chicken Bruschetta Pasta",
            "amount": {
                "value": 5.0,
                "unit": "servings"
            }
        },
        {
            "name": "Pork Chops",
            "amount": {
                "us_value": 1.5,
                "us_unit": "lb",
                "metric_value": 680.389,
                "metric_unit": "g"
            }
        }
    ],
    "instructions": [
        {"step_number": 1, "description": "Wash and rinse pork chops and place into the skillet."},
        {"step_number": 2, "description": "Cut them into bite-sized pieces and add half of the Basil Garlic simmer sauce."},
        {"step_number": 3, "description": "Boil your water and start working on cooking your bow-tie pasta."},
        {"step_number": 4, "description": "When you have finished boiling and draining your pasta, add it to the pork along with the rest of the Basil Garlic Simmering Sauce, mixing lightly."},
        {"step_number": 5, "description": "Next, you will top with the Chunky Bruschetta Finishing Sauce, cover with Parmesan, and cover."},
        {"step_number": 6, "description": "Cook on low heat 2 to 3 minutes or until heated through."}
    ]
}

# Authentication token
token = os.getenv('AUTH_TOKEN')

# Headers including the authentication token
headers = {
    "Authorization": f"Token {token}",
    "Content-Type": "application/json"
}

# Define the user ID
user_id = os.getenv('USER_ID')

# Test creating a recipe via the Django view
recipe_create_url = os.getenv('RECIPE_CREATE_URL')
response = requests.post(recipe_create_url, json=recipe_data, headers=headers)

if response.status_code == 201:
    recipe_id = response.json()['id']
    print(f"Recipe successfully created: {recipe_id}")

    # Proceed to link the recipe to a user's MyPlate
    my_plate_data = {
        "user_id": user_id,
        "recipe_id": recipe_id
    }

    my_plate_create_url = os.getenv('MY_PLATE_CREATE_URL')
    response = requests.post(my_plate_create_url, json=my_plate_data, headers=headers)

    if response.status_code == 201:
        print(f"MyPlate successfully created: {response.json()['id']}")
    else:
        print(f"Failed to create MyPlate: {response.text}")

    # Update the User document to include the new MyPlate
    user = User.objects(id=user_id).first()
    if user:
        user.my_plates.append(my_plate_data)
        user.save()
        print(f"User updated with new MyPlate: {user.email}")
    else:
        print(f"User with id {user_id} not found")

else:
    print(f"Failed to create recipe: {response.text}")
