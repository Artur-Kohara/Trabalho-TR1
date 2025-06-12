# Arquivo onde será desenvolvido o receptor do sistema de comunicação
import numpy as np

class Receptor:
    def __init__(self, config):
        self.config = config

    def receive(self, bits):
        text = self.bits2Text(bits)
        print(f"[Rx] Texto: {text}")
        return text

    def bits2Text(self, bits):
        # Pega o trem de bits e separa em blocos de 8 bits(1 byte)
        chars = [bits[i:i+8] for i in range(0, len(bits), 8)]
        # Transforma cada bloco de bits em um inteiro e depois em um caractere (ASCII)
        return ''.join(chr(int(b, 2)) for b in chars)
    
################################################################################
# Demodulação de sinais
################################################################################

    def demodule_ask(self, signal, bit_samples=100, treshold=0.1):
        """
        signal: array de float, contendo o signal modulado ASK
        bit_samples: número de amostras por bit
        treshold: limiar de decisão da presença de onda
        return: string com os bits demodulados
        """
        bits = []

        # Percorre o signal em segmentos de tamanho bit_samples
        for i in range(0, len(signal), bit_samples):
            # Extrai um segmento (correspondente a um bit)
            segment = signal[i:i+bit_samples]
            # Cálculo de energia média do segmento (eleva ao quadrado cada amostra e tira a média)
            energy = np.mean(np.square(segment))

            if energy > treshold:
                bits.append("1")
            else:
                bits.append("0")

        return ''.join(bits)

    def demodule_fsk(self, signal, f0=1000, f1=2000, fs=10000, dur=0.01):
        """
        signal: np.array com o sinal FSK recebido
        f0: frequência do bit 0
        f1: frequência do bit 1
        fs: taxa de amostragem
        dur: duração de um bit (em segundos)
        return: string com os bits demodulados
        """
        n = int(fs * dur)  # número de amostras por bit
        bits = []

        # Vetor de tempo para instantes uniformemente espaçados de 0 a dur (dur excluído) para as amostras
        t = np.linspace(0, dur, n, endpoint=False)

        # Vetores ref_0 e ref_1 são sinais senoidais de referência para as frequências f0 e f1
        ref_0 = np.sin(2 * np.pi * f0 * t)
        ref_1 = np.sin(2 * np.pi * f1 * t)

        # O sinal FSK é dividido em segmentos de n amostras (cada um correspondendo a um bit)
        for i in range(0, len(signal), n):
            segment = signal[i:i+n]
            if len(segment) < n:
                break

            # Para cada segmento, calcula-se o produto escalar (correlação) com os sinais de referência
            # (mede a semelhança entre o segmento do sinal recebido e os sinais senoidais de f0 e f1
            cor_0 = np.dot(segment, ref_0)
            cor_1 = np.dot(segment, ref_1)

            # Se a correlação com ref_1 for maior, a frequência predominante é f1 → bit "1"
            # Caso contrário, é f0 → bit "0"
            if abs(cor_1) > abs(cor_0):
                bits.append("1")
            else:
                bits.append("0")

        return ''.join(bits)
