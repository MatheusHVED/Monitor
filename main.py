#!/usr/bin/env python3
"""
Monitor de Hardware - Arquivo Principal

Este é o arquivo principal para executar o monitor de hardware.
Ele importa e executa a interface gráfica que mostra:
- Uso da CPU (total e por núcleo)
- Uso da GPU (se disponível)  
- Uso da RAM
- Lista dos processos que mais consomem recursos

Para executar: python main.py

Dependências necessárias:
- psutil: pip install psutil
- tkinter: já vem com Python (na maioria das instalações)

Para GPU NVIDIA: instalar nvidia-smi (geralmente vem com drivers)
Para GPU AMD: instalar ROCm tools (opcional)
"""

import sys
import os

def verificar_dependencias():
    """Verifica se as dependências necessárias estão instaladas"""
    
    try:
        import psutil
        print("✓ psutil encontrado")
    except ImportError:
        print("✗ psutil não encontrado!")
        print("Instale com: pip install psutil")
        return False
    
    try:
        import tkinter
        print("✓ tkinter encontrado")
    except ImportError:
        print("✗ tkinter não encontrado!")
        print("No Ubuntu/Debian: sudo apt install python3-tk")
        print("No CentOS/RHEL: sudo yum install tkinter")
        return False
    
    return True

def verificar_arquivos():
    """Verifica se todos os arquivos do monitor estão presentes"""
    
    arquivos_necessarios = [
        'cpu_monitor.py',
        'ram_monitor.py', 
        'gpu_monitor.py',
        'process_monitor.py',
        'interface_grafica.py'
    ]
    
    arquivos_faltando = []
    
    for arquivo in arquivos_necessarios:
        if not os.path.exists(arquivo):
            arquivos_faltando.append(arquivo)
    
    if arquivos_faltando:
        print("✗ Arquivos não encontrados:")
        for arquivo in arquivos_faltando:
            print(f"  - {arquivo}")
        print("\nCertifique-se de que todos os arquivos estão na mesma pasta")
        return False
    
    print("✓ Todos os arquivos encontrados")
    return True

def main():
    """Função principal"""
    
    print("=== MONITOR DE HARDWARE ===")
    print("Verificando sistema...")
    
    # Verifica dependências
    if not verificar_dependencias():
        print("\n❌ Erro: Dependências não encontradas")
        sys.exit(1)
    
    # Verifica arquivos
    if not verificar_arquivos():
        print("\n❌ Erro: Arquivos não encontrados")
        sys.exit(1)
    
    print("\n✓ Sistema OK, iniciando monitor...")
    print("╔══════════════════════════════════════╗")
    print("║          MONITOR DE HARDWARE         ║")
    print("║                                      ║")
    print("║  Navegue pelas abas:                 ║")
    print("║  📊 Visão Geral - Resumo do sistema ║")
    print("║  🖥️  CPU - Detalhes do processador   ║") 
    print("║  🎮 GPU - Informações da placa de    ║")
    print("║       vídeo                          ║")
    print("║  💾 RAM - Detalhes da memória        ║")
    print("╚══════════════════════════════════════╝")
    print()
    
    try:
        # Importa e executa a interface
        from interface_grafica import MonitorHardware
        
        print("🚀 Iniciando interface gráfica...")
        monitor = MonitorHardware()
        monitor.iniciar()
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Monitor interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro ao executar monitor: {e}")
        print("Verifique se todas as dependências estão instaladas")

if __name__ == "__main__":
    main()