import psutil

def obter_processos_top(limite=5):
    """
    Obtém os processos que mais consomem CPU
    
    Args:
        limite: quantos processos retornar (padrão: 5)
    
    Returns:
        Lista de dicionários com informações dos processos
    """
    try:
        processos = []
        
        # Percorre todos os processos do sistema
        for processo in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                # Obtém informações do processo
                info = processo.info
                
                # Só adiciona se o processo está usando CPU
                if info['cpu_percent'] and info['cpu_percent'] > 0:
                    mem = processo.memory_info()
                    memoria_bytes = getattr(mem, 'wset', mem.rss)
                    processos.append({
                        'pid': info['pid'],
                        'nome': info['name'][:20],  # Limita o nome a 20 caracteres
                        'cpu_percent': round(info['cpu_percent'], 1),
                        'memoria_percent': round(info['memory_percent'], 1),
                        'memoria_bytes': memoria_bytes
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                # Ignora processos que não conseguimos acessar
                continue
        
        # Ordena por uso de CPU (maior primeiro) e pega os primeiros
        processos_ordenados = sorted(processos, 
                                   key=lambda x: x['cpu_percent'], 
                                   reverse=True)
        
        return processos_ordenados[:limite]
        
    except Exception as e:
        print(f"Erro ao obter processos: {e}")
        return []

def obter_processos_memoria(limite=5):
    """
    Obtém os processos que mais consomem memória
    """
    try:
        processos = []
        
        for processo in psutil.process_iter(['pid', 'name', 'memory_percent']):
            try:
                info = processo.info
                
                if info['memory_percent'] and info['memory_percent'] > 0:
                    mem = processo.memory_info()
                    memoria_bytes = getattr(mem, 'wset', mem.rss)
                    processos.append({
                        'pid': info['pid'],
                        'nome': info['name'][:20],
                        'memoria_percent': round(info['memory_percent'], 1),
                        'memoria_bytes': memoria_bytes
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Ordena por uso de memória
        processos_ordenados = sorted(processos, 
                                   key=lambda x: x['memoria_percent'], 
                                   reverse=True)
        
        return processos_ordenados[:limite]
        
    except Exception as e:
        print(f"Erro ao obter processos por memória: {e}")
        return []

def obter_info_sistema():
    """
    Obtém informações gerais do sistema
    """
    try:
        return {
            'processos_totais': len(psutil.pids()),
            'boot_time': psutil.boot_time(),
            'usuarios_logados': len(psutil.users())
        }
    except:
        return {
            'processos_totais': 0,
            'boot_time': 0,
            'usuarios_logados': 0
        }

# Teste da função (só executa se rodar este arquivo diretamente)
if __name__ == "__main__":
    print("=== TESTE DO MONITOR DE PROCESSOS ===")
    
    print("\n--- TOP 5 PROCESSOS POR CPU ---")
    processos_cpu = obter_processos_top(5)
    for i, proc in enumerate(processos_cpu, 1):
        print(f"{i}. {proc['nome']} (PID: {proc['pid']}) - CPU: {proc['cpu_percent']}%")
    
    print("\n--- TOP 5 PROCESSOS POR MEMÓRIA ---")
    processos_mem = obter_processos_memoria(5)
    for i, proc in enumerate(processos_mem, 1):
        print(f"{i}. {proc['nome']} (PID: {proc['pid']}) - RAM: {proc['memoria_percent']}%")
    
    info = obter_info_sistema()
    print(f"\n--- INFO SISTEMA ---")
    print(f"Total de processos: {info['processos_totais']}")
    print(f"Usuários logados: {info['usuarios_logados']}")