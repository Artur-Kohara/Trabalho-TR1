from transmissor import Transmissor
from receptor import Receptor

def main():
    config = {
    'frameSize': x, 
    'bitrate': 0,  # 1 Mbps
    'encoding': 'NRZ',   # Exemplo de codificação
    'protocol': 'CRC',   # Exemplo de protocolo de controle de erros
    'frequency': 0  # Frequência de operação, exemplo: 2.4 GHz
    }  
    tx = Transmissor(config)
    rx = Receptor(config)


    print(f"[Final] Recebido: {resultado}")

if __name__ == "__main__":
    main()
