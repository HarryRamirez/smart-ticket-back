import requests
import re
import json
from django.conf import settings



def extract_clean_json(text):
    """
    Extrae JSON válido desde cualquier texto que contenga contenido extra.
    - Busca el primer '{' y el último '}'.
    - Intenta cargarlo con json.loads.
    - Si no es válido, lanza un error.
    """

    if not isinstance(text, str):
        raise ValueError("La respuesta de la IA no es texto.")

    # Buscar rango del JSON
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1 or start >= end:
        raise ValueError("No se encontró un JSON válido en la respuesta.")

    json_str = text[start:end+1]

    # Limpieza opcional de caracteres invisibles
    json_str = re.sub(r"[\x00-\x1F]+", "", json_str).strip()

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON inválido después de limpiar: {str(e)}")
    


def ticket_with_ollama(title, description):
    url = f"{settings.OLLAMA_URL}/api/generate"

    prompt = f"""
    Eres un asistente especializado en clasificación y análisis de tickets técnicos para sistemas de gestión. 
    Tu tarea es recibir dos campos obligatorios: "title" y "description", enviados por el usuario. 
    Con base únicamente en esta información, debes analizar el problema y completar los campos del formulario de creación de ticket, seleccionando las opciones correctas entre las listas permitidas.

    - Tu respuesta SIEMPRE debe ser exclusivamente un JSON válido. No agregues explicaciones, texto adicional ni comentarios.
    - Si no hay suficiente información, realiza la mejor inferencia posible sin inventar datos inexistentes.


    **LISTAS PERMITIDAS:**
    category: ["Backend", "Frontend", "Base de Datos", "Integraciones", "UI/UX", "Documentación", "General"]
    priority: ["Crítica", "Alta", "Media", "Baja", "Muy baja"]
    type: ["Bug", "Tarea", "Historia de usuario", "Mejora", "Épica"]

    **CAMPOS QUE DEBES GENERAR:**
    - "category"
    - "priority"
    - "type"
    - "summary"
    - "suggested_solution"

    **CRITERIOS DE CLASIFICACIÓN:**
    - "category": Escoge la categoría que mejor describa la naturaleza técnica del ticket.
    - "priority": Determina la urgencia según el impacto sugerido en el título y descripción.  
    - "type": Identifica bien si es Tarea o epica por el tiempo que lleva, según lo sugerido en el título y descripción.
    - "summary": Resume en máximo 2 o 3 líneas el problema descrito.
    - "suggested_solution": Propuesta clara, directa y razonable basada en la información dada.

    FORMATO DE RESPUESTA OBLIGATORIO:
    Devuelve únicamente un JSON con esta estructura:

    "category": "",
    "priority": "",
    "type": "",
    "summary": "",
    "suggested_solution": ""


    Ahora procesa la siguiente información del usuario:
    Título: "{title}"
    Descripción: "{description}"

    La repuesta es en formato JSON valido,  no le agrege nada de mas al formato.
    """

    body = {
        "model": settings.OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(url, json=body, timeout=60)
    response.raise_for_status()

    raw_text = response.json().get("response")  
    # Limpieza del JSON
    cleaned = extract_clean_json(raw_text)
    

    return cleaned