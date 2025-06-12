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

    def demodular_ask(self, signal, bit_samples=100, treshold=0.1):
        """
        signal: array de float, contendo o signal modulado ASK
        bit_samples: número de amostras por bit
        treshold: limiar de decisão da presença de onda
        """
        bits = []

        # Percorre o sinal em segmentos de tamanho bit_samples
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