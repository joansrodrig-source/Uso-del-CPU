import psutil
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ======================
# CONFIG VENTANA
# ======================
root = tk.Tk()
root.title("CPU Monitor PRO")
root.geometry("900x600")

# ======================
# ESTILO MODERNO
# ======================
style = ttk.Style()
style.theme_use("clam")

style.configure("TFrame", background="#1e1e1e")
style.configure("TLabel", background="#1e1e1e", foreground="white")
style.configure("TButton", background="#2d2d2d", foreground="white")
style.configure("Treeview",
                background="#2d2d2d",
                foreground="white",
                fieldbackground="#2d2d2d")

# ======================
# HEADER (ARRIBA)
# ======================
header = ttk.Frame(root)
header.pack(fill="x")

ttk.Label(header, text="CPU MONITOR PRO", font=("Arial", 16)).pack(pady=10)

# ======================
# TABS (como administrador)
# ======================
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# ======================
# TAB 1: CPU GENERAL
# ======================
tab1 = ttk.Frame(notebook)
notebook.add(tab1, text="CPU General")

fig1 = plt.Figure(figsize=(6,3))
canvas1 = FigureCanvasTkAgg(fig1, master=tab1)
canvas1.get_tk_widget().pack(fill="both", expand=True)

valores_cpu = []

def actualizar_cpu():
    cpu = psutil.cpu_percent(interval=1)

    valores_cpu.append(cpu)
    if len(valores_cpu) > 30:
        valores_cpu.pop(0)

    fig1.clear()
    ax = fig1.add_subplot(111)
    ax.plot(valores_cpu)
    ax.set_title("Uso de CPU (%)")

    canvas1.draw()
    root.after(1000, actualizar_cpu)

actualizar_cpu()

# ======================
# TAB 2: PROCESOS
# ======================
tab2 = ttk.Frame(notebook)
notebook.add(tab2, text="Aplicaciones")

# TABLA (como administrador de tareas)
tree = ttk.Treeview(tab2, columns=("PID", "Nombre", "CPU", "RAM"), show="headings")
tree.heading("PID", text="PID")
tree.heading("Nombre", text="Nombre")
tree.heading("CPU", text="CPU (%)")
tree.heading("RAM", text="RAM (MB)")
tree.pack(fill="both", expand=True)

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
                procesos.append((proc.info['pid'], proc.info['name'], cpu, ram))
        except:
            pass

    procesos.sort(key=lambda x: x[3], reverse=True)

    for p in procesos[:15]:
        tree.insert("", "end", values=(p[0], p[1], f"{p[2]:.1f}", f"{p[3]:.0f}"))

    root.after(2000, actualizar_tabla)

actualizar_tabla()

# ======================
# INICIAR APP
# ======================
root.mainloop()