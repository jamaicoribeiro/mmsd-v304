import sys
import time

try:
    import numpy as np

    def simular_escala(iteracoes, distancia_km=15.0, frequencia_hz=5.0):
        t_inicio = time.time()
        
        # Geração de ruído estocástico gaussiano proporcional ao volume da amostra
        amostras_ruido = np.random.normal(loc=1.0, scale=0.05, size=iteracoes)
        fator_atenuacao = np.exp(-0.05 * distancia_km) * (frequencia_hz ** 1.2)
        respostas = 15000.0 * fator_atenuacao * amostras_ruido
        
        resposta_media = np.mean(respostas)
        desvio_padrao = np.std(respostas)
        erro_padrao = desvio_padrao / np.sqrt(iteracoes) # Erro estocástico
        estabilidade = (1.0 - (desvio_padrao / resposta_media)) * 100
        
        latencia_ms = (time.time() - t_inicio) * 1000
        taxa_amostras_seg = iteracoes / (latencia_ms / 1000.0) if latencia_ms > 0 else 0
        
        return resposta_media, erro_padrao, latencia_ms, estabilidade, taxa_amostras_seg

    # Volumes de amostragem a testar
    volumes_amostra = [1000, 5000, 25000, 100000, 500000]

    print("=" * 95)
    print(f"{'Volume (Iterações)':<20} | {'Resp. Média':<15} | {'Erro Padrão':<12} | {'Latência (ms)':<15} | {'Estabilidade':<12} | {'Amostras/seg'}")
    print("=" * 95)

    for vol in volumes_amostra:
        resp, erro, lat, est, taxa = simular_escala(vol)
        print(f"{vol:<20,d} | {resp:<15.2e} | {erro:<12.4f} | {lat:<15.2f} | {est:<11.2f}% | {taxa:,.0f}".replace(",", "."))

    print("=" * 95)

except Exception as e:
    print(f"\n[ERRO OCORRIDO]: {e}")

finally:
    input("\nPressione ENTER para fechar a janela...")