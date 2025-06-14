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
# Demodulação (portadora)
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
    
################################################################################
# Demodulação (banda base)
################################################################################

    def polarNRZDecoder(self, signal, V=1):
        """
        Decodifica um sinal modulado polar NRZ
        signal: lista de amplitudes do sinal modulado
        V: amplitude do sinal (padrão = 1)
        return: string com o trem de bits decodificado
        """
        bits = []
        for amplitude in signal:
            if amplitude >= V:
                bits.append('1')
            elif amplitude <= -V:
                bits.append('0')
        
        return ''.join(bits)
    
    def manchesterDecoder(self, signal, V=1):
        """
        Decodifica um sinal modulado Manchester
        signal: lista de amplitudes do sinal modulado
        V: amplitude do sinal (padrão = 1)
        return: string com o trem de bits decodificado
        """
        bits = []
        # Itera sobre os índices do sinal, de 2 em 2, porque cada bit codificado ocupa dois valores no sinal
        for i in range(0, len(signal), 2):
            # Se a primeira metade está alta (+V) e a segunda está baixa (-V), representa um bit 1
            if signal[i] >= V and signal[i + 1] <= -V:
                bits.append('1')
            #Se a primeira metade está baixa (-V) e a segunda está alta (+V), representa um bit 0
            elif signal[i] <= -V and signal[i + 1] >= V:
                bits.append('0')
        
        return ''.join(bits)

################################################################################
# Desenquadramentos
################################################################################

    def chCountUnframing(self, frames):
        """
        Desenquadra os frames por contagem de caracteres
        Recebe uma lista de frames, onde cada frame é uma lista de bits
        Retorna o trem de bits desenquadrado
        """
        bitStream = []
        for frame in frames:
            # Seleciona os 6 primeiros bits do quadro, converte para string e depois para inteiro
            # Esses 6 bits representam o tamanho do frame
            frame_size = int(''.join(map(str, frame[:8])), 2)
            # Seleciona os próximos bits do quadro, que são os dados reais
            data_bits = frame[8:8 + frame_size]
            # Adiciona os bits de dados (data_bits) na lista bitStream
            bitStream.extend(data_bits)
        # Converte a lista de bits para uma string de bits
        return ''.join(map(str, bitStream))
    
    def byteInsertionUnframing(self, frames):
        """
        Desenquadra os frames por inserção de bytes
        frames: lista de frames, onde cada frame é uma lista de bits
        return: string com o trem de bits desenquadrado
        """
        bitStream = []
        flag = [0, 1, 1, 1, 1, 1, 1, 0]
        escape = [0, 1, 1, 1, 1, 1, 0, 1]
        for frame in frames:
            # Verifica se o quadro começa e termina com a flag
            if frame[:8] == flag and frame[-8:] == flag:
                # Remove a flag do início e do fim do quadro
                data_bits = frame[8:-8]
                i = 0
                # Percorre os bits do quadro para verificar a presença de escape
                while i < len(data_bits):
                    byte = data_bits[i:i + 8]
                    # Verifica se o byte é um byte de escape
                    if byte == escape and i + 8 < len(data_bits):
                        next_byte = data_bits[i + 8:i + 16]
                        # Adiciona o próximo byte normal
                        bitStream.extend(next_byte)
                        i += 16
                    else:
                        # Adiciona o byte normal ao bitStream
                        bitStream.extend(byte)
                        i += 8
        # Converte a lista de bits para uma string de bits
        return ''.join(map(str, bitStream))
    
    def bitInsertionUnframing(self, frames):
        """
        Desenquadra os frames por inserção de bits
        frames: lista de frames, onde cada frame é uma lista de bits
        return: string com o trem de bits desenquadrado
        """
        bitStream = []
        flag = [0, 1, 1, 1, 1, 1, 1, 0]
        
        for frame in frames:
            # Verifica se o quadro começa e termina com a flag
            if frame[:8] == flag and frame[-8:] == flag:
                # Remove a flag do início e do fim do quadro
                data_bits = frame[8:-8]

                # Remove os bits 0 inseridos após cinco bits 1
                cleaned_data = self.removeBit0(data_bits)
                bitStream.extend(cleaned_data)

        # Converte a lista de bits para uma string de bits
        return ''.join(map(str, bitStream))
    
    # Função auxiliar que remove o bit 0 inserido após cinco bits 1 seguidos
    def removeBit0(self, frame_data):
        cleaned_data = []
        counter = 0
        i = 0

        while i < len(frame_data):
            bit = frame_data[i]
            cleaned_data.append(bit)

            if bit == 1:
                counter += 1
            else:
                counter = 0

            if counter == 5:
                # Pula o próximo bit (deve ser o 0 inserido)
                i += 1
                counter = 0
            i += 1

        return cleaned_data