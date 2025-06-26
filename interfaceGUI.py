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


def main():
  win = InterfaceGUI()
  win.connect("destroy", Gtk.main_quit)
  win.show_all()
  Gtk.main()
