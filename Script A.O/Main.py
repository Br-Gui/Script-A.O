import cv2
import numpy as np
import pyautogui
import pytesseract
import time
import random
import keyboard

pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
NOME_ALVO = "Yuuki99"
executando = True

template_nome = cv2.imread("nome_template.png", 0)
OCR_CONFIG = "--psm 6 --oem 3"

def preprocessar_imagem(frame):
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    frame = cv2.GaussianBlur(frame, (3, 3), 0)
    frame = cv2.threshold(frame, 180, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    return frame

def localizar_texto():
    screenshot = pyautogui.screenshot()
    frame = np.array(screenshot)
    frame = preprocessar_imagem(frame)
    res = cv2.matchTemplate(frame, template_nome, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(res)
    if max_val > 0.8:
        x, y = max_loc
        w, h = template_nome.shape[::-1]
        return (x + w // 2, y + h // 2, x, y + h + 5, x + w, y + h + 10)
    return None

def obter_porcentagem_vida(posicao_vida):
    screenshot = pyautogui.screenshot()
    frame = np.array(screenshot)
    x_start, y_start, x_end, y_end = posicao_vida
    barra_vida = frame[y_start:y_end, x_start:x_end]
    barra_vida_hsv = cv2.cvtColor(barra_vida, cv2.COLOR_RGB2HSV)
    mascara_amarela = cv2.inRange(barra_vida_hsv, (20, 100, 100), (30, 255, 255))
    total_pixels = mascara_amarela.shape[1]
    pixels_amarelos = cv2.countNonZero(mascara_amarela)
    porcentagem_vida = (pixels_amarelos / total_pixels) * 100 if total_pixels > 0 else 0
    return max(0, min(100, porcentagem_vida))

def obter_tempo_recarga(pos_mouse):
    pyautogui.moveTo(pos_mouse[0], pos_mouse[1], duration=random.uniform(0.1, 0.3))
    time.sleep(random.uniform(0.3, 0.6))
    screenshot = pyautogui.screenshot()
    frame = np.array(screenshot)
    frame = preprocessar_imagem(frame)
    texto = pytesseract.image_to_string(frame, config=OCR_CONFIG)
    for token in texto.split():
        if token.isdigit():
            return int(token)
    return 0

def executar_acoes():
    global executando
    resultado = localizar_texto()
    if resultado and executando:
        posicao = resultado[:2]
        posicao_vida = resultado[2:]
        pyautogui.moveTo(posicao[0] + random.randint(-5, 5), posicao[1] + random.randint(-5, 5), duration=random.uniform(0.2, 0.5))
        time.sleep(random.uniform(0.3, 0.7))
        pyautogui.click()
        time.sleep(random.uniform(0.4, 1.0))

        vida = obter_porcentagem_vida(posicao_vida)
        posicoes_habilidades = {
            'q': (905, 960),
            'w': (960, 960),
            'e': (1015, 960)
        }

        tempo_q = obter_tempo_recarga(posicoes_habilidades['q'])
        tempo_w = obter_tempo_recarga(posicoes_habilidades['w'])
        tempo_e = obter_tempo_recarga(posicoes_habilidades['e'])

        if vida <= 80 and tempo_q == 0:
            pyautogui.press('q')
            time.sleep(random.uniform(0.4, 0.7))
        if vida <= 60 and tempo_w == 0:
            pyautogui.press('w')
            time.sleep(random.uniform(0.4, 0.7))
        if vida <= 50 and tempo_e == 0:
            pyautogui.press('e')
            time.sleep(random.uniform(0.4, 0.7))

        minha_vida = obter_porcentagem_vida((90, 1010, 220, 1025))
        if minha_vida <= 40:
            pyautogui.press('r')
            time.sleep(random.uniform(0.3, 0.6))

        for _ in range(random.randint(1, 3)):
            deslocamento_x = random.choice([-960, 960])
            deslocamento_y = random.choice([-540, 540])
            nova_posicao = (posicao[0] + deslocamento_x, posicao[1] + deslocamento_y)
            pyautogui.moveTo(nova_posicao[0], nova_posicao[1], duration=random.uniform(0.4, 0.8))
            time.sleep(random.uniform(1.0, 2.5))
            pyautogui.click(button="right")
        time.sleep(random.uniform(0.8, 1.5))
    else:
        print("Nome não encontrado na tela. Tentando novamente...")

def toggle_execucao():
    global executando
    executando = not executando
    print("Retomando" if executando else "Pausado")

keyboard.add_hotkey("f8", toggle_execucao)

while True:
    executar_acoes()
    time.sleep(random.uniform(4.0, 7.0))
