def test_crear_pregunta_sin_question_falla(client):
    """Falta campo obligatorio 'question'"""
    response = client.post("/questions", json={"answer": "Solo respuesta"})
    assert response.status_code == 422


def test_crear_pregunta_sin_answer_falla(client):
    """Falta campo obligatorio 'answer'"""
    response = client.post("/questions", json={"question": "¿Sin respuesta?"})
    assert response.status_code == 422


def test_crear_pregunta_tipo_incorrecto(client):
    """category debe ser string, no número"""
    response = client.post("/questions", json={
        "question": "¿Test?",
        "answer": "Sí",
        "category": 123,
    })
    assert response.status_code == 422


def test_obtener_pregunta_id_no_numerico(client):
    """El path param question_id debe ser int"""
    response = client.get("/questions/abc")
    assert response.status_code == 422


def test_obtener_pregunta_inexistente_404(client):
    """Válida sintácticamente, pero no existe -> 404, no 422"""
    response = client.get("/questions/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Pregunta no encontrada"


def test_categoria_sin_resultados_404(client):
    response = client.get("/questions/category/inexistente")
    assert response.status_code == 404


def test_eliminar_pregunta_inexistente_404(client):
    response = client.delete("/questions/99999")
    assert response.status_code == 404


def test_crear_pregunta_campos_opcionales_ausentes(client):
    """category y source son opcionales: debe aceptar sin ellos"""
    response = client.post("/questions", json={
        "question": "¿Solo obligatorios?",
        "answer": "Sí",
    })
    assert response.status_code == 201
    assert response.json()["category"] is None