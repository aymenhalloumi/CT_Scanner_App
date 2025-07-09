from dotenv import load_dotenv
import os

load_dotenv()  # This loads the .env file

print("SECRET_KEY:", os.environ.get("SECRET_KEY"))
print("OPENAI_API_KEY:", os.environ.get("OPENAI_API_KEY"))