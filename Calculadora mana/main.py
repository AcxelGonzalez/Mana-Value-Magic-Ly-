"""
Calculadora de Probabilidades para MTG Commander
Basada en Distribución Hipergeométrica

Por: Orion
Para: Mazo de Omnath, Locus of the Roil
"""

import os
import sys
from colorama import init, Fore, Style
from tabulate import tabulate

from moxfield_parser import MoxfieldParser
from scryfall_api import ScryfallAPI
from deck_analyzer import DeckAnalyzer
from mana_base_analyzer import ManaBaseAnalyzer
from card_lister import CardLister
from card_filter import CardFilter
from hypergeometric import (
    probability_at_least,
    probability_at_most,
    probability_between,
    hypergeometric_probability,
    calculate_full_distribution,
    format_percentage
)

# Inicializar colorama para Windows
init()


class MTGCalculator:
    
    def __init__(self):
        self.deck_cards = []
        self.cards_data = {}
        self.analyzer = None
        self.deck_size = 99  # Commander (100 - 1 comandante)
    
    def print_header(self):
        """Imprime el header de la aplicación."""
        print(Fore.CYAN + "=" * 70)
        print(" 🎴  CALCULADORA DE PROBABILIDADES MTG COMMANDER")
        print(" 📊 Distribución Hipergeométrica")
        print(" ⚡ Optimizada para Omnath, Locus of the Roil")
        print("=" * 70 + Style.RESET_ALL)
    
    def load_deck_menu(self):
        """Menú para cargar un mazo."""
        print(Fore.YELLOW + "\n📁 CARGAR MAZO" + Style.RESET_ALL)
        print("1. Cargar desde archivo (Moxfield CSV/TXT)")
        print("2. Cargar mazo de ejemplo (Omnath)")
        print("3. Volver")
        
        choice = input("\nElige una opción: ").strip()
        
        if choice == '1':
            filepath = input("Ingresa la ruta del archivo: ").strip()
            self.load_deck_from_file(filepath)
        elif choice == '2':
            self.load_example_deck()
        elif choice == '3':
            return
    
    def load_deck_from_file(self, filepath: str):
        """Carga un mazo desde un archivo."""
        print(Fore.CYAN + f"\n🔄 Cargando mazo desde: {filepath}" + Style.RESET_ALL)
        
        # Parsear archivo
        cards = MoxfieldParser.load_deck(filepath)
        
        if not cards:
            print(Fore.RED + "❌ No se pudo cargar el mazo." + Style.RESET_ALL)
            return
        
        print(f"✅ Archivo parseado: {len(cards)} entradas encontradas")
        
        # Obtener nombres únicos
        unique_names = MoxfieldParser.get_unique_cards(cards)
        
        # Consultar Scryfall
        api = ScryfallAPI()
        self.cards_data = api.get_multiple_cards(unique_names)
        
        # Crear lista expandida de cartas
        self.deck_cards = MoxfieldParser.get_card_list(cards)
        self.deck_size = len(self.deck_cards)
        
        # Crear analizador pasando la lista completa
        self.analyzer = DeckAnalyzer(self.cards_data, self.deck_cards)
        
        print(Fore.GREEN + f"\n✅ Mazo cargado exitosamente: {self.deck_size} cartas" + Style.RESET_ALL)
        
        # Mostrar estadísticas
        self.analyzer.print_statistics()
    
    def load_example_deck(self):
        """Carga un mazo de ejemplo para pruebas."""
        print(Fore.CYAN + "\n🎴 Cargando mazo de ejemplo..." + Style.RESET_ALL)
        print("(Esta es una simulación, no un mazo real completo)")
        
        # Mazo de ejemplo simplificado
        example_cards = [
            {'quantity': 1, 'name': 'Omnath, Locus of the Roil'},
            {'quantity': 15, 'name': 'Island'},
            {'quantity': 15, 'name': 'Forest'},
            {'quantity': 7, 'name': 'Mountain'},
            {'quantity': 5, 'name': 'Cultivate'},
            {'quantity': 5, 'name': 'Risen Reef'},
            {'quantity': 5, 'name': 'Lightning Bolt'},
            {'quantity': 5, 'name': 'Counterspell'},
            {'quantity': 42, 'name': 'Other Cards'},  # Placeholder
        ]
        
        unique_names = MoxfieldParser.get_unique_cards(example_cards)
        
        # Solo consultar cartas reales (no "Other Cards")
        real_cards = [name for name in unique_names if name != 'Other Cards']
        
        api = ScryfallAPI()
        self.cards_data = api.get_multiple_cards(real_cards)
        
        # Agregar placeholder para "Other Cards"
        self.cards_data['Other Cards'] = {
            'name': 'Other Cards',
            'cmc': 3,
            'type_line': 'Various',
            'is_land': False,
            'is_creature': False,
            'is_ramp': False,
        }
        
        self.deck_cards = MoxfieldParser.get_card_list(example_cards)
        self.deck_size = len(self.deck_cards)
        
        self.analyzer = DeckAnalyzer(self.cards_data, self.deck_cards)
        
        print(Fore.GREEN + f"\n✅ Mazo de ejemplo cargado: {self.deck_size} cartas" + Style.RESET_ALL)
        self.analyzer.print_statistics()
    
    def calculate_probabilities_menu(self):
        """Menú principal de cálculos de probabilidad."""
        if not self.analyzer:
            print(Fore.RED + "\n❌ Primero debes cargar un mazo." + Style.RESET_ALL)
            return
        
        while True:
            print(Fore.YELLOW + "\n🎲 CALCULAR PROBABILIDADES" + Style.RESET_ALL)
            print("1. Probabilidad de tierras en mano")
            print("2. Probabilidad de ramp temprano")
            print("3. Probabilidad de elementales")
            print("4. Probabilidad de interacción")
            print("5. Cálculo personalizado")
            print("6. Volver al menú principal")
            
            choice = input("\nElige una opción: ").strip()
            
            if choice == '1':
                self.calculate_lands_probability()
            elif choice == '2':
                self.calculate_ramp_probability()
            elif choice == '3':
                self.calculate_elementals_probability()
            elif choice == '4':
                self.calculate_interaction_probability()
            elif choice == '5':
                self.calculate_custom_probability()
            elif choice == '6':
                break
    
    def calculate_lands_probability(self):
        """Calcula probabilidades de tener tierras en mano inicial."""
        lands_count = len(self.analyzer.get_category('lands'))
        
        print(Fore.CYAN + f"\n🏔️  PROBABILIDAD DE TIERRAS" + Style.RESET_ALL)
        print(f"Tierras en mazo: {lands_count}/{self.deck_size}")
        
        # Mano inicial de 7
        cards_drawn = 7
        
        print(f"\nEn mano inicial de {cards_drawn} cartas:")
        
        results = []
        for k in range(8):
            prob = hypergeometric_probability(self.deck_size, lands_count, cards_drawn, k)
            results.append([f"Exactamente {k}", format_percentage(prob)])
        
        print(tabulate(results, headers=["Escenario", "Probabilidad"], tablefmt="grid"))
        
        # Probabilidades útiles
        print(Fore.GREEN + "\n📊 Rangos útiles:" + Style.RESET_ALL)
        prob_2_to_4 = probability_between(self.deck_size, lands_count, cards_drawn, 2, 4)
        prob_3_to_4 = probability_between(self.deck_size, lands_count, cards_drawn, 3, 4)
        prob_at_least_2 = probability_at_least(self.deck_size, lands_count, cards_drawn, 2)
        
        print(f"  • 2-4 tierras (keepable): {format_percentage(prob_2_to_4)}")
        print(f"  • 3-4 tierras (ideal): {format_percentage(prob_3_to_4)}")
        print(f"  • Al menos 2 tierras: {format_percentage(prob_at_least_2)}")
    
    def calculate_ramp_probability(self):
        """Calcula probabilidades de tener ramp."""
        ramp_count = len(self.analyzer.get_category('ramp'))
        
        print(Fore.CYAN + f"\n💎 PROBABILIDAD DE RAMP TEMPRANO" + Style.RESET_ALL)
        print(f"Cartas de ramp en mazo: {ramp_count}/{self.deck_size}")
        
        if ramp_count == 0:
            print(Fore.RED + "⚠️  No hay cartas de ramp detectadas en el mazo." + Style.RESET_ALL)
            return
        
        cards_drawn = int(input("\n¿Hasta qué turno quieres calcular? (ej: 10 para primeros 10 robos): ").strip() or "10")
        
        print(f"\nEn los primeros {cards_drawn} robos:")
        
        prob_at_least_1 = probability_at_least(self.deck_size, ramp_count, cards_drawn, 1)
        prob_at_least_2 = probability_at_least(self.deck_size, ramp_count, cards_drawn, 2)
        prob_exactly_0 = hypergeometric_probability(self.deck_size, ramp_count, cards_drawn, 0)
        
        results = [
            ["Al menos 1 ramp", format_percentage(prob_at_least_1)],
            ["Al menos 2 ramps", format_percentage(prob_at_least_2)],
            ["Ningún ramp", format_percentage(prob_exactly_0)],
        ]
        
        print(tabulate(results, headers=["Escenario", "Probabilidad"], tablefmt="grid"))
    
    def calculate_elementals_probability(self):
        """Calcula probabilidades de tener elementales."""
        elementals_count = len(self.analyzer.get_category('elementals'))
        
        print(Fore.CYAN + f"\n🔥 PROBABILIDAD DE ELEMENTALES" + Style.RESET_ALL)
        print(f"Elementales en mazo: {elementals_count}/{self.deck_size}")
        
        if elementals_count == 0:
            print(Fore.RED + "⚠️  No hay elementales detectados en el mazo." + Style.RESET_ALL)
            return
        
        # Mano inicial
        cards_drawn = 7
        
        print(f"\nEn mano inicial de {cards_drawn} cartas:")
        
        prob_at_least_1 = probability_at_least(self.deck_size, elementals_count, cards_drawn, 1)
        prob_at_least_2 = probability_at_least(self.deck_size, elementals_count, cards_drawn, 2)
        prob_exactly_0 = hypergeometric_probability(self.deck_size, elementals_count, cards_drawn, 0)
        
        results = [
            ["Al menos 1 elemental", format_percentage(prob_at_least_1)],
            ["Al menos 2 elementales", format_percentage(prob_at_least_2)],
            ["Ningún elemental", format_percentage(prob_exactly_0)],
        ]
        
        print(tabulate(results, headers=["Escenario", "Probabilidad"], tablefmt="grid"))
    
    def calculate_interaction_probability(self):
        """Calcula probabilidades de tener interacción."""
        removal = len(self.analyzer.get_category('removal'))
        counters = len(self.analyzer.get_category('counterspells'))
        total_interaction = removal + counters
        
        print(Fore.CYAN + f"\n⚔️  PROBABILIDAD DE INTERACCIÓN" + Style.RESET_ALL)
        print(f"Removal: {removal}, Contras: {counters}, Total: {total_interaction}/{self.deck_size}")
        
        if total_interaction == 0:
            print(Fore.RED + "⚠️  No hay interacción detectada en el mazo." + Style.RESET_ALL)
            return
        
        cards_drawn = int(input("\n¿Cartas a robar? (default 7): ").strip() or "7")
        
        print(f"\nEn {cards_drawn} cartas:")
        
        prob_at_least_1 = probability_at_least(self.deck_size, total_interaction, cards_drawn, 1)
        prob_at_least_2 = probability_at_least(self.deck_size, total_interaction, cards_drawn, 2)
        
        results = [
            ["Al menos 1 interacción", format_percentage(prob_at_least_1)],
            ["Al menos 2 interacciones", format_percentage(prob_at_least_2)],
        ]
        
        print(tabulate(results, headers=["Escenario", "Probabilidad"], tablefmt="grid"))
    
    def calculate_custom_probability(self):
        """Permite cálculo personalizado."""
        print(Fore.CYAN + "\n🎯 CÁLCULO PERSONALIZADO" + Style.RESET_ALL)
        
        try:
            K = int(input(f"¿Cuántas cartas del tipo que buscas hay en el mazo? (de {self.deck_size}): ").strip())
            n = int(input("¿Cuántas cartas vas a robar?: ").strip())
            k = int(input("¿Cuántas de ese tipo quieres encontrar (mínimo)?: ").strip())
            
            prob = probability_at_least(self.deck_size, K, n, k)
            
            print(Fore.GREEN + f"\n📊 Resultado:" + Style.RESET_ALL)
            print(f"Probabilidad de encontrar al menos {k} cartas del tipo deseado")
            print(f"en {n} robos, con {K} en el mazo: {format_percentage(prob)}")
            
        except ValueError:
            print(Fore.RED + "❌ Entrada inválida." + Style.RESET_ALL)
    
    def recommend_mana_base(self):
        """Muestra recomendaciones de base de maná."""
        if not self.analyzer:
            print(Fore.RED + "\n❌ Primero debes cargar un mazo." + Style.RESET_ALL)
            return
        
        print(Fore.CYAN + "\n🏔️  ANALIZADOR DE BASE DE MANA" + Style.RESET_ALL)
        
        # Crear analizador de base de maná
        mana_analyzer = ManaBaseAnalyzer(self.cards_data, self.deck_cards)
        
        # Análisis automático - sin pedirle nada al usuario
        mana_analyzer.print_recommendations()
    
    def list_cards_menu(self):
        """Menú para listar cartas del mazo."""
        if not self.analyzer:
            print(Fore.RED + "\n❌ Primero debes cargar un mazo." + Style.RESET_ALL)
            return
        
        lister = CardLister(self.cards_data, self.deck_cards)
        card_filter = CardFilter(self.cards_data, self.deck_cards)
        
        while True:
            print(Fore.YELLOW + "\n📋 LISTAR CARTAS" + Style.RESET_ALL)
            print("1. Ver todas las tierras")
            print("2. Ver ramp")
            print("3. Ver criaturas")
            print("4. Ver interacciones")
            print("5. Listar mazo completo")
            print(Fore.CYAN + "6. 🔥 Filtros Avanzados (PRO)" + Style.RESET_ALL)
            print("7. Volver al menú principal")
            
            choice = input("\nElige una opción: ").strip()
            
            if choice == '1':
                lister.list_lands()
            elif choice == '2':
                ramp_cards = self.analyzer.get_category('ramp')
                lister.list_ramp(ramp_cards)
            elif choice == '3':
                lister.list_creatures()
            elif choice == '4':
                removal = self.analyzer.get_category('removal')
                board_wipes = self.analyzer.get_category('board_wipes')
                card_draw = self.analyzer.get_category('card_draw')
                counterspells = self.analyzer.get_category('counterspells')
                lister.list_interactions(removal, board_wipes, card_draw, counterspells)
            elif choice == '5':
                lister.list_full_deck()
            elif choice == '6':
                card_filter.show_menu()
            elif choice == '7':
                break
            else:
                print(Fore.RED + "❌ Opción inválida." + Style.RESET_ALL)
    
    def main_menu(self):
        """Menú principal de la aplicación."""
        self.print_header()
        
        while True:
            print(Fore.YELLOW + "\n🎮 MENÚ PRINCIPAL" + Style.RESET_ALL)
            print("1. Cargar mazo")
            print("2. Calcular probabilidades")
            print("3. Ver estadísticas del mazo")
            print("4. Recomendar base de maná")
            print("5. Listar cartas")
            print("6. Salir")
            
            choice = input("\nElige una opción: ").strip()
            
            if choice == '1':
                self.load_deck_menu()
            elif choice == '2':
                self.calculate_probabilities_menu()
            elif choice == '3':
                if self.analyzer:
                    self.analyzer.print_statistics()
                else:
                    print(Fore.RED + "\n❌ Primero debes cargar un mazo." + Style.RESET_ALL)
            elif choice == '4':
                self.recommend_mana_base()
            elif choice == '5':
                self.list_cards_menu()
            elif choice == '6':
                print(Fore.CYAN + "\n👋 ¡Hasta luego! Good luck en tus partidas." + Style.RESET_ALL)
                break
            else:
                print(Fore.RED + "❌ Opción inválida." + Style.RESET_ALL)


def main():
    calculator = MTGCalculator()
    calculator.main_menu()


if __name__ == "__main__":
    main()
