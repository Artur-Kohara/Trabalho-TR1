import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango, Gdk
from matplotlib.figure import Figure
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
import numpy as np
from transmissor import Transmitter

class InterfaceGUI(Gtk.Window):
  def __init__(self):
    Gtk.Window.__init__(self, title="Sistema de Comunicação - Camada Física e Enlace")
    self.set_default_size(1200, 800)
    self.set_border_width(15)
    
    # Cores e estilos
    self.set_style()
    
    # Layout principal
    main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
    self.add(main_box)
    
    # Cabeçalho
    self.create_header(main_box)
    
    # Divisor horizontal
    separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    main_box.pack_start(separator, False, False, 10)
    
    # Área de transmissão/recepção
    tx_rx_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
    main_box.pack_start(tx_rx_box, True, True, 0)
    
    # Transmissor
    self.create_transmitter(tx_rx_box)
    
    # Divisor vertical
    separator = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
    tx_rx_box.pack_start(separator, False, False, 10)
    
    # Receptor
    self.create_receiver(tx_rx_box)
    
    # Botões
    btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    btn_box.set_halign(Gtk.Align.CENTER)
    main_box.pack_start(btn_box, False, False, 10)
    
    self.btn_transmit = Gtk.Button.new_with_label("Transmitir Mensagem")
    self.btn_transmit.set_size_request(200, 40)
    self.btn_transmit.get_style_context().add_class("suggested-action")
    btn_box.pack_start(self.btn_transmit, False, False, 0)
    
    self.btn_receive = Gtk.Button.new_with_label("Receber Mensagem")
    self.btn_receive.set_size_request(200, 40)
    self.btn_receive.get_style_context().add_class("destructive-action")
    btn_box.pack_start(self.btn_receive, False, False, 0)
    
    self.show_all()
  
  def set_style(self):
    style_provider = Gtk.CssProvider()
    css = b"""
    .header {
      background-color: #5d6d7e;
      color: white;
      border-radius: 5px;
      padding: 10px;
    }
    .section-title {
      font-weight: bold;
      font-size: 14pt;
      margin-bottom: 8px;
    }
    .option-frame {
      border-radius: 5px;
      padding: 10px;
    }
    .graph-container {
      background-color: #f5f5f5;
      border: 1px solid #d3d3d3;
      border-radius: 5px;
      padding: 5px;
    }
    .received-text {
      background-color: #f0f0f0;
      padding: 15px;
      font-family: monospace;
      border-radius: 5px;
    }
    .suggested-action {
      background-color: #2ecc71;
      color: white;
    }
    .destructive-action {
      background-color: #e74c3c;
      color: white;
    }
    """
    style_provider.load_from_data(css)
    Gtk.StyleContext.add_provider_for_screen(
      Gdk.Screen.get_default(),
      style_provider,
      Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )
  
  def create_header(self, parent):
    header_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    header_box.get_style_context().add_class("header")
    parent.pack_start(header_box, False, False, 0)
    
    # Título
    title = Gtk.Label(label="Simulador de Comunicação - Camada Física e Enlace")
    title.set_halign(Gtk.Align.CENTER)
    title.set_justify(Gtk.Justification.CENTER)
    title.override_font(Pango.font_description_from_string("Bold 16"))
    header_box.pack_start(title, False, False, 5)
    
    # Entrada de texto
    entry_frame = Gtk.Frame()
    entry_frame.set_shadow_type(Gtk.ShadowType.IN)
    entry_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
    entry_frame.add(entry_box)
    
    self.entry_text = Gtk.Entry()
    self.entry_text.set_placeholder_text("Digite sua mensagem aqui...")
    self.entry_text.set_size_request(600, 40)
    entry_box.pack_start(self.entry_text, True, True, 10)
    
    header_box.pack_start(entry_frame, False, False, 5)
    
    # Opções de configuração
    options_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
    header_box.pack_start(options_box, False, False, 10)
    
    # Frame Enquadramento
    frame_enq = Gtk.Frame(label=" Enquadramento ")
    frame_enq.get_style_context().add_class("option-frame")
    hbox_enq = Gtk.Box(spacing=10)
    frame_enq.add(hbox_enq)
    self.enq_opts = {}
    for label in ["Cont. de Caracteres", "Inserção de Bits", "Inserção de Bytes"]:
      btn = Gtk.RadioButton.new_with_label_from_widget(next(iter(self.enq_opts.values()), None), label)
      hbox_enq.pack_start(btn, False, False, 0)
      self.enq_opts[label] = btn
    options_box.pack_start(frame_enq, True, True, 0)
    
    # Frame EDC
    frame_edc = Gtk.Frame(label=" Detecção/Correção de Erro ")
    frame_edc.get_style_context().add_class("option-frame")
    hbox_edc = Gtk.Box(spacing=10)
    frame_edc.add(hbox_edc)
    self.edc_opts = {}
    for label in ["Bit de Paridade Par", "CRC", "Hamming"]:
      btn = Gtk.RadioButton.new_with_label_from_widget(next(iter(self.edc_opts.values()), None), label)
      hbox_edc.pack_start(btn, False, False, 0)
      self.edc_opts[label] = btn
    options_box.pack_start(frame_edc, True, True, 0)
  
  def create_transmitter(self, parent):
    tx_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
    parent.pack_start(tx_box, True, True, 0)
    
    # Título da seção
    tx_title = Gtk.Label(label="TRANSMISSOR")
    tx_title.set_halign(Gtk.Align.START)
    tx_title.get_style_context().add_class("section-title")
    tx_box.pack_start(tx_title, False, False, 5)
    
    # Modulação Banda Base
    frame_bb = Gtk.Frame(label=" Modulação Banda Base ")
    frame_bb.get_style_context().add_class("option-frame")
    vbox_bb = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    frame_bb.add(vbox_bb)
    
    # Opções
    hbox_bb = Gtk.Box(spacing=15)
    self.bb_opts = {}
    for label in ["NRZ", "Manchester", "Bipolar"]:
      btn = Gtk.RadioButton.new_with_label_from_widget(next(iter(self.bb_opts.values()), None), label)
      hbox_bb.pack_start(btn, False, False, 0)
      self.bb_opts[label] = btn
    vbox_bb.pack_start(hbox_bb, False, False, 5)
    
    # Área do gráfico
    graph_box = Gtk.Frame()
    graph_box.get_style_context().add_class("graph-container")
    graph_box.set_shadow_type(Gtk.ShadowType.IN)
    self.figure_bb = Figure(figsize=(5, 2), dpi=100)
    self.canvas_bb = FigureCanvas(self.figure_bb)
    self.canvas_bb.set_size_request(500, 150)
    graph_box.add(self.canvas_bb)
    vbox_bb.pack_start(graph_box, True, True, 5)
    
    tx_box.pack_start(frame_bb, True, True, 0)
    
    # Modulação Portadora
    frame_bp = Gtk.Frame(label=" Modulação Portadora ")
    frame_bp.get_style_context().add_class("option-frame")
    vbox_bp = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    frame_bp.add(vbox_bp)
    
    # Opções
    hbox_bp = Gtk.Box(spacing=15)
    self.bp_opts = {}
    for label in ["ASK", "FSK", "8-QAM"]:
      btn = Gtk.RadioButton.new_with_label_from_widget(next(iter(self.bp_opts.values()), None), label)
      hbox_bp.pack_start(btn, False, False, 0)
      self.bp_opts[label] = btn
    vbox_bp.pack_start(hbox_bp, False, False, 5)
    
    # Área do gráfico
    graph_box = Gtk.Frame()
    graph_box.get_style_context().add_class("graph-container")
    graph_box.set_shadow_type(Gtk.ShadowType.IN)
    self.figure_bp = Figure(figsize=(5, 2), dpi=100)
    self.canvas_bp = FigureCanvas(self.figure_bp)
    self.canvas_bp.set_size_request(500, 150)
    graph_box.add(self.canvas_bp)
    vbox_bp.pack_start(graph_box, True, True, 5)
    
    tx_box.pack_start(frame_bp, True, True, 10)
  
  def create_receiver(self, parent):
    rx_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
    parent.pack_start(rx_box, True, True, 0)
    
    # Título da seção
    rx_title = Gtk.Label(label="RECEPTOR")
    rx_title.set_halign(Gtk.Align.START)
    rx_title.get_style_context().add_class("section-title")
    rx_box.pack_start(rx_title, False, False, 5)
    
    # Demodulação Banda Base
    frame_rx_bb = Gtk.Frame(label=" Demodulação Banda Base ")
    frame_rx_bb.get_style_context().add_class("option-frame")
    rx_bb_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
    frame_rx_bb.add(rx_bb_box)
    
    # Área do gráfico
    graph_box = Gtk.Frame()
    graph_box.get_style_context().add_class("graph-container")
    graph_box.set_shadow_type(Gtk.ShadowType.IN)
    self.figure_rx_bb = Figure(figsize=(5, 2), dpi=100)
    self.canvas_rx_bb = FigureCanvas(self.figure_rx_bb)
    self.canvas_rx_bb.set_size_request(500, 150)
    graph_box.add(self.canvas_rx_bb)
    rx_bb_box.pack_start(graph_box, True, True, 5)
    
    rx_box.pack_start(frame_rx_bb, True, True, 0)
    
    # Demodulação Portadora
    frame_rx_bp = Gtk.Frame(label=" Demodulação Portadora ")
    frame_rx_bp.get_style_context().add_class("option-frame")
    rx_bp_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
    frame_rx_bp.add(rx_bp_box)
    
    # Área do gráfico
    graph_box = Gtk.Frame()
    graph_box.get_style_context().add_class("graph-container")
    graph_box.set_shadow_type(Gtk.ShadowType.IN)
    self.figure_rx_bp = Figure(figsize=(5, 2), dpi=100)
    self.canvas_rx_bp = FigureCanvas(self.figure_rx_bp)
    self.canvas_rx_bp.set_size_request(500, 150)
    graph_box.add(self.canvas_rx_bp)
    rx_bp_box.pack_start(graph_box, True, True, 5)
    
    rx_box.pack_start(frame_rx_bp, True, True, 10)
    
    # Texto recebido
    frame_text = Gtk.Frame(label=" Texto Recebido ")
    frame_text.get_style_context().add_class("option-frame")
    text_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
    frame_text.add(text_box)
    
    self.label_rx_text = Gtk.Label(label="Aguardando transmissão...")
    self.label_rx_text.set_halign(Gtk.Align.START)
    self.label_rx_text.get_style_context().add_class("received-text")
    self.label_rx_text.set_size_request(-1, 80)
    text_box.pack_start(self.label_rx_text, True, True, 5)
    
    rx_box.pack_start(frame_text, False, False, 0)







  def on_transmit_clicked(self, button):
    text = self.entry.get_text()

    # Atualiza config com seleção do usuário
    self.config['framing'] = self.combo_enq.get_active_text()
    self.config['edc'] = self.combo_edc.get_active_text()
    self.config['banda_base'] = self.combo_bb.get_active_text()
    self.config['banda_passante'] = self.combo_bp.get_active_text()

    self.tx = Transmitter(self.config)

    # 1️⃣ Texto para bits
    bits = self.tx.text2Binary(text)

    # 2️⃣ Enquadramento
    frame_size = 32  # valor fixo ou configurable depois
    if self.config['framing'] == 'chCount':
        frames = self.tx.chCountFraming(bits, frame_size)
    elif self.config['framing'] == 'byteInsertion':
        frames = self.tx.byteInsertionFraming(bits, frame_size)
    else:  # bitInsertion
        frames = self.tx.bitInsertionFraming(bits, frame_size)

    # Junta os frames em um único trem de bits
    framed_bits = [bit for frame in frames for bit in frame]

    # 3️⃣ EDC
    if self.config['edc'] == 'paridade':
        edc_bits = self.tx.addEvenParityBit(framed_bits)
    elif self.config['edc'] == 'crc':
        edc_bits = self.tx.addCRC(framed_bits)
    else:  # hamming
        edc_bits = self.tx.addHamming(framed_bits)

    # 4️⃣ Banda base
    if self.config['banda_base'] == 'nrz':
        bb_signal = self.tx.polarNRZCoder(edc_bits)
    elif self.config['banda_base'] == 'manchester':
        bb_signal = self.tx.manchesterCoder(edc_bits)
    else:  # bipolar
        bb_signal = self.tx.bipolarCoder(edc_bits)

    # 5️⃣ Banda passante
    if self.config['banda_passante'] == 'ask':
        mod_signal = self.tx.ASK(bb_signal, A=1, f=5)
    elif self.config['banda_passante'] == 'fsk':
        mod_signal = self.tx.FSK(bb_signal, A=1, f1=5, f2=10)
    else:  # 8qam
        mod_signal = self.tx.QAM8(bb_signal, A=1, f=5)

    # Armazena para receptor
    self.last_signal = mod_signal

    # Plota
    self.ax.clear()
    self.ax.plot(mod_signal)
    self.canvas.draw()

  def on_receive_clicked(self, button):
    if not hasattr(self, 'last_signal'):
        self.result_label.set_text("Erro: Nenhum sinal transmitido!")
        return

    # Passo 1: demodulação
    bp = self.config['banda_passante']
    if bp == 'ask':
        bits_bb_str = self.rx.demoduleASK(self.last_signal)
    elif bp == 'fsk':
        bits_bb_str = self.rx.demoduleFSK(self.last_signal, f0=1, f1=2)
    elif bp == '8qam':
        bits_bb_str = self.rx.demodule8QAM(self.last_signal)
    else:
        self.result_label.set_text("Erro: Modulação desconhecida")
        return

    # Converte bits_bb_str para lista de ints
    bits_bb = [int(b) for b in bits_bb_str]

    # Passo 2: decodificação banda base
    bb = self.config['banda_base']
    if bb == 'nrz':
        bits_str = self.rx.polarNRZDecoder(bits_bb)
    elif bb == 'manchester':
        bits_str = self.rx.manchesterDecoder(bits_bb)
    elif bb == 'bipolar':
        bits_str = self.rx.bipolarDecoder(bits_bb)
    else:
        self.result_label.set_text("Erro: Codificação desconhecida")
        return

    # Converte para lista de ints
    bits = [int(b) for b in bits_str]

    # Passo 3: desenquadramento
    # Primeiro transforma em lista de frames (ex: lista de listas de bits)
    # Vamos supor que você tenha recebido frames já agrupados ou faça isso por outro método
    # Aqui vamos simular que cada 16 bits são um frame (exemplo, ajuste se necessário)
    frame_size = 32  # ou outro valor conforme seu protocolo
    frames = [bits[i:i+frame_size] for i in range(0, len(bits), frame_size)]

    fr = self.config['framing']
    if fr == 'chCount':
        desenq_str = self.rx.chCountUnframing(frames)
    elif fr == 'byteInsertion':
        desenq_str = self.rx.byteInsertionUnframing(frames)
    elif fr == 'bitInsertion':
        desenq_str = self.rx.bitInsertionUnframing(frames)
    else:
        self.result_label.set_text("Erro: Enquadramento desconhecido")
        return

    desenq_bits = [int(b) for b in desenq_str]

    # Passo 4: EDC
    edc = self.config['edc']
    if edc == 'paridade':
        ok = self.rx.checkEvenParityBit(desenq_bits)
        if not ok:
            self.result_label.set_text("Erro de paridade detectado!")
            return
        bits_final = desenq_bits[:-1]
    elif edc == 'crc':
        ok = self.rx.checkCRC(desenq_bits.copy())  # passa cópia, pois o método altera
        if not ok:
            self.result_label.set_text("Erro de CRC detectado!")
            return
        bits_final = desenq_bits[:-7]  # remove CRC, se necessário
    elif edc == 'hamming':
        bits_corrigido_str, err_pos = self.rx.checkHamming(desenq_bits)
        bits_final = [int(b) for b in bits_corrigido_str]
        if err_pos != 0:
            self.result_label.set_text(f"Hamming corrigiu erro na posição {err_pos}")
    else:
        self.result_label.set_text("Erro: EDC desconhecido")
        return

    # Passo 5: bits para texto
    text_out = self.rx.bits2Text(bits_final)

    # Exibe o texto recebido
    self.result_label.set_text(f"Texto recebido: {text_out}")


def main():
  win = InterfaceGUI()
  win.connect("destroy", Gtk.main_quit)
  win.show_all()
  Gtk.main()



