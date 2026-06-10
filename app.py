from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import egyptian_food_rec as efr
import math

get_recommendations = efr.get_recommendations
app = FastAPI()

class RecommendationRequest(BaseModel):
    user_id: int
    food_name: str
    n_recommendations: int = 10
    diseases_list: list[str] | None = None
    allergy_ingredients: list[str] | None = None

def sanitize(obj):
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    if isinstance(obj, dict):
        return {k: sanitize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [sanitize(i) for i in obj]
    return obj

@app.post("/recommend")
def recommend(request: RecommendationRequest):
    MAX_REC = 30
    n = min(request.n_recommendations, MAX_REC)
    results = get_recommendations(
        user_id=request.user_id,
        food_name=request.food_name,
        diseases_list=request.diseases_list,
        allergy_ingredients=request.allergy_ingredients,
        n_recommendations=n
    )
    return JSONResponse(content=sanitize({
        "user_id": request.user_id,
        "count": len(results),
        "recommendations": results
    }))

@app.get("/health")
def health_check():
    return {"status": "ok", "HAS_SURPRISE": efr.HAS_SURPRISE}

@app.get("/sample_recommend")
def sample_recommend():
    try:
        sample_food = efr.df['food_name_en'].iloc[0]
        recs = efr.get_recommendations(user_id=1, food_name=sample_food, n_recommendations=5)
        return JSONResponse(content=sanitize({
            "sample_food": sample_food,
            "HAS_SURPRISE": efr.HAS_SURPRISE,
            "recommendations": recs
        }))
    except Exception as e:
        return {"error": str(e)}
