from typing import Any
import requests
import os
import uuid
from dotenv import load_dotenv
from flask import Flask, Request, request, jsonify
from time import time
from prompts import PROMPTS


APP_PORT = 5000
APP_HOST = "0.0.0.0"

GIGACHAT_API_URL = "https://gigachat.devices.sberbank.ru/api/v1/"
GIGACHAT_TOKEN_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

load_dotenv()

history = """
    Работа:
    1. Учитель, зарплата 20 т. р.
    2. Самозанятый, в среднем месячный доход 20 т. р.
    
    Кредиты:
    1. Кредит на автомобиль:
     - Сумма: 1 000 000 рублей
     - Срок: 5 лет
     - Процентная ставка: 15%
     - Дата оформления: 01.01.2015
     - Дата погашения: 31.12.2020
    
    2. Кредит на ремонт жилья:
     - Сумма: 500 000 рублей
     - Срок: 3 года
     — Процентная ставка: 12%
     — Дата оформления: 01.01.2018
     — Дата погашения: 31.12.2021
    
    3. Кредит на образование:
     — Сумма: 600 000 рублей
     — Срок: 4 года
     — Процентная ставка: 10%
     — Дата оформления: 01.01.2019
     — Дата погашения: 31.12.2023
    
    4. Кредит на путешествие:
     — Сумма: 300 000 рублей
     — Срок: 2 года
     — Процентная ставка: 9%
     — Дата оформления: 01.01.2020
     — Дата погашения: 31.12.2022
    
    Долги:
    1. Задолженность по кредиту на автомобиль:
     — Сумма: 150 000 рублей
     — Дата последнего платежа: 31.12.2019
    
    2. Задолженность по кредиту на ремонт жилья:
     — Сумма: 100 000 рублей
     — Дата последнего платежа: 31.12.2020
    
    3. Задолженность по кредиту на образование:
     — Сумма: 50 000 рублей
     — Дата последнего платежа: 31.12.2021
    
    4. Задолженность по кредиту на путешествие:
     — Сумма: 20 000 рублей
     — Дата последнего платежа: 31.12.2022
    """

app = Flask(__name__)

GIGACHAT_TOKEN = os.getenv("auth_data")

if GIGACHAT_TOKEN is None:
    print("Missing auth_data env variable")
    exit()

AUTH_TOKEN = os.getenv("access_token")
if AUTH_TOKEN is None:
    print("Missing access_token env variable")
    exit()

TOKEN_EXPIRATION = os.getenv("expires_at")
if TOKEN_EXPIRATION is None:
    print("Missing expires_at env variable, ignoring")
    TOKEN_EXPIRATION = str(time())

ACCESS_INTERNAL_TOKEN = os.getenv("access_token_internal")
if ACCESS_INTERNAL_TOKEN is None:
    print("No internal access token provided, some features may be disabled")


def auth_internal(request: Request):
    if request.headers.get("Authorization", "nope") != ACCESS_INTERNAL_TOKEN:
        return False
    return True


def get_auth_token(auth_data):
    app.logger.info("Getting auth token")
    headers = {
        "Authorization": f"Bearer {auth_data}",
        "RqUID": str(uuid.uuid4()),
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data_urlencode = "scope=GIGACHAT_API_PERS"
    response = requests.post(
        GIGACHAT_TOKEN_URL, headers=headers, data=data_urlencode, verify=False
    )
    # TODO: save uuid and data of the request to db
    app.logger.info(f"code: {response.status_code}")
    return response.json()


def update_auth_token(auth_data):
    response = get_auth_token(auth_data)
    return (response.get("access_token"), response.get("expires_at"))


def ask_gigachat(auth_data: str, prompt: str):
    app.logger.info(f"Asking gigachat {prompt}")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth_data}",
    }

    data = {
        "model": "GigaChat:latest",
        "messages": [{"role": "user", "content": prompt}],
    }

    response = requests.post(
        GIGACHAT_API_URL + "chat/completions", headers=headers, json=data, verify=False
    )
    app.logger.info(f"code: {response.status_code}")
    return response.json()


def get_models_gigachat(auth_data: str):
    headers = {
        "Authorization": f"Bearer {auth_data}",
    }
    response = requests.get(GIGACHAT_API_URL + "models", headers=headers, verify=False)
    app.logger.info(f"code: {response.status_code}")
    return response.json()


@app.route("/api/loan_rating", methods=["POST"])
def loan_rating():
    global TOKEN_EXPIRATION
    global AUTH_TOKEN

    # TODO: get history from external service
    global history

    prompt = PROMPTS["loan_rating"] + history

    if time() < int(TOKEN_EXPIRATION):
        (AUTH_TOKEN, TOKEN_EXPIRATION) = update_auth_token(GIGACHAT_TOKEN)

    answer = ask_gigachat(AUTH_TOKEN, prompt)
    app.logger.info(answer)
    # TODO: make it prettier
    response = {"answer": answer.get("choices")[0].get("message").get("content")}
    return jsonify(response)


@app.route("/api/vk_analisis", methods=["POST"])
def vk_analisis():
    global TOKEN_EXPIRATION
    global AUTH_TOKEN

    profile_info = request.get_json().get("profile_info")
    prompt = PROMPTS["vk_analitics_pt_1"] + profile_info + PROMPTS["vk_analitics_pt_2"]

    if time() < int(TOKEN_EXPIRATION):
        (AUTH_TOKEN, TOKEN_EXPIRATION) = update_auth_token(GIGACHAT_TOKEN)

    answer = ask_gigachat(AUTH_TOKEN, prompt)
    app.logger.info(answer)

    response = {"answer": answer.get("choices")[0].get("message").get("content")}
    return jsonify(response)


@app.route("/api/vk_friends", methods=["POST"])
def vk_friends():
    global TOKEN_EXPIRATION
    global AUTH_TOKEN

    friends_info = request.get_json().get("friends_info")
    prompt = PROMPTS["vk_friends"] + friends_info + ">"

    if time() < int(TOKEN_EXPIRATION):
        (AUTH_TOKEN, TOKEN_EXPIRATION) = update_auth_token(GIGACHAT_TOKEN)

    answer = ask_gigachat(AUTH_TOKEN, prompt)
    app.logger.info(answer)

    response = {"answer": answer.get("choices")[0].get("message").get("content")}
    return jsonify(response)


@app.route("/api/raw_prompt", methods=["POST"])
def raw_prompt():
    global TOKEN_EXPIRATION
    global AUTH_TOKEN

    json_data = request.get_json()
    prompt = json_data.get("prompt")
    if time() < int(TOKEN_EXPIRATION):
        (AUTH_TOKEN, TOKEN_EXPIRATION) = update_auth_token(GIGACHAT_TOKEN)

    answer = ask_gigachat(AUTH_TOKEN, prompt)
    app.logger.info(answer)
    # TODO: make it prettier
    response = {"answer": answer.get("choices")[0].get("message").get("content")}
    return jsonify(response)


@app.route("/api/health_check", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "authenticated": auth_internal(request)})


if __name__ == "__main__":
    app.run(host=APP_HOST, port=APP_PORT, debug=True)
