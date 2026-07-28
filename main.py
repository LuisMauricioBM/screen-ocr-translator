import os
import re
import sys
import time
import ctypes
import threading
import tkinter as tk

import mss
import torch
from PIL import Image
from transformers import AutoModel, AutoTokenizer
from deep_translator import GoogleTranslator

# ---------------------------------------------------------------
# Corrige el desfase entre lo que ves y lo que se captura cuando
# Windows tiene escalado de pantalla activado (125%, 150%, etc).
# ---------------------------------------------------------------
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

# =================================================================
# CONFIGURACIÓN INICIAL
# =================================================================
POSICION_X_INICIAL = 100
POSICION_Y_INICIAL = 100
ANCHO_INICIAL = 400
ALTO_INICIAL = 250
TAMANO_MINIMO = 100

INTERVALO_SEGUNDOS = 1.5  # Puedes probar ajustándolo a tu gusto

CARPETA_TEMPORAL = "salida_ocr"
os.makedirs(CARPETA_TEMPORAL, exist_ok=True)
RUTA_CAPTURA = os.path.join(CARPETA_TEMPORAL, "captura.png")
RUTA_RESULTADO = os.path.join(CARPETA_TEMPORAL, "result.md")

COLOR_TRANSPARENTE = "#ff00ff"
COLOR_FONDO_TEXTO = "#0d0d0d"
OPACIDAD_VENTANA = 0.80

TAMANO_FUENTE_MIN = 10
TAMANO_FUENTE_MAX = 22

# =================================================================
# Cargar el modelo UNA SOLA VEZ al iniciar
# =================================================================
print("Cargando Unlimited-OCR... (puede tardar un momento)")
MODEL_NAME = "baidu/Unlimited-OCR"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)

with torch.inference_mode():
    model = AutoModel.from_pretrained(
        MODEL_NAME,
        trust_remote_code=True,
        use_safetensors=True,
        torch_dtype=torch.bfloat16,
    )
    model = model.eval().cuda()

print("Modelo cargado. Iniciando overlay...")


def limpiar_texto_ocr(texto_markdown):
    """Quita marcas de imagen/markdown y deja solo el texto plano."""
    lineas_limpias = []
    for linea in texto_markdown.splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("!["):
            continue
        linea = re.sub(r"[#*_`]", "", linea)
        lineas_limpias.append(linea)
    return " ".join(lineas_limpias)


def ocr_con_unlimited(ruta_imagen):
    """Corre el modelo sobre una imagen y devuelve el texto limpio detectado."""
    with torch.inference_mode():
        model.infer(
            tokenizer,
            prompt="<image>Free OCR.",
            image_file=ruta_imagen,
            output_path=CARPETA_TEMPORAL,
            base_size=640,
            image_size=512,
            crop_mode=False,
            max_length=256,
            no_repeat_ngram_size=20,
            ngram_window=64,
            save_results=True,
        )
    if not os.path.exists(RUTA_RESULTADO):
        return ""
    with open(RUTA_RESULTADO, "r", encoding="utf-8") as f:
        contenido = f.read()
    return limpiar_texto_ocr(contenido)


