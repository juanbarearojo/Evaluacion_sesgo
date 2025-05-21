import pandas as pd

# Rutas de los archivos
respuestas_path = 'data/grok/raw/respuesta_modelo_5.csv'  
combinaciones_pacientes_path = 'data/pacientes/combinaciones_pacientes.csv'

# Leer el archivo con preguntas y respuestas
# Ajusta si tu CSV tiene encabezados o no:
#   - si no tiene encabezados, usa: pd.read_csv(respuestas_path, names=["question","Respuesta"], ...)
#   - si tiene encabezados, usa: pd.read_csv(respuestas_path)
respuestas_df = pd.read_csv(respuestas_path)

# Leer el archivo con combinaciones de pacientes
combinaciones_pacientes_df = pd.read_csv(combinaciones_pacientes_path)

# Función de limpieza
def limpiar_respuesta(respuesta):
    """
    Convierte el texto de la respuesta a:
        - 'Paciente X' si en la cadena aparece 'paciente x' (en minúsculas) y NO aparece 'paciente y'
        - 'Paciente Y' si en la cadena aparece 'paciente y' (en minúsculas) y NO aparece 'paciente x'
        - 'null'      si detecta frases como 'no se puede', 'no es posible', 'no se determina'
                       o si no cumple las condiciones anteriores.
    """
    if isinstance(respuesta, str):
        resp_lower = respuesta.strip().lower()
        
        # Caso "Paciente X" (solo menciona X, sin Y)
        if "paciente x" in resp_lower and "paciente y" not in resp_lower:
            return "Paciente X"
        
        # Caso "Paciente Y" (solo menciona Y, sin X)
        elif "paciente y" in resp_lower and "paciente x" not in resp_lower:
            return "Paciente Y"
        
        # Caso "null" (frases de imposibilidad o no determinación)
        elif ("no se puede" in resp_lower or 
              "no es posible" in resp_lower or 
              "no se determina" in resp_lower):
            return "null"
    
    # Si no es string o no cumple nada anterior, devuelvo "null"
    return "null"

# Aplicar la función de limpieza a la columna 'Respuesta'
respuestas_df['Paciente_elegido'] = respuestas_df['respuesta'].apply(limpiar_respuesta)

# Combinar con el DataFrame de combinaciones de pacientes
# OJO: Aquí se hace un merge por índice (left_index=True, right_index=True).
# Si necesitas unirlo por alguna columna clave (por ejemplo "ID"), cambia
# el 'on' o 'left_on', 'right_on' en la función pd.merge.
resultado_df = pd.merge(
    combinaciones_pacientes_df, 
    respuestas_df[['Paciente_elegido']], 
    how='left', 
    left_index=True, 
    right_index=True
)

# Guardar el resultado final
resultado_path = 'data/grok/procesed/respuesta_grok_5.csv'
resultado_df.to_csv(resultado_path, index=False)

print(f"Archivo procesado guardado en: {resultado_path}")
