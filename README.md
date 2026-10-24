# Capa 9 — Asistente IA local (RAG)

[![CI](https://github.com/lazarolpro/proyectia-asistente/actions/workflows/ci.yml/badge.svg)](https://github.com/lazarolpro/proyectia-asistente/actions/workflows/ci.yml)
[`lazarolpro/proyectia-asistente`](https://github.com/lazarolpro/proyectia-asistente) · parte del [portafolio de 9 capacidades](https://github.com/lazarolpro/portafolio)

> © 2026 Ronny L. Díaz López. **Todos los derechos reservados.** Prohibida su
> venta o uso comercial sin autorización escrita. Ver [`LICENSE`](LICENSE).

**Capacidad demostrada:** construir un asistente que responde sobre una base de
conocimiento propia mediante **recuperación aumentada (RAG)**, sin depender de
APIs externas ni de la nube: recupera los pasajes relevantes y cita las fuentes.

## Problema real

Buscar en manuales, procedimientos o documentación de proyecto a mano consume
tiempo y se pierde el contexto. Un asistente RAG local responde con la información
correcta, **citando de dónde sale**, y funciona 100 % offline.

## Qué hace

- Indexa una base de conocimiento local (JSON) con **TF-IDF**.
- Recupera los pasajes más relevantes por **similitud coseno**.
- Compone una **respuesta extractiva** citando las fuentes y su puntuación.
- Funciona sin conexión y sin tokens de pago.

> Alcance honesto: esta demo implementa el **motor de recuperación** (TF-IDF +
> coseno) con solo la biblioteca estándar. El asistente ProyectIA real añade un
> modelo de lenguaje local (Ollama) para redactar la respuesta y una base
> vectorial; aquí se conserva el mecanismo de RAG para que sea reproducible.

## Cómo ejecutar

```bash
python asistente.py --demo                          # responde 3 preguntas -> report.md + data/consultas.json
python asistente.py --pregunta "como gestiono los riesgos"
python -m pytest -q
```

## Evidencia que produce

- [`report.md`](report.md) — preguntas, respuestas y fuentes recuperadas.
- `data/documentos.json` — base de conocimiento de entrada.
- `data/consultas.json` — respuestas reproducibles con su puntuación.
- Pruebas de recuperación (acierta el documento correcto) en verde.

## Stack

Python 3 (solo biblioteca estándar: `re`, `math`, `json`, `unicodedata`). Sin
dependencias.

## Por qué le importa a la empresa

Cubre **IA aplicada y automatización del conocimiento**: consultar procedimientos
internos por lenguaje natural, con trazabilidad de la fuente y sin exponer datos
a terceros.

**En mantenimiento:** consultar manuales, fichas técnicas y procedimientos desde
el móvil, en el sitio, sin conexión.