class Overlay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", OPACIDAD_VENTANA)
        self.root.configure(bg=COLOR_TRANSPARENTE)

        try:
            self.root.wm_attributes("-transparentcolor", COLOR_TRANSPARENTE)
        except tk.TclError:
            pass

        self.root.geometry(
            f"{ANCHO_INICIAL}x{ALTO_INICIAL}+{POSICION_X_INICIAL}+{POSICION_Y_INICIAL}"
        )

        self.label = tk.Label(
            self.root,
            text="Esperando texto...",
            font=("Helvetica", 14, "bold"),
            fg="white",
            bg=COLOR_FONDO_TEXTO,
            wraplength=ANCHO_INICIAL - 20,
            justify="left",
        )
        self.label.place(x=10, y=18, width=ANCHO_INICIAL - 20, height=ALTO_INICIAL - 36)

        self.barra_mover = tk.Frame(self.root, bg="#333333", height=15, cursor="fleur")
        self.barra_mover.place(x=0, y=0, relwidth=1, height=15)
        self.barra_mover.bind("<ButtonPress-1>", self.iniciar_mover)
        self.barra_mover.bind("<B1-Motion>", self.mover)

        self.boton_cerrar = tk.Label(
            self.barra_mover, text="✕", bg="#333333", fg="white",
            font=("Helvetica", 10, "bold"), cursor="hand2",
        )
        self.boton_cerrar.place(relx=1.0, x=-2, y=0, anchor="ne")
        self.boton_cerrar.bind("<Button-1>", self.cerrar)

        self.esquina_resize = tk.Frame(
            self.root, bg="#666666", width=18, height=18, cursor="size_nw_se"
        )
        self.esquina_resize.place(relx=1.0, rely=1.0, anchor="se")
        self.esquina_resize.bind("<ButtonPress-1>", self.iniciar_resize)
        self.esquina_resize.bind("<B1-Motion>", self.redimensionar)

    def cerrar(self, event=None):
        self.root.destroy()
        os._exit(0)

    def iniciar_mover(self, event):
        self._mover_x = event.x
        self._mover_y = event.y

    def mover(self, event):
        x = self.root.winfo_pointerx() - self._mover_x
        y = self.root.winfo_pointery() - self._mover_y
        self.root.geometry(f"+{x}+{y}")

    def iniciar_resize(self, event):
        self._resize_x = event.x_root
        self._resize_y = event.y_root
        self._ancho_inicial = self.root.winfo_width()
        self._alto_inicial = self.root.winfo_height()

    def redimensionar(self, event):
        delta_x = event.x_root - self._resize_x
        delta_y = event.y_root - self._resize_y
        nuevo_ancho = max(TAMANO_MINIMO, self._ancho_inicial + delta_x)
        nuevo_alto = max(TAMANO_MINIMO, self._alto_inicial + delta_y)
        self.root.geometry(f"{nuevo_ancho}x{nuevo_alto}")
        self.label.place(width=nuevo_ancho - 20, height=nuevo_alto - 36)
        self.label.config(wraplength=nuevo_ancho - 20)
        self.aplicar_tamano_fuente()

    def calcular_tamano_fuente(self, ancho, alto, largo_texto=0):
        tamano = ancho // 22
        tamano = max(TAMANO_FUENTE_MIN, min(TAMANO_FUENTE_MAX, tamano))
        if largo_texto > 160:
            tamano = max(TAMANO_FUENTE_MIN, tamano - 4)
        elif largo_texto > 90:
            tamano = max(TAMANO_FUENTE_MIN, tamano - 2)
        return tamano

    def aplicar_tamano_fuente(self):
        ancho = self.root.winfo_width()
        alto = self.root.winfo_height()
        largo_texto = len(self.label.cget("text"))
        tamano = self.calcular_tamano_fuente(ancho, alto, largo_texto)
        self.label.config(font=("Helvetica", tamano, "bold"))

    def actualizar_texto(self, texto):
        self.label.config(text=texto)
        self.aplicar_tamano_fuente()

    def region_actual(self):
        self.root.update_idletasks()
        return {
            "left": self.root.winfo_x(),
            "top": self.root.winfo_y(),
            "width": self.root.winfo_width(),
            "height": self.root.winfo_height(),
        }

    def ocultar(self):
        self.root.withdraw()

    def mostrar(self):
        self.root.deiconify()


def bucle_traduccion(overlay):
    ultimo_texto = ""
    traductor = GoogleTranslator(source="en", target="es")

    with mss.mss() as sct:
        while True:
            try:
                region = overlay.region_actual()

                overlay.root.after(0, overlay.ocultar)
                time.sleep(0.08)

                captura = sct.grab(region)
                img = Image.frombytes("RGB", captura.size, captura.bgra, "raw", "BGRX")
                img.save(RUTA_CAPTURA)

                overlay.root.after(0, overlay.mostrar)

                texto_detectado = ocr_con_unlimited(RUTA_CAPTURA)

                if texto_detectado and texto_detectado != ultimo_texto:
                    ultimo_texto = texto_detectado
                    traduccion = traductor.translate(texto_detectado)
                    overlay.root.after(0, overlay.actualizar_texto, traduccion)
                elif not texto_detectado:
                    overlay.root.after(0, overlay.actualizar_texto, "(sin texto detectado)")

            except Exception as e:
                overlay.root.after(0, overlay.mostrar)
                overlay.root.after(0, overlay.actualizar_texto, f"Error: {e}")

            time.sleep(INTERVALO_SEGUNDOS)


if __name__ == "__main__":
    overlay = Overlay()
    hilo = threading.Thread(target=bucle_traduccion, args=(overlay,), daemon=True)
    hilo.start()
    overlay.root.mainloop()