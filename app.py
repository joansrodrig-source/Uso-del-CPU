import psutil
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ======================
# CONFIG VENTANA
# ======================
root = tk.Tk()
root.title("CPU Monitor PRO MAX")
root.geometry("1000x650")

# ======================
# ESTILO OSCURO
# ======================
style = ttk.Style()
style.theme_use("clam")

style.configure("TFrame", background="#1e1e1e")
style.configure("TLabel", background="#1e1e1e", foreground="white")
style.configure("Treeview",
                background="#2b2b2b",
                foreground="white",
                fieldbackground="#2b2b2b")

# ======================
# HEADER
# ======================
header = ttk.Frame(root)
header.pack(fill="x")

ttk.Label(header, text="CPU MONITOR PRO MAX", font=("Arial", 16)).pack(pady=10)

# ======================
# TABS
# ======================
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# ======================
# TAB 1: CPU GENERAL
# ======================
tab1 = ttk.Frame(notebook)
notebook.add(tab1, text="CPU General")

# Barra de CPU
cpu_bar = ttk.Progressbar(tab1, length=400)
cpu_bar.pack(pady=10)

fig1 = plt.Figure(figsize=(6,3))
canvas1 = FigureCanvasTkAgg(fig1, master=tab1)
canvas1.get_tk_widget().pack(fill="both", expand=True)

valores_cpu = []

def actualizar_cpu():
    cpu = psutil.cpu_percent(interval=1)

    cpu_bar["value"] = cpu

    valores_cpu.append(cpu)
    if len(valores_cpu) > 30:
        valores_cpu.pop(0)

    fig1.clear()
    ax = fig1.add_subplot(111)
    ax.plot(valores_cpu)
    ax.set_title("CPU (%)")

    canvas1.draw()
    root.after(1000, actualizar_cpu)

actualizar_cpu()

# ======================
# TAB 2: PROCESOS
# ======================
tab2 = ttk.Frame(notebook)
notebook.add(tab2, text="Aplicaciones")

# Tabla
tree = ttk.Treeview(tab2, columns=("PID", "Nombre", "CPU", "RAM"), show="headings")
tree.heading("PID", text="PID")
tree.heading("Nombre", text="Nombre")
tree.heading("CPU", text="CPU (%)")
tree.heading("RAM", text="RAM (MB)")
tree.pack(fill="both", expand=True)

# ======================
# GRÁFICA PROCESO
# ======================
fig2 = plt.Figure(figsize=(5,2))
canvas2 = FigureCanvasTkAgg(fig2, master=tab2)
canvas2.get_tk_widget().pack(fill="x")

proceso_actual = {"proc": None}
valores_proc = []

# Inicializar CPU
for p in psutil.process_iter():
    try:
        p.cpu_percent(None)
    except:
        pass

# ======================
# ACTUALIZAR TABLA
# ======================
def actualizar_tabla():
    for row in tree.get_children():
        tree.delete(row)

    procesos = []

    for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
        try:
            cpu = proc.cpu_percent()
            ram = proc.info['memory_info'].rss / (1024 * 1024)

            if ram > 30:
                procesos.append((proc, cpu, ram))
        except:
            pass

    procesos.sort(key=lambda x: x[2], reverse=True)

    for proc, cpu, ram in procesos[:15]:
        tree.insert("", "end",
                    values=(proc.pid, proc.info['name'], f"{cpu:.1f}", f"{ram:.0f}"))

    root.after(2000, actualizar_tabla)

# ======================
# SELECCIÓN
# ======================
def seleccionar(event):
    item = tree.selection()
    if not item:
        return

    valores_proc.clear()

    valores = tree.item(item)["values"]
    pid = int(valores[0])

    try:
        proceso_actual["proc"] = psutil.Process(pid)
    except:
        proceso_actual["proc"] = None

tree.bind("<<TreeviewSelect>>", seleccionar)

# ======================
# ACTUALIZAR GRÁFICA PROCESO
# ======================
def actualizar_proc():
    proc = proceso_actual["proc"]

    if proc:
        try:
            cpu = proc.cpu_percent(interval=0.5)

            valores_proc.append(cpu)
            if len(valores_proc) > 30:
                valores_proc.pop(0)

            fig2.clear()
            ax = fig2.add_subplot(111)
            ax.plot(valores_proc)
            ax.set_title(f"{proc.name()} CPU")

            canvas2.draw()
        except:
            proceso_actual["proc"] = None

    root.after(1000, actualizar_proc)

actualizar_tabla()
actualizar_proc()

# ======================
# INICIAR
# ======================
root.mainloop()