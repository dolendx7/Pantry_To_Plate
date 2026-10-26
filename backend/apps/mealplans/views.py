import random
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import WeeklyMealPlan, MenuChangeRequest, MealCompletionLog, WaterIntakeLog, WeightLog
from apps.recipes.models import Recipe
from apps.buylist.models import ToBuyItem

# ── Default meal-plan template used when no saved plan exists ──────────────
DEFAULT_PLAN = {
    'monday': {
        'breakfast': {'name': 'Idli & Sambar',         'ingredients': ['Rice Flour','Lentils','Onion','Tomato'],              'time_required': 20, 'notes': 'Serve hot with coconut chutney'},
        'lunch':     {'name': 'Dal Tadka & Jeera Rice', 'ingredients': ['Lentils','Rice','Turmeric','Cumin','Ghee'],           'time_required': 30, 'notes': ''},
        'dinner':    {'name': 'Chole Bhature',           'ingredients': ['Chickpeas','Wheat Flour','Onion','Tomato','Spices'], 'time_required': 50, 'notes': 'Fry bhaturas fresh'},
    },
    'tuesday': {
        'breakfast': {'name': 'Poha',           'ingredients': ['Poha','Onion','Green Chillies','Peanuts','Curry Leaves'], 'time_required': 15, 'notes': ''},
        'lunch':     {'name': 'Chicken Curry',   'ingredients': ['Chicken','Tomato','Onion','Coconut Milk','Spices'],       'time_required': 40, 'notes': ''},
        'dinner':    {'name': 'Chicken Biryani', 'ingredients': ['Chicken','Basmati Rice','Yogurt','Onion','Spices'],       'time_required': 75, 'notes': 'Dum cook for best aroma'},
    },
    'wednesday': {
        'breakfast': {'name': 'Masala Oatmeal',  'ingredients': ['Oats','Milk','Honey','Nuts'],                 'time_required': 10, 'notes': ''},
        'lunch':     {'name': 'Aloo Gobi',        'ingredients': ['Potato','Cauliflower','Onion','Tomato'],     'time_required': 35, 'notes': ''},
        'dinner':    {'name': 'Palak Paneer',     'ingredients': ['Spinach','Paneer','Cream','Onion','Spices'], 'time_required': 35, 'notes': 'Blanch spinach before blending'},
    },
    'thursday': {
        'breakfast': {'name': 'Rava Upma',          'ingredients': ['Semolina','Vegetables','Oil','Spices'],        'time_required': 15, 'notes': ''},
        'lunch':     {'name': 'Egg Curry',            'ingredients': ['Eggs','Tomato','Onion','Coconut Milk'],       'time_required': 30, 'notes': ''},
        'dinner':    {'name': 'Paneer Butter Masala', 'ingredients': ['Paneer','Butter','Tomatoes','Cream','Spices'], 'time_required': 45, 'notes': 'Finish with kasuri methi'},
    },
    'friday': {
        'breakfast': {'name': 'Bread Omelette',   'ingredients': ['Bread','Eggs','Butter','Cheese'],                                        'time_required': 15, 'notes': ''},
        'lunch':     {'name': 'Fish Curry',        'ingredients': ['Fish','Tomato','Coconut Milk','Spices'],                                  'time_required': 35, 'notes': ''},
        'dinner':    {'name': 'Veg Hakka Noodles', 'ingredients': ['Noodles','Cabbage','Capsicum','Carrot','Spring Onion','Soy Sauce'],       'time_required': 25, 'notes': 'High-heat wok for best texture'},
    },
    'saturday': {
        'breakfast': {'name': 'Stuffed Paratha',       'ingredients': ['Wheat Flour','Onion','Butter','Spices'],                         'time_required': 25, 'notes': ''},
        'lunch':     {'name': 'Veg Pulao',              'ingredients': ['Rice','Vegetables','Spices','Ghee'],                             'time_required': 30, 'notes': ''},
        'dinner':    {'name': 'Chicken Tikka Masala',   'ingredients': ['Chicken','Yogurt','Cream','Tomato Puree','Garlic','Ginger'],     'time_required': 55, 'notes': 'Grill tikka before adding to gravy'},
    },
    'sunday': {
        'breakfast': {'name': 'Fruit Salad',   'ingredients': ['Apples','Bananas','Honey','Yogurt'],                                    'time_required': 10, 'notes': 'Add chaat masala for zing'},
        'lunch':     {'name': 'Rajma Chawal',   'ingredients': ['Kidney Beans','Rice','Tomato','Spices','Ghee'],                        'time_required': 50, 'notes': 'Pressure cook rajma overnight'},
        'dinner':    {'name': 'Masala Dosa',    'ingredients': ['Rice','Urad Dal','Potatoes','Onion','Mustard Seeds','Curry Leaves'],   'time_required': 30, 'notes': 'Ferment batter overnight for best results'},
    },
}

DAYS = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']
MEAL_SLOTS = ['breakfast','lunch','dinner']


def _get_kitchen_id(request):
    """Extracts a stable kitchen identifier from the request user."""
    kitchen = getattr(request.user, 'kitchen_id', None)
    if kitchen:
        kitchen_id = getattr(kitchen, 'id', kitchen)
        return str(kitchen_id)
    uid = str(getattr(request.user, 'id', 'default'))
    return uid


from datetime import timedelta

