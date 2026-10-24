import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

MODULE = ROOT / "asistente.py"
spec = importlib.util.spec_from_file_location("asistente", MODULE)
asistente = importlib.util.module_from_spec(spec)
sys.modules["asistente"] = asistente
spec.loader.exec_module(asistente)

construir_indice = asistente.construir_indice
responder = asistente.responder
similitud_coseno = asistente.similitud_coseno
tokenizar = asistente.tokenizar
vector_consulta = asistente.vector_consulta


def _indice():
    return construir_indice(json.loads(
        (ROOT / "data" / "documentos.json").read_text(encoding="utf-8")))


def test_tokenizar_quita_acentos_y_vacias():
    assert tokenizar("La Matriz de Marco Lógico") == ["matriz", "marco", "logico"]


def test_similitud_identica_es_uno():
    v = {"a": 0.6, "b": 0.8}
    assert abs(similitud_coseno(v, v) - 1.0) < 1e-9


def test_recupera_documento_correcto():
    indice = _indice()
    r = responder("¿Qué contiene la matriz de marco lógico?", indice)
    assert r["fuentes"][0]["id"] == "marco-logico"


def test_recupera_presupuesto():
    indice = _indice()
    r = responder("¿Cómo se estima el presupuesto y la financiación?", indice)
    assert r["fuentes"][0]["id"] == "presupuesto"


def test_recupera_riesgos():
    indice = _indice()
    r = responder("¿Cómo se gestionan los riesgos del proyecto?", indice)
    assert r["fuentes"][0]["id"] == "riesgos"


def test_consulta_sin_coincidencias():
    indice = _indice()
    r = responder("xyzzy plugh", indice)
    assert r["fuentes"] == []
    assert "Sin coincidencias" in r["respuesta"]


def test_vector_consulta_vacia():
    indice = _indice()
    assert vector_consulta("de la el", indice) == {}


def test_demo_responde_y_serializa():
    indice = _indice()
    respuestas = [responder(p, indice) for p in
                  ("¿Qué es el árbol de problemas?", "¿Cómo mido el avance?")]
    assert all(r["fuentes"] for r in respuestas)
    assert json.dumps(respuestas, ensure_ascii=False)
