import uvicorn
import os
import sys

if __name__ == "__main__":
    print("=" * 65)
    print(" GeoNex - AI Drone Geospatial Mapping & Change Detection System")
    print(" SIH 2026 Problem Statement ID: 26012 | Team: GeoNex")
    print("=" * 65)
    print(" Starting FastAPI server on http://localhost:8000 ...")
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
