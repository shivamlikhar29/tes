import csv
import os
from app.models import FoodItem  # Replace 'yourapp' with your actual app name
from django.conf import settings

csv_file_path = os.path.join(settings.BASE_DIR, 'app', 'dataset', 'indian_food_items.csv')

with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        FoodItem.objects.create(
            name=row['name'],
            calories=float(row['calories']),
            protein_g=float(row['protein_g']),
            carbs_g=float(row['carbs_g']),
            fats_g=float(row['fats_g']),
            sugar_g=float(row['sugar_g']),
            fiber_g=float(row['fiber_g']),
            glycemic_index=float(row['glycemic_index']),
            food_type=row['food_type'],
            suitable_for_conditions=row['suitable_for_conditions'],
            suitable_for_goal=row['suitable_for_goal'],
        )
print("Data imported successfully!")


# python manage.py shell < app/dataset/r.py
