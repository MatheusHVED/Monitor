import subprocess
import re

def obter_uso_gpu_nvidia():
    """
    Tenta obter informações da GPU NVIDIA usando nvidia-smi
    Retorna um dicionário com informações da GPU ou None se não conseguir
    """
    try:
        # Executa o comando nvidia-smi para obter informações da GPU
        resultado = subprocess.run([
            'nvidia-smi', 
            '--query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu,name',
            '--format=csv,noheader,nounits'
        ], capture_output=True, text=True, timeout=5)
        
        if resultado.returncode == 0:
            # Processa a saída do comando
            linha = resultado.stdout.strip()
            partes = linha.split(',')
            
            if len(partes) >= 5:
                uso_gpu = float(partes[0].strip())
                memoria_usada = float(partes[1].strip())
                memoria_total = float(partes[2].strip())
                temperatura = float(partes[3].strip())
                nome_gpu = partes[4].strip()
                
                return {
                    'uso_porcentagem': round(uso_gpu, 1),
                    'memoria_usada_mb': round(memoria_usada, 0),
                    'memoria_total_mb': round(memoria_total, 0),
                    'memoria_porcentagem': round((memoria_usada / memoria_total) * 100, 1),
                    'temperatura': round(temperatura, 0),
                    'nome': nome_gpu,
                    'disponivel': True
                }
    except:
        pass
    
    return None

def obter_uso_gpu_amd():
    """
    Tenta obter informações básicas da GPU AMD
    (Implementação simplificada - AMD tem menos ferramentas padrão)
    """
    try:
        # Tenta usar rocm-smi se estiver disponível
        resultado = subprocess.run(['rocm-smi', '--showuse'], 
                                 capture_output=True, text=True, timeout=5)
        
        if resultado.returncode == 0:
            # Processa a saída (implementação básica)
            linhas = resultado.stdout.split('\n')
            for linha in linhas:
                if 'GPU use' in linha:
                    # Extrai porcentagem usando regex
                    match = re.search(r'(\d+)%', linha)
                    if match:
                        uso = float(match.group(1))
                        return {
                            'uso_porcentagem': round(uso, 1),
                            'memoria_usada_mb': 0,
                            'memoria_total_mb': 0,
                            'memoria_porcentagem': 0,
                            'temperatura': 0,
                            'nome': 'GPU AMD',
                            'disponivel': True
                        }
    except:
        pass
    
    return None

def obter_uso_gpu():
    """
    Função principal para obter dados da GPU
    Tenta diferentes métodos dependendo da GPU disponível
    """
    # Primeiro tenta NVIDIA
    dados_nvidia = obter_uso_gpu_nvidia()
    if dados_nvidia:
        return dados_nvidia
    
    # Se não achou NVIDIA, tenta AMD
    dados_amd = obter_uso_gpu_amd()
    if dados_amd:
        return dados_amd
    
    # Se não conseguiu obter dados de nenhuma GPU
    return {
        'uso_porcentagem': 0.0,
        'memoria_usada_mb': 0,
        'memoria_total_mb': 0,
        'memoria_porcentagem': 0.0,
        'temperatura': 0,
        'nome': 'GPU não detectada',
        'disponivel': False
    }

# Teste da função (só executa se rodar este arquivo diretamente)
if __name__ == "__main__":
    dados = obter_uso_gpu()
    
    print("=== TESTE DO MONITOR DE GPU ===")
    if dados['disponivel']:
        print(f"GPU: {dados['nome']}")
        print(f"Uso: {dados['uso_porcentagem']}%")
        print(f"Memória: {dados['memoria_usada_mb']}/{dados['memoria_total_mb']} MB")
        print(f"Memória: {dados['memoria_porcentagem']}%")
        print(f"Temperatura: {dados['temperatura']}°C")
    else:
        print("GPU não detectada ou drivers não instalados")
        print("Para NVIDIA: instale nvidia-smi")
        print("Para AMD: instale ROCm tools")