import cv2
import numpy as np
import pyautogui
import pytesseract
import time
import random
import keyboard

pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
NOME_ALVO = "yuuki99"
executando = True

template_nome = cv2.imread("name.png", 0)

def preprocessar_imagem(frame):
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    frame = cv2.GaussianBlur(frame, (3, 3), 0)
    frame = cv2.threshold(frame, 180, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    return frame

def localizar_nome_por_template():
    screenshot = pyautogui.screenshot()
    frame = np.array(screenshot)
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    
    res = cv2.matchTemplate(frame_gray, template_nome, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(res)
    
    if max_val > 0.8:
        x, y = max_loc
        w, h = template_nome.shape[::-1]
        centro_nome = (x + w // 2, y + h // 2)
        
        x_start = x
        y_start = y + h + 18
        x_end = x + w
        y_end = y_start + 6
        
        return centro_nome, (x_start, y_start, x_end, y_end)
    
    return None

def obter_porcentagem_vida_azul(posicao_vida):
    screenshot = pyautogui.screenshot()
    frame = np.array(screenshot)
    
    x_start, y_start, x_end, y_end = posicao_vida
    barra_vida = frame[y_start:y_end, x_start:x_end]
    
    barra_vida_hsv = cv2.cvtColor(barra_vida, cv2.COLOR_RGB2HSV)
   
    mascara_azul = cv2.inRange(barra_vida_hsv, (100, 100, 100), (140, 255, 255))
    
    total_pixels = mascara_azul.shape[1]
    pixels_azuis = cv2.countNonZero(mascara_azul)
    
    porcentagem = (pixels_azuis / total_pixels) * 100 if total_pixels > 0 else 0
    return max(0, min(100, porcentagem))

def executar_acoes():
    global executando
    resultado = localizar_nome_por_template()
    
    if resultado and executando:
        posicao, posicao_vida = resultado
        pyautogui.moveTo(posicao[0], posicao[1], duration=random.uniform(0.2, 0.5))
        pyautogui.click()
        time.sleep(random.uniform(0.4, 0.9))

        vida = obter_porcentagem_vida_azul(posicao_vida)
        print(f"Vida de {NOME_ALVO}: {vida:.2f}%")

        habilidades = {
            'q': (905, 960),
            'w': (960, 960),
            'e': (1015, 960)
        }

        if vida <= 80:
            pyautogui.press('q')
        if vida <= 60:
            pyautogui.press('w')
        if vida <= 50:
            pyautogui.press('e')

        minha_vida = obter_porcentagem_vida_azul((90, 1010, 220, 1025))
        if minha_vida <= 40:
            pyautogui.press('r')

    else:
        print("Nome não encontrado. Tentando novamente...")

def toggle_execucao():
    global executando
    executando = not executando
    print("Retomando" if executando else "Pausado")

keyboard.add_hotkey("f8", toggle_execucao)

while True:
    if executando:
        executar_acoes()
    else:
        print("Pausado...")

    time.sleep(random.uniform(3.5, 6.5))

