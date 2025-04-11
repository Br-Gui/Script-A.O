import pyautogui
import time
import random
import keyboard
import sys

# --- Configuração ---
TOGGLE_HOTKEY = 'f9'
RECORD_HOTKEY = 'f8'
SCRIPT_RUNNING = False
SCRIPT_PAUSED = False
PAUSE_HOTKEY = 'f10'
MIN_REACTION_TIME = 0.3
MAX_REACTION_TIME = 0.8
MOUSE_MOVE_MIN_DURATION = 0.2
MOUSE_MOVE_MAX_DURATION = 0.5
MOUSE_COORD_OFFSET = 5
LOOP_DELAY_MIN = 2  # Mínimo delay entre loops (segundos)
LOOP_DELAY_MAX = 5  # Máximo delay entre loops (segundos)

recorded_actions = []  # Lista para armazenar (x, y, button, delay)

# --- Funções de Simulação Humana ---
def human_like_delay(min_time, max_time):
    delay = random.uniform(min_time, max_time)
    time.sleep(delay)

def human_like_mouse_move(x, y):
    target_x = int(x + random.gauss(0, MOUSE_COORD_OFFSET))
    target_y = int(y + random.gauss(0, MOUSE_COORD_OFFSET))
    duration = random.uniform(MOUSE_MOVE_MIN_DURATION, MOUSE_MOVE_MAX_DURATION)
    pyautogui.moveTo(target_x, target_y, duration=duration)

def human_like_click(button='left'):
    human_like_delay(MIN_REACTION_TIME, MAX_REACTION_TIME)
    pyautogui.click(button=button)

# --- Funções de Gravação e Execução ---
def record_action():
    if not SCRIPT_RUNNING:
        x, y = pyautogui.position()
        while True:
            button_choice = input("Botão para este ponto (left/right)? ").lower()
            if button_choice in ['left', 'right']:
                break
            else:
                print("Opção inválida. Digite 'left' ou 'right'.")

        while True:
            delay_str = input("Delay após este clique (em segundos)? ")
            try:
                delay = float(delay_str)
                break
            except ValueError:
                print("Entrada inválida. Digite um número para o delay.")

        recorded_actions.append((x, y, button_choice, delay))
        print(f"Ação gravada: ({x}, {y}), botão '{button_choice}', delay {delay}s")

def executar_sequencia():
    if not SCRIPT_RUNNING or SCRIPT_PAUSED:
        return

    if not recorded_actions:
        print("Nenhuma ação gravada para executar.")
        return

    print("Executando sequência de ações...")
    for i, (x, y, button, delay) in enumerate(recorded_actions):
        if not SCRIPT_RUNNING or SCRIPT_PAUSED:
            break
        print(f"Movendo para o ponto {i+1}: ({x}, {y}) e clicando com '{button}'...")
        human_like_mouse_move(x, y)
        human_like_click(button=button)
        print(f"Aguardando {delay} segundos...")
        time.sleep(delay)

    print("Fim da sequência de ações.")

# --- Funções de Controle ---
def toggle_script_state():
    global SCRIPT_RUNNING, SCRIPT_PAUSED
    SCRIPT_RUNNING = not SCRIPT_RUNNING
    SCRIPT_PAUSED = False
    status = "ATIVADO" if SCRIPT_RUNNING else "DESATIVADO"
    print(f"--- Script {status} ---")
    if SCRIPT_RUNNING:
        print("Pressione F8 para gravar as ações do mouse (posição, botão, delay).")
        print("Pressione F9 para iniciar/parar a execução em loop.")
        print("Pressione F10 para pausar/retomar a execução.")

def pause_script():
    global SCRIPT_PAUSED, SCRIPT_RUNNING
    if SCRIPT_RUNNING:
        SCRIPT_PAUSED = not SCRIPT_PAUSED
        status = "PAUSADO" if SCRIPT_PAUSED else "RETOMADO"
        print(f"--- Script {status} ---")

def setup_hotkeys():
    try:
        keyboard.remove_hotkey(TOGGLE_HOTKEY)
        keyboard.remove_hotkey(RECORD_HOTKEY)
        keyboard.remove_hotkey(PAUSE_HOTKEY)
    except Exception:
        pass

    try:
        keyboard.add_hotkey(TOGGLE_HOTKEY, toggle_script_state)
        keyboard.add_hotkey(RECORD_HOTKEY, record_action)
        keyboard.add_hotkey(PAUSE_HOTKEY, pause_script)
        print(f"Script iniciado. Pressione '{TOGGLE_HOTKEY}' para ativar/desativar a gravação/execução em loop.")
        print(f"Pressione '{RECORD_HOTKEY}' para gravar uma ação (posição, botão, delay).")
        print(f"Pressione '{PAUSE_HOTKEY}' para pausar/retomar a execução.")
        print(f"Script está atualmente {'ATIVO' if SCRIPT_RUNNING else 'INATIVO'}.")
    except Exception as e:
        print(f"Erro ao configurar hotkeys: {e}. Tente executar como administrador.")
        sys.exit(1)

# --- Loop Principal ---
if __name__ == "__main__":
    pyautogui.PAUSE = 0.03
    pyautogui.FAILSAFE = True

    setup_hotkeys()

    print("Script aguardando ativação (F9) e gravação de ações (F8)...")
    try:
        while True:
            if SCRIPT_RUNNING and not SCRIPT_PAUSED and recorded_actions:
                executar_sequencia()
                loop_delay = random.uniform(LOOP_DELAY_MIN, LOOP_DELAY_MAX)
                print(f"Aguardando {loop_delay:.2f} segundos antes de repetir o loop...")
                time.sleep(loop_delay)
            else:
                time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nScript interrompido pelo usuário (Ctrl+C).")
    finally:
        print("Encerrando script.")