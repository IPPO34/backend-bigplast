import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = "postgresql://base_de_datos_bigplast_user:ltFDyaG6SNDBSuSqMCzNTjmavSjjVW5P@dpg-d3cpm1j7mgec73ao7jtg-a.oregon-postgres.render.com/base_de_datos_bigplast"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET = os.getenv("JWT_SECRET", "change_me")
    JWT_EXP_DAYS = int(os.getenv("JWT_EXP_DAYS", "7"))
