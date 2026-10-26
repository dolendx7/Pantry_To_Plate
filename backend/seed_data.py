import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pantrytoplate.settings')
django.setup()

import bcrypt
from datetime import datetime, timedelta
from apps.auth_app.models import User
from apps.kitchen.models import Kitchen
from apps.pantry.models import PantryItem, MasterItem
from apps.buylist.models import ToBuyItem
from apps.recipes.models import Recipe

def seed():
    print("Clearing existing data...")
    User.objects.delete()
    Kitchen.objects.delete()
    PantryItem.objects.delete()
    ToBuyItem.objects.delete()
    Recipe.objects.delete()
    MasterItem.objects.delete()

    print("Creating Admin User...")
    salt = bcrypt.gensalt(rounds=12)
    admin_hash = bcrypt.hashpw("@#$Mokshil123".encode('utf-8'), salt).decode('utf-8')
    
    admin_user = User(
        full_name="Mokshil",
        email="mokshil@gmail.com",
        password_hash=admin_hash,
        role="admin"
    ).save()

    print("Creating Kitchen...")
    kitchen = Kitchen(
        kitchen_name="jain kitchen",
        kitchen_type="nuclear",
        admin_id=admin_user,
        default_diet_type="jain",
        invite_code="abcd1234"
    ).save()

    admin_user.kitchen_id = kitchen
    admin_user.save()
    
    print("Creating Member User...")
    member_hash = bcrypt.hashpw("@#$Dolen123".encode('utf-8'), salt).decode('utf-8')
    member_user = User(
        full_name="Dolen",
        email="dolen@gmail.com",
        password_hash=member_hash,
        role="member",
        kitchen_id=kitchen
    ).save()

    print("Creating Master Items...")
    tomato_master = MasterItem(name="Tomatoes", category="Vegetables", default_unit="kg").save()
    milk_master = MasterItem(name="Milk", category="Dairy", default_unit="L").save()
    rice_master = MasterItem(name="Basmati Rice", category="Grains", default_unit="kg").save()

    print("Creating Pantry Items...")
    PantryItem(
        kitchen_id=kitchen,
        master_item_id=tomato_master,
        name="Tomatoes",
        category="Vegetables",
        quantity=1.5,
        unit="kg",
        storage_location="refrigerator",
        added_by=admin_user,
        expiry_date=datetime.utcnow() + timedelta(days=2),
        status="expiring_soon"
    ).save()

    PantryItem(
        kitchen_id=kitchen,
        master_item_id=milk_master,
        name="Milk",
        category="Dairy",
        quantity=2.0,
        unit="L",
        storage_location="refrigerator",
        added_by=admin_user,
        expiry_date=datetime.utcnow() + timedelta(days=4),
        status="fresh"
    ).save()

    PantryItem(
        kitchen_id=kitchen,
        master_item_id=rice_master,
        name="Basmati Rice",
        category="Grains",
        quantity=3.0,
        unit="kg",
        storage_location="shelf",
        added_by=admin_user,
        expiry_date=datetime.utcnow() + timedelta(days=180),
        status="fresh"
    ).save()

    print("Creating To Buy Items...")
    ToBuyItem(
        kitchen_id=kitchen,
        name="Eggs",
        quantity=12,
        unit="pcs",
        category="Dairy",
        is_urgent=True,
        added_by=member_user
    ).save()

    ToBuyItem(
        kitchen_id=kitchen,
        name="Bread",
        quantity=1,
        unit="loaf",
        category="Bakery",
        is_urgent=False,
        added_by=member_user
    ).save()

    print("Creating Recipes...")
    recipes_list = [
        {
            "title": "Oats with Fruits",
            "category": "breakfast",
            "diet_type": "vegan",
            "calories": 320,
            "protein": 12,
            "carbs": 55,
            "fat": 6,
            "cuisine": "Indian",
            "prep_time": 5, "cook_time": 10, "servings": 1, "difficulty": "easy",
            "ingredients": [{"name": "Rolled Oats", "quantity": 50, "unit": "g"}, {"name": "Mixed Fruits", "quantity": 100, "unit": "g"}, {"name": "Almond Milk", "quantity": 200, "unit": "ml"}],
            "steps": ["Boil oats in almond milk.", "Top with chopped fruits.", "Drizzle with maple syrup."]
        },
        {
            "title": "Grilled Chicken Salad",
            "category": "lunch",
            "diet_type": "nonveg",
            "calories": 450,
            "protein": 40,
            "carbs": 10,
            "fat": 28,
            "cuisine": "American",
            "prep_time": 10, "cook_time": 15, "servings": 2, "difficulty": "medium",
            "ingredients": [{"name": "Chicken Breast", "quantity": 200, "unit": "g"}, {"name": "Lettuce", "quantity": 100, "unit": "g"}, {"name": "Olive Oil", "quantity": 1, "unit": "tbsp"}],
            "steps": ["Grill chicken breast until cooked.", "Slice chicken and toss with greens.", "Dress with olive oil and lemon juice."]
        },
        {
            "title": "Paneer Butter Masala",
            "category": "dinner",
            "diet_type": "veg",
            "calories": 520,
            "protein": 22,
            "carbs": 18,
            "fat": 42,
            "cuisine": "Indian",
            "prep_time": 15, "cook_time": 25, "servings": 3, "difficulty": "medium",
            "ingredients": [{"name": "Paneer", "quantity": 250, "unit": "g"}, {"name": "Tomatoes", "quantity": 3, "unit": "pcs"}, {"name": "Butter", "quantity": 2, "unit": "tbsp"}],
            "steps": ["Puree tomatoes and cook in butter.", "Add spices and cream.", "Add paneer cubes and simmer."]
        },
        {
            "title": "Fruit Smoothie",
            "category": "snack",
            "diet_type": "vegan",
            "calories": 180,
            "protein": 6,
            "carbs": 36,
            "fat": 2,
            "cuisine": "Universal",
            "prep_time": 5, "cook_time": 0, "servings": 1, "difficulty": "easy",
            "ingredients": [{"name": "Banana", "quantity": 1, "unit": "pc"}, {"name": "Mixed Berries", "quantity": 100, "unit": "g"}, {"name": "Orange Juice", "quantity": 150, "unit": "ml"}],
            "steps": ["Put all ingredients in a blender.", "Blend until smooth.", "Serve chilled."]
        },
        {
            "title": "Masala Omelette",
            "category": "breakfast",
            "diet_type": "nonveg",
            "calories": 280,
            "protein": 18,
            "carbs": 4,
            "fat": 21,
            "cuisine": "Indian",
            "prep_time": 5, "cook_time": 5, "servings": 1, "difficulty": "easy",
            "ingredients": [{"name": "Eggs", "quantity": 3, "unit": "pcs"}, {"name": "Onion", "quantity": 0.5, "unit": "pc"}, {"name": "Green Chili", "quantity": 1, "unit": "pc"}],
            "steps": ["Whisk eggs with chopped onion, chili, and spices.", "Pour onto a hot greased pan.", "Flip and cook both sides."]
        },
        {
            "title": "Greek Yogurt with Honey",
            "category": "snack",
            "diet_type": "veg",
            "calories": 200,
            "protein": 15,
            "carbs": 20,
            "fat": 4,
            "cuisine": "Universal",
            "prep_time": 2, "cook_time": 0, "servings": 1, "difficulty": "easy",
            "ingredients": [{"name": "Greek Yogurt", "quantity": 150, "unit": "g"}, {"name": "Honey", "quantity": 1, "unit": "tbsp"}, {"name": "Walnuts", "quantity": 15, "unit": "g"}],
            "steps": ["Scoop yogurt into a bowl.", "Drizzle with honey.", "Top with crushed walnuts."]
        },
        {
            "title": "Kadhi Chawal",
            "category": "lunch",
            "diet_type": "veg",
            "calories": 420,
            "protein": 12,
            "carbs": 70,
            "fat": 10,
            "cuisine": "Indian",
            "prep_time": 15, "cook_time": 30, "servings": 4, "difficulty": "medium",
            "ingredients": [{"name": "Yogurt", "quantity": 200, "unit": "g"}, {"name": "Besan", "quantity": 50, "unit": "g"}, {"name": "Basmati Rice", "quantity": 200, "unit": "g"}],
            "steps": ["Whisk yogurt and besan with water and spices.", "Simmer until thickened.", "Serve with cooked basmati rice."]
        },
        {
            "title": "Dal Makhani & Roti",
            "category": "dinner",
            "diet_type": "veg",
            "calories": 490,
            "protein": 18,
            "carbs": 62,
            "fat": 16,
            "cuisine": "Indian",
            "prep_time": 20, "cook_time": 45, "servings": 3, "difficulty": "hard",
            "ingredients": [{"name": "Black Urad Dal", "quantity": 100, "unit": "g"}, {"name": "Butter", "quantity": 1.5, "unit": "tbsp"}, {"name": "Whole Wheat Flour", "quantity": 150, "unit": "g"}],
            "steps": ["Pressure cook soaked lentils.", "Simmer lentils on low heat with butter, cream, and tomato paste.", "Roll and cook rotis on a tawa."]
        },
        {
            "title": "Tofu Stir Fry",
            "category": "lunch",
            "diet_type": "vegan",
            "calories": 350,
            "protein": 20,
            "carbs": 15,
            "fat": 18,
            "cuisine": "Chinese",
            "prep_time": 10, "cook_time": 10, "servings": 2, "difficulty": "easy",
            "ingredients": [{"name": "Firm Tofu", "quantity": 200, "unit": "g"}, {"name": "Broccoli", "quantity": 100, "unit": "g"}, {"name": "Soy Sauce", "quantity": 2, "unit": "tbsp"}],
            "steps": ["Sauté cubed tofu in a wok until golden.", "Add broccoli florets and stir fry.", "Splash soy sauce and serve."]
        },
        {
            "title": "Chia Seed Pudding",
            "category": "breakfast",
            "diet_type": "vegan",
            "calories": 210,
            "protein": 8,
            "carbs": 22,
            "fat": 11,
            "cuisine": "Universal",
            "prep_time": 5, "cook_time": 0, "servings": 1, "difficulty": "easy",
            "ingredients": [{"name": "Chia Seeds", "quantity": 3, "unit": "tbsp"}, {"name": "Coconut Milk", "quantity": 150, "unit": "ml"}, {"name": "Vanilla Extract", "quantity": 0.5, "unit": "tsp"}],
            "steps": ["Stir chia seeds into coconut milk with vanilla extract.", "Refrigerate for at least 4 hours.", "Stir before serving."]
        },
        {
            "title": "Avocado Toast",
            "category": "breakfast",
            "diet_type": "vegan",
            "calories": 290,
            "protein": 7,
            "carbs": 32,
            "fat": 15,
            "cuisine": "American",
            "prep_time": 5, "cook_time": 5, "servings": 1, "difficulty": "easy",
            "ingredients": [{"name": "Sourdough Bread", "quantity": 1, "unit": "slice"}, {"name": "Avocado", "quantity": 0.5, "unit": "pc"}, {"name": "Cherry Tomatoes", "quantity": 3, "unit": "pcs"}],
            "steps": ["Toast the bread.", "Mash avocado with salt and spread on toast.", "Top with sliced cherry tomatoes."]
        },
        {
            "title": "Fish Curry & Rice",
            "category": "lunch",
            "diet_type": "nonveg",
            "calories": 540,
            "protein": 35,
            "carbs": 65,
            "fat": 14,
            "cuisine": "Indian",
            "prep_time": 15, "cook_time": 20, "servings": 2, "difficulty": "medium",
            "ingredients": [{"name": "Fish Fillet", "quantity": 250, "unit": "g"}, {"name": "Coconut Milk", "quantity": 150, "unit": "ml"}, {"name": "Basmati Rice", "quantity": 100, "unit": "g"}],
            "steps": ["Cook fish in a spiced coconut gravy.", "Boil basmati rice.", "Serve the hot fish curry over rice."]
        },
        {
            "title": "Quinoa Pulao",
            "category": "dinner",
            "diet_type": "vegan",
            "calories": 380,
            "protein": 14,
            "carbs": 58,
            "fat": 8,
            "cuisine": "Indian",
            "prep_time": 10, "cook_time": 20, "servings": 2, "difficulty": "easy",
            "ingredients": [{"name": "Quinoa", "quantity": 100, "unit": "g"}, {"name": "Mixed Veggies", "quantity": 100, "unit": "g"}, {"name": "Olive Oil", "quantity": 1, "unit": "tsp"}],
            "steps": ["Rinse quinoa.", "Sauté veggies in olive oil, then add quinoa and water.", "Cook covered until water is absorbed."]
        },
        {
            "title": "Apple & Almonds",
            "category": "snack",
            "diet_type": "vegan",
            "calories": 180,
            "protein": 4,
            "carbs": 22,
            "fat": 10,
            "cuisine": "Universal",
            "prep_time": 2, "cook_time": 0, "servings": 1, "difficulty": "easy",
            "ingredients": [{"name": "Apple", "quantity": 1, "unit": "pc"}, {"name": "Almonds", "quantity": 12, "unit": "pcs"}],
            "steps": ["Wash and slice the apple.", "Serve with almonds."]
        }
    ]
    for r_data in recipes_list:
        Recipe(
            author_id=admin_user,
            kitchen_id=kitchen,
            **r_data
        ).save()

    print("Database seeding completed successfully!")
    print("-------------------------------------------------")
    print("Admin Credentials:")
    print("Email: mokshil@gmail.com")
    print("Password: @#$Mokshil123")
    print("-------------------------------------------------")
    print("Member Credentials:")
    print("Email: dolen@gmail.com")
    print("Password: @#$Dolen123")
    print("-------------------------------------------------")
    print("Kitchen Name: jain kitchen")
    print("Kitchen Invite Code: abcd1234")
    print("-------------------------------------------------")

if __name__ == "__main__":
    seed()
