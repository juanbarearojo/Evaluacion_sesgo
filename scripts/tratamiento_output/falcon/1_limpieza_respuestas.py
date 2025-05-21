import pandas as pd
import re
import unicodedata

# Rutas de los archivos
respuestas_path = 'data/falcon/raw/respuesta_falcon_5.csv'  
combinaciones_pacientes_path = 'data/pacientes/combinaciones_pacientes.csv'

# Leer el archivo con preguntas y respuestas
respuestas_df = pd.read_csv(respuestas_path)

# Leer el archivo con combinaciones de pacientes
combinaciones_pacientes_df = pd.read_csv(combinaciones_pacientes_path)

def remove_accents(input_str):
    """
    Elimina los acentos y caracteres especiales de una cadena.
    """
    if not isinstance(input_str, str):
        return input_str
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])

# Función de limpieza ajustada
def limpiar_respuesta(respuesta):
    """
    Asigna 'Paciente X' o 'Paciente Y' basado en cuál aparece primero en la respuesta.
    Asigna 'null' si ninguno se encuentra.
    """
    if isinstance(respuesta, str):
        # Convertir a minúsculas y eliminar espacios adicionales
        respuesta_clean = respuesta.strip().lower()
        
        # Eliminar puntuación
        respuesta_clean = re.sub(r'[^\w\s]', '', respuesta_clean)
        
        # Eliminar acentos y caracteres especiales
        respuesta_clean = remove_accents(respuesta_clean)
        
        # Buscar posiciones de 'paciente x' y 'paciente y'
        pos_x = respuesta_clean.find('paciente x')
        pos_y = respuesta_clean.find('paciente y')
        
        # Determinar cuál aparece primero
        if pos_x != -1 and pos_y != -1:
            if pos_x < pos_y:
                return "Paciente X"
            elif pos_y < pos_x:
                return "Paciente Y"
            else:
                # En el raro caso de que ambos empiecen en la misma posición
                return "null"
        elif pos_x != -1:
            return "Paciente X"
        elif pos_y != -1:
            return "Paciente Y"
        else:
            return "null"
    
    # Si no es una cadena, asignar 'null'
    return "null"

# Aplicar la función de limpieza a la columna 'Respuesta'
respuestas_df['Paciente_elegido'] = respuestas_df['Respuesta'].apply(limpiar_respuesta)

# Verificar las asignaciones
print("Conteo de asignaciones:")
print(respuestas_df['Paciente_elegido'].value_counts())

# Filtrar y revisar filas que fueron asignadas a "null"
filas_null = respuestas_df[respuestas_df['Paciente_elegido'] == 'null']
print("\nEjemplos de respuestas asignadas a 'null':")
print(filas_null['Respuesta'].head(10))

# Combinar con el DataFrame de combinaciones de pacientes
# Asegúrate de que los índices de ambos DataFrames estén alineados correctamente.
# Si existe una columna clave (por ejemplo, 'ID'), es mejor usarla para el merge.
# Aquí se asume que los índices están alineados.

resultado_df = pd.merge(
    combinaciones_pacientes_df, 
    respuestas_df[['Paciente_elegido']], 
    how='left', 
    left_index=True, 
    right_index=True
)

# Guardar el resultado final
resultado_path = 'data/falcon/procesed/respuesta_falcon_5.csv'
resultado_df.to_csv(resultado_path, index=False)

print(f"\nArchivo procesado guardado en: {resultado_path}")
