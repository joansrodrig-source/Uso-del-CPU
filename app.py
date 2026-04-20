import sys
import psutil
import numpy as np
import random
from collections import deque

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import QFont

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


# =========================
# GLOBALS
# =========================
proc = None
proc_data = deque(maxlen=100)


# =========================
# CPU ENGINE
# =========================
class CPUEngine:
    def __init__(self):
        self.data = deque(maxlen=200)

    def update(self):
        v = psutil.cpu_percent(interval=None)
        self.data.append(v)
        return v

    def series(self):
        return np.array(self.data)


# =========================
# APP
# =========================
app = QApplication(sys.argv)

app.setStyleSheet("""
QWidget { background:#0b0d12; color:#eaeaea; }
QPushButton { background:#1a1f2c; padding:8px; border-radius:8px; }
QPushButton:hover { background:#232838; }
QTableWidget { background:#121522; }
QHeaderView::section { background:#1a1f2c; }
QProgressBar::chunk { background:#00d4ff; }
""")

engine = CPUEngine()


# =========================
# WINDOW
# =========================
window = QWidget()
window.setWindowTitle("MonitorCPU")
window.resize(1350, 820)

layout = QHBoxLayout(window)


# =========================
# MENU
# =========================
menu = QVBoxLayout()

btn_home = QPushButton("Inicio")
btn_cpu = QPushButton("CPU")
btn_proc = QPushButton("Procesos")
btn_calc = QPushButton("Cálculo")
btn_about = QPushButton("Acerca de")

for b in [btn_home, btn_cpu, btn_proc, btn_calc, btn_about]:
    b.setMinimumHeight(45)
    menu.addWidget(b)

menu.addStretch()

menu_widget = QWidget()
menu_widget.setLayout(menu)
menu_widget.setFixedWidth(200)


# =========================
# STACK
# =========================
stack = QStackedWidget()


# =========================
# BOT EDUCATIVO
# =========================
BOT_TEXT = [
    "La derivada mide cambio instantáneo",
    "El límite describe tendencia",
    "Si f'(x)=0 hay punto crítico",
    "Las constantes desaparecen al derivar",
    "Continuidad no implica derivabilidad",
    "El cálculo conecta gráfica y comportamiento",
    "Una derivada es la pendiente de la curva"
]


# =========================
# HOME
# =========================
home = QWidget()
hl = QVBoxLayout(home)

title = QLabel("MONITORCPU")
title.setFont(QFont("Segoe UI", 26, QFont.Bold))

bot = QLabel()
bot.setFont(QFont("Segoe UI", 16))

info = QLabel()
info.setFont(QFont("Segoe UI", 14))

hl.addWidget(title)
hl.addWidget(bot)
hl.addWidget(info)

stack.addWidget(home)


# =========================
# CPU PAGE
# =========================
cpu_page = QWidget()
cl = QVBoxLayout(cpu_page)

bar = QProgressBar()

fig_cpu = Figure()
canvas_cpu = FigureCanvas(fig_cpu)
ax_cpu = fig_cpu.add_subplot(111)

line_cpu, = ax_cpu.plot([], label="CPU")
line_deriv, = ax_cpu.plot([], label="derivada")

ax_cpu.set_ylim(0, 100)
ax_cpu.legend()

cl.addWidget(bar)
cl.addWidget(canvas_cpu)

stack.addWidget(cpu_page)


# =========================
# PROCESOS
# =========================
proc_page = QWidget()
pl = QVBoxLayout(proc_page)

btn_kill = QPushButton("Terminar proceso")

table = QTableWidget()
table.setColumnCount(4)
table.setHorizontalHeaderLabels(["PID", "Nombre", "CPU", "RAM"])

status = QLabel("Selecciona proceso")

fig_p = Figure()
canvas_p = FigureCanvas(fig_p)
ax_p = fig_p.add_subplot(111)
line_p, = ax_p.plot([])

ax_p.set_ylim(0, 100)

pl.addWidget(btn_kill)
pl.addWidget(table)
pl.addWidget(status)
pl.addWidget(canvas_p)

stack.addWidget(proc_page)


# =========================
# CALC GAME
# =========================
calc_page = QWidget()
cl2 = QVBoxLayout(calc_page)

title_game = QLabel("Juego Cálculo Diferencial")
title_game.setFont(QFont("Segoe UI", 14, QFont.Bold))

btn_start = QPushButton("Iniciar juego")

question = QLabel("")
feedback = QLabel("")
score_lbl = QLabel("Score: 0")

btnA = QPushButton("")
btnB = QPushButton("")
btnC = QPushButton("")

history = QTableWidget()
history.setColumnCount(2)
history.setHorizontalHeaderLabels(["Partida", "Score"])

cl2.addWidget(title_game)
cl2.addWidget(btn_start)
cl2.addWidget(question)
cl2.addWidget(btnA)
cl2.addWidget(btnB)
cl2.addWidget(btnC)
cl2.addWidget(feedback)
cl2.addWidget(score_lbl)
cl2.addWidget(history)

stack.addWidget(calc_page)


# =========================
# ABOUT
# =========================
about = QWidget()
al = QVBoxLayout(about)

about_title = QLabel("Acerca del proyecto")
about_title.setFont(QFont("Segoe UI", 18, QFont.Bold))

