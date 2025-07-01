import psutil

def obter_uso_cpu():
    """
    Coleta informações de uso da CPU
    Retorna um dicionário com:
    - uso_total: porcentagem de uso total da CPU
    - uso_por_core: lista com uso de cada núcleo
    - numero_cores: quantidade de núcleos
    """
    try:
        # Obtém o uso total da CPU (média de 0.1 segundos)
        uso_total = psutil.cpu_percent(interval=0.1)
        
        # Obtém o uso de cada núcleo individual
        uso_por_core = psutil.cpu_percent(interval=0.1, percpu=True)
        
        # Conta quantos núcleos temos
        numero_cores = psutil.cpu_count()
        
        # Organiza tudo em um dicionário
        dados_cpu = {
            'uso_total': round(uso_total, 1),
            'uso_por_core': [round(core, 1) for core in uso_por_core],
            'numero_cores': numero_cores
        }
        
        return dados_cpu
        
    except Exception as e:
        print(f"Erro ao obter dados da CPU: {e}")
        # Retorna dados padrão em caso de erro
        return {
            'uso_total': 0.0,
            'uso_por_core': [0.0, 0.0, 0.0, 0.0],
            'numero_cores': 4
        }

def obter_frequencia_cpu():
    """
    Obtém a frequência atual da CPU em MHz
    """
    try:
        freq = psutil.cpu_freq()
        if freq:
            return round(freq.current, 0)
        return 0
    except:
        return 0

# Teste da função (só executa se rodar este arquivo diretamente)
if __name__ == "__main__":
    dados = obter_uso_cpu()
    print("=== TESTE DO MONITOR DE CPU ===")
    print(f"Uso total: {dados['uso_total']}%")
    print(f"Número de cores: {dados['numero_cores']}")
    print("Uso por core:")
    for i, uso in enumerate(dados['uso_por_core']):
        print(f"  Core {i}: {uso}%")
    print(f"Frequência: {obter_frequencia_cpu()} MHz")