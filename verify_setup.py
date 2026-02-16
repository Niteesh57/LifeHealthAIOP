import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

try:
    from app import main
    print("Successfully imported app.main")
    from app.core import config
    print("Successfully imported app.core.config")
    from app.models import user
    print("Successfully imported app.models.user")
    from app.schemas import user as user_schema
    print("Successfully imported app.schemas.user")
    from app.crud import user as user_crud
    print("Successfully imported app.crud.user")
    from app.api import api
    print("Successfully imported app.api.api")
    print("All imports successful!")
except Exception as e:
    print(f"Import failed: {e}")
    sys.exit(1)
