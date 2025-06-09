from django.contrib import admin
from .models import User, UserProfile, DiabeticProfile, UserMeal, FoodItem,Feedback,PatientReminder,NutritionistProfile,DietRecommendation
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


# ------------------------------
# Custom User Admin Configuration
# ------------------------------
class CustomUserAdmin(BaseUserAdmin):
    list_display = ("email", "role", "is_active", "is_admin")
    list_filter = ("role", "is_admin")
    
    fieldsets = (
        (None, {"fields": ("email", "password", "role")}),
        ("Permissions", {"fields": ("is_active", "is_admin")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "role")}
        ),
    )

    search_fields = ("email",)
    ordering = ("email",)
    filter_horizontal = ()


# ------------------------------
# Register Models with Admin
# ------------------------------
admin.site.register(User, CustomUserAdmin)  # Register custom User admin
admin.site.register(UserProfile)
admin.site.register(DiabeticProfile)
admin.site.register(UserMeal)
admin.site.register(FoodItem)
admin.site.register(Feedback)
admin.site.register(PatientReminder)
admin.site.register(NutritionistProfile)
admin.site.register(DietRecommendation)