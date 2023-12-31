PROMPTS = {
    "loan_rating": "Сделай выжимку по данной истории. Оцени, насколько хорошая или плохая финансовая ситуация у человека и какие факторы на нее влияют: ",
    "vk_analitics_pt_1": """
    Ты получишь на вход структуру JSON в треугольных скобках. Эта структура описывает профиль человека в социальной сети. Структура обладает полями: о себе(about), карьера(career), контакты(contscts), город(city), страна(country), пол(sex), сайт(site), отношения(relation), родственники(relatives), университеты(universities), статус(status). Некоторые из полей могут быть пустыми. Твоя задача: Если есть что то в поле about, напиши: “О человеке: <about>” Если есть что то в поле mobile_phone, напиши: “Номер телефона: <mobile_phone>” Если есть что то в поле site, напиши: “Сайт: <site>” Если есть что то в поле universities, о каждом из объектов в массиве напиши: “Полученное образование: <faculty_name>, <name>” Если есть что то в поле career, о каждом из объектов в массиве напиши: “Опыт работы: …” Если в поле relatives есть объект с типом parent, о каждом из таких объектов в массиве напиши: “Есть родственник родитель с идентификатором : <id>” Ответ должен быть около 400 знаков. Сделай ответ для следующего профиля:
    <""",
    "vk_analitics_pt_2": """>
    Убедись, что в ответе есть вся информация из непустых полей структуры. Не придумывай информацию, используй ее только из структуры.
    """,
    "vk_friends": """
    Ты получишь на вход структуру JSON в треугольных скобках. Эта структура описывает друзей человека. Твоя задача: проанализируй данную информацию о друзьях. Есть ли у них образование, отношения, хорошая карьера. Если есть, то это положительный круг общения. Если же у большинства друзей нет образования, университетов, карьеры, отношений, то это отрицательный круг обзения. После анализа напиши ответ следующего формата, вставив в фигурные скобки свои результаты: \"Исходя из анализа друзей, круг общения скорее является {положитеьным/отрицательным}, потому что {результат анализа}.\" Ответ должен быть около 400 знаков. Сделай ответ для следующей структуры: <
    """,
}
