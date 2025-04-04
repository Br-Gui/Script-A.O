import cv2
import numpy as np
import pyautogui
import pytesseract
import time
import random

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
NOME_ALVO = "Yuuki99"

def localizar_texto():
    screenshot = pyautogui.screenshot()
    frame = np.array(screenshot)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    
    dados_texto = pytesseract.image_to_data(frame, output_type=pytesseract.Output.DICT)
    for i, texto in enumerate(dados_texto["text"]):
        if NOME_ALVO.lower() in texto.lower():
            x, y, w, h = (dados_texto["left"][i], dados_texto["top"][i], 
                          dados_texto["width"][i], dados_texto["height"][i])
            return (x + w // 2, y + h // 2, y + h + 10, y + h + 15)
    return None

def obter_porcentagem_vida(posicao_vida):
    screenshot = pyautogui.screenshot()
    frame = np.array(screenshot)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    area_vida = frame[posicao_vida[2]:posicao_vida[3], posicao_vida[0]-50:posicao_vida[0]+50]
    vida_branca = np.count_nonzero(area_vida > 200)
    vida_total = area_vida.size
    return (vida_branca / vida_total) * 100

def executar_acoes():
    resultado = localizar_texto()
    
    if resultado:
        posicao = resultado[:2]
        posicao_vida = resultado[2:]
        pyautogui.moveTo(posicao[0], posicao[1], duration=random.uniform(0.3, 0.7))
        time.sleep(random.uniform(0.5, 1.2))
        pyautogui.click()
        time.sleep(random.uniform(0.5, 1.5))
        
        vida = obter_porcentagem_vida(posicao_vida)
        if vida <= 80:
            pyautogui.moveTo(posicao[0], posicao[1], duration=random.uniform(0.3, 0.7))
            time.sleep(random.uniform(0.3, 0.7))
            pyautogui.click()
            pyautogui.press('q')
            time.sleep(random.uniform(0.3, 0.8))
        if vida <= 60:
            pyautogui.moveTo(posicao[0], posicao[1], duration=random.uniform(0.3, 0.7))
            time.sleep(random.uniform(0.3, 0.7))
            pyautogui.click()
            pyautogui.press('w')
            time.sleep(random.uniform(0.3, 0.8))
        if vida <= 50:
            pyautogui.moveTo(posicao[0], posicao[1], duration=random.uniform(0.3, 0.7))
            time.sleep(random.uniform(0.3, 0.7))
            pyautogui.click()
            pyautogui.press('e')
            time.sleep(random.uniform(0.3, 0.8))
        
        for _ in range(random.randint(2, 4)):
            deslocamento_x = random.choice([-1920, 1920])
            deslocamento_y = random.choice([-1920, 1920])
            nova_posicao = (posicao[0] + deslocamento_x, posicao[1] + deslocamento_y)
            pyautogui.moveTo(nova_posicao[0], nova_posicao[1], duration=random.uniform(0.5, 1.0))
            time.sleep(random.uniform(4.0, 6.0))
            pyautogui.click(button="right")
    else:
        print("Nome não encontrado na tela. Tentando novamente...")

while True:
    executar_acoes()
    time.sleep(random.uniform(5, 10))
