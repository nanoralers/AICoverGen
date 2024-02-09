import json
import os
import shutil
import urllib.request
import zipfile
from argparse import ArgumentParser

import gradio as gr
from main import song_cover_pipeline

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

mdxnet_models_dir = os.path.join(BASE_DIR, 'mdxnet_models')
rvc_models_dir = os.path.join(BASE_DIR, 'rvc_models')
output_dir = os.path.join(BASE_DIR, 'song_output')


def get_current_models(models_dir):
    models_list = os.listdir(models_dir)
    items_to_remove = ['hubert_base.pt', 'MODELS.txt', 'public_models.json', 'rmvpe.pt']
    return [item for item in models_list if item not in items_to_remove]


def update_models_list():
    models_l = get_current_models(rvc_models_dir)
    return gr.Dropdown.update(choices=models_l)


def load_public_models():
    models_table = []
    for model in public_models['voice_models']:
        if not model['name'] in voice_models:
            model = [model['name'], model['description'], model['credit'], model['url'], ', '.join(model['tags'])]
            models_table.append(model)

    tags = list(public_models['tags'].keys())
    return gr.DataFrame.update(value=models_table), gr.CheckboxGroup.update(choices=tags)


def extract_zip(extraction_folder, zip_name):
    os.makedirs(extraction_folder)
    with zipfile.ZipFile(zip_name, 'r') as zip_ref:
        zip_ref.extractall(extraction_folder)
    os.remove(zip_name)

    index_filepath, model_filepath = None, None
    for root, dirs, files in os.walk(extraction_folder):
        for name in files:
            if name.endswith('.index') and os.stat(os.path.join(root, name)).st_size > 1024 * 100:
                index_filepath = os.path.join(root, name)

            if name.endswith('.pth') and os.stat(os.path.join(root, name)).st_size > 1024 * 1024 * 40:
                model_filepath = os.path.join(root, name)

    if not model_filepath:
        raise gr.Error(f'No se encontró ningún archivo de modelo .pth en el zip extraído. Por favor compruebe {extraction_folder}.')

    # move model and index file to extraction folder
    os.rename(model_filepath, os.path.join(extraction_folder, os.path.basename(model_filepath)))
    if index_filepath:
        os.rename(index_filepath, os.path.join(extraction_folder, os.path.basename(index_filepath)))

    # remove any unnecessary nested folders
    for filepath in os.listdir(extraction_folder):
        if os.path.isdir(os.path.join(extraction_folder, filepath)):
            shutil.rmtree(os.path.join(extraction_folder, filepath))


def download_online_model(url, dir_name, progress=gr.Progress()):
    try:
        progress(0, desc=f'[~] Descargando modelo de voz {dir_name}...')
        zip_name = url.split('/')[-1]
        extraction_folder = os.path.join(rvc_models_dir, dir_name)
        if os.path.exists(extraction_folder):
            raise gr.Error(f'El directorio del modelo de voz {dir_name} ya existe! Elija otro nombre para su modelo de voz.')

        if 'pixeldrain.com' in url:
            url = f'https://pixeldrain.com/api/file/{zip_name}'

        urllib.request.urlretrieve(url, zip_name)

        progress(0.5, desc='[~] Extrayendo zip...')
        extract_zip(extraction_folder, zip_name)
        return f'[+] {dir_name} Modelo cargado con éxito!'

    except Exception as e:
        raise gr.Error(str(e))


def upload_local_model(zip_path, dir_name, progress=gr.Progress()):
    try:
        extraction_folder = os.path.join(rvc_models_dir, dir_name)
        if os.path.exists(extraction_folder):
            raise gr.Error(f'El directorio del modelo de voz {dir_name} ya existe! Elija otro nombre para su modelo de voz.')

        zip_name = zip_path.name
        progress(0.5, desc='[~] Extrayendo zip...')
        extract_zip(extraction_folder, zip_name)
        return f'[+] {dir_name} Modelo cargado con éxito!'

    except Exception as e:
        raise gr.Error(str(e))


