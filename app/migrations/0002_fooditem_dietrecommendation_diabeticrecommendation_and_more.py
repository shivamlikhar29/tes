# Generated by Django 5.2.1 on 2025-05-28 07:14

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FoodItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('calories', models.FloatField()),
                ('protein_g', models.FloatField()),
                ('carbs_g', models.FloatField()),
                ('fats_g', models.FloatField()),
                ('sugar_g', models.FloatField()),
                ('fiber_g', models.FloatField()),
                ('glycemic_index', models.FloatField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='DietRecommendation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('notes', models.TextField(blank=True)),
                ('reason', models.TextField(help_text='ML model reason or rule-based logic')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('recommended_foods', models.ManyToManyField(to='app.fooditem')),
            ],
        ),
        migrations.CreateModel(
            name='DiabeticRecommendation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('sugar_limit_g', models.FloatField(help_text='Recommended sugar limit in grams')),
                ('glycemic_index_note', models.TextField(blank=True)),
                ('reason', models.TextField(help_text='ML/logic-based reason for diabetic recommendation')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('recommended_foods', models.ManyToManyField(to='app.fooditem')),
            ],
        ),
        migrations.CreateModel(
            name='UserMeal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity_g', models.FloatField(help_text='Quantity in grams')),
                ('meal_type', models.CharField(choices=[('breakfast', 'Breakfast'), ('lunch', 'Lunch'), ('dinner', 'Dinner'), ('snack', 'Snack')], max_length=20)),
                ('consumed_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('food_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.fooditem')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('age', models.PositiveIntegerField()),
                ('gender', models.CharField(choices=[('male', 'Male'), ('female', 'Female')], max_length=10)),
                ('height_cm', models.FloatField()),
                ('weight_kg', models.FloatField()),
                ('activity_level', models.CharField(choices=[('sedentary', 'Sedentary'), ('light', 'Light Activity'), ('moderate', 'Moderate Activity'), ('active', 'Active'), ('very_active', 'Very Active')], max_length=50)),
                ('goal', models.CharField(choices=[('lose_weight', 'Lose Weight'), ('maintain', 'Maintain Weight'), ('gain_weight', 'Gain Weight')], max_length=20)),
                ('is_diabetic', models.BooleanField(default=False)),
                ('health_conditions', models.TextField(blank=True, help_text='e.g., hypertension')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
