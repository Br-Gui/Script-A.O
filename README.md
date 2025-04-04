# Projeto: IA de Cliques e Movimentos

## Descrição
Este projeto utiliza **visão computacional** para detectar um nome específico na tela e interagir automaticamente com ele, realizando **cliques e comandos de teclado**. Além disso, permite que o usuário pause e retome a execução a qualquer momento.

## Funcionalidades
- **Detecção de nome na tela** usando OCR (Tesseract)
- **Cliques automáticos** (botão esquerdo e direito) com movimentos aleatórios
- **Execução de comandos de teclado (Q, W, E) com base na vida do personagem**
- **Controle por atalhos**:
  - **F8**: Pausa o programa
  - **F9**: Retoma o programa

## Requisitos
- Python 3.x
- OpenCV (`cv2`)
- NumPy (`numpy`)
- PyAutoGUI (`pyautogui`)
- Tesseract OCR
- Keyboard (`keyboard`)

## Instalação
1. **Instale o Python 3.x** (se ainda não tiver).
2. **Instale as dependências** executando o seguinte comando no terminal:
   ```sh
   pip install opencv-python numpy pyautogui pytesseract keyboard
   ```
3. **Instale o Tesseract OCR**:
   - Baixe o instalador [aqui](https://github.com/UB-Mannheim/tesseract/wiki)
   - Durante a instalação, **anote o caminho do diretório do Tesseract**
   - Atualize a linha abaixo no código para refletir o caminho correto:
     ```python
     pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
     ```

## Uso
1. **Execute o script**:
   ```sh
   python main.py
   ```
2. O programa procurará pelo nome especificado na tela e interagirá automaticamente.
3. Para **pausar**, pressione **F8**.
4. Para **retomar**, pressione **F9**.

## Notas
- O desempenho pode variar dependendo da resolução da tela e configurações do jogo.
- Certifique-se de que o Tesseract OCR está instalado corretamente.

## Aviso Legal
Este software foi desenvolvido apenas para **fins educacionais**. O uso de automação em jogos pode violar os Termos de Serviço de algumas plataformas. Use por sua conta e risco.