def filter_models(tags, query):
    models_table = []

    # no filter
    if len(tags) == 0 and len(query) == 0:
        for model in public_models['voice_models']:
            models_table.append([model['name'], model['description'], model['credit'], model['url'], model['tags']])

    # filter based on tags and query
    elif len(tags) > 0 and len(query) > 0:
        for model in public_models['voice_models']:
            if all(tag in model['tags'] for tag in tags):
                model_attributes = f"{model['name']} {model['description']} {model['credit']} {' '.join(model['tags'])}".lower()
                if query.lower() in model_attributes:
                    models_table.append([model['name'], model['description'], model['credit'], model['url'], model['tags']])

    # filter based on only tags
    elif len(tags) > 0:
        for model in public_models['voice_models']:
            if all(tag in model['tags'] for tag in tags):
                models_table.append([model['name'], model['description'], model['credit'], model['url'], model['tags']])

    # filter based on only query
    else:
        for model in public_models['voice_models']:
            model_attributes = f"{model['name']} {model['description']} {model['credit']} {' '.join(model['tags'])}".lower()
            if query.lower() in model_attributes:
                models_table.append([model['name'], model['description'], model['credit'], model['url'], model['tags']])

    return gr.DataFrame.update(value=models_table)


def pub_dl_autofill(pub_models, event: gr.SelectData):
    return gr.Text.update(value=pub_models.loc[event.index[0], 'URL']), gr.Text.update(value=pub_models.loc[event.index[0], 'Model Name'])


def swap_visibility():
    return gr.update(visible=True), gr.update(visible=False), gr.update(value=''), gr.update(value=None)


def process_file_upload(file):
    return file.name, gr.update(value=file.name)


def show_hop_slider(pitch_detection_algo):
    if pitch_detection_algo == 'mangio-crepe':
        return gr.update(visible=True)
    else:
        return gr.update(visible=False)


