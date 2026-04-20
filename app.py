import sys
import psutil
from PySide6.QtWidgets import *
from PySide6.QtCore import QTimer
from PySide6.QtGui import QFont
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

app = QApplication(sys.argv)

# ======================
# VENTANA
# ======================
window = QWidget()
window.setWindowTitle("Monitor PRO MAX")
window.resize(1100, 650)

main_layout = QHBoxLayout()

# ======================
# MENU LATERAL
# ======================
menu = QVBoxLayout()

btn_inicio = QPushButton("Inicio")
btn_cpu = QPushButton("CPU")
btn_apps = QPushButton("Aplicaciones")
btn_rend = QPushButton("Rendimiento")
btn_about = QPushButton("Acerca de")

menu.addWidget(btn_inicio)
menu.addWidget(btn_cpu)
menu.addWidget(btn_apps)
menu.addWidget(btn_rend)
menu.addWidget(btn_about)
menu.addStretch()

menu_widget = QWidget()
menu_widget.setLayout(menu)
menu_widget.setFixedWidth(160)

# ======================
# STACK
# ======================
stack = QStackedWidget()

# ======================
# INICIO
# ======================
inicio = QWidget()
inicio_layout = QVBoxLayout()

label_info = QLabel("Cargando...")
label_info.setFont(QFont("Segoe UI", 12))

inicio_layout.addWidget(label_info)
inicio.setLayout(inicio_layout)
stack.addWidget(inicio)

# ======================
# CPU GENERAL
# ======================
cpu_tab = QWidget()
cpu_layout = QVBoxLayout()

cpu_bar = QProgressBar()
cpu_layout.addWidget(cpu_bar)

fig_cpu = Figure()
canvas_cpu = FigureCanvas(fig_cpu)
cpu_layout.addWidget(canvas_cpu)

valores_cpu = []

def update_cpu():
    cpu = psutil.cpu_percent()
    cpu_bar.setValue(int(cpu))

    valores_cpu.append(cpu)
    if len(valores_cpu) > 30:
        valores_cpu.pop(0)

    fig_cpu.clear()
    ax = fig_cpu.add_subplot(111)
    ax.plot(valores_cpu)
    ax.set_title("CPU (%)")
    canvas_cpu.draw()

cpu_tab.setLayout(cpu_layout)
stack.addWidget(cpu_tab)

# ======================
# APLICACIONES
# ======================
apps_tab = QWidget()
apps_layout = QVBoxLayout()

table = QTableWidget()
table.setColumnCount(4)
table.setHorizontalHeaderLabels(["PID", "Nombre", "CPU", "RAM"])
apps_layout.addWidget(table)

btn_kill = QPushButton("Cerrar proceso seleccionado")
apps_layout.addWidget(btn_kill)

fig_proc = Figure()
canvas_proc = FigureCanvas(fig_proc)
apps_layout.addWidget(canvas_proc)

valores_proc = []
proceso_actual = None

def update_table():
    procesos = []

    for p in psutil.process_iter(['pid', 'name', 'memory_info']):
        try:
            ram = p.info['memory_info'].rss / (1024*1024)
            cpu = p.cpu_percent()

            if ram > 30:
                procesos.append((p.pid, p.info['name'], cpu, ram))
        except:
            pass

    procesos.sort(key=lambda x: x[3], reverse=True)

    table.setRowCount(len(procesos[:15]))

    for i, p in enumerate(procesos[:15]):
        table.setItem(i, 0, QTableWidgetItem(str(p[0])))
        table.setItem(i, 1, QTableWidgetItem(p[1]))
        table.setItem(i, 2, QTableWidgetItem(f"{p[2]:.1f}"))
        table.setItem(i, 3, QTableWidgetItem(f"{p[3]:.0f}"))

def seleccionar():
    global proceso_actual
    row = table.currentRow()
    if row < 0:
        return

    pid = int(table.item(row, 0).text())

    try:
        proceso_actual = psutil.Process(pid)
        valores_proc.clear()
    except:
        proceso_actual = None

table.clicked.connect(seleccionar)

