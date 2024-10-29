# AI Moderation Bot

**This project is a simple Telegram bot for moderating obscene language in chats.**

# Features

* User Registration: Allows users to register.
* User Login: Allows users to log in.
* Real-Time Content Moderation: Automatically filters and moderates obscene or inappropriate messages in real time within Telegram chats.
* Policy Management Interface: User-friendly interface for setting and updating content filtering policies.

# Technologies

* Python 3.8
* FastAPI
* Pydantic
* PostgreSQL
* SQLAlchemy
* Vertex AI

# Obtaining Google Cloud Credentials

**To enable AI moderation and automatic responses, you need to obtain credentials from Google Cloud:**

* Go to the https://console.cloud.google.com/
* Select your project or create a new one.
* Go to the APIs & Services. Enabled APIs & services
* Enable Vertex AI API
* Navigate to the "IAM & Admin" section and then "Service Accounts".
* Click on "Create Service Account".
* Fill in the required details and click "Create".
* Assign the necessary roles to the service account and click "Continue".
* Download the JSON key file and save it to your project directory as gcloud_credentials.json.

# Guide to obtain a token for Telegram bot:
1. Open Telegram and search for the user @BotFather (this is the official bot for managing Telegram bots).
2. Start a chat with @BotFather and type the command /newbot to create a new bot.
3. Follow the instructions provided by BotFather:
   * You'll be asked to name your bot (e.g., "MyModerationBot"). 
   * Then, choose a username for the bot, ending with "bot" (e.g., "MyModerationBot_bot").
4. Once you complete these steps, BotFather will send you a unique token for your bot.


# Setup

**Clone the Repository**
    git clone git@github.com:d1mmm/ai_moderation_bot.git
     
**Add environment variables**

    export CREDENTIALS_AI=path to gcloud_credentials.json.
    export VERTEX_AI_ID=project id
    export DATABASE_URL=postgresql://user:password@db:5432/ai_moderation
    export TELEGRAM_TOKEN=token
   
1. **Set up a virtual environment**:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

2. **Install dependencies**:
    Ensure you have `pip` installed, then run:
    ```bash
    pip install -r requirements.txt
    python3.8 setup.py sdist bdist_wheel 
    pip install dist/ai_moderation_bot-<version>-py3-none-any.whl
    ```
   
3. **Set up the database**:
    ```bash
    psql -U <postgres> <password>
    CREATE DATABASE ai_moderation;
    ```

4. **Run the applications**:  
    Use the following command to start the bot:
    ```bash
   python3.8 -m ai_moderation_bot.main
    ```
   Use the following command to start the api:
    ```bash
   python3.8 -m ai_moderation_bot.api
    ```
