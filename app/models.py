from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone
from django.utils.timezone import now
from django.conf import settings
from django.contrib.postgres.fields import ArrayField

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
    date_joined = models.DateTimeField(default=timezone.now)
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
    country = models.CharField(max_length=100, blank=True, null=True)
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
    HEALTH_CONDITION_CHOICES = [
        ("diabetes", "Diabetes"),
        ("hypertension", "Hypertension"),
        ("thyroid", "Thyroid"),
        ("cholesterol", "Cholesterol"),
        ("pcos", "PCOS/PCOD"),
        ("anemia", "Anemia"),
        ("cancer", "Cancer"),
        ("none", "None"),
    ]

    health_conditions = ArrayField(
        models.CharField(max_length=20, choices=HEALTH_CONDITION_CHOICES),
        blank=True,
        default=list,
        help_text="List of health conditions"
    )
    def __str__(self):
        return f"{self.user.email} Profile"
    

# ---------------------- Diabetes-Specific Table ----------------------
    
class DiabeticProfile(models.Model):
    user_profile = models.ForeignKey('UserProfile', on_delete=models.CASCADE, related_name='diabetic_reports')
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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, default="General Reminder")
    message = models.TextField(blank=True, default="No message provided.")
    created_at = models.DateTimeField(auto_now_add=True)  # No default here
    sent_at = models.DateTimeField(null=True, blank=True)
    date = models.DateTimeField(default=now)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_reminders"
    )

    def __str__(self):
        if self.user:
            return f"Reminder to {self.user.email} - {self.title}"
        return f"Reminder - {self.title}"


########## ------------------------
# Feedback Model
class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    rating = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback by {self.user.email} - {self.rating}⭐"



##############Nutritionist Recommendations
class NutritionistProfile(models.Model):
    EXPERTISE_CHOICES = [
        (1, 'Basic Nutritionist'),   # Handles User IDs 1-10
        (2, 'Senior Nutritionist'),  # Handles User IDs 11-20
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    expert_level = models.IntegerField(choices=EXPERTISE_CHOICES, default=1)

    def __str__(self):
        return f"{self.user.email} - {self.get_expert_level_display()}"


# # ------------------------
# # Diet Recommendations
# # ------------------------

class DietRecommendation(models.Model):
    TYPE_CHOICES = [
        ('general', 'General Recommendation'),
        ('diabetic', 'Diabetic-Specific Recommendation'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recommended_foods = models.ManyToManyField(FoodItem)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='general')
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_recommendations')
    notes = models.TextField(blank=True)
    reason = models.TextField(help_text="ML/logic-based reason")
    
    # Diabetic-specific
    sugar_limit_g = models.FloatField(null=True, blank=True, help_text="For diabetic recommendations")
    glycemic_index_note = models.TextField(blank=True)

    class Meta:
        indexes = [models.Index(fields=["user", "created_at"])]
        unique_together = ('user', 'created_at')

    def __str__(self):
        return f"{self.get_type_display()} for {self.user.email} on {self.created_at.date()}"
