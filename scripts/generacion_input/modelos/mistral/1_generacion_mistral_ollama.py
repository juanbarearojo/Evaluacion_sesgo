import re
import subprocess
import pandas as pd
from datasets import Dataset

# ----------------------------------------------------
# Función para llamar a ollama usando el modelo Mistral
# (Usando "ollama run" en lugar de "ollama generate")
# ----------------------------------------------------
def call_mistral(question, context):
    """
    Llama a ollama para generar la respuesta usando el modelo Mistral,
    ahora empleando el subcomando 'run' en vez de 'generate'.
    """
    # Construimos el prompt para Mistral
    prompt = f"""Pregunta: {question}
    Contexto: {context}
    Respuesta:"""

    # Comando para invocar a ollama (cambiamos 'generate' por 'run' 
    # y quitamos las opciones -m, --prompt).
    command = [
        r"C:\Users\Usuario\AppData\Local\Programs\ollama\ollama.exe",
        "run",          # subcomando 'run'
        "mistral",      # nombre del modelo
        prompt          # prompt directamente como argumento
    ]

    # Ejecutamos el comando con subprocess
    result = subprocess.run(command, capture_output=True, text=True)

    # El texto generado por Mistral se encontrará en result.stdout
    return result.stdout.strip()


# ----------------------------------------------------
# Lógica principal
# ---------------------------------------------------- 
# Configuración de rutas
prompts_file_path = r"C:\Users\Usuario\Desktop\PROYECTOS\Paciente_Y_Modelos\data\pacientes\prompt_usado.txt"
csv_output_path   = r"C:\Users\Usuario\Desktop\PROYECTOS\Paciente_Y_Modelos\data\mistral\raw\respuesta_mistral_5.csv"

# 1. Leer el archivo de prompts
with open(prompts_file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()


# 2. Procesar todas las líneas y extraer preguntas, contextos
qa_pairs = []
for line in lines:
    line = line.strip()
    parts = re.split('Opciones de pacientes:', line)
    if len(parts) == 2:
        question_part = parts[0].strip()
        context_part_and_more = parts[1].strip()
        context_and_response_expected = re.split('Respuesta esperada:', context_part_and_more)
        context_part = (
            context_and_response_expected[0].strip() 
            if len(context_and_response_expected) == 2 
            else context_part_and_more
        )
    else:
        question_part = line
        context_part = ''
    qa_pairs.append({'question': question_part, 'context': context_part})

# 3. Crear el dataset de Hugging Face
dataset = Dataset.from_pandas(pd.DataFrame(qa_pairs))

# 4. Definir la función que mapea sobre el dataset y llama a Mistral
def process_batch(batch):
    respuestas = []
    for question, context in zip(batch['question'], batch['context']):
        respuesta = call_mistral(question, context)
        respuestas.append(respuesta)
    batch['Respuesta'] = respuestas
    return batch

# 5. Aplicar la función al dataset en lotes
dataset = dataset.map(process_batch, batched=True, batch_size=1)

# 6. Guardar las preguntas, contextos y respuestas en un archivo CSV
df_answers = dataset.to_pandas()
df_answers.to_csv(csv_output_path, index=False, encoding='utf-8')

print(f"\nPreguntas, contextos y respuestas guardadas en {csv_output_path}")
