import pyautogui
import pytesseract
import cv2
import numpy as np
import time

# Configuração do Tesseract OCR (caso necessário, ajuste o caminho)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Nome a ser localizado na tela
nome_alvo = "Yuuki99"

# Lista de comandos configurados pelo usuário (serão executados após o clique)
comandos = ["q", "w", "e", "r", "f", "d"]

def capturar_tela():
    """ Captura a tela e converte para um formato compatível com OCR """
    screenshot = pyautogui.screenshot()
    frame = np.array(screenshot)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)  # Converte para escala de cinza
    return frame

def localizar_texto(frame, nome):
    """ Usa OCR para procurar o nome na tela """
    texto_detectado = pytesseract.image_to_data(frame, output_type=pytesseract.Output.DICT)
    for i, palavra in enumerate(texto_detectado["text"]):
        if nome.lower() in palavra.lower():
            x, y, w, h = (
                texto_detectado["left"][i],
                texto_detectado["top"][i],
                texto_detectado["width"][i],
                texto_detectado["height"][i],
            )
            return x + w // 2, y + h // 2  # Retorna posição central do texto
    return None

def executar_comandos():
    """ Executa os comandos do teclado após o clique """
    for comando in comandos:
        pyautogui.press(comando)  # Pressiona a tecla
        time.sleep(0.5)  # Pequeno delay entre ações

def main():
    print("Procurando por:", nome_alvo)
    while True:
        tela = capturar_tela()
        posicao = localizar_texto(tela, nome_alvo)

        if posicao:
            print(f"Nome '{nome_alvo}' encontrado em {posicao}, clicando...")
            pyautogui.moveTo(posicao)  # Move o mouse até o nome
            pyautogui.click()  # Clica no nome primeiro
            time.sleep(1)  # Pequeno delay para garantir que o clique foi processado
            
            print("Executando comandos do teclado...")
            executar_comandos()  # Depois do clique, executa os comandos do teclado
            break  # Encerra após encontrar e executar os comandos
        else:
            print("Nome não encontrado, tentando novamente...")
        time.sleep(2)  # Aguarda antes de tentar novamente

if __name__ == "__main__":
    main()
