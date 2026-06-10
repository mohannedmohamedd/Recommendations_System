import importlib, sys
sys.path.append(r'D:/Graduation Project/Recommender System')
try:
    efr = importlib.import_module('egyptian_food_rec')
    print('HAS_SURPRISE=', getattr(efr,'HAS_SURPRISE', None))
    print('df shape=', getattr(efr,'df').shape)
except Exception as e:
    import traceback
    traceback.print_exc()
