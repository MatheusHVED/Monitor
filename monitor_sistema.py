import customtkinter as ctk
import psutil
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import collections
import platform

# Tenta importar e inicializar a biblioteca da NVIDIA
try:
    import pynvml
    pynvml.nvmlInit()
    GPU_MONITORING_AVAILABLE = True
except (ImportError, pynvml.NVMLError):
    GPU_MONITORING_AVAILABLE = False


class SystemMonitorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Configuração da Janela Principal ---
        self.title("Monitor de Recursos do Sistema")
        self.geometry("1000x650")
        self.grid_columnconfigure((0, 1, 2), weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Armazenamento de Dados para Gráficos ---
        # Usamos deque para manter uma lista de tamanho fixo de forma eficiente
        self.history_points = 100
        self.cpu_data = collections.deque([0] * self.history_points, maxlen=self.history_points)
        self.mem_data = collections.deque([0] * self.history_points, maxlen=self.history_points)
        if GPU_MONITORING_AVAILABLE:
            self.gpu_data = collections.deque([0] * self.history_points, maxlen=self.history_points)

        # --- Inicialização da UI ---
        self.create_widgets()

        # --- Iniciar a atualização dos dados ---
        self.update_stats()
        
        # --- Lidar com o fechamento da janela ---
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        # --- Título Principal ---
        title_label = ctk.CTkLabel(self, text="Monitor de Desempenho em Tempo Real", font=ctk.CTkFont(size=24, weight="bold"))
        title_label.grid(row=0, column=0, columnspan=3, padx=20, pady=(20, 10))

        # --- Seção da CPU ---
        self.cpu_frame, self.cpu_percent_label, self.cpu_ax = self.create_monitor_frame("CPU", 1, 0)

        # --- Seção da Memória ---
        self.mem_frame, self.mem_percent_label, self.mem_ax = self.create_monitor_frame("Memória RAM", 1, 1)

        # --- Seção da GPU ---
        self.gpu_frame, self.gpu_percent_label, self.gpu_ax = self.create_monitor_frame("GPU", 1, 2)
        
        # --- Rótulo de Informações do Sistema ---
        sys_info = f"Sistema: {platform.system()} {platform.release()} | Processador: {platform.processor()}"
        info_label = ctk.CTkLabel(self, text=sys_info, font=ctk.CTkFont(size=10))
        info_label.grid(row=2, column=0, columnspan=3, padx=20, pady=(10, 20), sticky="s")


    def create_monitor_frame(self, title, row, col):
        """Cria um frame padronizado para um recurso (CPU, RAM, GPU)."""
        frame = ctk.CTkFrame(self)
        frame.grid(row=row, column=col, padx=20, pady=10, sticky="nsew")
        frame.grid_rowconfigure(2, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        # Título do Frame
        title_label = ctk.CTkLabel(frame, text=f"Uso de {title}", font=ctk.CTkFont(size=16, weight="bold"))
        title_label.grid(row=0, column=0, padx=10, pady=(10, 5))

        # Rótulo da Porcentagem
        percent_label = ctk.CTkLabel(frame, text="0.0%", font=ctk.CTkFont(size=28))
        percent_label.grid(row=1, column=0, padx=10, pady=5)
        
        if title == "GPU" and not GPU_MONITORING_AVAILABLE:
            percent_label.configure(text="N/A (GPU NVIDIA não detectada)", font=ctk.CTkFont(size=14))

        # Frame para o Gráfico
        graph_frame = ctk.CTkFrame(frame, fg_color="transparent")
        graph_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

        # Configuração do Gráfico Matplotlib
        fig = Figure(figsize=(5, 4), dpi=100)
        fig.patch.set_facecolor("#2b2b2b") # Cor de fundo doCTkFrame padrão
        ax = fig.add_subplot(111)

        # Estilizando o gráfico
        ax.set_facecolor("#343638")
        ax.tick_params(axis='y', colors='white')
        ax.tick_params(axis='x', colors='white')
        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.set_ylim(0, 100)
        ax.set_title(f"Histórico de Uso (%)", color="white", fontsize=10)

        canvas = FigureCanvasTkAgg(fig, master=graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=ctk.TOP, fill=ctk.BOTH, expand=True)

        return frame, percent_label, ax

    def update_stats(self):
        """Função principal para atualizar dados e gráficos."""
        # --- Atualizar CPU ---
        cpu_percent = psutil.cpu_percent(interval=None)
        self.cpu_percent_label.configure(text=f"{cpu_percent:.1f}%")
        self.cpu_data.append(cpu_percent)
        self.update_plot(self.cpu_ax, self.cpu_data, "CPU", "#1f77b4") # Azul

        # --- Atualizar Memória ---
        mem_info = psutil.virtual_memory()
        self.mem_percent_label.configure(text=f"{mem_info.percent:.1f}%")
        self.mem_data.append(mem_info.percent)
        self.update_plot(self.mem_ax, self.mem_data, "Memória", "#2ca02c") # Verde

        # --- Atualizar GPU (se disponível) ---
        if GPU_MONITORING_AVAILABLE:
            try:
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                gpu_percent = util.gpu
                self.gpu_percent_label.configure(text=f"{gpu_percent:.1f}%")
                self.gpu_data.append(gpu_percent)
                self.update_plot(self.gpu_ax, self.gpu_data, "GPU", "#ff7f0e") # Laranja
            except pynvml.NVMLError:
                 self.gpu_percent_label.configure(text="Erro ao ler GPU", font=ctk.CTkFont(size=14))

        # Agendar a próxima atualização para daqui a 1 segundo (1000 ms)
        self.after(1000, self.update_stats)

    def update_plot(self, ax, data, label, color):
        """Atualiza um único gráfico."""
        ax.clear()
        ax.plot(list(data), color=color, linewidth=2)
        ax.set_ylim(0, 100)
        
        # Re-aplica estilo após limpar
        ax.set_facecolor("#343638")
        ax.tick_params(axis='y', colors='white', labelsize=8)
        ax.set_xticks([]) # Oculta os rótulos do eixo X para um visual mais limpo
        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.set_title(f"Histórico de Uso (%)", color="white", fontsize=10)
        
        # Redesenha o canvas do respectivo gráfico
        ax.figure.canvas.draw()
        
    def on_closing(self):
        """Função chamada ao fechar a janela."""
        if GPU_MONITORING_AVAILABLE:
            pynvml.nvmlShutdown()
        self.destroy()


if __name__ == "__main__":
    # Define a aparência do app (System, Dark, Light)
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    app = SystemMonitorApp()
    app.mainloop()