about_text = QLabel("""
MonitorCPU

Herramienta educativa de cálculo diferencial aplicada a CPU.

- CPU en tiempo real
- derivadas
- procesos activos
- juego de aprendizaje

Creado por:
Joan
Juan Roa
Juan Torres
""")

about_text.setWordWrap(True)

al.addWidget(about_title)
al.addWidget(about_text)

stack.addWidget(about)


# =========================
# GAME DATA
# =========================
questions = [
    {"q":"lim c", "a":"c", "opt":["c","0","∞"]},
    {"q":"d(c)", "a":"0", "opt":["0","c","1"]},
    {"q":"d(x^n)", "a":"n·x^(n-1)", "opt":["n·x^(n-1)","x^n","n·x^n"]},
    {"q":"d(sin x)", "a":"cos x", "opt":["cos x","-sin x","tan x"]},
]

current = {"q":None}
score = 0
active = False
history_data = []


# =========================
# GAME LOGIC
# =========================
def start_game():
    global score, active
    score = 0
    active = True
    next_q()


def next_q():
    q = random.choice(questions)
    current["q"] = q

    question.setText(q["q"])

    opts = q["opt"][:]
    random.shuffle(opts)

    btnA.setText(opts[0])
    btnB.setText(opts[1])
    btnC.setText(opts[2])

    score_lbl.setText(f"Score: {score}")


def end_game():
    global active
    active = False

    history_data.append(score)

    history.setRowCount(len(history_data))

    for i, s in enumerate(history_data):
        history.setItem(i,0,QTableWidgetItem(str(i+1)))
        history.setItem(i,1,QTableWidgetItem(str(s)))


def check(ans):
    global score, active

    if not active:
        return

    if ans == current["q"]["a"]:
        score += 1
        feedback.setText("Correcto")
        next_q()
    else:
        feedback.setText("Incorrecto")
        end_game()


btn_start.clicked.connect(start_game)
btnA.clicked.connect(lambda: check(btnA.text()))
btnB.clicked.connect(lambda: check(btnB.text()))
btnC.clicked.connect(lambda: check(btnC.text()))


# =========================
# PROCESS CONTROL FIX
# =========================
def update_table():
    procs = []

    for p in psutil.process_iter(['pid','name']):
        try:
            cpu = p.cpu_percent(interval=None)
            ram = p.memory_info().rss / 1024 / 1024
            procs.append((p.pid,p.info['name'],cpu,ram))
        except:
            pass

    procs = sorted(procs, key=lambda x: x[2], reverse=True)[:10]

    table.setRowCount(len(procs))

    for i,p in enumerate(procs):
        table.setItem(i,0,QTableWidgetItem(str(p[0])))
        table.setItem(i,1,QTableWidgetItem(str(p[1])))
        table.setItem(i,2,QTableWidgetItem(f"{p[2]:.1f}"))
        table.setItem(i,3,QTableWidgetItem(f"{p[3]:.1f}"))


def select_proc():
    global proc, proc_data

    row = table.currentRow()
    if row < 0:
        return

    pid = int(table.item(row,0).text())

    try:
        proc = psutil.Process(pid)
        proc_data.clear()
        status.setText(proc.name())
    except:
        proc = None


def kill_proc():
    global proc

    if proc is None:
        status.setText("No proceso")
        return

    try:
        proc.terminate()
        proc = None
        proc_data.clear()
        status.setText("Proceso terminado")
    except:
        status.setText("Error")


btn_kill.clicked.connect(kill_proc)
table.clicked.connect(select_proc)


# =========================
# UPDATES
# =========================
def update_cpu():
    v = engine.update()

    y = engine.series()
    x = np.arange(len(y))

    line_cpu.set_data(x,y)

    if len(y)>2:
        d = np.gradient(y)
        line_deriv.set_data(x,d)

    ax_cpu.relim()
    ax_cpu.autoscale_view()

    bar.setValue(int(v))
    canvas_cpu.draw_idle()


def update_home():
    info.setText(f"Cores: {psutil.cpu_count()}")
    bot.setText(random.choice(BOT_TEXT))


def update_proc():
    global proc

    if proc is None:
        return

    try:
        cpu = proc.cpu_percent(interval=None)
        proc_data.append(cpu)

        y = np.array(proc_data)
        x = np.arange(len(y))

        line_p.set_data(x,y)
        ax_p.relim()
        ax_p.autoscale_view()
        canvas_p.draw_idle()

    except:
        proc = None


# =========================
# NAV
# =========================
btn_home.clicked.connect(lambda: stack.setCurrentIndex(0))
btn_cpu.clicked.connect(lambda: stack.setCurrentIndex(1))
btn_proc.clicked.connect(lambda: stack.setCurrentIndex(2))
btn_calc.clicked.connect(lambda: stack.setCurrentIndex(3))
btn_about.clicked.connect(lambda: stack.setCurrentIndex(4))


layout.addWidget(menu_widget)
layout.addWidget(stack)


# =========================
# TIMERS
# =========================
t1 = QTimer(); t1.timeout.connect(update_home); t1.start(2000)
t2 = QTimer(); t2.timeout.connect(update_cpu); t2.start(1000)
t3 = QTimer(); t3.timeout.connect(update_table); t3.start(3000)
t4 = QTimer(); t4.timeout.connect(update_proc); t4.start(1000)


window.show()
sys.exit(app.exec())