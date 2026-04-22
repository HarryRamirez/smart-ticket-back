from openai import OpenAI
from django.conf import settings
import re
import json

client = OpenAI(
    api_key=settings.GROK_API_KEY,
    base_url=settings.GROK_BASE_URL
)


def extract_clean_json(text): 
    """ Extrae JSON válido desde cualquier texto que contenga contenido extra. 
    - Busca el primer '{' y el último '}'. 
    - Intenta cargarlo con json.loads. 
    - Si no es válido, lanza un error. """ 
    
    if not isinstance(text, str): 
        raise ValueError("La respuesta de la IA no es texto.") # Buscar rango del JSON 
    
    start = text.find("{") 
    end = text.rfind("}") 
    
    if start == -1 or end == -1 or start >= end: 
        raise ValueError("No se encontró un JSON válido en la respuesta.") 
    
    json_str = text[start:end+1] # Limpieza opcional de caracteres invisibles 
    json_str = re.sub(r"[\x00-\x1F]+", "", json_str).strip() 
    
    try: return json.loads(json_str) 
    except json.JSONDecodeError as e: 
        raise ValueError(f"JSON inválido después de limpiar: {str(e)}")




def ticket_with_llm(title: str, description: str) -> dict:
    prompt = f"""
Eres un asistente especializado en clasificación y análisis de tickets técnicos.

Responde EXCLUSIVAMENTE en JSON válido.

Listas permitidas:
category: ["Backend", "Frontend", "Base de Datos", "Integraciones", "UI/UX", "Documentación", "General"]
priority: ["Crítica", "Alta", "Media", "Baja", "Muy baja"]
type: ["Bug", "Tarea", "Historia de usuario", "Mejora", "Épica"]

Campos requeridos:
- category
- priority
- type
- summary
- suggested_solution

Título: "{title}"
Descripción: "{description}"
"""

    response = client.chat.completions.create(
        model=settings.GROK_MODEL,
        messages=[
            {"role": "system", "content": "Responde solo JSON válido."},
            {"role": "user", "content": prompt},
        ],
        temperature=0
    )

    content = response.choices[0].message.content

    try:
        return extract_clean_json(content)
    except json.JSONDecodeError:
        raise ValueError("La IA no devolvió un JSON válido")
