# quick test script to verify imports and a sample recommendation
import importlib, sys
sys.path.append(r'D:/Graduation Project/Recommender System')
try:
    efr = importlib.import_module('egyptian_food_rec')
    print('HAS_SURPRISE =', efr.HAS_SURPRISE)
    print('df shape =', efr.df.shape)
    # sample recommendation (may raise if sim not computed)
    try:
        sample_food = efr.df['food_name_en'].iloc[0]
        print('sample food:', sample_food)
        recs = efr.get_recommendations(user_id=1, food_name=sample_food, n_recommendations=5)
        print('recommendations (sample):', recs)
    except Exception as e:
        print('sample recommendation error:', e)
except Exception as e:
    import traceback
    traceback.print_exc()
