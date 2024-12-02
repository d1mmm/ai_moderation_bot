import logging
from datetime import datetime
from typing import List

import bcrypt
import jwt
import vertexai
from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from vertexai.generative_models import GenerativeModel
from google.oauth2 import service_account
from vertexai.generative_models._generative_models import SafetyRating
from vertexai.preview import generative_models

from ai_moderation_bot.config import KEY, JWT_SECRET, ALGORITHM
from ai_moderation_bot.data_models import UpdateSafetySetting
from ai_moderation_bot.db import get_session
from ai_moderation_bot.config import VERTEX_AI_ID, CREDENTIALS
from ai_moderation_bot.db_models import SafetySetting

try:
    credentials = service_account.Credentials.from_service_account_file(CREDENTIALS)
    vertexai.init(project=VERTEX_AI_ID, location="us-central1", credentials=credentials)
except FileNotFoundError as e:
    logging.error(f"Error: The credentials file was not found. {e}")
except ValueError as e:
    logging.error(f"Error: Invalid credentials or project ID. {e}")
except Exception as e:
    logging.error(f"An unexpected error occurred: {e}")

model = GenerativeModel(model_name="gemini-1.5-flash-001")

generation_config = generative_models.GenerationConfig(
        max_output_tokens=100, temperature=0.4, top_p=1, top_k=32
    )

safety_config = [
    generative_models.SafetySetting(
        category=generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        method=generative_models.SafetySetting.HarmBlockMethod.SEVERITY,
        threshold=generative_models.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    ),
    generative_models.SafetySetting(
        category=generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT,
        method=generative_models.SafetySetting.HarmBlockMethod.SEVERITY,
        threshold=generative_models.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    ),
    generative_models.SafetySetting(
        category=generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        method=generative_models.SafetySetting.HarmBlockMethod.SEVERITY,
        threshold=generative_models.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    ),
    generative_models.SafetySetting(
        category=generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        method=generative_models.SafetySetting.HarmBlockMethod.SEVERITY,
        threshold=generative_models.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    )
]


def add_safety_settings_to_db(safety_configs = None):
    if safety_configs is None:
        safety_configs = safety_config

    session = get_session()
    for setting in safety_configs:
        if isinstance(setting, generative_models.SafetySetting):
            dict_setting = setting.to_dict()
            safety_category = dict_setting["category"]
            safety_method = dict_setting["method"]
            safety_threshold = dict_setting["threshold"]

            if safety_category and safety_method and safety_threshold is None:
                continue

            existing_setting = session.query(SafetySetting).filter(SafetySetting.category == safety_category and
                                                                   SafetySetting.method == safety_method and
                                                                   SafetySetting.threshold == safety_threshold).first()

            if existing_setting:
                logging.info(f"Setting for category {safety_category} already exists. Skipping.")
                continue

            new_setting = SafetySetting(
                category=safety_category,
                method=safety_method,
                threshold=safety_threshold
            )
            session.add(new_setting)
        else:
            new_setting = SafetySetting(
                category=setting.category,
                method=setting.method,
                threshold=setting.threshold
            )
            session.add(new_setting)
    session.commit()
    session.close()


def update_safety_settings_in_db(updated_settings: List[UpdateSafetySetting]):
    add_safety_settings_to_db(updated_settings)
    get_latest_settings()


def get_latest_settings():
    session = get_session()
    subquery = session.query(
        SafetySetting.category,
        func.max(SafetySetting.id).label("max_id")
    ).group_by(SafetySetting.category).subquery()

    latest_settings = session.query(SafetySetting).join(
        subquery,
        (SafetySetting.category == subquery.c.category) & (SafetySetting.id == subquery.c.max_id)
    ).all()

    session.close()

    updated_safety_config = []
    for setting in latest_settings:
        updated_safety_config.append(
            generative_models.SafetySetting(
                category=generative_models.SafetySetting.HarmCategory[setting.category],
                method=generative_models.SafetySetting.HarmBlockMethod[setting.method],
                threshold=generative_models.SafetySetting.HarmBlockThreshold[setting.threshold]
            )
        )
    global safety_config
    safety_config = updated_safety_config


def generate_answer(content):
    return model.generate_content(
        [content],
        generation_config=generation_config,
        safety_settings=safety_config,
    )



def analyze_content(content):
    response = generate_answer(content)
    result = next((severity for severity in response.candidates[0].safety_ratings if severity.severity !=
                   SafetyRating.HarmSeverity.HARM_SEVERITY_NEGLIGIBLE), None)
    if result:
        return False
    return True


async def validate_jwt_token(headers):
    token = None
    if "Authorization" in headers:
        token = headers["Authorization"].split(" ")[0]
        if not token:
            raise HTTPException(status_code=400, detail="Authentication Token is missing!")

    try:
        data = jwt.decode(token, JWT_SECRET, ALGORITHM)
        current_email = data["email"]
        if current_email is None:
            raise HTTPException(status_code=401, detail="Invalid Authentication token!")

        expiration_datetime = datetime.fromtimestamp(data["exp"])
        current_time = datetime.now()
        if current_time > expiration_datetime:
            raise HTTPException(status_code=401, detail="Token has expired")

        return data
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token is invalid")


def encryption(password):
    return bcrypt.hashpw(password.encode(), KEY).decode()


def insert_into_db(obj):
    session = get_session()
    try:
        session.add(obj)
        session.commit()
        session.refresh(obj)
    except SQLAlchemyError as e:
        logging.error(f"Error occurred while executing SQL commands: {e}")
        session.rollback()
    finally:
        session.close()
