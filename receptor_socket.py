# receiver_socket.py
import socket
import pickle
import numpy as np
from receptor import Receiver
from gi.repository import GLib

HOST = '127.0.0.1'
PORT = 5000
rx = None

# Atualiza a interface GTK de forma thread-safe
def update_interface(gui, demod_bb, demod_bp, text, config):
    ax1 = gui.figure_rx_bb.gca()
    rx.plotBaseband(demod_bb, config["mod_bb"], V=config.get("V", 1.0), ax=ax1)
    gui.canvas_rx_bb.draw()

    ax2 = gui.figure_rx_bp.gca()
    rx.plotPassband(demod_bp, config["mod_bp"],
                    A=config.get("A", 1.0),
                    f=config.get("f", 2.0),
                    f1=config.get("f1", 2.0),
                    f2=config.get("f2", 4.0),
                    ax=ax2)
    gui.canvas_rx_bp.draw()

    gui.label_rx_text.set_text(text)
    return False

def start_receiver(gui):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(1)
        print("[Receptor] Aguardando conexão...")

        conn, addr = s.accept()
        with conn:
            print(f"[Receptor] Conectado a {addr}")
            data = b""
            while True:
                packet = conn.recv(4096)
                if not packet:
                    break
                data += packet

            packet = pickle.loads(data)
            signal_bb = packet['signal_bb']
            signal_bp = packet['signal_bp']
            config = packet['config']

            global rx
            rx = Receiver(config)


            mod_bp = config.get("mod_bp")
            mod_bb = config.get("mod_bb")
            framing = config.get("framing")
            edc = config.get("edc")

            print(f"[Receptor] Config: {config}")

            # 1. Demodulação de portadora
            # Adiciona ruído no sinal analógico (portadora)
            analog_signal_noise = rx.addAnalogNoise(signal_bp, None)

            if mod_bp == "ASK":
                demod_bp = rx.demoduleASK(analog_signal_noise, 100, 0.1)
            elif mod_bp == "FSK":
                demod_bp = rx.demoduleFSK(analog_signal_noise, f0=config["f2"], f1=config["f1"], A=config["A"], bit_samples=100)
            elif mod_bp == "8-QAM":
                demod_bp = rx.demodule8QAM(analog_signal_noise, A=config["A"], f=config["f"], symbol_samples=100)
            else:
                raise ValueError("Modulação de portadora inválida")

            # 2. Demodulação de banda base
            # Adiciona ruído no sinal digital (banda base)
            digital_signal_noise = rx.addDigitalNoise(signal_bb, V=config["V"], bit_error_prob=None)
            if mod_bb == "NRZ":
                demod_bb = rx.polarNRZDecoder(digital_signal_noise)
            elif mod_bb == "Manchester":
                demod_bb = rx.manchesterDecoder(digital_signal_noise)
            elif mod_bb == "Bipolar":
                demod_bb = rx.bipolarDecoder(digital_signal_noise)
            else:
                raise ValueError("Modulação de banda base inválida")

            # 3. Desenquadramento
            if framing == "Cont. de Caracteres":
                bitStream = rx.chCountUnframing(demod_bb, edc)

            elif framing == "Inserção de Bits":
                bitStream = rx.bitInsertionUnframing(demod_bb, edc)

            elif framing == "Inserção de Bytes":
                bitStream = rx.byteInsertionUnframing(demod_bb, edc)

            else:
                raise ValueError("Enquadramento inválido")

            text = rx.receive(bitStream)

            # Atualizar interface
            GLib.idle_add(update_interface, gui, demod_bb, demod_bp, text, config)
