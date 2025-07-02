import tkinter as tk
from tkinter import ttk, font
import threading
import time
from datetime import datetime
import os
import platform
import psutil

# Importa nossos módulos de monitoramento
from cpu_monitor import obter_uso_cpu, obter_frequencia_cpu, obter_modelo_cpu
from ram_monitor import obter_uso_ram, obter_swap
from gpu_monitor import obter_uso_gpu
from process_monitor import obter_processos_top, obter_processos_memoria

class MonitorHardware:
    def __init__(self):
        # Cria a janela principal
        self.root = tk.Tk()
        self.root.title("Monitor de Hardware")
        self.root.geometry("1000x700")
        self.root.configure(bg='#1a1a1a')
        
        # Configura fontes
        self.fonte_titulo = font.Font(family="Arial", size=14, weight="bold")
        self.fonte_subtitulo = font.Font(family="Arial", size=12, weight="bold")
        self.fonte_normal = font.Font(family="Arial", size=10)
        self.fonte_pequena = font.Font(family="Arial", size=9)
        
        # Variável para controlar se o programa está rodando
        self.rodando = True
        
        # Variável para controlar qual tela está ativa
        self.tela_atual = "overview"
        
        self.botoes_nav = {}  # <-- Mova esta linha para cá, antes de criar a interface
        
        # Cria a interface
        self.criar_interface()
        
        # Inicia o thread de atualização dos dados
        self.thread_atualizacao = threading.Thread(target=self.loop_atualizacao)
        self.thread_atualizacao.daemon = True
        self.thread_atualizacao.start()
    
    def criar_interface(self):
        """Cria a interface principal com barra lateral"""
        
        # Frame principal que contém tudo
        main_container = tk.Frame(self.root, bg='#1a1a1a')
        main_container.pack(fill='both', expand=True)
        
        # === BARRA LATERAL ===
        self.criar_barra_lateral(main_container)
        
        # === ÁREA DE CONTEÚDO ===
        self.content_frame = tk.Frame(main_container, bg='#1a1a1a')
        self.content_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)
        
        # Cria todas as telas (inicialmente ocultas)
        self.criar_todas_telas()
        
        # Mostra a tela inicial
        self.mostrar_tela("overview")
    
    def criar_barra_lateral(self, parent):
        """Cria a barra lateral com botões de navegação modernos"""
        sidebar = tk.Frame(parent, bg='#18181b', width=220)
        sidebar.pack(side='left', fill='y', padx=(0,0), pady=0)
        sidebar.pack_propagate(False)

        # Título
        title_container = tk.Frame(sidebar, bg='#18181b')
        title_container.pack(pady=(30, 30))
        titulo = tk.Label(
            sidebar,
            text="⚙️  Monitor",
            bg='#18181b',
            fg='#4a9eff',
            font=self.fonte_titulo,
            anchor='w'
        )
        titulo.pack(pady=(30, 30), padx=18, anchor='w')

        # Função para criar botão estilizado
        def criar_botao(parent, texto, icone, tela):
            def comando(event=None):
                self.mostrar_tela(tela)
            btn = tk.Frame(parent, bg='#23232b', cursor="hand2")
            btn.pack(fill='x', padx=18, pady=6)
            btn.bind("<Button-1>", comando)

            # Ícone
            lbl_icone = tk.Label(btn, text=icone, bg='#23232b', fg='#f3f3f3', font=("Segoe UI Emoji", 16))
            lbl_icone.pack(side='left', padx=(12, 8), pady=8)
            # Texto
            lbl_texto = tk.Label(btn, text=texto, bg='#23232b', fg='#f3f3f3', font=self.fonte_normal)
            lbl_texto.pack(side='left', pady=8)

            # Hover e ativo
            def on_enter(e):
                if self.tela_atual != tela:
                    btn.config(bg='#2d2d38')
                    lbl_icone.config(bg='#2d2d38')
                    lbl_texto.config(bg='#2d2d38')
            def on_leave(e):
                cor = '#4a9eff' if self.tela_atual == tela else '#23232b'
                btn.config(bg=cor)
                lbl_icone.config(bg=cor)
                lbl_texto.config(bg=cor)
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)

            # Salva referência para atualização de cor
            self.botoes_nav[tela] = (btn, lbl_icone, lbl_texto)

        # Crie os botões assim:
        criar_botao(sidebar, "Visão Geral", "📊", "overview")
        criar_botao(sidebar, "CPU", "🖥️", "cpu")
        criar_botao(sidebar, "GPU", "🎮", "gpu")
        criar_botao(sidebar, "RAM", "💾", "ram")

        # Espaçador
        tk.Frame(sidebar, bg='#18181b', height=20).pack()

        # Informações do sistema
        info_frame = tk.Frame(sidebar, bg='#18181b')
        info_frame.pack(fill='x', padx=10, pady=10)
        tk.Label(info_frame, text="Sistema:", bg='#18181b', fg='#888888', font=self.fonte_pequena).pack(anchor='w')
        self.label_sistema = tk.Label(info_frame, text="Detectando...", bg='#18181b', fg='#ffffff', font=self.fonte_pequena, wraplength=150)
        self.label_sistema.pack(anchor='w')

        # Hora atual
        self.label_hora = tk.Label(sidebar, text="", bg='#18181b', fg='#888888', font=self.fonte_pequena)
        self.label_hora.pack(side='bottom', pady=10)
        
        so = platform.system()
        versao = platform.release()
        self.label_sistema.config(text=f"{so} {versao}")
    
    def criar_todas_telas(self):
        """Cria todas as telas do aplicativo"""
        
        # Dicionário para armazenar as telas
        self.telas = {}
        
        # Cria cada tela
        self.telas['overview'] = self.criar_tela_overview()
        self.telas['cpu'] = self.criar_tela_cpu()
        self.telas['gpu'] = self.criar_tela_gpu()
        self.telas['ram'] = self.criar_tela_ram()
    
    def criar_tela_overview(self):
        """Cria a tela de visão geral"""
        frame = tk.Frame(self.content_frame, bg='#1a1a1a')

        # Título e subtítulo
        titulo = tk.Label(frame, text="Visão Geral do Sistema", bg='#1a1a1a', fg='#4a9eff', font=("Arial", 20, "bold"))
        titulo.pack(pady=(10, 0))
        subtitulo = tk.Label(
            frame,
            text=f"{platform.node()} • {platform.system()} {platform.release()}",
            bg='#1a1a1a', fg='#888', font=("Arial", 10)
        )
        subtitulo.pack(pady=(0, 10))

        # Cards de resumo
        resumo_frame = tk.Frame(frame, bg='#1a1a1a')
        resumo_frame.pack(fill='x', pady=10)

        self.card_cpu = self.criar_card_resumo(resumo_frame, "CPU", "🖥️", "Carregando...")
        self.card_gpu = self.criar_card_resumo(resumo_frame, "GPU", "🎮", "Carregando...")
        self.card_ram = self.criar_card_resumo(resumo_frame, "RAM", "💾", "Carregando...")

        # Informações extras
        info_frame = tk.Frame(frame, bg='#23232b')
        info_frame.pack(fill='x', pady=(10, 0), padx=10)
        # Uptime
        uptime = int(time.time() - psutil.boot_time())
        horas, resto = divmod(uptime, 3600)
        minutos, segundos = divmod(resto, 60)
        uptime_str = f"{horas}h {minutos}m"
        # Usuário
        usuario = os.getlogin() if hasattr(os, "getlogin") else "Usuário"
        # Processos ativos
        n_proc = len(psutil.pids())
        # Labels
        tk.Label(info_frame, text=f"⏱️ Uptime: {uptime_str}", bg='#23232b', fg='#f3f3f3', font=self.fonte_pequena).pack(side='left', padx=12, pady=6)
        tk.Label(info_frame, text=f"👤 Usuário: {usuario}", bg='#23232b', fg='#f3f3f3', font=self.fonte_pequena).pack(side='left', padx=12, pady=6)
        tk.Label(info_frame, text=f"⚙️ Processos: {n_proc}", bg='#23232b', fg='#f3f3f3', font=self.fonte_pequena).pack(side='left', padx=12, pady=6)

        # Tabela de processos
        proc_frame = tk.LabelFrame(frame, text="Processos com Maior Consumo", bg='#23232b', fg='#4a9eff', font=self.fonte_subtitulo)
        proc_frame.pack(fill='both', expand=True, pady=16, padx=0)

        # Cabeçalho da tabela
        header = tk.Frame(proc_frame, bg='#23232b')
        header.pack(fill='x', padx=10, pady=(8, 2))
        tk.Label(header, text="📝 Nome", bg='#23232b', fg='#4a9eff', font=self.fonte_pequena, width=22, anchor='w').pack(side='left')
        tk.Label(header, text="CPU %", bg='#23232b', fg='#4a9eff', font=self.fonte_pequena, width=8, anchor='e').pack(side='left')
        tk.Label(header, text="RAM MB", bg='#23232b', fg='#4a9eff', font=self.fonte_pequena, width=10, anchor='e').pack(side='left')

        # Container para linhas dos processos
        self.proc_table_container = tk.Frame(proc_frame, bg='#23232b')
        self.proc_table_container.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        return frame
    
    def criar_card_resumo(self, parent, titulo, icone, valor):
        """Cria um card de resumo para a tela overview"""
        card = tk.Frame(parent, bg='#23232b', relief='ridge', bd=1)
        card.pack(side='left', fill='x', expand=True, padx=8, pady=5)
        # Ícone
        tk.Label(card, text=icone, bg='#23232b', fg='#4a9eff', font=("Segoe UI Emoji", 22)).pack(pady=(8, 0))
        # Valor
        label_valor = tk.Label(card, text=valor, bg='#23232b', fg='#fff', font=("Arial", 18, "bold"))
        label_valor.pack(pady=(2, 0))
        # Título
        tk.Label(card, text=titulo, bg='#23232b', fg='#aaa', font=self.fonte_pequena).pack(pady=(0, 8))
        return label_valor
    
    def criar_tela_cpu(self):
        """Cria a tela detalhada da CPU"""
        
        frame = tk.Frame(self.content_frame, bg='#1a1a1a')
        
        # Título
        titulo = tk.Label(frame, text="Detalhes da CPU", 
                         bg='#1a1a1a', fg='#4a9eff', font=self.fonte_titulo)
        titulo.pack(pady=10)
        
        # Frame superior com informações gerais
        info_frame = tk.LabelFrame(frame, text="Informações Gerais", 
                                 bg='#2a2a2a', fg='#4a9eff', 
                                 font=self.fonte_subtitulo)
        info_frame.pack(fill='x', pady=5)
        
        # Labels de informações
        self.cpu_info_frame = tk.Frame(info_frame, bg='#2a2a2a')
        self.cpu_info_frame.pack(fill='x', padx=10, pady=5)
        
        self.label_cpu_modelo = tk.Label(self.cpu_info_frame, text="Modelo: Detectando...", 
                                       bg='#2a2a2a', fg='#ffffff', font=self.fonte_normal)
        self.label_cpu_modelo.pack(anchor='w')
        
        self.label_cpu_cores = tk.Label(self.cpu_info_frame, text="Núcleos: --", 
                                      bg='#2a2a2a', fg='#ffffff', font=self.fonte_normal)
        self.label_cpu_cores.pack(anchor='w')
        
        self.label_cpu_freq = tk.Label(self.cpu_info_frame, text="Frequência: -- MHz", 
                                     bg='#2a2a2a', fg='#ffffff', font=self.fonte_normal)
        self.label_cpu_freq.pack(anchor='w')
        
        self.label_cpu_uso_total = tk.Label(self.cpu_info_frame, text="Uso Total: --%", 
                                          bg='#2a2a2a', fg='#ff8c42', font=self.fonte_normal)
        self.label_cpu_uso_total.pack(anchor='w')
        
        # Frame dos núcleos
        cores_frame = tk.LabelFrame(frame, text="Uso por Núcleo", 
                                  bg='#2a2a2a', fg='#4a9eff', 
                                  font=self.fonte_subtitulo)
        cores_frame.pack(fill='both', expand=True, pady=5)
        
        # Container dos cores
        self.cpu_cores_container = tk.Frame(cores_frame, bg='#2a2a2a')
        self.cpu_cores_container.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Lista será criada dinamicamente baseada no número de cores
        self.labels_cpu_cores = []
        
        return frame
    
    def criar_tela_gpu(self):
        """Cria a tela detalhada da GPU"""
        
        frame = tk.Frame(self.content_frame, bg='#0f0f0f')
        
        # Container principal com padding
        container = tk.Frame(frame, bg='#0f0f0f')
        container.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Título 
        titulo = tk.Label(container, text="GPU Performance", 
                         bg='#0f0f0f', fg='#ffffff', 
                         font=('Segoe UI', 20, 'bold'))
        titulo.pack(pady=(0, 20))
        
        # Cards de métricas principais
        metrics_frame = tk.Frame(container, bg='#0f0f0f')
        metrics_frame.pack(fill='x', pady=(0, 20))
        
        # Card de Uso
        uso_card = tk.Frame(metrics_frame, bg='#1a1a1a')
        uso_card.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        tk.Label(uso_card, text="Uso GPU", bg='#1a1a1a', fg='#94a3b8', 
                 font=('Segoe UI', 10)).pack(pady=(10, 0))
        self.label_gpu_uso_card = tk.Label(uso_card, text="0%", bg='#1a1a1a', fg='#3b82f6', 
                                          font=('Segoe UI', 18, 'bold'))
        self.label_gpu_uso_card.pack(pady=(5, 10))
        
        # Card de Memória
        mem_card = tk.Frame(metrics_frame, bg='#1a1a1a')
        mem_card.pack(side='left', fill='both', expand=True, padx=5)
        
        tk.Label(mem_card, text="Memória", bg='#1a1a1a', fg='#94a3b8', 
                 font=('Segoe UI', 10)).pack(pady=(10, 0))
        self.label_gpu_mem_card = tk.Label(mem_card, text="0 GB", bg='#1a1a1a', fg='#10b981', 
                                          font=('Segoe UI', 18, 'bold'))
        self.label_gpu_mem_card.pack(pady=(5, 10))
        
        # Card de Temperatura
        temp_card = tk.Frame(metrics_frame, bg='#1a1a1a')
        temp_card.pack(side='left', fill='both', expand=True, padx=(5, 0))
        
        tk.Label(temp_card, text="Temperatura", bg='#1a1a1a', fg='#94a3b8', 
                 font=('Segoe UI', 10)).pack(pady=(10, 0))
        self.label_gpu_temp_card = tk.Label(temp_card, text="0°C", bg='#1a1a1a', fg='#f59e0b', 
                                           font=('Segoe UI', 18, 'bold'))
        self.label_gpu_temp_card.pack(pady=(5, 10))
        
        # Informações detalhadas
        info_frame = tk.Frame(container, bg='#1a1a1a')
        info_frame.pack(fill='x', pady=(0, 20), ipady=15, ipadx=15)
        
        tk.Label(info_frame, text="Informações", bg='#1a1a1a', fg='#ffffff', 
                 font=('Segoe UI', 12, 'bold')).pack(anchor='w', pady=(0, 10))
        
        # Labels das informações
        self.label_gpu_nome_det = tk.Label(info_frame, text="Nome: Detectando...", 
                                          bg='#1a1a1a', fg='#e2e8f0', 
                                          font=('Segoe UI', 10))
        self.label_gpu_nome_det.pack(anchor='w', pady=2)
        
        self.label_gpu_uso_det = tk.Label(info_frame, text="Uso: --%", 
                                         bg='#1a1a1a', fg='#e2e8f0', 
                                         font=('Segoe UI', 10))
        self.label_gpu_uso_det.pack(anchor='w', pady=2)
        
        self.label_gpu_memoria_det = tk.Label(info_frame, text="Memória: -- / -- MB", 
                                             bg='#1a1a1a', fg='#e2e8f0', 
                                             font=('Segoe UI', 10))
        self.label_gpu_memoria_det.pack(anchor='w', pady=2)
        
        self.label_gpu_temp = tk.Label(info_frame, text="Temperatura: --°C", 
                                      bg='#1a1a1a', fg='#e2e8f0', 
                                      font=('Segoe UI', 10))
        self.label_gpu_temp.pack(anchor='w', pady=2)
        
        # Gráfico
        grafico_frame = tk.Frame(container, bg='#1a1a1a')
        grafico_frame.pack(fill='both', expand=True, ipady=15, ipadx=15)
        
        tk.Label(grafico_frame, text="Histórico de Uso", bg='#1a1a1a', fg='#ffffff', 
                 font=('Segoe UI', 12, 'bold')).pack(anchor='w', pady=(0, 10))
        
        # Canvas para o gráfico
        self.canvas_gpu = tk.Canvas(grafico_frame, bg='#0f0f0f', height=200)
        self.canvas_gpu.pack(fill='both', expand=True)
        
        # Lista para armazenar histórico de uso
        self.historico_gpu = []
        
        return frame

    def atualizar_cards_gpu(self, uso=None, memoria_usada=None, memoria_total=None, temperatura=None):
        """Atualiza os cards de métricas de forma simples"""
        
        if uso is not None:
            self.label_gpu_uso_card.config(text=f"{uso:.1f}%")
            # Muda cor baseado no uso
            cor = "#ef4444" if uso > 80 else "#f59e0b" if uso > 50 else "#10b981"
            self.label_gpu_uso_card.config(fg=cor)
        
        if memoria_usada is not None and memoria_total is not None:
            mem_gb = memoria_usada / 1024
            self.label_gpu_mem_card.config(text=f"{mem_gb:.1f} GB")
        
        if temperatura is not None:
            self.label_gpu_temp_card.config(text=f"{temperatura}°C")
            # Muda cor baseado na temperatura
            cor = "#ef4444" if temperatura > 80 else "#f59e0b" if temperatura > 70 else "#10b981"
            self.label_gpu_temp_card.config(fg=cor)
    
    def atualizar_cores_sidebar(self):
        for tela, (btn, lbl_icone, lbl_texto) in self.botoes_nav.items():
            cor = '#4a9eff' if tela == self.tela_atual else '#23232b'
            fg = '#fff' if tela == self.tela_atual else '#f3f3f3'
            btn.config(bg=cor)
            lbl_icone.config(bg=cor, fg=fg)
            lbl_texto.config(bg=cor, fg=fg)
    
    def criar_tela_ram(self):
        """Cria a tela detalhada da RAM"""
        
        frame = tk.Frame(self.content_frame, bg='#1a1a1a')
        
        # Título
        titulo = tk.Label(frame, text="Detalhes da Memória RAM", 
                         bg='#1a1a1a', fg='#4a9eff', font=self.fonte_titulo)
        titulo.pack(pady=10)
        
        # Frame de informações da RAM
        ram_frame = tk.LabelFrame(frame, text="Memória Principal", 
                                bg='#2a2a2a', fg='#4a9eff', 
                                font=self.fonte_subtitulo)
        ram_frame.pack(fill='x', pady=5)
        
        self.ram_info_container = tk.Frame(ram_frame, bg='#2a2a2a')
        self.ram_info_container.pack(fill='x', padx=10, pady=5)
        
        # Labels da RAM
        self.label_ram_total = tk.Label(self.ram_info_container, text="Total: -- GB", 
                                      bg='#2a2a2a', fg='#ffffff', font=self.fonte_normal)
        self.label_ram_total.pack(anchor='w')
        
        self.label_ram_usada = tk.Label(self.ram_info_container, text="Usada: -- GB", 
                                      bg='#2a2a2a', fg='#ff8c42', font=self.fonte_normal)
        self.label_ram_usada.pack(anchor='w')
        
        self.label_ram_livre = tk.Label(self.ram_info_container, text="Livre: -- GB", 
                                      bg='#2a2a2a', fg='#4eff4a', font=self.fonte_normal)
        self.label_ram_livre.pack(anchor='w')
        
        self.label_ram_percent = tk.Label(self.ram_info_container, text="Porcentagem: --%", 
                                        bg='#2a2a2a', fg='#ff8c42', font=self.fonte_normal)
        self.label_ram_percent.pack(anchor='w')
        
        # Frame do Swap
        swap_frame = tk.LabelFrame(frame, text="Memória Swap", 
                                 bg='#2a2a2a', fg='#4a9eff', 
                                 font=self.fonte_subtitulo)
        swap_frame.pack(fill='x', pady=5)
        
        self.swap_info_container = tk.Frame(swap_frame, bg='#2a2a2a')
        self.swap_info_container.pack(fill='x', padx=10, pady=5)
        
        self.label_swap_info = tk.Label(self.swap_info_container, text="Swap: -- / -- GB", 
                                      bg='#2a2a2a', fg='#ffffff', font=self.fonte_normal)
        self.label_swap_info.pack(anchor='w')
        
        # Frame dos processos que mais usam RAM
        proc_ram_frame = tk.LabelFrame(frame, text="Processos que Mais Usam RAM", 
                                     bg='#2a2a2a', fg='#4a9eff', 
                                     font=self.fonte_subtitulo)
        proc_ram_frame.pack(fill='both', expand=True, pady=5)
        
        self.listbox_ram_proc = tk.Listbox(proc_ram_frame, bg='#1a1a1a', fg='#ffffff',
                                         font=self.fonte_pequena, height=6)
        self.listbox_ram_proc.pack(fill='both', expand=True, padx=10, pady=5)
        
        return frame
    
    def mostrar_tela(self, nome_tela):
        """Mostra uma tela específica e esconde as outras"""
        
        # Esconde todas as telas
        for tela in self.telas.values():
            tela.pack_forget()
        
        # Mostra a tela solicitada
        if nome_tela in self.telas:
            self.telas[nome_tela].pack(fill='both', expand=True)
            self.tela_atual = nome_tela
            self.atualizar_cores_sidebar()
            
            # Atualiza cor dos botões de navegação
            for tela, (btn, lbl_icone, lbl_texto) in self.botoes_nav.items():
                cor = '#4a9eff' if tela == nome_tela else '#3a3a3a'
                btn.config(bg=cor)
                lbl_icone.config(bg=cor)
                lbl_texto.config(bg=cor)
    
    def atualizar_dados(self):
        """Atualiza todos os dados nas interfaces"""
        
        # Atualiza hora
        agora = datetime.now().strftime("%H:%M:%S")
        self.label_hora.config(text=agora)
        
        # Obtém dados de todos os componentes
        dados_cpu = obter_uso_cpu()
        dados_gpu = obter_uso_gpu()
        dados_ram = obter_uso_ram()
        dados_swap = obter_swap()
        processos_cpu = obter_processos_top(8)
        processos_ram = obter_processos_memoria(6)
        
        # Atualiza tela overview
        self.atualizar_overview(dados_cpu, dados_gpu, dados_ram, processos_cpu)
        
        # Atualiza tela específica da CPU
        self.atualizar_cpu_detalhada(dados_cpu)
        
        # Atualiza tela específica da GPU
        self.atualizar_gpu_detalhada(dados_gpu)
        
        # Atualiza tela específica da RAM
        self.atualizar_ram_detalhada(dados_ram, dados_swap, processos_ram)
    
    def atualizar_overview(self, cpu, gpu, ram, processos):
        """Atualiza a tela de visão geral"""
        self.card_cpu.config(text=f"{cpu['uso_total']}%")
        if gpu['disponivel']:
            self.card_gpu.config(text=f"{gpu['uso_porcentagem']}%")
        else:
            self.card_gpu.config(text="N/A")
        self.card_ram.config(text=f"{ram['porcentagem_usada']}%")

        # Limpa tabela de processos
        for widget in self.proc_table_container.winfo_children():
            widget.destroy()
        for proc in processos:
            if proc['nome'].lower() in ["system idle process", "idle"]:
                continue
            memoria_mb = proc.get('memoria_bytes', 0) / (1024 * 1024) if 'memoria_bytes' in proc else proc.get('memoria_mb', 0)
            row = tk.Frame(self.proc_table_container, bg='#23232b')
            row.pack(fill='x', pady=1)
            # Ícone de processo + nome
            tk.Label(row, text="🔹", bg='#23232b', fg='#4a9eff', font=("Segoe UI Emoji", 10), width=2, anchor='w').pack(side='left')
            tk.Label(row, text=f"{proc['nome'][:20]}", bg='#23232b', fg='#fff', font=self.fonte_pequena, width=20, anchor='w').pack(side='left')
            tk.Label(row, text=f"{proc['cpu_percent']:>5.1f}%", bg='#23232b', fg='#ff8c42', font=self.fonte_pequena, width=8, anchor='e').pack(side='left')
            tk.Label(row, text=f"{memoria_mb:>7.1f} MB", bg='#23232b', fg='#4eff4a', font=self.fonte_pequena, width=10, anchor='e').pack(side='left')
    
    def atualizar_cpu_detalhada(self, dados):
        """Atualiza a tela detalhada da CPU"""
        # Atualiza informações gerais
        self.label_cpu_modelo.config(text=f"Modelo: {obter_modelo_cpu()}")
        self.label_cpu_cores.config(text=f"Núcleos: {dados['numero_cores']}")
        self.label_cpu_freq.config(text=f"Frequência: {obter_frequencia_cpu()} MHz")
        self.label_cpu_uso_total.config(text=f"Uso Total: {dados['uso_total']}%")
        
        # Atualiza cores (cria se necessário)
        if len(self.labels_cpu_cores) != dados['numero_cores']:
            # Limpa container
            for widget in self.cpu_cores_container.winfo_children():
                widget.destroy()
            self.labels_cpu_cores.clear()
            
            # Cria novos labels para cores
            for i in range(dados['numero_cores']):
                core_frame = tk.Frame(self.cpu_cores_container, bg='#3a3a3a', relief='ridge', bd=1)
                core_frame.pack(fill='x', pady=2)
                
                label = tk.Label(core_frame, text=f"Core {i}: {dados['uso_por_core'][i]}%", 
                               bg='#3a3a3a', fg='#ffffff', font=self.fonte_normal)
                label.pack(padx=10, pady=5)
                
                self.labels_cpu_cores.append(label)
        
        # Atualiza valores dos cores
        for i, label in enumerate(self.labels_cpu_cores):
            if i < len(dados['uso_por_core']):
                uso = dados['uso_por_core'][i]
                cor = '#ff4444' if uso > 80 else '#ff8c42' if uso > 50 else '#ffffff'
                label.config(text=f"Core {i}: {uso}%", fg=cor)
    
    def atualizar_gpu_detalhada(self, dados):
        """Atualiza a tela detalhada da GPU"""
        if dados['disponivel']:
            self.label_gpu_nome_det.config(text=f"Nome: {dados['nome']}")
            self.label_gpu_uso_det.config(text=f"Uso: {dados['uso_porcentagem']}%")
            self.label_gpu_memoria_det.config(text=f"Memória: {dados['memoria_usada_mb']} / {dados['memoria_total_mb']} MB")
            self.label_gpu_temp.config(text=f"Temperatura: {dados['temperatura']}°C")

            # Atualiza os CARDS principais
            self.atualizar_cards_gpu(
                uso=dados['uso_porcentagem'],
                memoria_usada=dados['memoria_usada_mb'],
                memoria_total=dados['memoria_total_mb'],
                temperatura=dados['temperatura']
            )

            # Atualiza histórico e gráfico
            self.historico_gpu.append(dados['uso_porcentagem'])
            if len(self.historico_gpu) > 50:  # Mantém apenas últimos 50 valores
                self.historico_gpu.pop(0)
            self.desenhar_grafico_gpu()
        else:
            self.label_gpu_nome_det.config(text="Nome: GPU não detectada")
            self.label_gpu_uso_det.config(text="Uso: N/A")
            self.label_gpu_memoria_det.config(text="Memória: N/A")
            self.label_gpu_temp.config(text="Temperatura: N/A")
            # Zera os cards
            self.atualizar_cards_gpu(uso=0, memoria_usada=0, memoria_total=0, temperatura=0)
    
    def atualizar_ram_detalhada(self, ram, swap, processos):
        """Atualiza a tela detalhada da RAM"""
        
        # Atualiza informações da RAM
        self.label_ram_total.config(text=f"Total: {ram['total_gb']} GB")
        self.label_ram_usada.config(text=f"Usada: {ram['usada_gb']} GB")
        self.label_ram_livre.config(text=f"Livre: {ram['disponivel_gb']} GB")
        self.label_ram_percent.config(text=f"Porcentagem: {ram['porcentagem_usada']}%")
        
        # Atualiza informações do swap
        self.label_swap_info.config(text=f"Swap: {swap['usada_gb']} / {swap['total_gb']} GB ({swap['porcentagem']}%)")
        
        # Atualiza lista de processos
        self.listbox_ram_proc.delete(0, tk.END)
        for proc in processos:
            # Exibe RAM em MB
            memoria_mb = proc.get('memoria_bytes', 0) / (1024 * 1024) if 'memoria_bytes' in proc else proc.get('memoria_mb', 0)
            texto = f"{proc['nome'][:25]:<25} RAM: {memoria_mb:>6.1f} MB"
            self.listbox_ram_proc.insert(tk.END, texto)
    
    def loop_atualizacao(self):
        """Loop que roda em background atualizando os dados"""
        while self.rodando:
            try:
                self.atualizar_dados()
                time.sleep(2)  # Atualiza a cada 2 segundos
            except Exception as e:
                print(f"Erro na atualização: {e}")
                time.sleep(5)  # Espera mais tempo se der erro
    
    def iniciar(self):
        """Inicia a aplicação"""
        self.root.protocol("WM_DELETE_WINDOW", self.fechar_aplicacao)
        self.root.mainloop()
    
    def fechar_aplicacao(self):
        """Fecha a aplicação de forma segura"""
        self.rodando = False
        self.root.quit()
        self.root.destroy()

    def desenhar_grafico_gpu(self):
        """Desenha um gráfico moderno, minimalista e polido do uso da GPU"""
        self.canvas_gpu.delete("all")

        if len(self.historico_gpu) < 2:
            self._desenhar_estado_vazio()
            return

        width = self.canvas_gpu.winfo_width()
        height = self.canvas_gpu.winfo_height()

        if width <= 1 or height <= 1:
            return

        # Margens para um visual mais limpo
        margin_x = 20
        margin_y = 15
        chart_width = width - (2 * margin_x)
        chart_height = height - (2 * margin_y)

        # Fundo escuro sutil
        self.canvas_gpu.create_rectangle(0, 0, width, height, fill='#18181b', outline='')

        # Grid minimalista
        self._desenhar_grid_moderno(margin_x, margin_y, chart_width, chart_height)

        # Curva suavizada
        pontos = self._calcular_pontos_suavizados(margin_x, margin_y, chart_width, chart_height)

        # Área sob a curva com camadas de azul
        self._desenhar_area_azul(pontos, margin_x, margin_y, chart_height)

        # Linha principal com sombra
        self._desenhar_linha_com_sombra(pontos)

        # Pontos de destaque nos extremos
        self._desenhar_pontos_destaque(pontos)

        # Labels de valores
        self._desenhar_labels_valores(margin_x, margin_y, chart_width, chart_height)

    def _desenhar_estado_vazio(self):
        width = self.canvas_gpu.winfo_width()
        height = self.canvas_gpu.winfo_height()
        self.canvas_gpu.create_text(
            width//2, height//2,
            text="Coletando dados...",
            fill='#6b7280',
            font=('Arial', 11),
            anchor='center'
        )

    def _desenhar_grid_moderno(self, margin_x, margin_y, chart_width, chart_height):
        # Linhas horizontais principais (0%, 50%, 100%)
        for percent, cor in zip([0, 50, 100], ['#23232b', '#333', '#23232b']):
            y = margin_y + chart_height - (percent / 100) * chart_height
            self.canvas_gpu.create_line(
                margin_x, y, margin_x + chart_width, y,
                fill=cor, width=1
            )
        # Linhas verticais sutis
        num_vertical_lines = 5
        for i in range(1, num_vertical_lines):
            x = margin_x + (chart_width / num_vertical_lines) * i
            self.canvas_gpu.create_line(
                x, margin_y, x, margin_y + chart_height,
                fill='#23232b', width=1
            )

    def _calcular_pontos_suavizados(self, margin_x, margin_y, chart_width, chart_height):
        pontos = []
        dados_suavizados = []
        window_size = min(3, len(self.historico_gpu))
        for i in range(len(self.historico_gpu)):
            start_idx = max(0, i - window_size // 2)
            end_idx = min(len(self.historico_gpu), i + window_size // 2 + 1)
            avg = sum(self.historico_gpu[start_idx:end_idx]) / (end_idx - start_idx)
            dados_suavizados.append(avg)
        for i, valor in enumerate(dados_suavizados):
            x = margin_x + (i / (len(dados_suavizados) - 1)) * chart_width
            y = margin_y + chart_height - (valor / 100) * chart_height
            pontos.append((x, y))
        return pontos

    def _desenhar_area_azul(self, pontos, margin_x, margin_y, chart_height):
        if len(pontos) < 2:
            return
        area_points = [(p[0], p[1]) for p in pontos]
        area_points.append((pontos[-1][0], margin_y + chart_height))
        area_points.append((pontos[0][0], margin_y + chart_height))
        # Camadas de azul para simular profundidade
        colors = ['#4a9eff', '#93c5fd', '#dbeafe']
        for i, color in enumerate(colors):
            offset = i * 2
            adjusted_points = [(x, y + offset) for (x, y) in area_points]
            flat_points = [coord for point in adjusted_points for coord in point]
            self.canvas_gpu.create_polygon(flat_points, fill=color, outline='')

    def _desenhar_linha_com_sombra(self, pontos):
        if len(pontos) < 2:
            return
        # Sombra da linha (offset)
        for i in range(len(pontos) - 1):
            self.canvas_gpu.create_line(
                pontos[i][0] + 1, pontos[i][1] + 1,
                pontos[i+1][0] + 1, pontos[i+1][1] + 1,
                fill='#222', width=4, smooth=True
            )
        # Linha principal
        for i in range(len(pontos) - 1):
            self.canvas_gpu.create_line(
                pontos[i][0], pontos[i][1],
                pontos[i+1][0], pontos[i+1][1],
                fill='#4a9eff', width=3, smooth=True,
                capstyle='round', joinstyle='round'
            )

    def _desenhar_pontos_destaque(self, pontos):
        if len(pontos) < 2:
            return
        for ponto in [pontos[0], pontos[-1]]:
            x, y = ponto
            self.canvas_gpu.create_oval(
                x-6, y-6, x+6, y+6,
                fill='#dbeafe', outline='#4a9eff', width=2
            )
            self.canvas_gpu.create_oval(
                x-3, y-3, x+3, y+3,
                fill='#4a9eff', outline=''
            )

    def _desenhar_labels_valores(self, margin_x, margin_y, chart_width, chart_height):
        for percent in [0, 50, 100]:
            y = margin_y + chart_height - (percent / 100) * chart_height
            self.canvas_gpu.create_text(
                margin_x - 5, y,
                text=f"{percent}%",
                fill='#6b7280',
                font=('Arial', 9),
                anchor='e'
            )
        if self.historico_gpu:
            valor_atual = self.historico_gpu[-1]
            self.canvas_gpu.create_text(
                margin_x + chart_width, margin_y,
                text=f"{valor_atual:.1f}%",
                fill='#4a9eff',
                font=('Arial', 12, 'bold'),
                anchor='ne'
            )

# Executa a aplicação se este arquivo for rodado diretamente
if __name__ == "__main__":
    print("Iniciando Monitor de Hardware...")
    print("Aguarde alguns segundos para os dados aparecerem...")
    
    monitor = MonitorHardware()
    monitor.iniciar()