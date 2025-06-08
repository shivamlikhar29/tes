from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone


# ---------------------- User Authentication ----------------------
class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError("Email is required")
        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        user = self.create_user(email, password)
        user.is_admin = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()
    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return self.is_admin

    @property
    def is_staff(self):
        return self.is_admin

# ------------------------
# User Profile
# ------------------------
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    mobile_number = models.CharField(max_length=15, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[("male", "Male"), ("female", "Female")])
    height_cm = models.FloatField()
    weight_kg = models.FloatField()
    activity_level = models.CharField(max_length=50, choices=[
        ("sedentary", "Sedentary"),
        ("light", "Light Activity"),
        ("moderate", "Moderate Activity"),
        ("active", "Active"),
        ("very_active", "Very Active"),
    ])
    goal = models.CharField(max_length=20, choices=[
        ("lose_weight", "Lose Weight"),
        ("maintain", "Maintain Weight"),
        ("gain_weight", "Gain Weight")
    ])

    diet_type = models.CharField(
        max_length=20,
        choices=[
            ("vegetarian", "Vegetarian"),
            ("non_vegetarian", "Non-Vegetarian"),
            ("vegan", "Vegan"),
            ("eggetarian", "Eggetarian"),
            ("other", "Other"),
        ],
        default="other"
    )
    health_conditions = models.TextField(blank=True, help_text="e.g., hypertension")

    def __str__(self):
        return f"{self.user.email} Profile"
    

# ---------------------- Diabetes-Specific Table ----------------------
    
class DiabeticProfile(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    hba1c = models.FloatField(help_text="HbA1c level (%)")
    fasting_blood_sugar = models.FloatField(help_text="Fasting Blood Sugar (mg/dL)")
    insulin_dependent = models.BooleanField(default=False)
    medications = models.TextField(blank=True, null=True)
    diagnosis_date = models.DateField()

    def __str__(self):
        return f"Diabetes Profile for {self.user_profile.name}"
    
# ------------------------
# Food Items
# ------------------------
class FoodItem(models.Model):
    FOOD_TYPE_CHOICES = [
        ("vegetarian", "Vegetarian"),
        ("non_vegetarian", "Non-Vegetarian"),
        ("vegan", "Vegan"),
        ("eggetarian", "Eggetarian"),
        ("other", "Other"),
    ]

    HEALTH_CONDITION_CHOICES = [
        ("none", "None"),
        ("diabetes", "Diabetes"),
        ("thyroid", "Thyroid"),
        ("hypertension", "Hypertension"),
    ]

    GOAL_CHOICES = [
        ("weight_loss", "Weight Loss"),
        ("maintain", "Maintain Weight"),
        ("gain_weight", "Gain Weight"),
    ]

    name = models.CharField(max_length=100)
    calories = models.FloatField()
    protein_g = models.FloatField()
    carbs_g = models.FloatField()
    fats_g = models.FloatField()
    sugar_g = models.FloatField()
    fiber_g = models.FloatField()
    glycemic_index = models.FloatField(null=True, blank=True)

    food_type = models.CharField(max_length=20, choices=FOOD_TYPE_CHOICES, default="other")
    
    suitable_for_conditions = models.CharField(
        max_length=50,
        choices=HEALTH_CONDITION_CHOICES,
        default="none",
        help_text="Health condition this food is suitable for"
    )

    suitable_for_goal = models.CharField(
        max_length=20,
        choices=GOAL_CHOICES,
        default="maintain",
        help_text="Goal this food is suitable for"
    )

    def __str__(self):
        return f"{self.name} ({self.food_type})"
# ------------------------
# User Meal Tracking
# ------------------------
class UserMeal(models.Model):
    UNIT_CHOICES = [
        ("g", "Grams"),
        ("kg", "Kilograms"),
        ("ml", "Milliliters"),
        ("l", "Liters"),
        ("cup", "Cup"),
        ("bowl", "Bowl"),
        ("piece", "Piece"),
        ("tbsp", "Tablespoon"),
        ("tsp", "Teaspoon"),
        ("slice", "Slice"),
        ("other", "Other"),
    ]

    MEAL_CHOICES = [
        ("breakfast", "Breakfast"),
        ("lunch", "Lunch"),
        ("dinner", "Dinner"),
        ("snack", "Snack"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quantity = models.FloatField(help_text="Enter the quantity of the food item")
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default="g")

    meal_type = models.CharField(max_length=20, choices=MEAL_CHOICES)
    consumed_at = models.DateTimeField(default=timezone.now)
    remarks = models.TextField(blank=True, help_text="Any additional notes about the meal")
    calories = models.FloatField()
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} on {self.consumed_at.date()} — {self.quantity} {self.unit}"





# # ------------------------
# # Diet Recommendations
# # ------------------------
# class DietRecommendation(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     recommended_foods = models.ManyToManyField(FoodItem)
#     created_at = models.DateTimeField(default=timezone.now)
#     notes = models.TextField(blank=True)
#     reason = models.TextField(help_text="ML model reason or rule-based logic")

#     def __str__(self):
#         return f"Recommendation for {self.user.email} on {self.created_at.date()}"

# # ------------------------
# # Diabetic-Specific Recommendations
# # ------------------------
# class DiabeticRecommendation(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     recommended_foods = models.ManyToManyField(FoodItem)
#     created_at = models.DateTimeField(default=timezone.now)
#     sugar_limit_g = models.FloatField(help_text="Recommended sugar limit in grams")
#     glycemic_index_note = models.TextField(blank=True)
#     reason = models.TextField(help_text="ML/logic-based reason for diabetic recommendation")

#     def __str__(self):
#         return f"Diabetic Plan for {self.user.email} on {self.created_at.date()}"