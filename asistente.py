#!/usr/bin/env python3
"""ProyectIA - asistente local con recuperacion aumentada (RAG).

Capacidad 9 - Asistente IA local.

Implementa el motor de un asistente de gestion de proyectos basado en
recuperacion aumentada (RAG): indexa una base de conocimiento local, recupera
los pasajes mas relevantes para una consulta mediante TF-IDF y similitud coseno,
y compone una respuesta extractiva citando las fuentes. El asistente real
anade un modelo de lenguaje local (Ollama) para redactar la respuesta; aqui se
conserva el motor de recuperacion para que la demo corra sin dependencias.

Uso:
    python asistente.py --demo
    python asistente.py --pregunta "como gestiono los riesgos"

Solo biblioteca estandar de Python 3.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULT_CORPUS = ROOT / "data" / "documentos.json"
DEFAULT_REPORT = ROOT / "report.md"
DEFAULT_JSON = ROOT / "data" / "consultas.json"

STOPWORDS = {
    "de", "la", "el", "los", "las", "un", "una", "y", "o", "que", "en", "con",
    "para", "por", "se", "del", "al", "es", "son", "como", "su", "sus", "lo",
    "mas", "muy", "sin", "sobre", "entre", "cada", "este", "esta",
}


def sin_acentos(texto: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", texto)
                   if unicodedata.category(c) != "Mn")


def tokenizar(texto: str) -> list[str]:
    """Minúsculas, sin acentos, sin signos, sin palabras vacías."""
    normalizado = sin_acentos(texto.lower())
    palabras = re.findall(r"[a-z0-9]+", normalizado)
    return [p for p in palabras if p not in STOPWORDS and len(p) > 1]


def construir_indice(documentos: list[dict]) -> dict:
    """Índice TF-IDF sobre los documentos (título + texto)."""
    n = len(documentos)
    tokens_por_doc = {
        d["id"]: tokenizar(d["titulo"] + " " + d["texto"]) for d in documentos
    }
    df: dict[str, int] = {}
    for tokens in tokens_por_doc.values():
        for termino in set(tokens):
            df[termino] = df.get(termino, 0) + 1

    idf = {t: math.log((n + 1) / (f + 1)) + 1 for t, f in df.items()}

    vectores: dict[str, dict[str, float]] = {}
    for doc_id, tokens in tokens_por_doc.items():
        tf: dict[str, int] = {}
        for t in tokens:
            tf[t] = tf.get(t, 0) + 1
        vector = {t: (c / len(tokens)) * idf[t] for t, c in tf.items()}
        norma = math.sqrt(sum(v * v for v in vector.values())) or 1.0
        vectores[doc_id] = {t: v / norma for t, v in vector.items()}
    return {"idf": idf, "vectores": vectores, "documentos": documentos}


def vector_consulta(consulta: str, indice: dict) -> dict[str, float]:
    idf = indice["idf"]
    tokens = tokenizar(consulta)
    tf: dict[str, int] = {}
    for t in tokens:
        tf[t] = tf.get(t, 0) + 1
    if not tokens:
        return {}
    vector = {t: (c / len(tokens)) * idf.get(t, math.log(len(indice["vectores"]) + 1) + 1)
              for t, c in tf.items()}
    norma = math.sqrt(sum(v * v for v in vector.values())) or 1.0
    return {t: v / norma for t, v in vector.items()}


def similitud_coseno(a: dict[str, float], b: dict[str, float]) -> float:
    comunes = set(a) & set(b)
    return sum(a[t] * b[t] for t in comunes)


def recuperar(consulta: str, indice: dict, top_k: int = 2) -> list[dict]:
    q = vector_consulta(consulta, indice)
    if not q:
        return []
    puntuados = [
        {"id": doc_id, "score": round(similitud_coseno(q, vec), 4)}
        for doc_id, vec in indice["vectores"].items()
    ]
    puntuados.sort(key=lambda r: r["score"], reverse=True)
    return [p for p in puntuados[:top_k] if p["score"] > 0]


def mejor_frase(consulta: str, texto: str) -> str:
    """Frase del texto con mayor solapamiento de términos con la consulta."""
    terminos = set(tokenizar(consulta))
    frases = re.split(r"(?<=[.;])\s+", texto)
    mejor, mejor_puntaje = "", -1
    for frase in frases:
        puntaje = len(terminos & set(tokenizar(frase)))
        if puntaje > mejor_puntaje:
            mejor, mejor_puntaje = frase.strip(), puntaje
    return mejor


def responder(consulta: str, indice: dict, top_k: int = 2) -> dict:
    docs = {d["id"]: d for d in indice["documentos"]}
    resultados = recuperar(consulta, indice, top_k)
    if not resultados:
        return {"pregunta": consulta, "respuesta": "Sin coincidencias en la base.",
                "fuentes": []}
    principal = docs[resultados[0]["id"]]
    return {
        "pregunta": consulta,
        "respuesta": mejor_frase(consulta, principal["texto"]),
        "fuentes": [{"id": r["id"], "titulo": docs[r["id"]]["titulo"],
                     "score": r["score"]} for r in resultados],
    }


def cargar_corpus(path: Path) -> list[dict]:
    documentos = json.loads(path.read_text(encoding="utf-8"))
    if not documentos:
        raise ValueError(f"corpus vacío en {path}")
    return documentos


def escribir_informe(respuestas: list[dict], out: Path) -> None:
    lineas = [
        "# ProyectIA — asistente de gestión de proyectos (demo)",
        "",
        "> Motor de recuperación aumentada (RAG) local sobre una base de conocimiento",
        "> de gestión de proyectos. Recupera pasajes por TF-IDF y responde citando",
        "> fuentes. El asistente real añade un LLM local (Ollama) para redactar.",
        "",
    ]
    for r in respuestas:
        lineas.append(f"## {r['pregunta']}")
        lineas.append("")
        lineas.append(f"**Respuesta:** {r['respuesta']}")
        lineas.append("")
        if r["fuentes"]:
            fuentes = ", ".join(f"{f['titulo']} ({f['score']})" for f in r["fuentes"])
            lineas.append(f"**Fuentes:** {fuentes}")
        else:
            lineas.append("**Fuentes:** —")
        lineas.append("")
    lineas += ["© 2026 Ronny L. Díaz López. Todos los derechos reservados.", ""]
    out.write_text("\n".join(lineas), encoding="utf-8")


PREGUNTAS_DEMO = [
    "¿Qué contiene la matriz de marco lógico?",
    "¿Cómo se estima el presupuesto y la financiación?",
    "¿Cómo se gestionan los riesgos del proyecto?",
]


def main() -> int:
    ap = argparse.ArgumentParser(description="Asistente RAG local (demo)")
    ap.add_argument("--demo", action="store_true", help="responde las preguntas de ejemplo")
    ap.add_argument("--pregunta", type=str, default=None)
    ap.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS)
    ap.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    ap.add_argument("--json", type=Path, default=DEFAULT_JSON)
    args = ap.parse_args()

    if not args.corpus.exists():
        print(f"[error] falta {args.corpus}")
        return 1

    indice = construir_indice(cargar_corpus(args.corpus))
    preguntas = [args.pregunta] if args.pregunta else PREGUNTAS_DEMO
    respuestas = [responder(p, indice) for p in preguntas]

    escribir_informe(respuestas, args.report)
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(respuestas, ensure_ascii=False, indent=2),
                         encoding="utf-8")
    for r in respuestas:
        fuente = r["fuentes"][0]["titulo"] if r["fuentes"] else "—"
        print(f"[ok] {r['pregunta']} -> {fuente}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
