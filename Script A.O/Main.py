import cv2
import numpy as np
import pyautogui
import time
import random
import keyboard
import os

# --- Configuração Centralizada ---
# --- Setup Básico ---
TARGET_PLAYER_NAME = "yuuki99" # Alvo a ser curado/monitorado
# !! IMPORTANTE: Use o nome do SEU template aqui !!
TEMPLATE_FILENAME = "meu_nome_template.png" # Template do NOME do alvo ("yuuki99")

# --- Tela & Coordenadas ---
IS_FULL_HD = False # Defina True para 1920x1080, False para outras (Ex: 1366x768)

# --- Coordenadas da Barra de Vida do ALVO (Ajuste por Tentativa e Erro!) ---
# --- RELATIVO ao Canto Superior Esquerdo do Template do NOME encontrado ---
# !! ESTA É A PARTE MAIS CRÍTICA PARA A LEITURA CORRETA DA VIDA !!
# Valores padrão alterados - ajuste observando onde a barra REALMENTE está no jogo!
TARGET_HEALTH_BAR_OFFSET_X = 2      # Offset X da barra relativo ao X do nome (Experimente 0, 1, 2...)
TARGET_HEALTH_BAR_OFFSET_Y = 12     # Offset Y da barra relativo ao Y do nome (TENTE 1, 2, 3... era 18!)
TARGET_HEALTH_BAR_HEIGHT = 8        # Altura da barra (TENTE 6, 8, 10...)
TARGET_HEALTH_BAR_WIDTH_MODE = 'template' # 'template' (largura do nome) ou 'fixed'
# TARGET_HEALTH_BAR_FIXED_WIDTH = 100 # Usar somente se WIDTH_MODE for 'fixed'
TARGET_HEALTH_BAR_WIDTH_ADD = 0     # Adicional à largura do template (TENTE 0, 5, 10...)

# Coordenadas da própria vida foram removidas - não são mais necessárias

# --- Cor da Barra de VIDA do ALVO (Formato HSV) ---
# !! VERIFIQUE A COR REAL DA *VIDA* DO ALVO NO JOGO !!
# Ajustado para VERDE (EXEMPLO - Use Color Picker para valores exatos!)
TARGET_HEALTH_LOWER_HSV = np.array([35, 80, 80])   # Baixei um pouco Sat/Val para pegar verdes menos vibrantes
TARGET_HEALTH_UPPER_HSV = np.array([85, 255, 255])

# --- Detecção & Ação (Healer) ---
TEMPLATE_MATCH_THRESHOLD = 0.75 # Confiança (ajuste 0.7 a 0.9)
TARGET_CLICK_BUTTON = 'left'   # Botão para selecionar o alvo "yuuki99"
# --- Limites de Vida do ALVO para Curar ---
# Ajuste as skills (Q, W, E) e os thresholds conforme suas curas
HEAL_Q_THRESHOLD = 85           # Usar 'Q' (ex: cura leve) se vida <= X%
HEAL_W_THRESHOLD = 65           # Usar 'W' (ex: cura média) se vida <= X%
HEAL_E_THRESHOLD = 45           # Usar 'E' (ex: cura forte) se vida <= X%

# --- Timing & Humanização (Mais Lento e Aleatório) ---
MIN_REACTION_TIME = 0.5         # Min seg antes de uma ação
MAX_REACTION_TIME = 1.5         # Max seg antes de uma ação
MOUSE_MOVE_MIN_DURATION = 0.3   # Min seg para mover mouse
MOUSE_MOVE_MAX_DURATION = 0.9   # Max seg para mover mouse
MOUSE_COORD_OFFSET = 5          # Variação no clique
LOOP_SLEEP_MIN = 3.0            # Min seg de pausa quando inativo
LOOP_SLEEP_MAX = 7.0            # Max seg de pausa quando inativo
ACTION_DELAY_MIN = 0.25         # Min seg entre pressionar teclas
ACTION_DELAY_MAX = 0.6          # Max seg entre pressionar teclas
CYCLE_DELAY_MIN = 1.0           # Min seg entre ciclos de verificação ATIVOS
CYCLE_DELAY_MAX = 2.5           # Max seg entre ciclos de verificação ATIVOS

