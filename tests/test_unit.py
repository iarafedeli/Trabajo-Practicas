from app.models import Question


def test_crear_instancia_question():
    """Unitario puro: no toca BD ni HTTP"""
    q = Question(question="¿Test?", answer="Sí", category="test")
    assert q.question == "¿Test?"
    assert q.answer == "Sí"
    assert q.category == "test"


def test_question_category_es_opcional():
    q = Question(question="¿Test?", answer="Sí")
    assert q.category is None
    assert q.source is None


def test_guardar_y_recuperar_question(db_session):
    """Unitario de persistencia, aislado del endpoint"""
    q = Question(question="¿Capital de Italia?", answer="Roma", category="geography")
    db_session.add(q)
    db_session.commit()
    db_session.refresh(q)

    assert q.id is not None
    recuperada = db_session.query(Question).filter(Question.id == q.id).first()
    assert recuperada.answer == "Roma"