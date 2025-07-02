# Monitor de Hardware

Um monitor de hardware feito em Python com Tkinter e psutil.

## Funcionalidades

- Visualização em tempo real do uso de **CPU**, **GPU** e **RAM**
- Exibição de informações detalhadas de cada componente
- Tabela de processos que mais consomem recursos
- Gráficos minimalistas e responsivos
- Interface escura, elegante e fácil de usar

## Requisitos

- **Python** 3.8 ou superior

| Biblioteca   | Função/Observação                      | Instalação                |
|--------------|----------------------------------------|---------------------------|
| `tkinter`    | Interface gráfica (GUI)                | Inclusa no Python         |
| `psutil`     | Monitoramento de hardware/processos     | `pip install psutil`      |
| `platform`   | Detecção de sistema operacional         | Inclusa no Python         |
| `wmi`        | Info detalhada da CPU (Windows, opc.)   | `pip install wmi`         |
| `threading`  | Execução paralela                      | Inclusa no Python         |
| `datetime`   | Manipulação de datas/horas              | Inclusa no Python         |
| `os`         | Operações de sistema                    | Inclusa no Python         |

> **Obs:**  
> - `wmi` só é necessário para informações detalhadas da CPU no Windows.
> - As demais bibliotecas são padrão do Python ou já inclusas.

## Como usar

1. Instale as dependências:
    ```sh
    pip install psutil
    pip install wmi  # (apenas no Windows, opcional)
    ```
2. Execute o programa:
    ```sh
    python interface_grafica.py
    ```

## Estrutura

- `interface_grafica.py` — Interface principal e lógica de exibição
- `cpu_monitor.py`, `gpu_monitor.py`, `ram_monitor.py`, `process_monitor.py` — Coleta de dados dos componentes

## Desenvolvido por [Gustavo Oestreich, Leonardo Saquet, Matheus Marcusso] — Projeto acadêmico.
