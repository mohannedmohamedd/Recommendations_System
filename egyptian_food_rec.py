import pandas as pd
import numpy as np
import pickle
import re
import matplotlib.pyplot as plt
from difflib import get_close_matches,SequenceMatcher
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from wordcloud import WordCloud 
import importlib
import math


HAS_SURPRISE = False
def _import_surprise():
    global HAS_SURPRISE, Reader, Dataset, SVD, train_test_split, accuracy
    try:
        mod_surprise = importlib.import_module('surprise')
        mod_model_selection = importlib.import_module('surprise.model_selection')
        Reader = mod_surprise.Reader
        Dataset = mod_surprise.Dataset
        SVD = mod_surprise.SVD
        train_test_split = mod_model_selection.train_test_split
        accuracy = mod_surprise.accuracy
        HAS_SURPRISE = True
    except Exception:
        HAS_SURPRISE = False

_import_surprise()

df = pd.read_csv("Egyptian_Food_CLEANED.csv")

df.drop_duplicates(subset=["food_name_en"], inplace = True)
df.reset_index(drop=True , inplace=True)

df["Selected_Cols"] = (df['food_name_en'] + ' ') * 1 + \
                       (df['ingredients_en'] + ' ') * 2 + \
                       (df['description_en'] + ' ') * 2 + \
                       (df['main_category_en'] + ' ') * 2 + \
                       (df['calorie_category'] + ' ') * 2

vec = TfidfVectorizer(stop_words='english')
df_after_vectorizer = vec.fit_transform(df['Selected_Cols'])
df_after_vectorizer

DISEASE_RESTRICTIONS = {
    'diabetes': {
        'max_carbs': 45,
        'forbidden_categories_ar': ['حلويات'],
        'forbidden_categories_en': ['Dessert'],
        'forbidden_words_ar': ['شوكولاتة', 'سكر', 'عسل', 'شيرة', 'كراميل','نوتيلا', 'توفي', 'حلوى', 'آيس كريم', 'بوظة','كيك', 'بسكويت', 'تارت', 'بودينغ'],
        'forbidden_words_en': ['chocolate', 'sugar', 'honey', 'syrup', 'caramel','nutella', 'toffee', 'candy', 'ice cream','cake', 'cookie', 'tart', 'pudding'],
    },
    'pressure': {
        # الضغط: نتجنب الأكل المصنّع والمملح - مش كل اللحوم والأسماك
        'forbidden_categories_ar': ['معجنات', 'مشروبات', 'مشروبات ساخنة'],
        'forbidden_categories_en': ['Pastry', 'Beverages', 'Hot Drinks'],
        'forbidden_words_ar': ['مخلل', 'مملح', 'مدخن', 'سجق', 'بسطرمة', 'رنجة', 'فسيخ'],
        'forbidden_words_en': ['pickled', 'salted', 'smoked', 'sausage', 'pastirma', 'cured'],
        'max_fats': 25,                                     # دهون عالية ترفع الضغط
    },
    'heart': {
        'max_fats': 15,
        # الكلمات الممنوعة - نفحص في الاسم والمكونات
        'forbidden_words_ar': ['كبد', 'سجق', 'بسطرمة', 'رنجة', 'فسيخ', 'مخ', 'قلب'],
        'forbidden_words_en': ['liver', 'sausage', 'pastirma', 'herring', 'brain', 'heart meat'],
        # تجنب المقلي
        'forbidden_cooking_words_ar': ['مقلي', 'محمر'],
    },
    'allergy': {
        'check_ingredients': True
        # allergy_ingredients تتجي من المستخدم
    }}
def clean_float(val, default=0.0):
    if val is None:
        return default
    try:
        f = float(val)
        if math.isnan(f) or math.isinf(f):
            return default
        return round(f, 2)
    except:
        return default


