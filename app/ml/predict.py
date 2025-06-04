import pandas as pd
import joblib
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Set base path for your model and label files
base_path = '/home/shivam-likhar/Desktop/backend/app/ml'

# Load the trained ML model that predicts nutrition given food category code
model = joblib.load(os.path.join(base_path, 'food_model.pkl'))

# Load the CSV containing food names and their corresponding category codes
label_df = pd.read_csv(os.path.join(base_path, 'food_labels.csv'))

# Extract all food names from the label dataframe as a list of strings
food_names = label_df['Name'].astype(str).tolist()

# Initialize and fit the TF-IDF vectorizer on the food names list
# This allows us to represent each food name as a vector for similarity comparison
vectorizer = TfidfVectorizer().fit(food_names)

# Transform the entire list of food names into their TF-IDF vectors once (for efficiency)
tfidf_matrix = vectorizer.transform(food_names)

def get_best_match(input_text):
    """
    Find the best matching food category and name for the input_text using TF-IDF fuzzy matching.

    Args:
        input_text (str): Food name input by user.

    Returns:
        food_cat (int or None): Numeric category code of the matched food or None if no good match.
        matched_name (str or None): Matched food name from the dataset or None.
        best_score (float): Similarity score between input and best match (0 to 1).
    """
    # Convert input text to TF-IDF vector
    input_vec = vectorizer.transform([input_text])

    # Calculate cosine similarity between input and all food names
    similarity = cosine_similarity(input_vec, tfidf_matrix)

    # Find the index of the best match (highest similarity score)
    best_match_idx = similarity.argmax()

    # Extract the highest similarity score
    best_score = similarity[0, best_match_idx]

    # If similarity is below threshold (0.5), consider no match found
    if best_score < 0.5:
        return None, None, best_score
    
    # Retrieve matched row from label dataframe by index
    matched_row = label_df.iloc[best_match_idx]

    # Return the category code, matched name, and similarity score
    return matched_row['Food_cat'], matched_row['Name'], best_score

def predict_nutrition(food_name, quantity=100):
    """
    Predict nutrition values for given food name and quantity (grams).
    Nutrition values are predicted per 100g by the model,
    so they are scaled by quantity/100.

    Args:
        food_name (str): User input food name to predict nutrition for.
        quantity (float): Quantity in grams to scale nutrition values.

    Returns:
        dict: Contains matched food name, quantity, nutrition info (Calories, Protein, Fat, Carbs),
              and confidence score of the match.
              If no match, returns error message and confidence.
    """
    # Get best match for the input food name
    food_cat, matched_name, confidence = get_best_match(food_name)

    # If no valid match found, return error with confidence score
    if food_cat is None:
        return {'error': 'Food not recognized', 'confidence': round(confidence, 2)}

    # --- FIXED: Prepare model input as DataFrame with correct column name to avoid sklearn warning ---
    input_df = pd.DataFrame({'Food_cat': [food_cat]})

    # Predict nutrition values (per 100g) from the model
    prediction = model.predict(input_df)[0]

    # Scale predicted nutrition values by the ratio quantity/100
    factor = quantity / 100

    # Return all results including scaled nutrition and confidence score
    return {
        'Matched_Food_Name': matched_name,
        'Quantity_in_grams': quantity,
        'Calories': round(prediction[0] * factor, 2),
        'Protein': round(prediction[1] * factor, 2),
        'Fat': round(prediction[2] * factor, 2),
        'Carbs': round(prediction[3] * factor, 2),
        'confidence': round(confidence, 2)
    }
