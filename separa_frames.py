from PIL import Image
import os

# Carrega o GIF
gif_path = 'c:\\Users\\Igor\\Downloads\\pepino.gif'
gif = Image.open(gif_path)

# Cria uma pasta para armazenar os frames
output_folder = 'pepino'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Itera sobre os frames e salva cada um como imagem separada
frame_number = 0
try:
    while True:
        gif.seek(frame_number)  # Move para o frame atual
        frame = gif.copy()  # Copia o frame para manipulação
        frame.save(os.path.join(output_folder, f'frame_{frame_number}.png'))
        frame_number += 1
except EOFError:
    pass  # O loop termina quando não houver mais frames

print(f'{frame_number} frames extraídos com sucesso.')