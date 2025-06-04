import pandas as pd                        # Import pandas for data manipulation
from sklearn.ensemble import RandomForestRegressor  # Import Random Forest regression model from sklearn
import joblib                             # Import joblib for saving and loading models
import os                                # Import os to handle file system operations like directories

# Step 1: Load dataset CSV containing food names and their nutrition data
# The dataset should have columns like 'Name', 'Calories', 'Protein', 'Fats', 'Carbohydrates'
df = pd.read_csv('/home/shivam-likhar/Desktop/backend/app/dataset/merged_nutrition_data.csv')

# Step 2: Encode the food names into numeric category codes
# This transforms the 'Name' column (text) into categorical codes (integers)
# This is needed because ML models require numeric input features
df['Food_cat'] = df['Name'].astype('category').cat.codes

# Step 3: Define features (inputs) and targets (outputs) for the ML model
# X contains just the food category code feature as a DataFrame (2D array)
X = df[['Food_cat']]

# y contains nutrition values we want to predict: Calories, Protein, Fats, Carbohydrates (all per 100g)
y = df[['Calories', 'Protein', 'Fats', 'Carbohydrates']]

# Step 4: Initialize the Random Forest Regressor model
# Random Forest is a robust and widely-used ensemble learning method for regression tasks
model = RandomForestRegressor()

# Step 5: Train the model using the features X and targets y
# This fits the model to learn how nutrition values relate to the food category codes
model.fit(X, y)

# Step 6: Prepare directory to save the trained model and label files
# os.makedirs will create the directory if it does not exist, with 'exist_ok=True' to avoid errors
save_dir = '/home/shivam-likhar/Desktop/backend/app/ml'
os.makedirs(save_dir, exist_ok=True)

# Step 7: Save the trained Random Forest model as a .pkl file using joblib
# This allows you to load the model later for predictions without retraining
joblib.dump(model, os.path.join(save_dir, 'food_model.pkl'))

# Step 8: Save the mapping of food names to their numeric category codes to a CSV file
# This is important for later matching user input to category codes for predictions
df[['Name', 'Food_cat']].drop_duplicates().to_csv(os.path.join(save_dir, 'food_labels.csv'), index=False)
