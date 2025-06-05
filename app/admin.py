from django.contrib import admin
from .models import User,UserProfile,DiabeticProfile,UserMeal

# Register your models here.
admin.site.register(User)
admin.site.register(UserProfile)
admin.site.register(DiabeticProfile)
admin.site.register(UserMeal)