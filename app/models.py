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
    ROLE_CHOICES = [
        ("user", "Normal User (Patient)"),
        ("nutritionist", "Nutritionist"),
        ("admin", "Admin"),
        ("owner", "Owner"),
        ("operator", "Operator"),
    ]

    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="user")

    objects = UserManager()
    USERNAME_FIELD = 'email'

    def __str__(self):
        return f"{self.email} ({self.role})"

    def has_perm(self, perm, obj=None):
        return self.is_admin or self.role == 'admin'

    def has_module_perms(self, app_label):
        return self.is_admin or self.role == 'admin'

    @property
    def is_staff(self):
        return self.is_admin or self.role in ['admin', 'owner']

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
    suitable_for_conditions = models.CharField(max_length=50, choices=HEALTH_CONDITION_CHOICES, default="none")
    suitable_for_goal = models.CharField(max_length=20, choices=GOAL_CHOICES, default="maintain")

    def __str__(self):
        return f"{self.name} ({self.food_type})"


class UserMeal(models.Model):
    UNIT_CHOICES = [
        ("g", "Grams"), ("kg", "Kilograms"),
        ("ml", "Milliliters"), ("l", "Liters"),
        ("cup", "Cup"), ("bowl", "Bowl"),
        ("piece", "Piece"), ("tbsp", "Tablespoon"),
        ("tsp", "Teaspoon"), ("slice", "Slice"),
        ("other", "Other"),
    ]

    MEAL_CHOICES = [
        ("breakfast", "Breakfast"),
        ("lunch", "Lunch"),
        ("dinner", "Dinner"),
        ("snack", "Snack"),
    ]

    user = models.ForeignKey('User', on_delete=models.CASCADE)
    food_item = models.ForeignKey('FoodItem', on_delete=models.SET_NULL, null=True, blank=True)
    food_name = models.CharField(max_length=100, blank=True, null=True)

    quantity = models.FloatField()
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default="g")
    meal_type = models.CharField(max_length=20, choices=MEAL_CHOICES)

    consumed_at = models.DateTimeField(default=timezone.now)
    remarks = models.TextField(blank=True)

    calories = models.FloatField(blank=True, null=True)
    protein = models.FloatField(blank=True, null=True)
    carbs = models.FloatField(blank=True, null=True)
    fats = models.FloatField(blank=True, null=True)
    sugar = models.FloatField(blank=True, null=True)
    fiber = models.FloatField(blank=True, null=True)

    date = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.food_name and self.food_item:
            self.food_name = self.food_item.name
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.email} ate {self.food_name or 'Unknown'} on {self.consumed_at.date()} — {self.quantity} {self.unit}"

# ------------------------# Nutritionist Profile
class NutritionistProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'role': 'nutritionist'})
    expert_level = models.PositiveSmallIntegerField(choices=[(1, 'Basic'), (2, 'Senior')], default=1)

    def __str__(self):
        return f"{self.user.email} - Level {self.expert_level}"



# ------------------------For OWNER/OPERATOR
class AppReport(models.Model):
    report_date = models.DateField(auto_now_add=True)
    new_users = models.IntegerField()
    active_patients = models.IntegerField()
    total_revenue = models.FloatField()
    feedback_summary = models.TextField(blank=True)

    def __str__(self):
        return f"Report on {self.report_date}"


# ------------------------# Patient Reminders
class PatientReminder(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'user'})
    message = models.TextField()
    reminder_time = models.DateTimeField()
    sent = models.BooleanField(default=False)

    def __str__(self):
        return f"Reminder for {self.patient.email} at {self.reminder_time}"
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