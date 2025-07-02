import psutil
import subprocess

def obter_tipo_ram():
    """
    Obtém a tecnologia da RAM (DDR3, DDR4, DDR5...) usando wmic (apenas Windows)
    Retorna uma string com a tecnologia ou 'Desconhecida'
    """
    try:
        # Executa o comando wmic para obter a MemoryType
        resultado = subprocess.run(
            ['wmic', 'MemoryChip', 'get', 'MemoryType'],
            capture_output=True, text=True, timeout=3
        )
        tipo_map = {
            "20": "DDR",
            "21": "DDR2",
            "24": "DDR3",
            "26": "DDR4",
            "30": "DDR5",
            "34": "LPDDR5"
        }
        if resultado.returncode == 0:
            linhas = resultado.stdout.strip().splitlines()
            tipos = [l.strip() for l in linhas[1:] if l.strip()]
            for tipo in tipos:
                tipo_clean = tipo.strip()
                if tipo_clean in tipo_map:
                    return tipo_map[tipo_clean]
            #Se não reconhecido, tenta SMBIOSMemoryType
            if tipos and all(t.strip() == "0" for t in tipos):
                resultado2 = subprocess.run(
                    ['wmic', 'MemoryChip', 'get', 'SMBIOSMemoryType'],
                    capture_output=True, text=True, timeout=3
                )
                smbios_map = {
                    "26": "DDR4",
                    "27": "DDR5",
                    "34": "LPDDR5"
                }
                if resultado2.returncode == 0:
                    linhas2 = resultado2.stdout.strip().splitlines()
                    tipos2 = [l.strip() for l in linhas2[1:] if l.strip()]
                    for tipo2 in tipos2:
                        tipo2_clean = tipo2.strip()
                        if tipo2_clean in smbios_map:
                            return smbios_map[tipo2_clean]
                    if tipos2:
                        return f"Desconhecida (SMBIOS: {', '.join(tipos2)})"
            if tipos:
                return f"Desconhecida (WMIC: {', '.join(tipos)})"
            return "Desconhecida (sem retorno WMIC)"
        else:
            return "Desconhecida (erro WMIC)"
    except Exception as e:
        return f"Desconhecida (erro: {e})"

def obter_uso_ram():
    """
    Coleta informações de uso da RAM
    Retorna um dicionário com:
    - porcentagem_usada: % de RAM em uso
    - total_gb: total de RAM em GB
    - usada_gb: RAM usada em GB
    - disponivel_gb: RAM disponível em GB
    - tipo_ram: tipo da RAM (DDR3, DDR4, DDR5...)
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
        tipo_ram = obter_tipo_ram()
        
        # Organiza os dados
        dados_ram = {
            'porcentagem_usada': porcentagem_usada,
            'total_gb': total_gb,
            'usada_gb': usada_gb,
            'disponivel_gb': disponivel_gb,
            'tipo_ram': tipo_ram
        }
        
        return dados_ram
        
    except Exception as e:
        print(f"Erro ao obter dados da RAM: {e}")
        # Retorna dados padrão em caso de erro
        return {
            'porcentagem_usada': 0.0,
            'total_gb': 8.0,
            'usada_gb': 0.0,
            'disponivel_gb': 8.0,
            'tipo_ram': 'Desconhecida'
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
    print(f"Tipo: {dados['tipo_ram']}")
    print(f"\nSwap: {swap['usada_gb']}/{swap['total_gb']} GB ({swap['porcentagem']}%)")