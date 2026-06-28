from fastapi import FastAPI
app=FastAPI()
@app.get("/")
def home(): 
    return {"message":"Hello Aishvarya! My first backend API is working!"}

@app.get("/about")
def about():
    return {
        "project": "AI Mutation Predictor",
        "developer": "Aishvarya"
    }
@app.get("/developer")
def developer():
    return {
        "name":"Aishvarya",
        "degreee":"BE CSE",
        "your dream job":"To learn more money any job"
    }
@app.get("/college")
def college():
    return{
        "college":"SREC",
        "dept":"CSE",
        "year":2
    }