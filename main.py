# 1. Import the FastAPI class
from fastapi import FastAPI

# 2. Create an instance of the FastAPI class
app = FastAPI()

# 3. Define the endpoint using a decorator
# @app.get("/") tells FastAPI that the function below
# is in charge of handling requests that go to:
# - the root path ("/")
# - using a GET method
@app.get("/")
async def read_root():
    # 4. Return the response
    return {"message": "Hello, World! Welcome to the LogIt backend."}