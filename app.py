from backend.main import app
import uvicorn

# This block is for local development and allows running the app with `python app.py`
# The Docker container will run uvicorn directly.
if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=7860, reload=True)