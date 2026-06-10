import importlib, sys
sys.path.append(r'D:/Graduation Project/Recommender System')
try:
    efr = importlib.import_module('egyptian_food_rec')
    print('HAS_SURPRISE =', efr.HAS_SURPRISE)
    print('df shape =', efr.df.shape)
    # try sample recommendation
    try:
        sample_food = efr.df['food_name_en'].iloc[0]
        recs = efr.get_recommendations(user_id=1, food_name=sample_food, n_recommendations=3)
        print('sample_recs =', recs)
    except Exception as e:
        print('sample_recs error =', e)
except Exception:
    import traceback
    traceback.print_exc()
