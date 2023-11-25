import requests
import os
import uuid
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from time import time


GIGACHAT_API_URL = "https://gigachat.devices.sberbank.ru/api/v1/"
GIGACHAT_TOKEN_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
load_dotenv()

GIGACHAT_TOKEN = os.getenv("auth_data")
AUTH_TOKEN = os.getenv("access_token")
TOKEN_EXPIRATION = os.getenv("expires_at")


def get_auth_token(auth_data: str):
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
    print(f"code: {response.status_code}")
    return response.json()


def ask_gigachat(auth_data: str, prompt: str):
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
    print(f"code: {response.status_code}")
    return response.json()


def get_models_gigachat(auth_data: str):
    headers = {
        "Authorization": f"Bearer {auth_data}",
    }
    response = requests.get(GIGACHAT_API_URL + "models", headers=headers, verify=False)
    print(f"code: {response.status_code}")
    return response.json()


app = Flask(__name__)


@app.route("/api/loan_rating", methods=["POST"])
def loan_rating():
    global TOKEN_EXPIRATION
    global AUTH_TOKEN
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

    prompt = (
        "Сделай выжимку по данной истории. Оцени, насколько хорошая или плохая финансовая ситуация у человека и какие факторы на нее влияют: "
        + history
    )

    #     В своей оценке используй следующие критерии:
    #
    # 1. Общий интегральный вывод по кредитной истории: хорошая, средняя, плохая.
    # 2. По характеру займов признаки:
    #     1. Часто использует микрозаймы.
    #     2. Погашение старых кредитов за счет других кредитов.
    # 3. Допускает прострочки.
    # 4. Есть текущая просрочка.
    #
    # Ты не должен оценить общую финансовую ситуацию человека, а только дать оценку того что есть, не надо включать в ответ фраза типа "Из предоставленных данных нельзя сделать однозначный ответ" и тп
    # # prompt = (
    # "На основе данной кредитной истории оцени насколько хорошая, плохая, очень хорошая, очень плохая, средняя финансовая ситуация у человека. Твой ответ должен содержать только одно слово или словосочетание, описывающее это. В своем ответе учитывай такие параметры как общее число кредитов, зарплату, даты выплаты кредитов и частоту их оформления, существуют ли просрочки кредитов "
    #     + history
    # )

    if time() < int(TOKEN_EXPIRATION):
        #     # TODO: token update in runtime
        print("getting new reg token")
        new_token = get_auth_token(GIGACHAT_TOKEN)
        AUTH_TOKEN = new_token.get("access_token")
        TOKEN_EXPIRATION = new_token.get("expires_at")

    answer = ask_gigachat(AUTH_TOKEN, prompt)
    print(answer)
    # TODO: make it prettier
    response = {"answer": answer.get("choices")[0].get("message").get("content")}
    return jsonify(response)


@app.route("/api/raw_prompt", methods=["POST"])
def post_example():
    global TOKEN_EXPIRATION
    global AUTH_TOKEN
    if request.method == "POST":
        json_data = request.get_json()
        prompt = json_data.get("prompt")
        if time() < int(TOKEN_EXPIRATION):
            #     # TODO: token update in runtime
            print("getting new reg token")
            new_token = get_auth_token(GIGACHAT_TOKEN)
            AUTH_TOKEN = new_token.get("access_token")
            TOKEN_EXPIRATION = new_token.get("expires_at")

        answer = ask_gigachat(AUTH_TOKEN, prompt)
        print(answer)
        # TODO: make it prettier
        response = {"answer": answer.get("choices")[0].get("message").get("content")}
        # response = {"answer": "None"}
        return jsonify(response)
    else:
        return jsonify({"status": "error", "message": "Invalid request method"})


if __name__ == "__main__":
    # if time() < int(TOKEN_EXPIRATION):
    #     #     # TODO: token update in runtime
    #     print("getting new reg token")
    #     new_token = get_auth_token(GIGACHAT_TOKEN)
    #     AUTH_TOKEN = new_token.get("access_token")
    #     TOKEN_EXPIRATION = new_token.get("expires_at")
    app.run(host='0.0.0.0', port=5000, debug=True)