if __name__ == '__main__':
    parser = ArgumentParser(description='Generar una versión AI de una canción en el directorio song_output/id.', add_help=True)
    parser.add_argument("--share", action="store_true", dest="share_enabled", default=False, help="Habilitar compartir")
    parser.add_argument("--listen", action="store_true", default=False, help="Hacer que la interfaz web sea accesible desde tu red local.")
    parser.add_argument('--listen-host', type=str, help='El nombre de host que utilizará el servidor.')
    parser.add_argument('--listen-port', type=int, help='El puerto de escucha que utilizará el servidor.')
    args = parser.parse_args()

    voice_models = get_current_models(rvc_models_dir)
    with open(os.path.join(rvc_models_dir, 'public_models.json'), encoding='utf8') as infile:
        public_models = json.load(infile)

    with gr.Blocks(title='Cambia voces WebUI') as app:

        gr.Label('Por que te I❤️U', show_label=False)

        # main tab
        with gr.Tab("Generar"):

            with gr.Accordion('Opciones principales'):
                with gr.Row():
                    with gr.Column():
                        rvc_model = gr.Dropdown(voice_models, label='Modelelos de Voces', info='Carpeta de modelos "AICoverGen --> rvc_models". Después de agregar nuevos modelos a esta carpeta, haz clic en el botón de actualización.')
                        ref_btn = gr.Button('Recarga modeles 🔁', variant='primary')

                    with gr.Column() as yt_link_col:
                        song_input = gr.Text(label='Entrada de canción', info='Enlace a una canción en YouTube o ruta completa a un archivo local. Para cargar un archivo, haz clic en el botón de abajo.')
                        show_file_upload_button = gr.Button('Cargar archivo en su lugar')

                    with gr.Column(visible=False) as file_upload_col:
                        local_file = gr.File(label='Archivo de audio')
                        song_input_file = gr.UploadButton('Cargar 📂', file_types=['audio'], variant='primary')
                        show_yt_link_button = gr.Button('Pegar enlace de YouTube/Ruta de archivo local en su lugar')
                        song_input_file.upload(process_file_upload, inputs=[song_input_file], outputs=[local_file, song_input])

                    with gr.Column():
                        pitch = gr.Slider(-3, 3, value=0, step=1, label='Cambio de tono (Solo voces)', info='Generalmente, usa 1 para conversiones de voz masculina a femenina y -1 viceversa. (Octavas)')
                        pitch_all = gr.Slider(-12, 12, value=0, step=1, label='Cambio general de tono', info='Cambia el tono/clave de las voces e instrumentales juntos. Alterar esto ligeramente reduce la calidad del sonido. (Semitonos)')
                    show_file_upload_button.click(swap_visibility, outputs=[file_upload_col, yt_link_col, song_input, local_file])
                    show_yt_link_button.click(swap_visibility, outputs=[yt_link_col, file_upload_col, song_input, local_file])


            with gr.Accordion('Opciones de conversión de voz', open=False):
                with gr.Row():
                    index_rate = gr.Slider(0, 1, value=0.5, label='Tasa de índice', info="Controla cuánto del acento de la voz de la IA mantener en las vocales")
                    filter_radius = gr.Slider(0, 7, value=3, step=1, label='Radio del filtro', info='Si >=3: aplica filtrado mediano a los resultados de tono obtenidos. Puede reducir la aspereza')
                    rms_mix_rate = gr.Slider(0, 1, value=0.25, label='Tasa de mezcla de RMS', info="Controla cuánto imitar la sonoridad original de la voz (0) o una sonoridad fija (1)")
                    protect = gr.Slider(0, 0.5, value=0.33, label='Tasa de protección', info='Protege las consonantes sin voz y los sonidos de la respiración. Ajusta a 0.5 para desactivar.')
                    with gr.Column():
                        f0_method = gr.Dropdown(['rmvpe', 'mangio-crepe'], value='rmvpe', label='Algoritmo de detección de tono', info='La mejor opción es rmvpe (claridad en las vocales), luego mangio-crepe (vocales más suaves)')
                        crepe_hop_length = gr.Slider(32, 320, value=128, step=1, visible=False, label='Longitud de salto de Crepe', info='Valores más bajos conducen a conversiones más largas y mayor riesgo de grietas en la voz, pero mejor precisión de tono.')
                        f0_method.change(show_hop_slider, inputs=f0_method, outputs=crepe_hop_length)
                keep_files = gr.Checkbox(label='Conservar archivos intermedios', info='Mantén todos los archivos de audio generados en el directorio song_output/id, como Voces Aisladas/Instrumentales. Desmarcar para ahorrar espacio')


            with gr.Accordion('Opciones de mezcla de audio', open=False):
                gr.Markdown('### Cambio de volumen (decibelios)')
                with gr.Row():
                    main_gain = gr.Slider(-20, 20, value=0, step=1, label='Voces principales')
                    backup_gain = gr.Slider(-20, 20, value=0, step=1, label='Voces de coros')
                    inst_gain = gr.Slider(-20, 20, value=0, step=1, label='Música')

                gr.Markdown('### Control de reverberación en las voces de la IA')
                with gr.Row():
                    reverb_rm_size = gr.Slider(0, 1, value=0.15, label='Tamaño de la habitación', info='A mayor tamaño de la habitación, mayor tiempo de reverberación')
                    reverb_wet = gr.Slider(0, 1, value=0.2, label='Nivel de humedad', info='Nivel de las voces de la IA con reverberación')
                    reverb_dry = gr.Slider(0, 1, value=0.8, label='Nivel de sequedad', info='Nivel de las voces de la IA sin reverberación')
                    reverb_damping = gr.Slider(0, 1, value=0.7, label='Nivel de amortiguación', info='Absorción de altas frecuencias en la reverberación')

                gr.Markdown('### Formato de salida de audio')
                output_format = gr.Dropdown(['mp3', 'wav'], value='wav', label='Tipo de archivo de salida', info='mp3: tamaño de archivo pequeño, calidad decente. wav: Tamaño de archivo grande, mejor calidad')


            with gr.Row():
                clear_btn = gr.ClearButton(value='Limpiar', components=[song_input, rvc_model, keep_files, local_file])
                generate_btn = gr.Button("Generar", variant='primary')
                ai_cover = gr.Audio(label='Versión AI', show_share_button=True)

            ref_btn.click(update_models_list, None, outputs=rvc_model)
            is_webui = gr.Number(value=1, visible=False)
            generate_btn.click(song_cover_pipeline,
                               inputs=[song_input, rvc_model, pitch, keep_files, is_webui, main_gain, backup_gain,
                                       inst_gain, index_rate, filter_radius, rms_mix_rate, f0_method, crepe_hop_length,
                                       protect, pitch_all, reverb_rm_size, reverb_wet, reverb_dry, reverb_damping,
                                       output_format],
                               outputs=[ai_cover])
            clear_btn.click(lambda: [0, 0, 0, 0, 0.5, 3, 0.25, 0.33, 'rmvpe', 128, 0, 0.15, 0.2, 0.8, 0.7, 'mp3', None],
                            outputs=[pitch, main_gain, backup_gain, inst_gain, index_rate, filter_radius, rms_mix_rate,
                                     protect, f0_method, crepe_hop_length, pitch_all, reverb_rm_size, reverb_wet,
                                     reverb_dry, reverb_damping, output_format, ai_cover])


        # Download tab
        with gr.Tab('Descargar modelo'):

            with gr.Tab('Desde URL de HuggingFace/Pixeldrain'):
                with gr.Row():
                    model_zip_link = gr.Text(label='Enlace de descarga del modelo', info='Debe ser un archivo zip que contenga un archivo de modelo .pth y, opcionalmente, un archivo .index.')
                    model_name = gr.Text(label='Nombrar tu modelo', info='Dale a tu nuevo modelo un nombre único diferente a tus otros modelos de voz.')

                with gr.Row():
                    download_btn = gr.Button('Descargar 🌐', variant='primary', scale=19)
                    dl_output_message = gr.Text(label='Mensaje de salida', interactive=False, scale=20)

                download_btn.click(download_online_model, inputs=[model_zip_link, model_name], outputs=dl_output_message)

                gr.Markdown('## Ejemplos de entrada')
                gr.Examples(
                    [
                        ['https://huggingface.co/phant0m4r/LiSA/resolve/main/LiSA.zip', 'Lisa'],
                        ['https://pixeldrain.com/u/3tJmABXA', 'Gura'],
                        ['https://huggingface.co/Kit-Lemonfoot/kitlemonfoot_rvc_models/resolve/main/AZKi%20(Hybrid).zip', 'Azki']
                    ],
                    [model_zip_link, model_name],
                    [],
                    download_online_model,
                )

            with gr.Tab('Desde el Índice Público'):

                gr.Markdown('## Cómo utilizar')
                gr.Markdown('- Haz clic en Inicializar la tabla de modelos públicos')
                gr.Markdown('- Filtra modelos usando etiquetas o la barra de búsqueda')
                gr.Markdown('- Selecciona una fila para autocompletar el enlace de descarga y el nombre del modelo')
                gr.Markdown('- Haz clic en Descargar')


                with gr.Row():
                    pub_zip_link = gr.Text(label='Link de descarga del modelo')
                    pub_model_name = gr.Text(label='Nombre del modelo')

                with gr.Row():
                    download_pub_btn = gr.Button('Descargar 🌐', variant='primary', scale=19)
                    pub_dl_output_message = gr.Text(label='Mensaje de salida', interactive=False, scale=20)

                filter_tags = gr.CheckboxGroup(value=[], label='Muestrar modelos de voz con etiquetas', choices=[])
                search_query = gr.Text(label='Buscar')
                load_public_models_button = gr.Button(value='Iniciar la tabla de modelos públicos', variant='primary')

                public_models_table = gr.DataFrame(value=[], headers=['Nombre del Modelo', 'Descripción', 'Autor', 'URL', 'Etiquetas'], label='Modelos públicos disponibles', interactive=False)
                public_models_table.select(pub_dl_autofill, inputs=[public_models_table], outputs=[pub_zip_link, pub_model_name])
                load_public_models_button.click(load_public_models, outputs=[public_models_table, filter_tags])
                search_query.change(filter_models, inputs=[filter_tags, search_query], outputs=public_models_table)
                filter_tags.change(filter_models, inputs=[filter_tags, search_query], outputs=public_models_table)
                download_pub_btn.click(download_online_model, inputs=[pub_zip_link, pub_model_name], outputs=pub_dl_output_message)

        # Upload tab
        with gr.Tab('Subir Modelo'):
            gr.Markdown('## Cargue el modelo RVC v2 entrenado localmente y el archivo de índice')
            gr.Markdown('- Encuentre el archivo del modelo (carpeta de pesos) y el archivo de índice opcional (en la carpeta (logs/[name])')
            gr.Markdown('- Archivos comprimidos en un zip')
            gr.Markdown('- Cargue el archivo zip y asigne un nombre único a la voz')
            gr.Markdown('- Haz clic en Subir modelo')

            with gr.Row():
                with gr.Column():
                    zip_file = gr.File(label='Archivo Zip')

                local_model_name = gr.Text(label='Nombre del modelo')

            with gr.Row():
                model_upload_button = gr.Button('Subir modelo', variant='primary', scale=19)
                local_upload_output_message = gr.Text(label='Salida de mensajes', interactive=False, scale=20)
                model_upload_button.click(upload_local_model, inputs=[zip_file, local_model_name], outputs=local_upload_output_message)

    app.launch(
        share=args.share_enabled,
        enable_queue=True,
        server_name=None if not args.listen else (args.listen_host or '0.0.0.0'),
        server_port=args.listen_port,
    )