def plan_to_flat_list(plan, kid):
    if not plan:
        return []
    
    # Calculate current week's dates starting from Monday
    today = datetime.utcnow()
    # today.weekday() returns 0 for Monday, 6 for Sunday
    monday = today - timedelta(days=today.weekday())
    monday = monday.replace(hour=0, minute=0, second=0, microsecond=0)
    
    days_list = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    flat_list = []
    
    for i, day_name in enumerate(days_list):
        day_date = monday + timedelta(days=i)
        day_date_str = day_date.strftime('%Y-%m-%d')
        
        day_data = getattr(plan, day_name, {})
        if not day_data:
            continue
            
        for slot in ['breakfast', 'lunch', 'dinner']:
            meal_info = day_data.get(slot, {})
            if isinstance(meal_info, dict) and meal_info.get('name'):
                synthetic_id = f"{plan.id}_{day_name}_{slot}"
                flat_list.append({
                    "id": synthetic_id,
                    "date": f"{day_date_str}T00:00:00.000Z",
                    "mealType": slot,
                    "name": meal_info['name']
                })
    return flat_list

# ─────────────────────────────────────────────────────────────────────────────
class WeeklyMealPlanView(APIView):
    """
    GET  /api/v1/mealplans/week/  → return this kitchen's current plan (flat array format)
    POST /api/v1/mealplans/week/  → save (upsert) a full new plan
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        kid  = _get_kitchen_id(request)
        plan = WeeklyMealPlan.objects(kitchen_id=kid).first()
        flat_list = plan_to_flat_list(plan, kid)
        return Response(flat_list)

    def post(self, request):
        kid  = _get_kitchen_id(request)
        data = request.data

        plan = WeeklyMealPlan.objects(kitchen_id=kid).first()
        if not plan:
            plan = WeeklyMealPlan(kitchen_id=kid, version=1)

        for day in DAYS:
            if day in data:
                setattr(plan, day, data[day])

        plan.week_label     = data.get('week_label', '')
        plan.is_ai_generated = data.get('is_ai_generated', False)
        plan.version        = (plan.version or 1) + 1
        plan.updated_at     = datetime.utcnow()
        plan.save()

        flat_list = plan_to_flat_list(plan, kid)
        return Response(flat_list, status=status.HTTP_201_CREATED)


# ─────────────────────────────────────────────────────────────────────────────
class RegeneratePlanView(APIView):
    """
    POST /api/v1/mealplans/regenerate/
    Regenerates the full weekly plan.  Currently cycles through the
    default template (real AI integration can replace this).
    Body: { "week_label": "Jun 9 – Jun 15" } (optional)
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        kid  = _get_kitchen_id(request)

        plan = WeeklyMealPlan.objects(kitchen_id=kid).first()
        if not plan:
            plan = WeeklyMealPlan(kitchen_id=kid, version=0)

        for day in DAYS:
            setattr(plan, day, DEFAULT_PLAN[day])

        plan.week_label      = request.data.get('week_label', '')
        plan.is_ai_generated = True
        plan.version         = (plan.version or 0) + 1
        plan.updated_at      = datetime.utcnow()
        plan.save()

        flat_list = plan_to_flat_list(plan, kid)
        return Response(flat_list)


# ─────────────────────────────────────────────────────────────────────────────
class UpdateDayView(APIView):
    """
    PATCH /api/v1/mealplans/day/<day>/
    Updates all three meal slots for a single day.
    Body: { "breakfast": {...}, "lunch": {...}, "dinner": {...} }
    """
    permission_classes = [IsAuthenticated]

    def patch(self, request, day):
        day = day.lower()
        if day not in DAYS:
            return Response({'error': f'Invalid day: {day}'}, status=status.HTTP_400_BAD_REQUEST)

        kid  = _get_kitchen_id(request)
        plan = WeeklyMealPlan.objects(kitchen_id=kid).first()
        if not plan:
            plan = WeeklyMealPlan(kitchen_id=kid, **{d: DEFAULT_PLAN[d] for d in DAYS})

        existing = dict(getattr(plan, day) or {})
        for slot in MEAL_SLOTS:
            if slot in request.data:
                existing[slot] = request.data[slot]

        setattr(plan, day, existing)
        plan.updated_at = datetime.utcnow()
        plan.save()

        return Response({'day': day, 'meals': getattr(plan, day)})


# ─────────────────────────────────────────────────────────────────────────────
class UpdateMealSlotView(APIView):
    """
    PATCH /api/v1/mealplans/meal/
    Updates a single meal slot (breakfast/lunch/dinner) within a day.
    Body: { "day": "monday", "slot": "dinner", "meal": { name, ingredients, time_required, notes } }
    """
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        day  = request.data.get('day', '').lower()
        slot = request.data.get('slot', '').lower()
        meal = request.data.get('meal', {})

        if day not in DAYS:
            return Response({'error': f'Invalid day: {day}'}, status=status.HTTP_400_BAD_REQUEST)
        if slot not in MEAL_SLOTS:
            return Response({'error': f'Invalid slot: {slot}'}, status=status.HTTP_400_BAD_REQUEST)
        if not meal.get('name'):
            return Response({'error': 'meal.name is required'}, status=status.HTTP_400_BAD_REQUEST)

        kid  = _get_kitchen_id(request)
        plan = WeeklyMealPlan.objects(kitchen_id=kid).first()
        if not plan:
            plan = WeeklyMealPlan(kitchen_id=kid, **{d: DEFAULT_PLAN[d] for d in DAYS})

        day_data = dict(getattr(plan, day) or DEFAULT_PLAN[day])
        day_data[slot] = meal
        setattr(plan, day, day_data)
        plan.updated_at = datetime.utcnow()
        plan.save()

        return Response({'day': day, 'slot': slot, 'meal': meal})


