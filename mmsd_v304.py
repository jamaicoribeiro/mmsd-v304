"""
================================================================================
MMSD v3.0.4 - Motor de Simulação Estocástica Sísmica
================================================================================
Descrição: Módulo autónomo para processamento de resposta espectral, ensaios 
           de sensibilidade paramétrica e convergência estatística (Monte Carlo).
Autor:     MMSD Core Engine
Licença:   MIT License / CC-BY-4.0
================================================================================
"""

import time
import csv
import os

try:
    import numpy as np
except ImportError:
    print("[ERRO]: A biblioteca NumPy não está instalada. Execute 'pip install numpy'.")
    exit(1)


class MMSDEngine:
    """Motor principal de simulação estocástica vetorizada."""

    def __init__(self, seed: int = None):
        if seed is not None:
            np.random.seed(seed)

    def simular(self, distancia_km: float, frequencia_hz: float, iteracoes: int = 25000) -> dict:
        """
        Executa uma simulação estocástica para uma dada distância e frequência.

        Parâmetros:
            distancia_km (float): Distância epicentral em quilómetros.
            frequencia_hz (float): Frequência dominante em Hertz.
            iteracoes (int): Número de amostras estocásticas (Monte Carlo).

        Retorna:
            dict: Dicionário com métricas estatísticas e de desempenho.
        """
        t_inicio = time.perf_counter()

        # Amostragem estocástica gaussiana (ruído vetorial)
        ruido = np.random.normal(loc=1.0, scale=0.05, size=iteracoes)

        # Modelo de atenuação geométrica e espectral
        fator_atenuacao = np.exp(-0.05 * distancia_km) * (frequencia_hz ** 1.2)
        respostas = 15000.0 * fator_atenuacao * ruido

        # Métricas estatísticas
        resposta_media = float(np.mean(respostas))
        desvio_padrao = float(np.std(respostas))
        erro_padrao = desvio_padrao / np.sqrt(iteracoes)
        estabilidade = (1.0 - (desvio_padrao / resposta_media)) * 100.0

        t_fim = time.perf_counter()
        latencia_ms = (t_fim - t_inicio) * 1000.0
        taxa_amostras_seg = iteracoes / (latencia_ms / 1000.0) if latencia_ms > 0 else 0.0

        return {
            "distancia_km": distancia_km,
            "frequencia_hz": frequencia_hz,
            "iteracoes": iteracoes,
            "resposta_espectral": resposta_media,
            "desvio_padrao": desvio_padrao,
            "erro_padrao": erro_padrao,
            "estabilidade_pct": estabilidade,
            "latencia_ms": latencia_ms,
            "taxa_amostras_seg": taxa_amostras_seg
        }

    def executar_bateria_cenarios(self, cenarios: list, iteracoes: int = 25000) -> list:
        """Executa uma lista de cenários paramétricos."""
        resultados = []
        for c in cenarios:
            res = self.simular(c["distancia"], c["freq"], iteracoes=iteracoes)
            res["nome_cenario"] = c["nome"]
            resultados.append(res)
        return resultados

    def testar_convergencia(self, volumes_amostra: list = None, distancia: float = 15.0, freq: float = 5.0) -> list:
        """Testa a convergência estatística em função do número de iterações."""
        if volumes_amostra is None:
            volumes_amostra = [1000, 5000, 25000, 100000, 500000]

        resultados = []
        for vol in volumes_amostra:
            res = self.simular(distancia, freq, iteracoes=vol)
            resultados.append(res)
        return resultados


def guardar_csv(caminho_ficheiro: str, dados: list, campos: list):
    """Exporta os resultados para um ficheiro CSV."""
    with open(caminho_ficheiro, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        for linha in dados:
            linha_filtrada = {k: linha[k] for k in campos if k in linha}
            writer.writerow(linha_filtrada)


# ==============================================================================
# EXECUÇÃO PRINCIPAL E DEMONSTRAÇÃO
# ==============================================================================
if __name__ == "__main__":
    try:
        engine = MMSDEngine()

        print("=" * 90)
        print("MMSD v3.0.4 - MOTOR DE SIMULAÇÃO ESTOCÁSTICA SÍSMICA (CÓDIGO-FONTE CONSOLIDADO)")
        print("=" * 90)

        # 1. ENSAIO DE SENSIBILIDADE PARAMÉTRICA
        cenarios_teste = [
            {"nome": "Campo Próximo (Severo)", "distancia": 5.0,  "freq": 5.0},
            {"nome": "Cenário Base (Validado)", "distancia": 15.0, "freq": 5.0},
            {"nome": "Campo Afastado",        "distancia": 30.0, "freq": 5.0},
            {"nome": "Baixa Frequência",      "distancia": 15.0, "freq": 1.0},
            {"nome": "Alta Frequência",       "distancia": 15.0, "freq": 10.0},
        ]

        print("\n>>> 1. ENSAIO DE SENSIBILIDADE PARAMÉTRICA")
        print("-" * 90)
        print(f"{'Cenário':<25} | {'Dist(km)':<8} | {'Freq(Hz)':<8} | {'Resp. Espectral':<16} | {'Latência':<10} | {'Estabilidade'}")
        print("-" * 90)

        res_cenarios = engine.executar_bateria_cenarios(cenarios_teste)
        for r in res_cenarios:
            print(f"{r['nome_cenario']:<25} | {r['distancia_km']:<8.1f} | {r['frequencia_hz']:<8.1f} | {r['resposta_espectral']:<16.2e} | {r['latencia_ms']:<8.2f} ms | {r['estabilidade_pct']:<10.2f}%")

        # 2. ENSAIO DE CONVERGÊNCIA DE MONTE CARLO
        print("\n>>> 2. ENSAIO DE CONVERGÊNCIA DE MONTE CARLO (ATÉ 500.000 ITERAÇÕES)")
        print("-" * 90)
        print(f"{'Iterações':<15} | {'Resp. Média':<16} | {'Erro Padrão':<12} | {'Latência (ms)':<15} | {'Amostras/seg'}")
        print("-" * 90)

        res_convergencia = engine.testar_convergencia()
        for r in res_convergencia:
            print(f"{r['iteracoes']:<15,d} | {r['resposta_espectral']:<16.2e} | {r['erro_padrao']:<12.4f} | {r['latencia_ms']:<15.2f} | {r['taxa_amostras_seg']:,.0f}".replace(",", "."))

        print("-" * 90)

        # 3. EXPORTAÇÃO DOS DADOS
        pasta_saida = r"C:\Projetos"
        if not os.path.exists(pasta_saida):
            os.makedirs(pasta_saida)

        caminho_csv = os.path.join(pasta_saida, "mmsd_resultados.csv")
        campos_csv = ["nome_cenario", "distancia_km", "frequencia_hz", "iteracoes", "resposta_espectral", "erro_padrao", "estabilidade_pct", "latencia_ms"]

        guardar_csv(caminho_csv, res_cenarios, campos_csv)
        print(f"\n[SUCESSO]: Dados dos cenários exportados para '{caminho_csv}'.")

    except Exception as e:
        print(f"\n[ERRO NA EXECUÇÃO]: {e}")

    finally:
        input("\nPressione ENTER para fechar a janela...")