import os

class Config:

    SECRET_KEY = "garage2026"

    SQLALCHEMY_DATABASE_URI = (
        "mysql+pymysql://admin:22112223@"
        "garage-nordikdb.ckjmwgqikrva.us-east-1.rds.amazonaws.com:3306/garage_nordik"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