# ─────────────────────────────────────────────────────────────────────────────
class MenuChangeRequestView(APIView):
    """
    POST /api/v1/mealplans/menu-request/    → member creates a change request
    GET  /api/v1/mealplans/menu-requests/   → list all requests for this kitchen
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        kid  = _get_kitchen_id(request)
        data = request.data
        day  = data.get('day', '').lower()
        slot = data.get('meal_slot', '').lower()

        if day not in DAYS:
            return Response({'error': f'Invalid day: {day}'}, status=status.HTTP_400_BAD_REQUEST)
        if slot not in MEAL_SLOTS:
            return Response({'error': f'Invalid meal slot: {slot}'}, status=status.HTTP_400_BAD_REQUEST)

        req = MenuChangeRequest(
            kitchen_id=kid,
            requested_by=str(getattr(request.user, 'id', 'unknown')),
            requester_name=data.get('requester_name', getattr(request.user, 'full_name', '')),
            day=day,
            meal_slot=slot,
            current_meal=data.get('current_meal', ''),
            reason=data.get('reason', ''),
            suggestion=data.get('suggestion', ''),
        )
        req.save()
        return Response(req.to_dict(), status=status.HTTP_201_CREATED)

    def get(self, request):
        kid = _get_kitchen_id(request)
        status_filter = request.query_params.get('status', None)
        qs = MenuChangeRequest.objects(kitchen_id=kid)
        if status_filter:
            qs = qs.filter(status=status_filter)
        return Response([r.to_dict() for r in qs.order_by('-created_at')[:50]])


# ─────────────────────────────────────────────────────────────────────────────
class MenuChangeRequestResolveView(APIView):
    """
    PATCH /api/v1/mealplans/menu-request/<id>/resolve/
    Admin approves or declines a menu change request.
    Body: { "status": "approved" | "declined", "admin_response": "..." }
    """
    permission_classes = [IsAuthenticated]

    def patch(self, request, request_id):
        try:
            kid = str(request.user.kitchen_id.id) if request.user.kitchen_id else ''
            req = MenuChangeRequest.objects(id=request_id, kitchen_id=kid).first()
        except Exception:
            return Response({'error': 'Invalid request ID'}, status=status.HTTP_400_BAD_REQUEST)

        if not req:
            return Response({'error': 'Request not found'}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get('status', '')
        if new_status not in ('approved', 'declined'):
            return Response({'error': 'status must be approved or declined'}, status=status.HTTP_400_BAD_REQUEST)

        req.status = new_status
        req.admin_response = request.data.get('admin_response', '')
        req.resolved_at = datetime.utcnow()
        req.save()
        return Response(req.to_dict())


class GeneratePlanView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Inputs
            data = request.data
            goal = data.get('goal', 'maintain').lower()
            age = int(data.get('age', 30))
            height = float(data.get('height', 175))
            weight = float(data.get('weight', 70))
            activity = data.get('activity_level', 'moderate').lower()
            allergies_str = data.get('allergies', '')
            pref_cuisine = data.get('preferred_cuisine', '').lower().strip()
            if not pref_cuisine:
                pref_cuisine = 'indian'
            
            # BMR calculations
            # General formula: BMR = 10 * weight + 6.25 * height - 5 * age + 5
            bmr = 10.0 * weight + 6.25 * height - 5.0 * age + 5.0
            
            # TDEE
            multipliers = {
                'sedentary': 1.2,
                'light': 1.375,
                'moderate': 1.55,
                'active': 1.725
            }
            multiplier = multipliers.get(activity, 1.375)
            tdee = bmr * multiplier
            
            # Goal adjustment
            calories = tdee
            if 'loss' in goal:
                calories = tdee - 400
            elif 'gain' in goal:
                calories = tdee + 400
            elif 'muscle' in goal:
                calories = tdee + 300
                
            calories = int(max(1200, min(4000, calories)))
            
            # Macros split
            if 'carb' in goal or 'low carb' in goal:
                p_pct, c_pct, f_pct = 0.30, 0.15, 0.55
            elif 'protein' in goal or 'muscle' in goal:
                p_pct, c_pct, f_pct = 0.35, 0.35, 0.30
            else:
                p_pct, c_pct, f_pct = 0.20, 0.50, 0.30
                
            protein = int((calories * p_pct) / 4)
            carbs = int((calories * c_pct) / 4)
            fat = int((calories * f_pct) / 9)
            
            # Filter by diet type
            diet_type = data.get('diet_type', '').lower().strip()
            if not diet_type:
                diet_type = 'veg'

            query_diet = None
            if diet_type == 'veg':
                query_diet = ['veg', 'vegan', 'jain']
            elif diet_type == 'vegan':
                query_diet = ['vegan']
            elif diet_type == 'jain':
                query_diet = ['jain', 'vegan']
            elif diet_type == 'upwas':
                query_diet = ['upwas']
            elif diet_type == 'nonveg':
                query_diet = ['nonveg', 'veg', 'vegan', 'jain']
            else:
                if 'veg' in goal or 'vegan' in goal or 'vegetarian' in goal:
                    query_diet = ['veg', 'vegan', 'jain']
                else:
                    query_diet = ['veg', 'vegan', 'jain'] # Default to veg
                
            all_recipes = Recipe.objects()
            
            # Filter allergies
            allergies = [a.strip().lower() for a in allergies_str.split(',') if a.strip()]
            filtered_recipes = []
            for r in all_recipes:
                # check diet type
                if query_diet and r.diet_type not in query_diet:
                    continue
                # check cuisine
                if pref_cuisine and pref_cuisine != 'all':
                    rc = (r.cuisine or '').lower()
                    if pref_cuisine not in rc:
                        continue
                # check allergies
                has_allergy = False
                for ing in r.ingredients:
                    ing_name = ing.get('name', '').lower()
                    for allergy in allergies:
                        if allergy in ing_name:
                            has_allergy = True
                            break
                    if has_allergy:
                        break
                if has_allergy:
                    continue
                filtered_recipes.append(r)
                
            # Fallback if cuisine filter was too strict
            if not filtered_recipes and pref_cuisine and pref_cuisine != 'all':
                for r in all_recipes:
                    if query_diet and r.diet_type not in query_diet:
                        continue
                    has_allergy = False
                    for ing in r.ingredients:
                        ing_name = ing.get('name', '').lower()
                        for allergy in allergies:
                            if allergy in ing_name:
                                has_allergy = True
                                break
                        if has_allergy:
                            break
                    if has_allergy:
                        continue
                    filtered_recipes.append(r)

            if not filtered_recipes:
                filtered_recipes = list(all_recipes)
                
            # Distribute meal slots (Breakfast, Morning Snack, Lunch, Evening Snack, Dinner)
            # Targets for slots:
            # breakfast (25%), morning_snack (10%), lunch (35%), evening_snack (10%), dinner (20%)
            slot_targets = {
                'breakfast': 0.25 * calories,
                'morning_snack': 0.10 * calories,
                'lunch': 0.35 * calories,
                'evening_snack': 0.10 * calories,
                'dinner': 0.20 * calories
            }

            # Try AI generation using Gemini if API key is configured
            import os
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key and api_key.strip():
                try:
                    import requests
                    import json
                    import re
                    
                    headers = {
                        "Content-Type": "application/json"
                    }
                    
                    prompt = (
                        f"You are a professional nutritionist. Generate a complete 7-day weekly meal plan for a family kitchen workspace.\n"
                        f"Parameters:\n"
                        f"- Diet Type: {diet_type if diet_type else 'Any'}\n"
                        f"- Cuisine preference: {pref_cuisine if pref_cuisine else 'Any'}\n"
                        f"- Goal: {goal}\n"
                        f"- Target daily calories: {calories} kcal\n"
                        f"- Target macros: protein={protein}g, carbs={carbs}g, fat={fat}g\n"
                        f"- Age={age}, height={height}cm, weight={weight}kg, activity level={activity}\n"
                        f"- Allergy warnings to avoid (do not use these ingredients): {allergies_str if allergies_str else 'None'}\n\n"
                        f"Format the plan exactly as a JSON object containing keys for each day ('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday').\n"
                        f"Each day must contain exactly 5 meal slots: 'breakfast', 'morning_snack', 'lunch', 'evening_snack', and 'dinner'.\n"
                        f"Each slot must be a JSON object with this structure:\n"
                        f"{{\n"
                        f"  \"name\": \"Recipe Name\",\n"
                        f"  \"calories\": 350,\n"
                        f"  \"protein\": 12,\n"
                        f"  \"carbs\": 45,\n"
                        f"  \"fat\": 10,\n"
                        f"  \"ingredients\": [\"ingredient 1\", \"ingredient 2\"],\n"
                        f"  \"time_required\": 25,\n"
                        f"  \"notes\": \"Cuisine/Type info\"\n"
                        f"}}\n\n"
                        f"Ensure recipes are diverse, healthy, and match the cuisine and diet type. "
                        f"Output ONLY the JSON object. Do not include markdown code block formatting or any introduction text."
                    )

                    payload = {
                        "contents": [{
                            "parts": [{
                                "text": prompt
                            }]
                        }],
                        "generationConfig": {
                            "responseMimeType": "application/json"
                        }
                    }
                    
                    response_api = requests.post(
                        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-lite:generateContent?key={api_key}",
                        headers=headers,
                        json=payload,
                        timeout=25
                    )
                    if response_api.status_code == 200:
                        result_json = response_api.json()
                        content = result_json['candidates'][0]['content']['parts'][0]['text'].strip()
                        
                        if content.startswith("```"):
                            content = re.sub(r"^```(?:json)?\n", "", content)
                            content = re.sub(r"\n```$", "", content)
                            content = content.strip()
                            
                        weekly_plan_data = json.loads(content)
                        
                        # Validate keys and slots
                        week_days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
                        slots = ['breakfast', 'morning_snack', 'lunch', 'evening_snack', 'dinner']
                        
                        for day in week_days:
                            if day not in weekly_plan_data:
                                weekly_plan_data[day] = {}
                            for slot in slots:
                                if slot not in weekly_plan_data[day]:
                                    weekly_plan_data[day][slot] = {'name': '', 'ingredients': [], 'time_required': 0, 'notes': ''}
                                else:
                                    item = weekly_plan_data[day][slot]
                                    if 'time_required' not in item and 'time' in item:
                                        item['time_required'] = item['time']
                                    if 'notes' not in item and 'cuisine' in item:
                                        item['notes'] = item['cuisine']
                                    item.setdefault('name', '')
                                    item.setdefault('ingredients', [])
                                    item.setdefault('time_required', 15)
                                    item.setdefault('notes', '')
                                    item.setdefault('calories', int(slot_targets.get(slot, 300)))
                                    item.setdefault('protein', 10)
                                    item.setdefault('carbs', 40)
                                    item.setdefault('fat', 10)
                        
                        kid = _get_kitchen_id(request)
                        plan = WeeklyMealPlan.objects(kitchen_id=kid).first()
                        if not plan:
                            plan = WeeklyMealPlan(kitchen_id=kid)
                            
                        plan.monday = weekly_plan_data['monday']
                        plan.tuesday = weekly_plan_data['tuesday']
                        plan.wednesday = weekly_plan_data['wednesday']
                        plan.thursday = weekly_plan_data['thursday']
                        plan.friday = weekly_plan_data['friday']
                        plan.saturday = weekly_plan_data['saturday']
                        plan.sunday = weekly_plan_data['sunday']
                        
                        plan.target_calories = calories
                        plan.target_protein = protein
                        plan.target_carbs = carbs
                        plan.target_fat = fat
                        plan.is_ai_generated = True
                        plan.version = (plan.version or 0) + 1
                        plan.updated_at = datetime.utcnow()
                        plan.save()
                        
                        try:
                            from apps.chat.models import Message
                            Message(
                                kitchen_id=request.user.kitchen_id,
                                sender_id=request.user,
                                sender_name="System",
                                message_type="system",
                                text="🤖 AI generated a personalized weekly meal plan for the family using Google Gemini!"
                            ).save()
                        except Exception:
                            pass
                            
                        flat_list = plan_to_flat_list(plan, kid)
                        return Response(flat_list, status=status.HTTP_201_CREATED)
                    else:
                        raise Exception(f"Gemini API returned status code {response_api.status_code}: {response_api.text}")
                except Exception as e:
                    print(f"Gemini Meal Plan API call failed: {str(e)}. Falling back to local database matcher.")
            
            # Group recipes by slot categories
            recipes_by_cat = {
                'breakfast': [r for r in filtered_recipes if r.category == 'breakfast'],
                'snack': [r for r in filtered_recipes if r.category in ('snack', 'desserts', 'salads', 'drinks')],
                'lunch': [r for r in filtered_recipes if r.category == 'lunch'],
                'dinner': [r for r in filtered_recipes if r.category == 'dinner']
            }
            
            used_recipe_ids = set()

            # Helper function to get recipe closest to target calories
            def get_best_recipe(category_key, target_cals):
                pool = recipes_by_cat.get(category_key, [])
                if not pool:
                    pool = filtered_recipes # Fallback
                if not pool:
                    pool = list(all_recipes) # Ultimate fallback
                
                # Filter out already used recipes to avoid repeating them in the same week
                unused_pool = [x for x in pool if str(x.id) not in used_recipe_ids]
                if not unused_pool:
                    unused_pool = pool
                
                # Find closest by calories
                sorted_pool = sorted(unused_pool, key=lambda x: abs((x.calories or 300) - target_cals))
                # Select a random recipe from the top 10 closest to avoid repetitive weekly meals
                selection_pool = sorted_pool[:min(10, len(sorted_pool))]
                chosen = random.choice(selection_pool) if selection_pool else None
                if chosen:
                    used_recipe_ids.add(str(chosen.id))
                return chosen

            def serialize_recipe(recipe):
                if not recipe:
                    return {'name': '', 'ingredients': [], 'time_required': 0, 'notes': ''}
                return {
                    'id': str(recipe.id),
                    'name': recipe.title,
                    'calories': recipe.calories or 300,
                    'protein': recipe.protein or 10,
                    'carbs': recipe.carbs or 40,
                    'fat': recipe.fat or 10,
                    'ingredients': [ing.get('name', '') for ing in recipe.ingredients],
                    'time_required': (recipe.prep_time or 0) + (recipe.cook_time or 0),
                    'notes': recipe.cuisine or '',
                    'image_url': recipe.image_url or ''
                }

            # Generate weekly plan dict
            week_days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            weekly_plan_data = {}
            for day in week_days:
                weekly_plan_data[day] = {
                    'breakfast': serialize_recipe(get_best_recipe('breakfast', slot_targets['breakfast'])),
                    'morning_snack': serialize_recipe(get_best_recipe('snack', slot_targets['morning_snack'])),
                    'lunch': serialize_recipe(get_best_recipe('lunch', slot_targets['lunch'])),
                    'evening_snack': serialize_recipe(get_best_recipe('snack', slot_targets['evening_snack'])),
                    'dinner': serialize_recipe(get_best_recipe('dinner', slot_targets['dinner']))
                }
                
            # Save weekly meal plan (upsert on user's kitchen ID)
            kid = _get_kitchen_id(request)
            plan = WeeklyMealPlan.objects(kitchen_id=kid).first()
            if not plan:
                plan = WeeklyMealPlan(kitchen_id=kid)
                
            plan.monday = weekly_plan_data['monday']
            plan.tuesday = weekly_plan_data['tuesday']
            plan.wednesday = weekly_plan_data['wednesday']
            plan.thursday = weekly_plan_data['thursday']
            plan.friday = weekly_plan_data['friday']
            plan.saturday = weekly_plan_data['saturday']
            plan.sunday = weekly_plan_data['sunday']
            
            plan.target_calories = calories
            plan.target_protein = protein
            plan.target_carbs = carbs
            plan.target_fat = fat
            plan.is_ai_generated = True
            plan.version = (plan.version or 0) + 1
            plan.updated_at = datetime.utcnow()
            plan.save()
            
            # Send system announcement in Family Chat
            try:
                from apps.chat.models import Message
                Message(
                    kitchen_id=request.user.kitchen_id,
                    sender_id=request.user,
                    sender_name="System",
                    message_type="system",
                    text="📅 Weekly meal plan updated for the family!"
                ).save()
            except Exception as chat_err:
                pass
            
            flat_list = plan_to_flat_list(plan, kid)
            return Response(flat_list, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GroceryListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            kid = _get_kitchen_id(request)
            plan = WeeklyMealPlan.objects(kitchen_id=kid).first()
            if not plan:
                return Response([])
                
            # Aggregate ingredients from all days and slots
            ingredients_map = {} # name -> {quantity, unit}
            week_days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            
            for day in week_days:
                day_meals = getattr(plan, day, {})
                for slot, meal in day_meals.items():
                    if not meal:
                        continue
                    recipe_id = meal.get('id')
                    if not recipe_id:
                        continue
                    # Fetch detailed recipe from DB to get structured ingredients
                    recipe = Recipe.objects(id=recipe_id, kitchen_id=kid).first()
                    if not recipe:
                        continue
                    for ing in recipe.ingredients:
                        name = ing.get('name', '').strip().title()
                        qty = float(ing.get('quantity', 1))
                        unit = ing.get('unit', 'unit').strip()
                        if not name:
                            continue
                        
                        key = f"{name.lower()}_{unit.lower()}"
                        if key in ingredients_map:
                            ingredients_map[key]['quantity'] += qty
                        else:
                            ingredients_map[key] = {
                                'name': name,
                                'quantity': qty,
                                'unit': unit
                            }
            
            grocery_list = list(ingredients_map.values())
            return Response(grocery_list)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ImportGroceryListView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            from apps.pantry.models import PantryItem
            kid = _get_kitchen_id(request)
            items = request.data.get('items', [])
            if not items:
                return Response({'error': 'No items to import'}, status=status.HTTP_400_BAD_REQUEST)
                
            # Fetch current pantry items to subtract already in-stock elements
            pantry_items = PantryItem.objects(kitchen_id=request.user.kitchen_id)
            pantry_map = {pi.name.lower().strip(): pi for pi in pantry_items}
            
            imported_count = 0
            excluded_count = 0
            deducted_count = 0
            
            for item in items:
                name = item.get('name', '').strip()
                qty = float(item.get('quantity', 1))
                unit = item.get('unit', 'unit').strip()
                if not name:
                    continue
                    
                name_lower = name.lower().strip()
                if name_lower in pantry_map:
                    pantry_qty = pantry_map[name_lower].quantity
                    if pantry_qty >= qty:
                        # Excluded completely as fully in stock
                        excluded_count += 1
                        continue
                    else:
                        # Deduct available quantity and buy the remainder
                        qty = qty - pantry_qty
                        deducted_count += 1
                
                # Add remaining/full qty to buy list
                ToBuyItem(
                    kitchen_id=request.user.kitchen_id,
                    name=name,
                    quantity=qty,
                    unit=unit,
                    category='Meal Planner',
                    added_by=request.user
                ).save()
                imported_count += 1
                
            # Send system announcement in Family Chat
            try:
                from apps.chat.models import Message
                announcement = f"🛒 Grocery List Updated: imported {imported_count} ingredients to kitchen shopping list!"
                if excluded_count > 0 or deducted_count > 0:
                    announcement += f" ({excluded_count} items excluded/deducted as they are in-stock in pantry)"
                Message(
                    kitchen_id=request.user.kitchen_id,
                    sender_id=request.user,
                    sender_name="System",
                    message_type="system",
                    text=announcement
                ).save()
            except Exception as chat_err:
                pass

            msg = f'Successfully imported {imported_count} items to your shopping list.'
            if excluded_count > 0:
                msg += f' Excluded {excluded_count} items already in stock.'
            return Response({'message': msg})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PrepareMealView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            from apps.pantry.models import PantryItem
            kid = _get_kitchen_id(request)
            data = request.data
            day = data.get('day', '').lower().strip()
            slot = data.get('slot', '').lower().strip()
            
            if day not in DAYS:
                return Response({'error': f'Invalid day: {day}'}, status=status.HTTP_400_BAD_REQUEST)
            if slot not in MEAL_SLOTS:
                return Response({'error': f'Invalid slot: {slot}'}, status=status.HTTP_400_BAD_REQUEST)
                
            plan = WeeklyMealPlan.objects(kitchen_id=kid).first()
            if not plan:
                return Response({'error': 'No weekly plan generated'}, status=status.HTTP_404_NOT_FOUND)
                
            day_meals = getattr(plan, day, {})
            meal = day_meals.get(slot)
            if not meal or not meal.get('name'):
                return Response({'error': f'No meal set for {day} {slot}'}, status=status.HTTP_400_BAD_REQUEST)
                
            raw_ingredients = meal.get('ingredients', [])
            deducted_items = []
            deleted_items = []
            
            pantry_items = PantryItem.objects(kitchen_id=request.user.kitchen_id)
            pantry_map = {pi.name.lower().strip(): pi for pi in pantry_items}
            
            for ing_name in raw_ingredients:
                ing_clean = ing_name.lower().strip()
                matched_item = pantry_map.get(ing_clean)
                if not matched_item:
                    for name_key, p_item in pantry_map.items():
                        if name_key in ing_clean or ing_clean in name_key:
                            matched_item = p_item
                            break
                            
                if matched_item:
                    unit_lower = (matched_item.unit or 'pcs').lower().strip()
                    sub_qty = 1.0
                    if unit_lower == 'kg':
                        sub_qty = 0.25
                    elif unit_lower == 'g':
                        sub_qty = 100.0
                    elif unit_lower in ('litre', 'l'):
                        sub_qty = 0.25
                    elif unit_lower == 'ml':
                        sub_qty = 250.0
                    elif unit_lower == 'dozen':
                        sub_qty = 1.0
                        
                    if matched_item.quantity > sub_qty:
                        matched_item.quantity -= sub_qty
                        matched_item.save()
                        deducted_items.append(f"{matched_item.name} (-{sub_qty} {matched_item.unit})")
                    else:
                        deleted_items.append(matched_item.name)
                        matched_item.delete()
                        
            # Post a system chat announcement
            try:
                from apps.chat.models import Message
                msg_text = f"🍳 {request.user.full_name or 'Someone'} prepared '{meal.get('name')}' for {day.capitalize()} {slot.capitalize()}!"
                if deducted_items or deleted_items:
                    detail = []
                    if deducted_items:
                        detail.append("deducted: " + ", ".join(deducted_items))
                    if deleted_items:
                        detail.append("depleted: " + ", ".join(deleted_items))
                    msg_text += " Pantry updated (" + "; ".join(detail) + ")"
                    
                Message(
                    kitchen_id=request.user.kitchen_id,
                    sender_id=request.user,
                    sender_name="System",
                    message_type="system",
                    text=msg_text
                ).save()
            except Exception:
                pass
                
            return Response({
                'message': f"Successfully marked meal as cooked and updated pantry inventory.",
                'deducted': deducted_items,
                'depleted': deleted_items
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DashboardSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            from apps.pantry.models import PantryItem
            from apps.buylist.models import ToBuyItem
            from datetime import timedelta, date

            kid = _get_kitchen_id(request)
            today_name = datetime.utcnow().strftime('%A').lower()

            # 1. Fetch Weekly Plan
            plan = WeeklyMealPlan.objects(kitchen_id=kid).first()
            
            # Helper to check if a slot is completed today
            def is_slot_completed(day, slot):
                return MealCompletionLog.objects(kitchen_id=kid, day=day, slot=slot, completed_at__gte=datetime.utcnow().replace(hour=0, minute=0, second=0)).first() is not None

            # Build today's meal plan list with completion flag
            day_plan = getattr(plan, today_name, {}) if plan else {}
            today_meals = []
            slots = ['breakfast', 'morning_snack', 'lunch', 'evening_snack', 'dinner']
            slots_caps = {'breakfast': 'Breakfast', 'morning_snack': 'Morning Snack', 'lunch': 'Lunch', 'evening_snack': 'Evening Snack', 'dinner': 'Dinner'}
            
            calories_consumed = 0
            protein_consumed = 0
            carbs_consumed = 0
            fat_consumed = 0

            # Today's logs for macros sum
            today_logs = MealCompletionLog.objects(kitchen_id=kid, completed_at__gte=datetime.utcnow().replace(hour=0, minute=0, second=0))
            for log in today_logs:
                calories_consumed += log.calories or 0
                # Approximate macros based on ratio
                protein_consumed += int((log.calories or 0) * 0.15 / 4)
                carbs_consumed += int((log.calories or 0) * 0.55 / 4)
                fat_consumed += int((log.calories or 0) * 0.30 / 9)

            for slot in slots:
                meal_data = day_plan.get(slot) if day_plan else None
                if meal_data and meal_data.get('name'):
                    today_meals.append({
                        'slot': slot,
                        'label': slots_caps[slot],
                        'name': meal_data['name'],
                        'time': meal_data.get('time_required', 20),
                        'calories': meal_data.get('calories', 350),
                        'completed': is_slot_completed(today_name, slot)
                    })

            # 2. Water Intake Today
            water_logs = WaterIntakeLog.objects(kitchen_id=kid, logged_at__gte=datetime.utcnow().replace(hour=0, minute=0, second=0))
            water_today = sum(log.amount for log in water_logs)

            # 3. Weight Progress
            latest_weight_log = WeightLog.objects(user_id=request.user).order_by('-logged_at').first()
            current_weight = latest_weight_log.weight if latest_weight_log else 70.0
            target_weight = latest_weight_log.target_weight if latest_weight_log else 65.0

            # 4. Grocery / Stock Overview
            to_buy_count = ToBuyItem.objects(kitchen_id=request.user.kitchen_id, is_purchased=False).count()
            pantry_items = PantryItem.objects(kitchen_id=request.user.kitchen_id)
            low_stock_count = 0
            expiring_count = 0
            
            now_dt = datetime.utcnow()
            week_away = now_dt + timedelta(days=7)

            for item in pantry_items:
                unit_lower = (item.unit or 'pcs').lower()
                threshold = 1.0
                if unit_lower == 'kg':
                    threshold = 0.5
                elif unit_lower == 'l':
                    threshold = 0.5
                elif unit_lower == 'g':
                    threshold = 200.0
                if item.quantity <= threshold:
                    low_stock_count += 1
                
                if item.expiry_date:
                    try:
                        exp_dt = datetime.fromisoformat(item.expiry_date.replace('Z', '+00:00')) if isinstance(item.expiry_date, str) else item.expiry_date
                        if now_dt <= exp_dt <= week_away:
                            expiring_count += 1
                    except Exception:
                        pass

            # 5. Alerts Generation
            alerts = []
            if water_today < 2.0:
                alerts.append({
                    'id': 'water_alert',
                    'title': '💧 Keep Hydrated',
                    'text': f"You've logged {water_today:.2f}L of water today. Reach your 2.0L goal!",
                    'type': 'warning'
                })
            
            expiring_items = []
            for item in pantry_items:
                if item.expiry_date:
                    try:
                        exp_dt = datetime.fromisoformat(item.expiry_date.replace('Z', '+00:00')) if isinstance(item.expiry_date, str) else item.expiry_date
                        if now_dt <= exp_dt <= now_dt + timedelta(days=2):
                            expiring_items.append(item.name)
                    except Exception:
                        pass
            if expiring_items:
                alerts.append({
                    'id': 'expiry_alert',
                    'title': '⚠️ Ingredients Expiring Soon',
                    'text': f"{', '.join(expiring_items[:2])} will expire within 48 hours.",
                    'type': 'danger'
                })
            
            alerts.append({
                'id': 'meal_reminder',
                'title': '🍳 Dinner Prep Reminder',
                'text': "Time to prepare tomorrow's lunch and review dinner ingredients.",
                'type': 'info'
            })

            # 6. Streak & Stats
            start_of_week = datetime.utcnow() - timedelta(days=datetime.utcnow().weekday())
            start_of_week = start_of_week.replace(hour=0, minute=0, second=0)
            weekly_completed_count = MealCompletionLog.objects(kitchen_id=kid, completed_at__gte=start_of_week).count()
            
            streak = 0
            for i in range(15):
                check_date = date.today() - timedelta(days=i)
                dt_min = datetime.combine(check_date, datetime.min.time())
                dt_max = datetime.combine(check_date, datetime.max.time())
                logs_exist = MealCompletionLog.objects(kitchen_id=kid, completed_at__gte=dt_min, completed_at__lte=dt_max).count() > 0
                if logs_exist:
                    streak += 1
                else:
                    if i > 0:
                        break

            return Response({
                'today_meals': today_meals,
                'nutrition': {
                    'target_calories': plan.target_calories if plan else 2000,
                    'target_protein': plan.target_protein if plan else 120,
                    'target_carbs': plan.target_carbs if plan else 220,
                    'target_fat': plan.target_fat if plan else 65,
                    'calories_consumed': calories_consumed,
                    'protein_consumed': protein_consumed,
                    'carbs_consumed': carbs_consumed,
                    'fat_consumed': fat_consumed,
                    'water_today': water_today
                },
                'weight': {
                    'current': current_weight,
                    'target': target_weight,
                    'progress_pct': min(100, max(0, int((70 - current_weight) / (70 - target_weight) * 100))) if current_weight != target_weight else 100
                },
                'grocery_overview': {
                    'to_buy': to_buy_count,
                    'low_stock': low_stock_count,
                    'expiring': expiring_count
                },
                'alerts': alerts,
                'stats': {
                    'completed_this_week': weekly_completed_count,
                    'recipes_cooked': weekly_completed_count,
                    'calories_tracked': calories_consumed,
                    'streak': streak or 3
                }
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LogWaterView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            amount = float(request.data.get('amount', 0.25))
            kid = _get_kitchen_id(request)
            log = WaterIntakeLog(
                user_id=request.user,
                kitchen_id=kid,
                amount=amount
            )
            log.save()
            return Response(log.to_dict(), status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UpdateWeightView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            weight = float(request.data.get('weight', 70))
            target_weight = float(request.data.get('target_weight', 65))
            log = WeightLog(
                user_id=request.user,
                weight=weight,
                target_weight=target_weight
            )
            log.save()
            return Response(log.to_dict(), status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CompleteMealView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            kid = _get_kitchen_id(request)
            day = request.data.get('day', '').lower().strip()
            slot = request.data.get('slot', '').lower().strip()
            meal_name = request.data.get('meal_name', 'Healthy Meal')
            calories = int(request.data.get('calories', 350))

            log = MealCompletionLog(
                kitchen_id=kid,
                day=day,
                slot=slot,
                meal_name=meal_name,
                calories=calories
            )
            log.save()
            return Response(log.to_dict(), status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PlanMealView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        kid = _get_kitchen_id(request)
        date = request.data.get('date')
        mealType = request.data.get('mealType', '').lower().strip()
        name = request.data.get('name')

        if not date or not mealType or not name:
            return Response({'error': 'date, mealType, and name are required'}, status=400)

        try:
            dt = datetime.strptime(date[:10], "%Y-%m-%d")
        except Exception:
            dt = datetime.utcnow()
            
        day_name = dt.strftime('%A').lower()

        if day_name not in DAYS:
            return Response({'error': f'Invalid day: {day_name}'}, status=400)
        if mealType not in MEAL_SLOTS:
            return Response({'error': f'Invalid mealType: {mealType}'}, status=400)

        try:
            plan = WeeklyMealPlan.objects(kitchen_id=kid).first()
            if not plan:
                plan = WeeklyMealPlan(kitchen_id=kid, version=1)

            # Get ingredients from Recipe if exists
            from apps.recipes.models import Recipe
            recipe = Recipe.objects(kitchen_id=kid, title__iexact=name).first()
            ingredients = []
            if recipe and recipe.ingredients:
                ingredients = [ing.get('name') for ing in recipe.ingredients if ing.get('name')]

            day_data = dict(getattr(plan, day_name) or {})
            day_data[mealType] = {
                "name": name,
                "ingredients": ingredients,
                "time_required": (recipe.prep_time + recipe.cook_time) if recipe else 20,
                "notes": (recipe.cuisine) if recipe else ""
            }
            setattr(plan, day_name, day_data)
            plan.updated_at = datetime.utcnow()
            plan.save()

            synthetic_id = f"{plan.id}_{day_name}_{mealType}"
            date_iso = dt.strftime('%Y-%m-%d') + "T00:00:00.000Z"
            return Response({
                "id": synthetic_id,
                "date": date_iso,
                "mealType": mealType,
                "name": name
            }, status=200)
        except Exception as e:
            return Response({'error': str(e)}, status=500)


class ClearPlanView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, plan_id):
        kid = _get_kitchen_id(request)
        parts = plan_id.split('_')
        if len(parts) < 3:
            return Response({'error': 'Invalid slot plan ID'}, status=400)

        real_plan_id = parts[0]
        day_name = parts[1]
        slot = parts[2]

        if day_name not in DAYS or slot not in MEAL_SLOTS:
            return Response({'error': 'Invalid day or slot'}, status=400)

        try:
            plan = WeeklyMealPlan.objects(id=real_plan_id, kitchen_id=kid).first()
            if not plan:
                return Response({'error': 'Meal plan not found'}, status=404)

            day_data = dict(getattr(plan, day_name) or {})
            if slot in day_data:
                day_data[slot] = { "name": "", "ingredients": [], "time_required": 0, "notes": "" }
                setattr(plan, day_name, day_data)
                plan.updated_at = datetime.utcnow()
                plan.save()

            return Response({"message": "Meal plan slot cleared successfully"}, status=200)
        except Exception as e:
            return Response({'error': str(e)}, status=500)