def update_proc():
    global proceso_actual

    if proceso_actual:
        try:
            cpu = proceso_actual.cpu_percent(interval=0.5)

            valores_proc.append(cpu)
            if len(valores_proc) > 30:
                valores_proc.pop(0)

            fig_proc.clear()
            ax = fig_proc.add_subplot(111)
            ax.plot(valores_proc)
            ax.set_title(f"{proceso_actual.name()} CPU")

            canvas_proc.draw()
        except:
            proceso_actual = None

def kill_process():
    row = table.currentRow()
    if row < 0:
        return

    pid = int(table.item(row, 0).text())
    try:
        psutil.Process(pid).terminate()
    except:
        pass

btn_kill.clicked.connect(kill_process)

apps_tab.setLayout(apps_layout)
stack.addWidget(apps_tab)

# ======================
# RENDIMIENTO
# ======================
rend_tab = QWidget()
rend_layout = QVBoxLayout()

label_temp = QLabel("Temperatura: No disponible")
rend_layout.addWidget(label_temp)

rend_tab.setLayout(rend_layout)
stack.addWidget(rend_tab)

def update_temp():
    try:
        temps = psutil.sensors_temperatures()
        if temps:
            for name, entries in temps.items():
                for entry in entries:
                    label_temp.setText(f"Temperatura: {entry.current} °C")
                    return
    except:
        pass

# ======================
# ACERCA DE
# ======================
about_tab = QWidget()
about_layout = QVBoxLayout()

titulo = QLabel("CPU Monitor PRO MAX")
titulo.setFont(QFont("Segoe UI", 16))

info = QLabel("""
Proyecto universitario desarrollado para el análisis del uso de la CPU 
mediante cálculo diferencial y monitoreo en tiempo real.

👨‍💻 Creadores:
- Joan Rodriguez
- Juan Roa
- Juan Torres

🎯 Propósito:
Analizar el rendimiento del sistema, visualizar el uso de CPU y permitir 
la gestión de procesos para optimizar el funcionamiento del equipo.
""")

info.setWordWrap(True)

about_layout.addWidget(titulo)
about_layout.addWidget(info)

about_tab.setLayout(about_layout)
stack.addWidget(about_tab)

# ======================
# INICIO INFO
# ======================
def update_inicio():
    procesos = []

    for p in psutil.process_iter(['pid', 'name']):
        try:
            cpu = p.cpu_percent()
            procesos.append((p.info['name'], cpu))
        except:
            pass

    if procesos:
        top = max(procesos, key=lambda x: x[1])
        label_info.setText(
            f"App más activa: {top[0]} ({top[1]}%)\nRecomendación: cerrar apps pesadas."
        )

# ======================
# BOTONES
# ======================
btn_inicio.clicked.connect(lambda: stack.setCurrentIndex(0))
btn_cpu.clicked.connect(lambda: stack.setCurrentIndex(1))
btn_apps.clicked.connect(lambda: stack.setCurrentIndex(2))
btn_rend.clicked.connect(lambda: stack.setCurrentIndex(3))
btn_about.clicked.connect(lambda: stack.setCurrentIndex(4))

# ======================
# TIMERS
# ======================
QTimer.singleShot(0, lambda: [p.cpu_percent(None) for p in psutil.process_iter()])

t1 = QTimer()
t1.timeout.connect(update_cpu)
t1.start(1000)

t2 = QTimer()
t2.timeout.connect(update_table)
t2.start(2000)

t3 = QTimer()
t3.timeout.connect(update_proc)
t3.start(1000)

t4 = QTimer()
t4.timeout.connect(update_inicio)
t4.start(2000)

t5 = QTimer()
t5.timeout.connect(update_temp)
t5.start(3000)

# ======================
# ESTILO
# ======================
app.setStyleSheet("""
QWidget { background: #1e1e1e; color: white; font-family: Segoe UI; }
QPushButton { background: #2b2b2b; padding: 8px; }
QPushButton:hover { background: #3a3a3a; }
QProgressBar { background: #2b2b2b; }
QProgressBar::chunk { background: #0078D7; }
QTableWidget { background: #2b2b2b; }
""")

# ======================
# FINAL
# ======================
main_layout.addWidget(menu_widget)
main_layout.addWidget(stack)

window.setLayout(main_layout)
window.show()

sys.exit(app.exec())