def filter_by_diseases(food_names_list, diseases_list=None, allergy_ingredients=None):
    if not diseases_list:
        return food_names_list
    
    filtered_foods = []
    for food_name in food_names_list:
        food_data = df[df['food_name_ar'] == food_name]
        if food_data.empty:
            continue
        
        food_row = food_data.iloc[0]
        is_allowed = True
        
        for disease in diseases_list:
            if disease == 'diabetes':
                if food_row['carbs_per_100g'] > DISEASE_RESTRICTIONS['diabetes']['max_carbs']:
                    is_allowed = False
                    break
                if food_row['main_category_ar'] in DISEASE_RESTRICTIONS['diabetes']['forbidden_categories_ar']:
                    is_allowed = False
                    break
                # contains check في الاسم والمكونات
                combined_ar = food_name.lower() + ' ' + str(food_row['ingredients_ar']).lower()
                if any(w in combined_ar for w in DISEASE_RESTRICTIONS['diabetes']['forbidden_words_ar']):
                    is_allowed = False
                    break
                combined_en = str(food_row['food_name_en']).lower() + ' ' + str(food_row['ingredients_en']).lower()
                if any(w in combined_en for w in DISEASE_RESTRICTIONS['diabetes']['forbidden_words_en']):
                    is_allowed = False
                    break
            
            # Pressure: avoid high sodium foods
            elif disease == 'pressure':
                if food_row['main_category_ar'] in DISEASE_RESTRICTIONS['pressure']['forbidden_categories_ar']:
                    is_allowed = False
                    break
                if food_row['fats_per_100g'] > DISEASE_RESTRICTIONS['pressure']['max_fats']:
                    is_allowed = False
                    break
                combined_ar = food_name.lower() + ' ' + str(food_row['ingredients_ar']).lower()
                if any(w in combined_ar for w in DISEASE_RESTRICTIONS['pressure']['forbidden_words_ar']):
                    is_allowed = False
                    break
                combined_en = str(food_row['main_category_en']).lower() + ' ' + str(food_row['ingredients_en']).lower()
                if any(w in combined_en for w in DISEASE_RESTRICTIONS['pressure']['forbidden_words_en']):
                    is_allowed = False
                    break
            
            # Heart: max fats 15g, avoid high cholesterol
            elif disease == 'heart':
                if food_row['fats_per_100g'] > DISEASE_RESTRICTIONS['heart']['max_fats']:
                    is_allowed = False
                    break
                combined_ar = food_name.lower() + ' ' + str(food_row['ingredients_ar']).lower()
                if any(w in combined_ar for w in DISEASE_RESTRICTIONS['heart']['forbidden_words_ar']):
                    is_allowed = False
                    break
                combined_en = str(food_row['food_name_en']).lower() + ' ' + str(food_row['ingredients_en']).lower()
                if any(w in combined_en for w in DISEASE_RESTRICTIONS['heart']['forbidden_words_en']):
                    is_allowed = False
                    break
                if any(w in food_name.lower() for w in DISEASE_RESTRICTIONS['heart']['forbidden_cooking_words_ar']):
                    is_allowed = False
                    break
            
            # Allergy: check ingredients
            elif disease == 'allergy' and allergy_ingredients:
                ingredients = str(food_row['ingredients_ar']).lower()
                if any(allergen.lower() in ingredients for allergen in allergy_ingredients):
                    is_allowed = False
                    break
        
        if is_allowed:
            filtered_foods.append(food_name)
    return filtered_foods 

def Calc_cosine():
    sim_socre = cosine_similarity(df_after_vectorizer)
    with open('sim_score.pkl', 'wb') as f:
        pickle.dump(sim_socre, f)

def Recommendation(User_Input, diseases_list=None, allergy_ingredients=None):
    try:
        with open('sim_score.pkl', 'rb') as f:
            sim_score = pickle.load(f)
    except:
        Calc_cosine()
        with open('sim_score.pkl', 'rb') as f:
            sim_score = pickle.load(f)

    Food_list = df["food_name_en"].to_list()
    Closest_match = get_close_matches(User_Input, Food_list)

    if not Closest_match:
        print("Food is Not Similar Enough! Enter it Correctly or Try Typing Another one.")
        return

    closest = Closest_match[0]
    matching_ratio = SequenceMatcher(None, User_Input.lower(), closest.lower()).ratio()

    if matching_ratio < 0.75:
        print("Food is Not Found in The Dataset! Enter Another one.")
        return

    input_index = df[df.food_name_en == closest].index[0]
    sim_score_list = list(enumerate(sim_score[input_index]))
    sorted_sim_score = sorted(sim_score_list, key=lambda x: x[1], reverse=True)

    recommendations = []
    
    i = 1
    for id, score in sorted_sim_score:
        index = id
        food_name_arabic = df.iloc[index]['food_name_ar']
        food_name_english = df.iloc[index]['food_name_en']

        if closest == food_name_english:
            continue
        
        recommendations.append((food_name_arabic, score))
        i += 1
        
        if diseases_list and i > 50:
            break
        elif not diseases_list and i > 15:
            break
    
    if diseases_list:
        food_names = [name for name, score in recommendations]
        filtered_names = filter_by_diseases(food_names, diseases_list, allergy_ingredients)
        recommendations = [(name, score) for name, score in recommendations if name in filtered_names]
    
    Final_dict = recommendations[:15]
    return Final_dict


ratings_df = df.iloc[:, 16:].drop('Selected_Cols',axis=1)
ratings_df['food_id'] = df['food_id']

user_rating_cols = [f'user_{i}_rating' for i in range(1, 21)]
# بعمل rows بعدد التقييمات لليوزر الواحد
# بيثبت الاول ويفك التاني والتالت اسم عمود يشيل اسماء الاعمدة اللي اتفكت والاخير يشيل القيم اللي كانت ف الاعمدة
new_long_ratings = ratings_df.melt(id_vars='food_id', value_vars=user_rating_cols, var_name='userId', value_name='rating')

new_long_ratings['userId'] = new_long_ratings['userId'].str.extract('(\d+)').astype(int)
new_long_ratings = new_long_ratings.dropna()


