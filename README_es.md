<div align="center">

# Retrieval-based-Voice-Conversion-WebUI
Un marco de cambio de voz simple y fácil de usar basado en VITS<br><br>

[![madewithlove](https://img.shields.io/badge/hecho_con-%E2%9D%A4-rojo?style=for-the-badge&labelColor=naranja
)](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI)

<img src="https://counter.seku.su/cmoe?name=rvc&theme=r34" /><br>

[![Abrir en Colab](https://img.shields.io/badge/Colab-F9AB00?style=for-the-badge&logo=googlecolab&color=525252)](https://colab.research.google.com/github/RVC-Project/Retrieval-based-Voice-Conversion-WebUI/blob/main/Retrieval_based_Voice_Conversion_WebUI.ipynb)
[![Licencia](https://img.shields.io/badge/LICENCIA-MIT-verde.svg?style=for-the-badge)](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI/blob/main/LICENSE)
[![Huggingface](https://img.shields.io/badge/🤗%20-Spaces-amarillo.svg?style=for-the-badge)](https://huggingface.co/lj1995/VoiceConversionWebUI/tree/main/)

[![Discord](https://img.shields.io/badge/Desarrolladores%20de%20RVC-Discord-7289DA?style=for-the-badge&logo=discord&logoColor=blanco)](https://discord.gg/HcsmBBGyVk)

[**Registro de actualizaciones**](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI/blob/main/docs/Changelog_CN.md) | [**Preguntas frecuentes**](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI/wiki/%E5%B8%B8%E8%A7%81%E9%97%AE%E9%A2%98%E8%A7%A3%E7%AD%94) | [**AutoDL·5毛钱训练AI歌手**](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI/wiki/Autodl%E8%AE%AD%E7%BB%83RVC%C2%B7AI%E6%AD%8C%E6%89%8B%E6%95%99%E7%A8%8B) | [**Registros de experimentos comparativos**](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI/wiki/Autodl%E8%AE%AD%E7%BB%83RVC%C2%B7AI%E6%AD%8C%E6%89%8B%E6%95%99%E7%A8%8B](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI/wiki/%E5%AF%B9%E7%85%A7%E5%AE%9E%E9%AA%8C%C2%B7%E5%AE%9E%E9%AA%8C%E8%AE%B0%E5%BD%95)) | [**Demo en línea**](https://modelscope.cn/studios/FlowerCry/RVCv2demo)

[**Inglés**](./docs/en/README.en.md) | [**Chino simplificado**](./README.md) | [**Japonés**](./docs/jp/README.ja.md) | [**Coreano**](./docs/kr/README.ko.md) ([**韓國語**](./docs/kr/README.ko.han.md)) | [**Francés**](./docs/fr/README.fr.md)| [**Turco**](./docs/tr/README.tr.md)

</div>

> El modelo base se entrena con cerca de 50 horas de conjunto de datos de alta calidad VCTK de código abierto. No hay preocupaciones de derechos de autor, así que siéntete libre de usarlo.

> Espera el modelo base de RVCv3, con parámetros más grandes, datos más extensos, mejor rendimiento, y una velocidad de inferencia básicamente igual. Se requiere menos cantidad de datos de entrenamiento.

<table>
   <tr>
		<td align="center">Interfaz de entrenamiento e inferencia</td>
		<td align="center">Interfaz de cambio de voz en tiempo real</td>
	</tr>
  <tr>
		<td align="center"><img src="https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI/assets/129054828/092e5c12-0d49-4168-a590-0b0ef6a4f630"></td>
    <td align="center"><img src="https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI/assets/129054828/730b4114-8805-44a1-ab1a-04668f3c30a6"></td>
	</tr>
	<tr>
		<td align="center">go-web.bat</td>
		<td align="center">go-realtime-gui.bat</td>
	</tr>
  <tr>
    <td align="center">Puedes elegir libremente la operación que deseas realizar.</td>
		<td align="center">Ya hemos logrado una latencia de extremo a extremo de 170 ms. Con dispositivos de entrada y salida ASIO, hemos logrado una latencia de extremo a extremo de 90 ms, pero esto depende en gran medida del soporte del controlador de hardware.</td>
	</tr>
</table>


## Introducción
Este repositorio presenta las siguientes características:
+ Utiliza la búsqueda top1 para reemplazar las características de la fuente de entrada con las características del conjunto de entrenamiento para evitar filtraciones de tono.
+ Se puede entrenar rápidamente incluso en tarjetas gráficas relativamente menos potentes.
+ Obtiene resultados decentes con cantidades mínimas de datos de entrenamiento (se recomienda recopilar al menos 10 minutos de datos de voz con poco ruido de fondo).
+ Puede cambiar la voz a través de la fusión de modelos (utilizando la pestaña de opciones de procesamiento "ckpt-merge").
+ Interfaz web simple y fácil de usar.
+ Puede invocar el modelo UVR5 para separar rápidamente la voz y el acompañamiento.
+ Utiliza el algoritmo de extracción de tono vocal más avanzado [InterSpeech2023-RMVPE](#参考项目) para abordar el problema de los sonidos sin tono. Ofrece el mejor rendimiento (notablemente) pero es más rápido y utiliza menos recursos que crepe_full.
+ Soporte de aceleración para tarjetas A y I.

Haz clic aquí para ver nuestro [video demostrativo](https://www.bilibili.com/video/BV1pm4y1z7Gm/) !

## Configuración del entorno
Las siguientes instrucciones deben ejecutarse en un entorno con Python versión superior a 3.8.

### Método universal para plataformas Windows/Linux/MacOS, etc.
Puedes elegir cualquiera de los siguientes métodos.
#### 1. Instalación de dependencias mediante pip
1. Instala PyTorch y sus dependencias principales. Si ya están instaladas, puedes omitir este paso. Consulta: https://pytorch.org/get-started/locally/
```bash
pip install torch torchvision torchaudio

```
2. Si estás utilizando un sistema Windows con arquitectura Nvidia Ampere (RTX30xx), según la experiencia en el problema #21, es necesario especificar la versión de CUDA correspondiente a PyTorch.
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117
```
3. Instala las dependencias según tu tarjeta gráfica.
- Tarjeta gráfica Nvidia (N卡)
```bash
pip install -r requirements.txt
```
- Tarjeta gráfica AMD (A卡/I卡)
```bash
pip install -r requirements-dml.txt
```
- Tarjeta gráfica AMD ROCM (Linux)
```bash
pip install -r requirements-amd.txt
```
- Tarjeta gráfica Intel IPEX (Linux)
```bash
pip install -r requirements-ipex.txt
```

### 2. Instalación de dependencias mediante poetry
Instala Poetry, la herramienta de gestión de dependencias. Si ya está instalada, puedes omitir este paso. Consulta: https://python-poetry.org/docs/#installation
```bash
curl -sSL https://install.python-poetry.org | python3 -
```
Instala las dependencias mediante poetry
```bash
poetry install
```

### MacOS
Puedes instalar las dependencias a través de `run.sh`
```bash
sh ./run.sh
```

## Preparación de Otros Modelos Preentrenados
RVC requiere algunos modelos preentrenados adicionales para la inferencia y el entrenamiento.

Puedes descargar estos modelos desde nuestro [Hugging Face space](https://huggingface.co/lj1995/VoiceConversionWebUI/tree/main/).

### 1. Descargar assets
Aquí tienes una lista que incluye los nombres de todos los modelos preentrenados y otros archivos necesarios para RVC. Puedes encontrar los scripts para descargarlos en la carpeta `tools`.

- ./assets/hubert/hubert_base.pt

- ./assets/pretrained 

- ./assets/uvr5_weights

Si deseas utilizar modelos de la versión v2, necesitarás descargar adicionalmente

- ./assets/pretrained_v2

### 2. Instalación de ffmpeg
Si ya tienes ffmpeg y ffprobe instalados, puedes omitir este paso.

#### Usuarios de Ubuntu/Debian
```bash
sudo apt install ffmpeg
```
#### Usuarios de MacOS
```bash
brew install ffmpeg
```
#### Usuarios de Windows
Coloca los siguientes archivos descargados en el directorio raíz.
- Descarga [ffmpeg.exe](https://huggingface.co/lj1995/VoiceConversionWebUI/blob/main/ffmpeg.exe)

- Descarga [ffprobe.exe](https://huggingface.co/lj1995/VoiceConversionWebUI/blob/main/ffprobe.exe)

### 3. Descargar archivos necesarios para el algoritmo de extracción de tono vocal RMVPE

Si deseas utilizar la última versión del algoritmo de extracción de tono vocal RMVPE, necesitarás descargar los parámetros del modelo de extracción de tono y colocarlos en el directorio raíz de RVC.

- Descarga [rmvpe.pt](https://huggingface.co/lj1995/VoiceConversionWebUI/blob/main/rmvpe.pt)

#### Descargar el entorno dml de rmvpe (opcional, para usuarios de tarjetas gráficas A/I)

- Descarga [rmvpe.onnx](https://huggingface.co/lj1995/VoiceConversionWebUI/blob/main/rmvpe.onnx)

### 4. Tarjetas gráficas AMD con Rocm (opcional, solo Linux)

Si deseas ejecutar RVC en un sistema Linux utilizando la tecnología Rocm de AMD, primero instala los controladores necesarios siguiendo las instrucciones disponibles [aquí](https://rocm.docs.amd.com/en/latest/deploy/linux/os-native/install.html).

Si estás utilizando Arch Linux, puedes instalar los controladores necesarios utilizando pacman:
````
pacman -S rocm-hip-sdk rocm-opencl-sdk
````
Para ciertos modelos de tarjetas gráficas, es posible que necesites configurar variables de entorno adicionales como las siguientes (por ejemplo: RX6700XT):
````
export ROCM_PATH=/opt/rocm
export HSA_OVERRIDE_GFX_VERSION=10.3.0
````
Asegúrate de que tu usuario actual pertenezca a los grupos de usuarios `render` y `video`:
````
sudo usermod -aG render $USERNAME
sudo usermod -aG video $USERNAME
````

## Comenzar a usar
### Iniciar directamente
Utiliza el siguiente comando para iniciar la interfaz de usuario web (WebUI):
```bash
python infer-web.py
```
### Utilizar el paquete integrado
Descarga y descomprime el archivo `RVC-beta.7z`
#### Usuarios de Windows
Haz doble clic en `go-web.bat`
#### Usuarios de MacOS
```bash
sh ./run.sh
```
### Para usuarios de tarjetas gráficas I que necesitan utilizar la tecnología IPEX (solo en Linux)
```bash
source /opt/intel/oneapi/setvars.sh
```

## Proyectos de referencia
+ [ContentVec](https://github.com/auspicious3000/contentvec/)
+ [VITS](https://github.com/jaywalnut310/vits)
+ [HIFIGAN](https://github.com/jik876/hifi-gan)
+ [Gradio](https://github.com/gradio-app/gradio)
+ [FFmpeg](https://github.com/FFmpeg/FFmpeg)
+ [Ultimate Vocal Remover](https://github.com/Anjok07/ultimatevocalremovergui)
+ [audio-slicer](https://github.com/openvpi/audio-slicer)
+ [Extracción de tono vocal: RMVPE](https://github.com/Dream-High/RMVPE)
  + El modelo preentrenado está entrenado y probado por [yxlllc](https://github.com/yxlllc/RMVPE) y [RVC-Boss](https://github.com/RVC-Boss).

## Agradecimientos a todos los contribuyentes por sus esfuerzos
<a href="https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI/graphs/contributors" target="_blank">
  <img src="https://contrib.rocks/image?repo=RVC-Project/Retrieval-based-Voice-Conversion-WebUI" />
</a>
