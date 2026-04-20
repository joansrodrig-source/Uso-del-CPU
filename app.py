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
window.resize(1100, 650)

main_layout = QHBoxLayout()

# ======================
# MENU
# ======================
menu = QVBoxLayout()

btn_inicio = QPushButton("Inicio")
btn_cpu = QPushButton("CPU")
btn_apps = QPushButton("Aplicaciones")
btn_about = QPushButton("Acerca de")

for b in [btn_inicio, btn_cpu, btn_apps, btn_about]:
    b.setMinimumHeight(40)
    b.setCursor(Qt.PointingHandCursor)
    menu.addWidget(b)

menu.addStretch()

menu_widget = QWidget()
menu_widget.setLayout(menu)
menu_widget.setFixedWidth(160)

# ======================
# STACK
# ======================
stack = QStackedWidget()

# ======================
# ANIMACION
# ======================
def cambiar(index):
    anim = QPropertyAnimation(stack, b"windowOpacity")
    anim.setDuration(200)
    anim.setStartValue(0.6)
    anim.setEndValue(1)
    anim.start()
    stack.setCurrentIndex(index)

# ======================
# INICIO
# ======================
inicio = QWidget()
inicio_layout = QVBoxLayout()

titulo = QLabel("Panel de Monitoreo")
titulo.setFont(QFont("Segoe UI", 16, QFont.Bold))

label_cpu = QLabel("CPU: 0%")
label_nucleos = QLabel("Núcleos: 0")
label_top = QLabel("App más activa: ...")
label_rec = QLabel("Recomendación: ...")

for lbl in [label_cpu, label_nucleos, label_top, label_rec]:
    lbl.setFont(QFont("Segoe UI", 12))
    inicio_layout.addWidget(lbl)

inicio.setLayout(inicio_layout)
stack.addWidget(inicio)

# ======================
# CPU
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
    cpu = psutil.cpu_percent(interval=None)
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
            cpu = p.cpu_percent(interval=None)
            ram = p.info['memory_info'].rss / (1024*1024)

            procesos.append((p.pid, p.info['name'], cpu, ram))
        except:
            pass

    procesos.sort(key=lambda x: x[2], reverse=True)

    table.setRowCount(len(procesos[:15]))

    for i, p in enumerate(procesos[:15]):
        table.setItem(i,0,QTableWidgetItem(str(p[0])))
        table.setItem(i,1,QTableWidgetItem(p[1]))
        table.setItem(i,2,QTableWidgetItem(f"{p[2]:.1f}"))
        table.setItem(i,3,QTableWidgetItem(f"{p[3]:.0f}"))

def seleccionar():
    global proceso_actual
    row = table.currentRow()
    if row < 0:
        return

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
            cpu = proceso_actual.cpu_percent(interval=None)

            valores_proc.append(cpu)
            if len(valores_proc) > 30:
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
    if row < 0:
        return

    pid = int(table.item(row,0).text())
    try:
        psutil.Process(pid).terminate()
    except:
        pass

btn_kill.clicked.connect(kill_process)

apps_tab.setLayout(apps_layout)
stack.addWidget(apps_tab)

# ======================
# ABOUT
# ======================
about = QWidget()
about_layout = QVBoxLayout()

about_layout.addWidget(QLabel("MonirtoCPU"))
about_layout.addWidget(QLabel("Proyecto universitario"))
about_layout.addWidget(QLabel("Creadores:\nJoan Rodriguez\nJuan Roa\nJuan Torres"))

about.setLayout(about_layout)
stack.addWidget(about)

# ======================
# INICIO UPDATE
# ======================
def update_inicio():
    cpu = psutil.cpu_percent(interval=None)
    nucleos = psutil.cpu_count()

    label_cpu.setText(f"CPU: {cpu}%")
    label_nucleos.setText(f"Núcleos: {nucleos}")

    procesos = []
    for p in psutil.process_iter(['name']):
        try:
            uso = p.cpu_percent(interval=None)
            procesos.append((p.info['name'], uso))
        except:
            pass

    if procesos:
        top = max(procesos, key=lambda x: x[1])
        label_top.setText(f"App más activa: {top[0]} ({top[1]}%)")

    if cpu > 80:
        label_rec.setText("Alto uso de CPU")
    else:
        label_rec.setText("Sistema estable")

# ======================
# BOTONES
# ======================
btn_inicio.clicked.connect(lambda: cambiar(0))
btn_cpu.clicked.connect(lambda: cambiar(1))
btn_apps.clicked.connect(lambda: cambiar(2))
btn_about.clicked.connect(lambda: cambiar(3))

# ======================
# CALENTAR PSUTIL (CLAVE)
# ======================
for p in psutil.process_iter():
    try:
        p.cpu_percent(None)
    except:
        pass

psutil.cpu_percent(None)

# ======================
# TIMERS
# ======================
QTimer(interval=1000, timeout=update_cpu).start()
QTimer(interval=2000, timeout=update_table).start()
QTimer(interval=1000, timeout=update_proc).start()
QTimer(interval=2000, timeout=update_inicio).start()

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