def svd_training_calculation():
    if not HAS_SURPRISE:
        raise ImportError("scikit-surprise is required for SVD training. Install it with: pip install scikit-surprise or conda install -c conda-forge scikit-surprise")

    reader = Reader(rating_scale=(1,5))
    dataset = Dataset.load_from_df(new_long_ratings[['userId','food_id','rating']],reader)
    trainset, testset = train_test_split(dataset, test_size=0.2, random_state=42)
    
    svd = SVD(n_factors=50 ,n_epochs=50 ,lr_all=0.005, reg_all=0.02, random_state=42)
    svd.fit(trainset)
    predictions = svd.test(testset)
    accuracy.rmse(predictions) 
    accuracy.mae(predictions)

    with open("svd_training.pkl",'wb') as f:
        pickle.dump(svd,f)


def Collaborative_filtering(user_id, num_of_recommendations=10, diseases_list=None, allergy_ingredients=None):
    if not HAS_SURPRISE:
        raise ImportError("scikit-surprise is required for collaborative filtering. Install it with: pip install scikit-surprise or conda install -c conda-forge scikit-surprise")

    try: 
        with open("svd_training.pkl",'rb') as f:
            svd = pickle.load(f)
    except:
        svd_training_calculation()
        with open("svd_training.pkl",'rb') as f:
            svd = pickle.load(f)

    foods_ids = set(new_long_ratings['food_id'].unique())
    eaten_food_ids = set(new_long_ratings[new_long_ratings['userId'] == user_id]['food_id'].unique())
    foods_to_predict = foods_ids - eaten_food_ids

    predictions = [(foodid, svd.predict(uid=user_id, iid=foodid).est) for foodid in foods_to_predict]

    # Get more if filtering
    top_count = num_of_recommendations * 3 if diseases_list else num_of_recommendations
    top_recommendations = sorted(predictions, key=lambda x: x[1], reverse=True)[:top_count]
    
    # ========== NEW: Filter by diseases ==========
    if diseases_list:
        # Convert food_id to food_name
        food_name_predictions = []
        for food_id, score in top_recommendations:
            food_name = df[df['food_id'] == food_id]['food_name_ar'].values
            if len(food_name) > 0:
                food_name_predictions.append((food_name[0], score))
        
        # Filter
        food_names = [name for name, score in food_name_predictions]
        filtered_names = filter_by_diseases(food_names, diseases_list, allergy_ingredients)
        
        result = []
        for name in filtered_names[:num_of_recommendations]:
            food_id = df[df['food_name_ar'] == name]['food_id'].values[0]
            # Find original score
            for fname, score in food_name_predictions:
                if fname == name:
                    result.append((food_id, score))
                    break
        return result
    
    return top_recommendations


def Weighted_Hybrid_Recommendations(user_id, food_name, diseases_list=None, allergy_ingredients=None, n_recommendations=10):
    
    content_recs = Recommendation(food_name, diseases_list, allergy_ingredients)
    if content_recs is None:
        content_recs = []
    content_dict = {name: score for name, score in content_recs}

    collab_dict = {}
    if user_id in new_long_ratings['userId'].unique():
        collab_recs = Collaborative_filtering(user_id, num_of_recommendations=20,diseases_list=diseases_list, allergy_ingredients=allergy_ingredients)
        for food_id, score in collab_recs:
            food_name_ar = df[df['food_id'] == food_id]['food_name_ar'].values
            if len(food_name_ar) > 0:
                collab_dict[food_name_ar[0]] = (score / 5)

    all_foods = set(content_dict.keys()) | set(collab_dict.keys())
    content_weight = 0.9
    collab_weight = 0.1
    final_list_foods = []

    for food in all_foods:
        content_score = content_dict.get(food, 0)
        collab_score = collab_dict.get(food, 0)
        
        if not collab_dict:
            final_score = content_score
        else:
            final_score = (content_score * content_weight) + (collab_score * collab_weight)
        
        final_list_foods.append((food, final_score))

    final_list_foods.sort(key=lambda x: x[1], reverse=True)
    
    # Remove duplicates and format
    seen = set()
    output_lines = [] 
    count = 0 
    for food, score in final_list_foods:
        if food in seen:
            continue
        
        food_data = df[df['food_name_ar'] == food]
        if food_data.empty:
            continue
            
        row = food_data.iloc[0]
        count += 1
        # line = f"{count}. {food} - {int(row['calories_per_100g'])} سعر (بروتين: {row['protein_per_100g']} , كاربوهيدرات: {row['carbs_per_100g']} , دهون: {row['fats_per_100g']})"
        output_lines.append({
        "rank": count,
        "food_name": food,
        "calories": int(row['calories_per_100g']) if not pd.isna(row['calories_per_100g']) else 0,
        "protein": clean_float(row['protein_per_100g']),
        "carbs": clean_float(row['carbs_per_100g']),
        "fats": clean_float(row['fats_per_100g'])
        })
        
        if count >= n_recommendations:
            break

    return output_lines


def get_recommendations(user_id,food_name,diseases_list=None,allergy_ingredients=None,n_recommendations=10):

    return Weighted_Hybrid_Recommendations(user_id=user_id,food_name=food_name,diseases_list=diseases_list,
    allergy_ingredients=allergy_ingredients,n_recommendations=n_recommendations
    )
