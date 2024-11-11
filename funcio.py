import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import serial
import threading

# Variables globales
ser = None
temperaturas = [0, 0, 0]
promedio_temperatura = 0
temperatura_objetiva = 25
temperatura_ventilador = 25
temperatura_foco = 25  # Temperatura a la que se enciende el foco

# Función para conectar al puerto serial
def conectar_puerto():
    global ser
    puerto = entry_puerto.get()
    if puerto:
        try:
            ser = serial.Serial(puerto, 115200, timeout=1)
            messagebox.showinfo("Conexión", f"Conectado al puerto: {puerto}")
            iniciar_lectura_datos()
        except serial.SerialException:
            messagebox.showerror("Error", f"No se pudo conectar al puerto: {puerto}")
    else:
        messagebox.showwarning("Advertencia", "Por favor, ingresa un puerto COM.")

# Función para leer datos del puerto serial y actualizar la GUI
def leer_datos():
    global ser, temperaturas, promedio_temperatura
    while ser and ser.is_open:
        try:
            if ser.in_waiting > 0:
                datos = ser.readline().decode('utf-8').strip()
                print(datos)

                if "Temperatura 1:" in datos:
                    temperaturas[0] = extraer_valor(datos)
                elif "Temperatura 2:" in datos:
                    temperaturas[1] = extraer_valor(datos)
                elif "Temperatura 3:" in datos:
                    temperaturas[2] = extraer_valor(datos)
                elif "Promedio de temperatura:" in datos:
                    promedio_temperatura = extraer_valor(datos)

                actualizar_gui()
                if "HUMEDAD:" in datos and "TEMP:" in datos:
                    separar_datos(datos)
        except Exception as e:
            print(f"Error en lectura de datos: {e}")
            break

# Función para extraer el valor numérico de un string
def extraer_valor(texto):
    return float(texto.split(": ")[1].split(" ")[0])

# Función para separar los datos de temperatura y humedad
def separar_datos(datos):
    try:
        partes = datos.split(" ")
        humedad = partes[0].split(":")[1]
        temperatura = partes[1].split(":")[1]

        label_humedad.config(text=f"Humedad: {humedad}%")
        label_temperatura.config(text=f"Temperatura: {temperatura}°C")

        controlar_foco(float(temperatura))  # Control del foco basado en la temperatura
        controlar_ventilador(float(temperatura))
    except Exception as e:
        print(f"Error al procesar los datos: {e}")

# Función para controlar el foco
def controlar_foco(temperatura_actual):
    global temperatura_foco
    if temperatura_actual >= temperatura_foco:
        if temperatura_actual >= 30:
            label_estado_foco.config(text="Foco: Encendido con baja intensidad", fg="orange")
            if ser and ser.is_open:
                ser.write(b"FOCO_BAJA\n")  # Comando para encender con baja intensidad
        else:
            label_estado_foco.config(text="Foco: Encendido", fg="green")
            if ser and ser.is_open:
                ser.write(b"FOCO_ON\n")  # Comando para encender el foco
    else:
        label_estado_foco.config(text="Foco: Apagado", fg="red")
        if ser and ser.is_open:
            ser.write(b"FOCO_OFF\n")  # Comando para apagar el foco

# Función para controlar el ventilador
def controlar_ventilador(temperatura_actual):
    global temperatura_ventilador
    if temperatura_actual >= temperatura_ventilador:
        label_estado_ventilador.config(text="Ventilador: Encendido", fg="green")
        if ser and ser.is_open:
            ser.write(b"VENTILADOR_ON\n")
    else:
        label_estado_ventilador.config(text="Ventilador: Apagado", fg="red")
        if ser and ser.is_open:
            ser.write(b"VENTILADOR_OFF\n")

# Función para controlar la bomba de agua
def controlar_bomba(estado):
    if estado == "ON":
        label_estado_bomba.config(text="Bomba: Encendida", fg="green")
        if ser and ser.is_open:
            ser.write(b"BOMBA_ON\n")
    else:
        label_estado_bomba.config(text="Bomba: Apagada", fg="red")
        if ser and ser.is_open:
            ser.write(b"BOMBA_OFF\n")

# Función para mover el servomotor
def mover_servomotor(posicion):
    if ser and ser.is_open:
        ser.write(f"SERVOMOTOR_{posicion}\n".encode())  # Envía la posición al servomotor
        label_estado_servomotor.config(text=f"Servomotor: Posición {posicion}", fg="blue")

