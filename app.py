import sys
import psutil

from PySide6.QtWidgets import *
from PySide6.QtCore import QTimer, Qt, QThread, Signal
from PySide6.QtGui import QFont

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


# ======================
# THREAD CPU (ESTABLE)
# ======================
class CPUThread(QThread):
    update_cpu = Signal(float)

    def run(self):
        # primera lectura "calienta psutil"
        psutil.cpu_percent(interval=None)

        while True:
            cpu = psutil.cpu_percent(interval=1)
            self.update_cpu.emit(cpu)


# ======================
# APP
# ======================
app = QApplication(sys.argv)


# ======================
# VENTANA PRINCIPAL
# ======================
window = QWidget()
window.setWindowTitle("MonirtoCPU Pro 🚀")
window.resize(1100, 650)

main_layout = QHBoxLayout(window)


# ======================
# MENU LATERAL
# ======================
menu = QVBoxLayout()

btn_inicio = QPushButton("Inicio")
btn_cpu = QPushButton("CPU")
btn_apps = QPushButton("Procesos")
btn_about = QPushButton("Acerca de")

for b in [btn_inicio, btn_cpu, btn_apps, btn_about]:
    b.setMinimumHeight(45)
    b.setCursor(Qt.PointingHandCursor)
    menu.addWidget(b)

menu.addStretch()

menu_widget = QWidget()
menu_widget.setLayout(menu)
menu_widget.setFixedWidth(170)


# ======================
# STACK (PÁGINAS)
# ======================
stack = QStackedWidget()


# ======================
# 1. INICIO
# ======================
inicio = QWidget()
inicio_layout = QVBoxLayout(inicio)

label_cpu = QLabel("CPU: ...")
label_cores = QLabel("Núcleos: ...")
label_top = QLabel("Proceso más activo: ...")

for l in [label_cpu, label_cores, label_top]:
    l.setFont(QFont("Segoe UI", 12))
    inicio_layout.addWidget(l)

stack.addWidget(inicio)


# ======================
# 2. CPU (GRÁFICA GLOBAL)
# ======================
cpu_tab = QWidget()
cpu_layout = QVBoxLayout(cpu_tab)

cpu_bar = QProgressBar()

fig_cpu = Figure()
canvas_cpu = FigureCanvas(fig_cpu)

cpu_layout.addWidget(cpu_bar)
cpu_layout.addWidget(canvas_cpu)

cpu_data = []


def update_cpu_graph(cpu):
    cpu_bar.setValue(int(cpu))

    cpu_data.append(cpu)
    if len(cpu_data) > 40:
        cpu_data.pop(0)

    fig_cpu.clear()
    ax = fig_cpu.add_subplot(111)
    ax.plot(cpu_data)
    ax.set_title("Uso de CPU (%)")
    ax.set_ylim(0, 100)

    canvas_cpu.draw()


stack.addWidget(cpu_tab)


# ======================
# 3. PROCESOS
# ======================
apps_tab = QWidget()
apps_layout = QVBoxLayout(apps_tab)

table = QTableWidget()
table.setColumnCount(4)
table.setHorizontalHeaderLabels(["PID", "Nombre", "CPU %", "RAM MB"])
apps_layout.addWidget(table)

fig_proc = Figure()
canvas_proc = FigureCanvas(fig_proc)
apps_layout.addWidget(canvas_proc)

proc_data = []
current_proc = None


def update_table():
    procesos = []

    for p in psutil.process_iter(['pid', 'name', 'memory_info']):
        try:
            cpu = p.cpu_percent(interval=None)
            ram = p.info['memory_info'].rss / 1024 / 1024
            procesos.append((p.pid, p.info['name'], cpu, ram))
        except:
            pass

    procesos.sort(key=lambda x: x[2], reverse=True)
    procesos = procesos[:10]

    table.setRowCount(len(procesos))

    for i, p in enumerate(procesos):
        table.setItem(i, 0, QTableWidgetItem(str(p[0])))
        table.setItem(i, 1, QTableWidgetItem(str(p[1])))
        table.setItem(i, 2, QTableWidgetItem(f"{p[2]:.1f}"))
        table.setItem(i, 3, QTableWidgetItem(f"{p[3]:.1f}"))


def select_process():
    global current_proc
    row = table.currentRow()

    if row < 0:
        return

    pid = int(table.item(row, 0).text())

    try:
        current_proc = psutil.Process(pid)
        proc_data.clear()
    except:
        current_proc = None


table.clicked.connect(select_process)


def update_process_graph():
    global current_proc

    if current_proc:
        try:
            cpu = current_proc.cpu_percent(interval=None)

            proc_data.append(cpu)
            if len(proc_data) > 40:
                proc_data.pop(0)

            fig_proc.clear()
            ax = fig_proc.add_subplot(111)
            ax.plot(proc_data)
            ax.set_title(f"{current_proc.name()} CPU")
            ax.set_ylim(0, 100)

            canvas_proc.draw()

        except:
            current_proc = None


stack.addWidget(apps_tab)


# ======================
# 4. ABOUT
# ======================
about = QWidget()
about_layout = QVBoxLayout(about)

about_layout.addWidget(QLabel("MonirtoCPU Pro"))
about_layout.addWidget(QLabel("Proyecto universitario"))
about_layout.addWidget(QLabel("Joan Rodriguez"))

stack.addWidget(about)


# ======================
# INICIO UPDATE
# ======================
def update_inicio():
    cpu = psutil.cpu_percent(interval=None)

    label_cpu.setText(f"CPU: {cpu}%")
    label_cores.setText(f"Núcleos: {psutil.cpu_count()}")

    top = ("-", 0)

    for p in psutil.process_iter(['name']):
        try:
            cpu_p = p.cpu_percent(interval=None)
            if cpu_p > top[1]:
                top = (p.info['name'], cpu_p)
        except:
            pass

    label_top.setText(f"Proceso más activo: {top[0]} ({top[1]:.1f}%)")


# ======================
# BOTONES
# ======================
btn_inicio.clicked.connect(lambda: stack.setCurrentIndex(0))
btn_cpu.clicked.connect(lambda: stack.setCurrentIndex(1))
btn_apps.clicked.connect(lambda: stack.setCurrentIndex(2))
btn_about.clicked.connect(lambda: stack.setCurrentIndex(3))


# ======================
# THREAD CPU
# ======================
thread = CPUThread()
thread.update_cpu.connect(update_cpu_graph)
thread.start()


# ======================
# TIMERS (SIN CONGELAR)
# ======================
QTimer().singleShot(1000, update_inicio)
timer_inicio = QTimer()
timer_inicio.timeout.connect(update_inicio)
timer_inicio.start(2000)

timer_table = QTimer()
timer_table.timeout.connect(update_table)
timer_table.start(3000)

timer_proc = QTimer()
timer_proc.timeout.connect(update_process_graph)
timer_proc.start(1000)


# ======================
# UI FINAL
# ======================
main_layout.addWidget(menu_widget)
main_layout.addWidget(stack)

window.show()

sys.exit(app.exec())