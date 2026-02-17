"""
Módulo de cálculos de distribución hipergeométrica para MTG.
Calcula probabilidades de robar cartas específicas de un mazo.
"""

from math import comb


def hypergeometric_probability(N, K, n, k):
    """
    Calcula la probabilidad hipergeométrica exacta.
    
    Args:
        N: Tamaño total del mazo
        K: Número de cartas del tipo deseado en el mazo
        n: Número de cartas robadas
        k: Número exacto de cartas del tipo deseado que queremos robar
    
    Returns:
        Probabilidad (0.0 a 1.0)
    """
    if k > K or k > n or (n - k) > (N - K):
        return 0.0
    
    numerator = comb(K, k) * comb(N - K, n - k)
    denominator = comb(N, n)
    
    return numerator / denominator


def probability_at_least(N, K, n, k_min):
    """
    Calcula la probabilidad de robar AL MENOS k_min cartas del tipo deseado.
    
    Args:
        N: Tamaño total del mazo
        K: Número de cartas del tipo deseado en el mazo
        n: Número de cartas robadas
        k_min: Mínimo número de cartas del tipo deseado que queremos
    
    Returns:
        Probabilidad (0.0 a 1.0)
    """
    max_possible = min(K, n)
    total_prob = 0.0
    
    for k in range(k_min, max_possible + 1):
        total_prob += hypergeometric_probability(N, K, n, k)
    
    return total_prob


def probability_at_most(N, K, n, k_max):
    """
    Calcula la probabilidad de robar A LO SUMO k_max cartas del tipo deseado.
    
    Args:
        N: Tamaño total del mazo
        K: Número de cartas del tipo deseado en el mazo
        n: Número de cartas robadas
        k_max: Máximo número de cartas del tipo deseado que queremos
    
    Returns:
        Probabilidad (0.0 a 1.0)
    """
    total_prob = 0.0
    
    for k in range(0, k_max + 1):
        total_prob += hypergeometric_probability(N, K, n, k)
    
    return total_prob


def probability_between(N, K, n, k_min, k_max):
    """
    Calcula la probabilidad de robar entre k_min y k_max cartas del tipo deseado.
    
    Args:
        N: Tamaño total del mazo
        K: Número de cartas del tipo deseado en el mazo
        n: Número de cartas robadas
        k_min: Mínimo número de cartas
        k_max: Máximo número de cartas
    
    Returns:
        Probabilidad (0.0 a 1.0)
    """
    total_prob = 0.0
    
    for k in range(k_min, k_max + 1):
        total_prob += hypergeometric_probability(N, K, n, k)
    
    return total_prob


def calculate_full_distribution(N, K, n):
    """
    Calcula la distribución completa de probabilidades para todos los resultados posibles.
    
    Args:
        N: Tamaño total del mazo
        K: Número de cartas del tipo deseado en el mazo
        n: Número de cartas robadas
    
    Returns:
        Lista de tuplas (k, probabilidad) para cada valor posible de k
    """
    max_possible = min(K, n)
    distribution = []
    
    for k in range(0, max_possible + 1):
        prob = hypergeometric_probability(N, K, n, k)
        distribution.append((k, prob))
    
    return distribution


def format_percentage(probability):
    """
    Formatea una probabilidad como porcentaje.
    
    Args:
        probability: Valor entre 0.0 y 1.0
    
    Returns:
        String formateado como porcentaje
    """
    return f"{probability * 100:.2f}%"