# --- Controle ---
TOGGLE_HOTKEY = 'f8'
SCRIPT_RUNNING = False

# --- Fim da Configuração ---

# --- Variáveis Globais ---
template_image = None
target_clicked_once = False # Flag para controlar o clique inicial

# --- Funções de Simulação Humana ---
def human_like_delay(min_time=MIN_REACTION_TIME, max_time=MAX_REACTION_TIME):
    delay = random.uniform(min_time, max_time)
    # print(f"   Delaying for {delay:.2f}s...") # Debug
    time.sleep(delay)

def human_like_mouse_move(x, y):
    target_x = x + random.randint(-MOUSE_COORD_OFFSET, MOUSE_COORD_OFFSET)
    target_y = y + random.randint(-MOUSE_COORD_OFFSET, MOUSE_COORD_OFFSET)
    duration = random.uniform(MOUSE_MOVE_MIN_DURATION, MOUSE_MOVE_MAX_DURATION)
    # print(f"   Moving mouse to ({target_x}, {target_y}) over {duration:.2f}s...") # Debug
    pyautogui.moveTo(target_x, target_y, duration=duration)

# --- Processamento de Imagem & Detecção ---
def locate_target_template(screen_frame_gray):
    global template_image
    if template_image is None:
        print("Erro: Imagem de template não carregada.")
        return None, None

    health_bar_region = None
    target_center = None

    try:
        result = cv2.matchTemplate(screen_frame_gray, template_image, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        if max_val >= TEMPLATE_MATCH_THRESHOLD:
            x_name, y_name = max_loc
            h_name, w_name = template_image.shape

            target_center = (x_name + w_name // 2, y_name + h_name // 2)

            # --- Calcula região da barra de vida ---
            # !! VERIFIQUE E AJUSTE OS OFFSETS NA CONFIGURAÇÃO !!
            x_bar_start = x_name + TARGET_HEALTH_BAR_OFFSET_X
            y_bar_start = y_name + h_name + TARGET_HEALTH_BAR_OFFSET_Y # y_name + altura_nome + offset_vertical

            if TARGET_HEALTH_BAR_WIDTH_MODE == 'template':
                bar_width = w_name + TARGET_HEALTH_BAR_WIDTH_ADD
            else: # Assume 'fixed' ou default
                try:
                    bar_width = TARGET_HEALTH_BAR_FIXED_WIDTH
                except NameError: # Fallback se a variável não existir
                    bar_width = w_name + TARGET_HEALTH_BAR_WIDTH_ADD

            x_bar_end = x_bar_start + bar_width
            y_bar_end = y_bar_start + TARGET_HEALTH_BAR_HEIGHT
            # -----------------------------------------

            health_bar_region = (x_bar_start, y_bar_start, x_bar_end, y_bar_end)
            # print(f"   Health bar region calculated: {health_bar_region}") # Debug

    except cv2.error as e:
        print(f"Erro OpenCV no template matching: {e}")
    except Exception as e:
        print(f"Erro inesperado no template matching: {e}")

    return target_center, health_bar_region

# --- Cálculo de Porcentagem de Vida ---
def get_health_percentage(health_bar_region, hsv_lower, hsv_upper):
    if not health_bar_region:
        return 100

    x_start, y_start, x_end, y_end = health_bar_region
    width = x_end - x_start
    height = y_end - y_start

    if width <= 0 or height <= 0:
        print(f"Aviso: Região da barra de vida inválida: {health_bar_region}")
        return 100

    try:
        screenshot = pyautogui.screenshot(region=(x_start, y_start, width, height))
        health_bar_img = np.array(screenshot)
        health_bar_img_rgb = cv2.cvtColor(health_bar_img, cv2.COLOR_BGR2RGB)
        hsv_img = cv2.cvtColor(health_bar_img_rgb, cv2.COLOR_RGB2HSV)

        mask = cv2.inRange(hsv_img, hsv_lower, hsv_upper)

        # --- Método: Pixel Mais à Direita (Default agora) ---
        total_pixels_in_width = mask.shape[1]
        if total_pixels_in_width == 0:
            return 100 # Evita divisão por zero
        health_pixels = cv2.findNonZero(mask)
        if health_pixels is not None:
            # Encontra o valor máximo da coordenada X entre todos os pixels não-zero
            rightmost_pixel_x = health_pixels[:, 0, 0].max()
            # Calcula porcentagem baseada na posição do pixel mais à direita (+1 para incluir ele)
            percentage = ((rightmost_pixel_x + 1) / total_pixels_in_width) * 100
        else:
            percentage = 0 # Nenhuma cor da vida encontrada

        # --- Método Alternativo: Contar Pixels (Comentado) ---
        # total_pixels_bar = mask.size # Total de pixels na região capturada
        # pixels_color = cv2.countNonZero(mask)
        # percentage = (pixels_color / total_pixels_bar) * 100 if total_pixels_bar > 0 else 0

        # Debug: Salva a máscara para ver o que está sendo detectado
        # cv2.imwrite(f"debug_mask_{time.time()}.png", mask)

        return max(0, min(100, percentage)) # Garante 0-100

    except Exception as e:
        print(f"Erro ao obter porcentagem de vida: {e}")
        print(f"Região que causou erro: {health_bar_region}")
        return 100 # Retorna valor seguro

# --- Ciclo Lógico Principal ---
def run_main_cycle():
    global target_clicked_once

    try:
        # 1. Captura Tela e Prepara Imagens
        # print("Capturando tela...") # Debug
        screenshot = pyautogui.screenshot()
        frame = np.array(screenshot)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_gray = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2GRAY)

        # 2. Localiza Alvo (Nome "yuuki99")
        # print("Localizando alvo...") # Debug
        target_center, target_health_region = locate_target_template(frame_gray)

        # 3. Ações se Alvo Encontrado
        if target_center:
            print(f"Alvo '{TARGET_PLAYER_NAME}' encontrado em {target_center}.")

            # Clica no alvo apenas uma vez inicialmente
            if not target_clicked_once:
                human_like_mouse_move(target_center[0], target_center[1])
                human_like_delay(0.1, 0.3) # Pequeno delay antes de clicar
                pyautogui.click(button=TARGET_CLICK_BUTTON)
                print(f"   Clicado em {TARGET_PLAYER_NAME} (initial click).")
                human_like_delay(0.6, 1.2) # Delay maior após clique antes de ler vida/curar
                target_clicked_once = True
            elif target_clicked_once:
                print(f"   Alvo '{TARGET_PLAYER_NAME}' já clicado inicialmente.")

            # Lê a vida da barra próxima ao nome
            # print("Lendo vida do alvo...") # Debug
            target_health = get_health_percentage(target_health_region, TARGET_HEALTH_LOWER_HSV, TARGET_HEALTH_UPPER_HSV)
            print(f"Vida do Alvo ({TARGET_PLAYER_NAME}): {target_health:.2f}%") # <-- Verifique este valor!

            # Decide qual cura usar baseado na vida do alvo
            heal_used = None
            if target_health <= HEAL_E_THRESHOLD:
                heal_used = 'e'
            elif target_health <= HEAL_W_THRESHOLD:
                heal_used = 'w'
            elif target_health <= HEAL_Q_THRESHOLD:
                heal_used = 'q'

            # Usa a cura selecionada
            if heal_used:
                print(f"   Vida baixa ({target_health:.1f}%), usando cura '{heal_used.upper()}'...")
                human_like_delay(ACTION_DELAY_MIN, ACTION_DELAY_MAX)
                pyautogui.press(heal_used)
                print(f"   >> Pressionado {heal_used.upper()}")

                # Verifica se a cura funcionou (se a vida ainda está baixa, clica novamente)
                human_like_delay(0.5, 1.0) # Espera um pouco para a cura ter efeito
                current_health = get_health_percentage(target_health_region, TARGET_HEALTH_LOWER_HSV, TARGET_HEALTH_UPPER_HSV)
                if current_health <= HEAL_E_THRESHOLD and heal_used == 'e':
                    print("   Cura 'E' não pareceu suficiente, clicando no alvo novamente...")
                    human_like_mouse_move(target_center[0], target_center[1])
                    human_like_delay(0.1, 0.3)
                    pyautogui.click(button=TARGET_CLICK_BUTTON)
                    human_like_delay(0.3, 0.7)
                elif current_health <= HEAL_W_THRESHOLD and heal_used == 'w':
                    print("   Cura 'W' não pareceu suficiente, clicando no alvo novamente...")
                    human_like_mouse_move(target_center[0], target_center[1])
                    human_like_delay(0.1, 0.3)
                    pyautogui.click(button=TARGET_CLICK_BUTTON)
                    human_like_delay(0.3, 0.7)
                elif current_health <= HEAL_Q_THRESHOLD and heal_used == 'q':
                    print("   Cura 'Q' não pareceu suficiente, clicando no alvo novamente...")
                    human_like_mouse_move(target_center[0], target_center[1])
                    human_like_delay(0.1, 0.3)
                    pyautogui.click(button=TARGET_CLICK_BUTTON)
                    human_like_delay(0.3, 0.7)

            else:
                print("   Vida do alvo OK, nenhuma cura necessária.")

            # Lógica de checar própria vida foi REMOVIDA

        else:
            print(f"Alvo '{TARGET_PLAYER_NAME}' não encontrado.")
            target_clicked_once = False # Reset flag if target is lost

    except pyautogui.FailSafeException:
        print("FailSafe Ativado! (Mouse no canto)")
        toggle_script_state()
    except Exception as e:
        print(f"Erro inesperado no ciclo principal: {e}")
        # Pausar em caso de erro pode ser uma boa ideia
        global SCRIPT_RUNNING
        if SCRIPT_RUNNING:
            toggle_script_state()

# --- Funções de Controle ---
def toggle_script_state():
    global SCRIPT_RUNNING
    SCRIPT_RUNNING = not SCRIPT_RUNNING
    status = "ATIVADO" if SCRIPT_RUNNING else "DESATIVADO"
    print(f"--- Script {status} ---")

def setup_hotkey():
    try:
        keyboard.remove_hotkey(TOGGLE_HOTKEY)
    except Exception: pass # Ignora se não existia ou erro ao remover

    try:
        keyboard.add_hotkey(TOGGLE_HOTKEY, toggle_script_state)
        print(f"Script iniciado. Pressione '{TOGGLE_HOTKEY}' para ativar/desativar.")
        print(f"Script está atualmente {'ATIVO' if SCRIPT_RUNNING else 'INATIVO'}.")
    except Exception as e:
        print(f"Erro ao configurar hotkey: {e}. Tente executar como administrador.")
        exit()

def load_template():
    global template_image
    script_dir = os.path.dirname(__file__) if "__file__" in locals() else os.getcwd()
    template_path = os.path.join(script_dir, TEMPLATE_FILENAME)

    if not os.path.exists(template_path):
        print(f"ERRO: Arquivo de template não encontrado em '{template_path}'")
        return False
    try:
        template_image = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        if template_image is None:
            print(f"ERRO: Falha ao carregar template de '{template_path}'.")
            return False
        print(f"Template '{TEMPLATE_FILENAME}' carregado (Dimensões: {template_image.shape[1]}x{template_image.shape[0]}).")
        return True
    except Exception as e:
        print(f"ERRO: Não foi possível carregar template '{template_path}': {e}")
        return False

# --- Execução Principal ---
if __name__ == "__main__":
    pyautogui.PAUSE = 0.03
    pyautogui.FAILSAFE = True

    if not load_template():
        exit()

    setup_hotkey()

    print("Entrando no loop principal...")
    try:
        while True:
            if SCRIPT_RUNNING:
                start_time = time.time()
                run_main_cycle()
                end_time = time.time()
                cycle_duration = end_time - start_time
                print(f"Ciclo levou {cycle_duration:.3f} seg.")
                # Delay entre ciclos ativos para não sobrecarregar e parecer mais humano
                sleep_duration = random.uniform(CYCLE_DELAY_MIN, CYCLE_DELAY_MAX)
                print(f"   Pausando por {sleep_duration:.2f}s antes do próximo ciclo...")
                time.sleep(sleep_duration)
            else:
                # Dorme mais quando pausado
                time.sleep(random.uniform(LOOP_SLEEP_MIN, LOOP_SLEEP_MAX))

    except KeyboardInterrupt:
        print("\nScript interrompido pelo usuário (Ctrl+C).")
    finally:
        print("Encerrando script.")