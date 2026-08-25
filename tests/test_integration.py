def test_crear_y_obtener_pregunta(client):
    response_post = client.post("/questions", json={
        "question": "¿Qué es FastAPI?",
        "answer": "Un framework web",
        "category": "tech",
    })
    assert response_post.status_code == 201
    question_id = response_post.json()["id"]

    response_get = client.get(f"/questions/{question_id}")
    assert response_get.status_code == 200
    assert response_get.json()["answer"] == "Un framework web"


def test_eliminar_pregunta_integracion(client):
    post = client.post("/questions", json={"question": "¿Borrar esto?", "answer": "sí"})
    question_id = post.json()["id"]

    delete_response = client.delete(f"/questions/{question_id}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/questions/{question_id}")
    assert get_response.status_code == 404


def test_listar_preguntas_con_paginacion(client, db_session):
    from app.models import Question
    for i in range(15):
        db_session.add(Question(question=f"Pregunta {i}", answer=f"Respuesta {i}"))
    db_session.commit()

    response = client.get("/questions?skip=0&limit=5")
    assert response.status_code == 200
    assert len(response.json()) == 5


def test_filtrar_por_categoria(client, sample_question):
    response = client.get("/questions/category/geography")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["category"] == "geography"


def test_stats_integracion(client, db_session):
    from app.models import Question
    db_session.add(Question(question="Q1", answer="A1", category="tech"))
    db_session.add(Question(question="Q2", answer="A2", category="tech"))
    db_session.add(Question(question="Q3", answer="A3", category="geography"))
    db_session.commit()

    response = client.get("/stats")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 3
    assert body["by_category"]["tech"] == 2
    assert body["by_category"]["geography"] == 1