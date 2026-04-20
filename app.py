import sys
import psutil
from PySide6.QtWidgets import *
from PySide6.QtCore import QTimer, Qt, QPropertyAnimation
from PySide6.QtGui import QFont, QIcon
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

app = QApplication(sys.argv)

# ======================
# VENTANA
# ======================
window = QWidget()
window.setWindowTitle("MonirtoCPU")
window.resize(1150, 680)

main_layout = QHBoxLayout()

# ======================
# MENU LATERAL
# ======================
menu = QVBoxLayout()

btn_inicio = QPushButton(" Inicio")
btn_cpu = QPushButton(" CPU")
btn_apps = QPushButton(" Aplicaciones")
btn_about = QPushButton(" Acerca de")

# ICONOS (si tienes carpeta icons/)
btn_inicio.setIcon(QIcon("icons/home.png"))
btn_cpu.setIcon(QIcon("icons/cpu.png"))
btn_apps.setIcon(QIcon("icons/apps.png"))
btn_about.setIcon(QIcon("icons/info.png"))

for b in [btn_inicio, btn_cpu, btn_apps, btn_about]:
    b.setCursor(Qt.PointingHandCursor)
    b.setMinimumHeight(40)
    menu.addWidget(b)

menu.addStretch()

menu_widget = QWidget()
menu_widget.setLayout(menu)
menu_widget.setFixedWidth(170)

# ======================
# STACK
# ======================
stack = QStackedWidget()

# ======================
# ANIMACIÓN
# ======================
def cambiar_pantalla(index):
    anim = QPropertyAnimation(stack, b"windowOpacity")
    anim.setDuration(200)
    anim.setStartValue(0.5)
    anim.setEndValue(1.0)
    anim.start()
    stack.setCurrentIndex(index)

# ======================
# INICIO
# ======================
inicio = QWidget()
inicio_layout = QVBoxLayout()

titulo_inicio = QLabel("Panel de Monitoreo")
titulo_inicio.setFont(QFont("Segoe UI", 16, QFont.Bold))

stats_layout = QHBoxLayout()

label_cpu = QLabel("CPU: 0%")
label_ram = QLabel("RAM: 0%")
label_nucleos = QLabel("Núcleos: 0")

for lbl in [label_cpu, label_ram, label_nucleos]:
    lbl.setFont(QFont("Segoe UI", 12))
    stats_layout.addWidget(lbl)

label_top = QLabel("App más activa: ...")
label_recomendacion = QLabel("Recomendación: ...")

inicio_layout.addWidget(titulo_inicio)
inicio_layout.addLayout(stats_layout)
inicio_layout.addWidget(label_top)
inicio_layout.addWidget(label_recomendacion)

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
    if len(valores_cpu) > 40:
        valores_cpu.pop(0)

    fig_cpu.clear()
    ax = fig_cpu.add_subplot(111)
    ax.plot(valores_cpu)
    ax.set_title("Uso de CPU (%)")
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

btn_kill = QPushButton("Cerrar proceso")
apps_layout.addWidget(btn_kill)

fig_proc = Figure()
canvas_proc = FigureCanvas(fig_proc)
apps_layout.addWidget(canvas_proc)

valores_proc = []
proceso_actual = None

def update_table():
    procesos = []
    for p in psutil.process_iter(['pid','name','memory_info']):
        try:
            ram = p.info['memory_info'].rss / (1024*1024)
            cpu = p.cpu_percent()
            if ram > 20:
                procesos.append((p.pid,p.info['name'],cpu,ram))
        except:
            pass

    procesos.sort(key=lambda x: x[3], reverse=True)
    table.setRowCount(len(procesos[:15]))

    for i,p in enumerate(procesos[:15]):
        table.setItem(i,0,QTableWidgetItem(str(p[0])))
        table.setItem(i,1,QTableWidgetItem(p[1]))
        table.setItem(i,2,QTableWidgetItem(str(p[2])))
        table.setItem(i,3,QTableWidgetItem(str(int(p[3]))))

def seleccionar():
    global proceso_actual
    row = table.currentRow()
    if row < 0: return
    pid = int(table.item(row,0).text())
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
            if len(valores_proc) > 40:
                valores_proc.pop(0)

            fig_proc.clear()
            ax = fig_proc.add_subplot(111)
            ax.plot(valores_proc)
            ax.set_title(proceso_actual.name())
            canvas_proc.draw()
        except:
            proceso_actual = None

def kill_process():
    row = table.currentRow()
    if row < 0: return
    pid = int(table.item(row,0).text())
    try:
        psutil.Process(pid).terminate()
    except:
        pass

btn_kill.clicked.connect(kill_process)

apps_tab.setLayout(apps_layout)
stack.addWidget(apps_tab)

# ======================
# ACERCA DE
# ======================
about = QWidget()
layout_about = QVBoxLayout()

layout_about.addWidget(QLabel("MonirtoCPU"))
layout_about.addWidget(QLabel("Proyecto universitario"))
layout_about.addWidget(QLabel("Creadores:\nJoan Rodriguez\nJuan Roa\nJuan Torres"))

about.setLayout(layout_about)
stack.addWidget(about)

# ======================
# BOTONES
# ======================
btn_inicio.clicked.connect(lambda: cambiar_pantalla(0))
btn_cpu.clicked.connect(lambda: cambiar_pantalla(1))
btn_apps.clicked.connect(lambda: cambiar_pantalla(2))
btn_about.clicked.connect(lambda: cambiar_pantalla(3))

# ======================
# TIMERS
# ======================
QTimer(interval=1000, timeout=update_cpu).start()
QTimer(interval=2000, timeout=update_table).start()
QTimer(interval=1000, timeout=update_proc).start()

# ======================
# ESTILO
# ======================
app.setStyleSheet("""
QWidget {background:#1e1e1e;color:white;font-family:Segoe UI;}
QPushButton {background:#2b2b2b;border-radius:6px;padding:8px;}
QPushButton:hover {background:#3a3a3a;}
QProgressBar {background:#2b2b2b;}
QProgressBar::chunk {background:#0078D7;}
QTableWidget {background:#2b2b2b;}
""")

# ======================
# FINAL
# ======================
main_layout.addWidget(menu_widget)
main_layout.addWidget(stack)

window.setLayout(main_layout)
window.show()

sys.exit(app.exec())