# Función para actualizar la GUI
def actualizar_gui():
    label_temperatura1.config(text=f"Temperatura 1: {temperaturas[0]} °C")
    label_temperatura2.config(text=f"Temperatura 2: {temperaturas[1]} °C")
    label_temperatura3.config(text=f"Temperatura 3: {temperaturas[2]} °C")
    label_promedio.config(text=f"Promedio de temperatura: {promedio_temperatura} °C")

# Función para iniciar el hilo de lectura de datos
def iniciar_lectura_datos():
    hilo = threading.Thread(target=leer_datos)
    hilo.daemon = True
    hilo.start()

# Crear ventana principal
ventana = tk.Tk()
ventana.title("Control de Temperatura, Foco, Ventilador, Bomba y Servomotor")
ventana.geometry("400x800")

# Crear un Notebook (pestañas)
notebook = ttk.Notebook(ventana)
notebook.pack(fill='both', expand=True)

# Pestañas y Frames
frame_principal = ttk.Frame(notebook)
notebook.add(frame_principal, text="Principal")

frame_objetiva = ttk.Frame(notebook)
notebook.add(frame_objetiva, text="Temperatura Objetiva")

# Sección para ingresar el puerto COM
label_puerto = tk.Label(frame_principal, text="Puerto COM:")
label_puerto.pack(fill='x', padx=10, pady=5)
entry_puerto = tk.Entry(frame_principal)
entry_puerto.pack(fill='x', padx=10, pady=5)
boton_conectar = tk.Button(frame_principal, text="Conectar", command=conectar_puerto)
boton_conectar.pack(pady=5)

# Labels de temperatura y humedad
label_temperatura = tk.Label(frame_principal, text="Temperatura: 0°C", font=("Arial", 12))
label_temperatura.pack(fill='x', padx=10, pady=10)

label_humedad = tk.Label(frame_principal, text="Humedad: 0%", font=("Arial", 12))
label_humedad.pack(fill='x', padx=10, pady=10)

# Lectura de sensores
boton_leer_temperatura = tk.Button(frame_principal, text="Leer Temperatura y Humedad", command=leer_datos)
boton_leer_temperatura.pack(pady=10)

# Temperaturas de los tres sensores y promedio
label_temperatura1 = tk.Label(frame_principal, text="Temperatura 1: 0°C")
label_temperatura1.pack()
label_temperatura2 = tk.Label(frame_principal, text="Temperatura 2: 0°C")
label_temperatura2.pack()
label_temperatura3 = tk.Label(frame_principal, text="Temperatura 3: 0°C")
label_temperatura3.pack()
label_promedio = tk.Label(frame_principal, text="Promedio de temperatura: 0°C")
label_promedio.pack()

# Control de foco
label_estado_foco = tk.Label(frame_principal, text="Foco: Apagado", font=("Arial", 12), fg="red")
label_estado_foco.pack(fill='x', padx=10, pady=10)

# Control de ventilador
label_estado_ventilador = tk.Label(frame_principal, text="Ventilador: Apagado", font=("Arial", 12), fg="red")
label_estado_ventilador.pack(fill='x', padx=10, pady=10)

# Control de bomba
label_estado_bomba = tk.Label(frame_principal, text="Bomba: Apagada", font=("Arial", 12), fg="red")
label_estado_bomba.pack(fill='x', padx=10, pady=10)

boton_encender_bomba = tk.Button(frame_principal, text="Encender Bomba", command=lambda: controlar_bomba("ON"))
boton_encender_bomba.pack(pady=5)

boton_apagar_bomba = tk.Button(frame_principal, text="Apagar Bomba", command=lambda: controlar_bomba("OFF"))
boton_apagar_bomba.pack(pady=5)

# Control del servomotor
label_estado_servomotor = tk.Label(frame_principal, text="Servomotor: Posición 0", font=("Arial", 12), fg="blue")
label_estado_servomotor.pack(fill='x', padx=10, pady=10)

boton_posicion1 = tk.Button(frame_principal, text="Posición 1", command=lambda: mover_servomotor(1))
boton_posicion1.pack(pady=5)

boton_posicion2 = tk.Button(frame_principal, text="Posición 2", command=lambda: mover_servomotor(2))
boton_posicion2.pack(pady=5)

ventana.mainloop()
