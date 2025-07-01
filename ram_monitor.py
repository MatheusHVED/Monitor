import psutil

def obter_uso_ram():
    """
    Coleta informações de uso da RAM
    Retorna um dicionário com:
    - porcentagem_usada: % de RAM em uso
    - total_gb: total de RAM em GB
    - usada_gb: RAM usada em GB
    - disponivel_gb: RAM disponível em GB
    """
    try:
        # Obtém informações da memória virtual (RAM)
        memoria = psutil.virtual_memory()
        
        # Converte bytes para gigabytes (dividindo por 1024³)
        total_gb = round(memoria.total / (1024**3), 1)
        usada_gb = round(memoria.used / (1024**3), 1)
        disponivel_gb = round(memoria.available / (1024**3), 1)
        
        # A porcentagem já vem calculada
        porcentagem_usada = round(memoria.percent, 1)
        
        # Organiza os dados
        dados_ram = {
            'porcentagem_usada': porcentagem_usada,
            'total_gb': total_gb,
            'usada_gb': usada_gb,
            'disponivel_gb': disponivel_gb
        }
        
        return dados_ram
        
    except Exception as e:
        print(f"Erro ao obter dados da RAM: {e}")
        # Retorna dados padrão em caso de erro
        return {
            'porcentagem_usada': 0.0,
            'total_gb': 8.0,
            'usada_gb': 0.0,
            'disponivel_gb': 8.0
        }

def obter_swap():
    """
    Obtém informações sobre a memória swap (arquivo de paginação)
    """
    try:
        swap = psutil.swap_memory()
        return {
            'total_gb': round(swap.total / (1024**3), 1),
            'usada_gb': round(swap.used / (1024**3), 1),
            'porcentagem': round(swap.percent, 1)
        }
    except:
        return {
            'total_gb': 0.0,
            'usada_gb': 0.0,
            'porcentagem': 0.0
        }

# Teste da função (só executa se rodar este arquivo diretamente)
if __name__ == "__main__":
    dados = obter_uso_ram()
    swap = obter_swap()
    
    print("=== TESTE DO MONITOR DE RAM ===")
    print(f"RAM total: {dados['total_gb']} GB")
    print(f"RAM usada: {dados['usada_gb']} GB")
    print(f"RAM disponível: {dados['disponivel_gb']} GB")
    print(f"Porcentagem usada: {dados['porcentagem_usada']}%")
    print(f"\nSwap: {swap['usada_gb']}/{swap['total_gb']} GB ({swap['porcentagem']}%)")