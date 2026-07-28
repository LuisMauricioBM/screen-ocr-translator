# 🔍 Real-Time Screen OCR & Translator Overlay

Una aplicación en Python que captura una región redimensionable de la pantalla en tiempo real, extrae texto mediante Inteligencia Artificial con el modelo **Baidu Unlimited-OCR** y muestra la traducción traducida al instante sobre una ventana transparente (_overlay_).

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)
![Hugging Face](https://img.shields.io/badge/HuggingFace-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

---

## ✨ Características

- 🎯 **Captura Regional Flotante:** Ajusta y mueve la ventana transparente sobre cualquier zona de la pantalla (manga, cómics, videojuegos, PDFs o videos).
- 🤖 **OCR Inteligente con IA:** Basado en el modelo `baidu/Unlimited-OCR` de Baidu a través de Hugging Face.
- 🌐 **Traducción Automática:** Traduce en tiempo real del inglés al español utilizando `deep-translator`.
- 🖥️ **Soporte HiDPI:** Corrige desfases de captura causados por el escalado de pantalla en Windows (125%, 150%, etc.).
- ⚡ **Optimización en GPU:** Carga el modelo directamente en la VRAM de la tarjeta de video (CUDA / `bfloat16`) una sola vez al iniciar para garantizar máxima fluidez.

---

## 🛠️ Requisitos e Instalación

### Prerrequisitos

- **Sistema Operativo:** Windows
- **Python:** 3.10 o superior
- **Hardware:** Tarjeta gráfica NVIDIA con soporte para CUDA (requerido para PyTorch)

### Pasos de Instalación

1. **Clona este repositorio:**

   ```bash
   git clone [https://github.com/LuisMauricioBM/screen-ocr-translator.git](https://github.com/LuisMauricioBM/screen-ocr-translator.git)
   cd screen-ocr-translator

   ```

2. **Crea y activa un entorno virtual (Recomendado):**
   - En **Windows (PowerShell):**

     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1

     ```

   - En **Windows (CMD):**

     ```cmd
     python -m venv .venv
     .venv\Scripts\activate.bat

     ```

3. **Instala PyTorch con soporte para GPU (CUDA):**

   ```bash
   pip install torch --index-url https://download.pytorch.org/whl/cu121

   ```

4. **Instala el resto de las dependencias necesarias:**

   ```bash
   pip install -r requirements.txt

   ```

---

## 🚀 Uso

1. **Ejecuta el programa desde la terminal:**

   ```bash
   python main.py

   ```

2. Espera unos segundos a que el modelo cargue en la tarjeta de video (`Modelo cargado. Iniciando overlay...`).
3. Mueve la barra gris superior para ubicar el área de lectura sobre el texto que deseas traducir.
4. Arrastra la esquina inferior derecha si necesitas hacer el área de captura más grande o pequeña.
5. El texto traducido aparecerá automáticamente en el recuadro cada 1.5 segundos.

---

## 🙏 Créditos y Agradecimientos

- **Modelo OCR:** Desarrollado por **Baidu** — [`baidu/Unlimited-OCR`](https://huggingface.co/baidu/Unlimited-OCR)
- **Traducción:** [`deep-translator`](https://github.com/nidhaloff/deep-translator)
- **Captura de pantalla:** [`mss`](https://github.com/BoboTiG/python-mss)

---

## 📜 Licencia

Este proyecto está bajo la [Licencia MIT](https://www.google.com/search?q=LICENSE).
