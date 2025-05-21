import pandas as pd
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
from datasets import Dataset

# Configuración de rutas
prompts_file_path = r"C:\Users\Usuario\Desktop\PROYECTOS\Paciente_Y_Modelos\data\pacientes\prompt_usado.txt"
csv_output_path   = r"C:\Users\Usuario\Desktop\PROYECTOS\Paciente_Y_Modelos\data\falcon\raw\respuesta_falcon_5.csv"

# Leer el archivo de prompts
with open(prompts_file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Crear la lista de entradas sin "context"
qa_pairs = []
for line in lines:
    line = line.strip()
    qa_pairs.append({
        'question': line
    })

# Crear el dataset de Hugging Face
dataset = Dataset.from_pandas(pd.DataFrame(qa_pairs))

# Modelo a usar
model_id = "tiiuae/Falcon3-1B-Instruct"

# Cargar el tokenizer y el modelo
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id)

# Ajuste del token de padding
if tokenizer.eos_token_id is None:
    # Si no hay eos_token, usa bos_token o un token arbitrario como pad
    tokenizer.pad_token_id = tokenizer.bos_token_id if tokenizer.bos_token_id is not None else 0
    model.config.pad_token_id = tokenizer.pad_token_id
else:
    # Si existe eos_token, lo usamos como pad
    tokenizer.pad_token_id = tokenizer.eos_token_id
    model.config.pad_token_id = tokenizer.pad_token_id

# Crear el pipeline de generación
qa_pipeline = pipeline(
    'text-generation',
    model=model,
    tokenizer=tokenizer,
    device=0  # 0 para GPU, -1 para CPU
)

# Definir la función para mapear sobre el dataset
def process_batch(batch):
    respuestas = []
    for question in batch['question']:
        prompt = f"{question}\nRespuesta:"

        # Generar respuesta
        output = qa_pipeline(
            prompt,
            max_new_tokens=20,     
            temperature=1.0,        # mayor variabilidad
            pad_token_id=tokenizer.pad_token_id
        )

        # Extraer solo la parte tras "Respuesta:"
        respuesta = output[0]['generated_text'].split("Respuesta:")[-1].strip()
        respuestas.append(respuesta)

    batch['Respuesta'] = respuestas
    return batch

# Aplicar la generación de respuestas al dataset en lotes
dataset = dataset.map(process_batch, batched=True, batch_size=8)

# Guardar las preguntas y respuestas en un archivo CSV
df_answers = dataset.to_pandas()
df_answers.to_csv(csv_output_path, index=False, encoding='utf-8')

print(f"\nSe han guardado las preguntas y respuestas en: {csv_output_path}")
