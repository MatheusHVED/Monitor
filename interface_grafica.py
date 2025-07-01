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
        titulo = tk.Label(sidebar, text="MONITOR", bg='#18181b', fg='#4a9eff', font=self.fonte_titulo)
        titulo.pack(pady=(30, 30))

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
        
        frame = tk.Frame(self.content_frame, bg='#1a1a1a')
        
        # Título
        titulo = tk.Label(frame, text="Detalhes da GPU", 
                         bg='#1a1a1a', fg='#4a9eff', font=self.fonte_titulo)
        titulo.pack(pady=10)
        
        # Frame de informações
        info_frame = tk.LabelFrame(frame, text="Informações da GPU", 
                                 bg='#2a2a2a', fg='#4a9eff', 
                                 font=self.fonte_subtitulo)
        info_frame.pack(fill='x', pady=5)
        
        self.gpu_info_container = tk.Frame(info_frame, bg='#2a2a2a')
        self.gpu_info_container.pack(fill='x', padx=10, pady=5)
        
        # Labels da GPU
        self.label_gpu_nome_det = tk.Label(self.gpu_info_container, text="Nome: Detectando...", 
                                         bg='#2a2a2a', fg='#ffffff', font=self.fonte_normal)
        self.label_gpu_nome_det.pack(anchor='w')
        
        self.label_gpu_uso_det = tk.Label(self.gpu_info_container, text="Uso: --%", 
                                        bg='#2a2a2a', fg='#ff8c42', font=self.fonte_normal)
        self.label_gpu_uso_det.pack(anchor='w')
        
        self.label_gpu_memoria_det = tk.Label(self.gpu_info_container, text="Memória: -- / -- MB", 
                                            bg='#2a2a2a', fg='#ffffff', font=self.fonte_normal)
        self.label_gpu_memoria_det.pack(anchor='w')
        
        self.label_gpu_temp = tk.Label(self.gpu_info_container, text="Temperatura: --°C", 
                                     bg='#2a2a2a', fg='#ffffff', font=self.fonte_normal)
        self.label_gpu_temp.pack(anchor='w')
        
        # Frame para gráfico simples de uso
        grafico_frame = tk.LabelFrame(frame, text="Histórico de Uso", 
                                    bg='#2a2a2a', fg='#4a9eff', 
                                    font=self.fonte_subtitulo)
        grafico_frame.pack(fill='both', expand=True, pady=5)
        
        # Canvas para desenhar um gráfico simples
        self.canvas_gpu = tk.Canvas(grafico_frame, bg='#1a1a1a', height=200)
        self.canvas_gpu.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Lista para armazenar histórico de uso
        self.historico_gpu = []
        
        return frame
    
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
    
    def desenhar_grafico_gpu(self):
        """Desenha um gráfico simples do uso da GPU"""
        
        self.canvas_gpu.delete("all")
        
        if len(self.historico_gpu) < 2:
            return
        
        width = self.canvas_gpu.winfo_width()
        height = self.canvas_gpu.winfo_height()
        
        if width <= 1 or height <= 1:
            return
        
        # Desenha linhas do gráfico
        for i in range(len(self.historico_gpu) - 1):
            x1 = (i / (len(self.historico_gpu) - 1)) * width
            y1 = height - (self.historico_gpu[i] / 100) * height
            x2 = ((i + 1) / (len(self.historico_gpu) - 1)) * width
            y2 = height - (self.historico_gpu[i + 1] / 100) * height
            
            self.canvas_gpu.create_line(x1, y1, x2, y2, fill='#4a9eff', width=2)
    
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

    def atualizar_cores_sidebar(self):
        for tela, (btn, lbl_icone, lbl_texto) in self.botoes_nav.items():
            cor = '#4a9eff' if tela == self.tela_atual else '#23232b'
            fg = '#fff' if tela == self.tela_atual else '#f3f3f3'
            btn.config(bg=cor)
            lbl_icone.config(bg=cor, fg=fg)
            lbl_texto.config(bg=cor, fg=fg)

# Executa a aplicação se este arquivo for rodado diretamente
if __name__ == "__main__":
    print("Iniciando Monitor de Hardware...")
    print("Aguarde alguns segundos para os dados aparecerem...")
    
    monitor = MonitorHardware()
    monitor.iniciar()