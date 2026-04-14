import psutil
import matplotlib.pyplot as plt
from tkinter import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# COLORES
BG = "#0f0f0f"
FG = "white"
BTN = "#1f1f1f"


# VENTANA

root = Tk()
root.title("Monitor CPU PRO")
root.geometry("800x600")
root.configure(bg=BG)

frame = Frame(root, bg=BG)
frame.pack(fill="both", expand=True)


# LIMPIAR

def limpiar():
    for widget in frame.winfo_children():
        widget.destroy()


# MENÚ

def menu():
    limpiar()

    Label(frame, text="MONITOR DE CPU", font=("Arial", 20), bg=BG, fg=FG).pack(pady=20)

    Button(frame, text="CPU General", bg=BTN, fg=FG, width=20, command=cpu_general).pack(pady=10)
    Button(frame, text="CPU por Aplicaciones", bg=BTN, fg=FG, width=20, command=cpu_apps).pack(pady=10)


# CPU GENERAL

valores_cpu = []

def cpu_general():
    limpiar()

    Label(frame, text="CPU EN TIEMPO REAL", font=("Arial", 14), bg=BG, fg=FG).pack()

    fig = plt.Figure(figsize=(6,3), facecolor=BG)
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.get_tk_widget().pack()

    def actualizar():
        cpu = psutil.cpu_percent(interval=1)

        valores_cpu.append(cpu)
        if len(valores_cpu) > 20:
            valores_cpu.pop(0)

        fig.clear()
        ax = fig.add_subplot(111)
        ax.plot(valores_cpu)

        ax.set_facecolor(BG)
        ax.tick_params(colors=FG)
        ax.set_title("CPU (%)", color=FG)
        ax.grid()

        canvas.draw()
        root.after(1000, actualizar)

    actualizar()

    Button(frame, text="Volver", bg=BTN, fg=FG, command=menu).pack(pady=10)


# CPU POR APPS

def cpu_apps():
    limpiar()

    Label(frame, text="APLICACIONES ACTIVAS", font=("Arial", 14), bg=BG, fg=FG).pack()

    lista = Listbox(frame, width=60, bg=BTN, fg=FG)
    lista.pack(pady=10)

    fig = plt.Figure(figsize=(6,3), facecolor=BG)
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.get_tk_widget().pack()

    proceso_actual = {"proc": None}
    valores = []

    
    for p in psutil.process_iter():
        try:
            p.cpu_percent(None)
        except:
            pass

    def actualizar_lista():
        lista.delete(0, END)

        procesos = []
        for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
            try:
                ram = proc.info['memory_info'].rss / (1024 * 1024)
                if ram > 50:
                    procesos.append((proc, ram))
            except:
                pass

        procesos.sort(key=lambda x: x[1], reverse=True)

        for proc, ram in procesos[:10]:
            lista.insert(END, f"{proc.info['name']} ({proc.pid}) → {ram:.0f}MB")

        root.after(3000, actualizar_lista)

    def seleccionar(event):
        if not lista.curselection():
            return

        index = lista.curselection()[0]
        texto = lista.get(index)

        pid = int(texto.split("(")[1].split(")")[0])

        try:
            proceso_actual["proc"] = psutil.Process(pid)
            valores.clear()
        except:
            proceso_actual["proc"] = None

    lista.bind("<<ListboxSelect>>", seleccionar)

    def actualizar_grafica():
        proc = proceso_actual["proc"]

        if proc:
            try:
                cpu = proc.cpu_percent(interval=0.5)

                valores.append(cpu)
                if len(valores) > 20:
                    valores.pop(0)

                fig.clear()
                ax = fig.add_subplot(111)
                ax.plot(valores)

                ax.set_facecolor(BG)
                ax.tick_params(colors=FG)
                ax.set_title(f"CPU: {proc.name()}", color=FG)
                ax.grid()

                canvas.draw()

            except:
                proceso_actual["proc"] = None

        root.after(1000, actualizar_grafica)

    actualizar_lista()
    actualizar_grafica()

    Button(frame, text="Volver", bg=BTN, fg=FG, command=menu).pack(pady=10)



menu()
root.mainloop()