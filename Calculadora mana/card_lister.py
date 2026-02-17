"""
Módulo para listar y categorizar cartas del mazo.
Todo dinámico basado en datos de Scryfall API.
"""

from typing import Dict, List
from collections import Counter


class CardLister:
    
    def __init__(self, cards_data: Dict[str, Dict], deck_list: List[str]):
        """
        Inicializa el listador de cartas.
        
        Args:
            cards_data: Diccionario {nombre_carta: info_scryfall}
            deck_list: Lista completa del mazo con duplicados
        """
        self.cards_data = cards_data
        self.deck_list = deck_list
    
    def _count_cards(self, card_names: List[str]) -> Dict[str, int]:
        """
        Cuenta cuántas veces aparece cada carta en una lista.
        
        Args:
            card_names: Lista de nombres de cartas
        
        Returns:
            Diccionario {nombre: cantidad}
        """
        return dict(Counter(card_names))
    
    def _get_card_type(self, type_line: str) -> str:
        """
        Extrae el tipo principal de una carta desde type_line.
        Ejemplo: "Legendary Creature — Ninja" -> "Creature"
        """
        # Orden de prioridad para cartas con múltiples tipos
        type_priority = ['Land', 'Creature', 'Planeswalker', 'Artifact', 
                        'Enchantment', 'Instant', 'Sorcery']
        
        for card_type in type_priority:
            if card_type in type_line:
                return card_type
        
        return 'Other'
    
    def _categorize_land_type(self, card_name: str, card_info: Dict) -> str:
        """
        Categoriza una tierra por subtipo (básica, fetch, dual, tri, utilidad).
        """
        type_line = card_info.get('type_line', '')
        oracle_text = card_info.get('oracle_text', '').lower()
        
        # Básicas
        if 'Basic Land' in type_line:
            return 'Basicas'
        
        # Fetch lands
        if 'search your library for' in oracle_text and 'land' in oracle_text:
            return 'Fetch'
        
        # Contar colores que produce
        colors_produced = []
        mana_symbols = ['{W}', '{U}', '{B}', '{R}', '{G}']
        for symbol in mana_symbols:
            if symbol.lower() in oracle_text or symbol in oracle_text:
                colors_produced.append(symbol)
        
        # Tri-lands (3+ colores)
        if len(colors_produced) >= 3:
            return 'Tri-lands'
        
        # Dual lands (2 colores)
        elif len(colors_produced) == 2:
            return 'Dual'
        
        # Utilidad (resto)
        else:
            return 'Utilidad'
    
    def list_lands(self):
        """Lista todas las tierras agrupadas por subtipo."""
        print("\n" + "=" * 60)
        print("TIERRAS DEL MAZO")
        print("=" * 60)
        
        # Filtrar tierras del mazo
        lands = [name for name in self.deck_list 
                if self.cards_data.get(name, {}).get('is_land', False)]
        
        if not lands:
            print("\nNo hay tierras en el mazo.")
            return
        
        # Agrupar por subtipo
        land_categories = {
            'Basicas': [],
            'Fetch': [],
            'Dual': [],
            'Tri-lands': [],
            'Utilidad': []
        }
        
        for land_name in lands:
            card_info = self.cards_data.get(land_name, {})
            category = self._categorize_land_type(land_name, card_info)
            land_categories[category].append(land_name)
        
        # Mostrar por categoría
        total = len(lands)
        print(f"\nTotal: {total} tierras\n")
        
        for category, cards in land_categories.items():
            if cards:
                counted = self._count_cards(cards)
                print(f"-- {category.upper()} ({len(cards)}) --")
                for card_name, count in sorted(counted.items()):
                    print(f"  {count}x {card_name}")
                print()
        
        print("=" * 60)
    
    def list_ramp(self, ramp_cards: List[str]):
        """Lista todas las cartas de ramp agrupadas por tipo."""
        print("\n" + "=" * 60)
        print("RAMP DEL MAZO")
        print("=" * 60)
        
        if not ramp_cards:
            print("\nNo hay ramp detectado en el mazo.")
            return
        
        # Agrupar por tipo de carta
        ramp_by_type = {
            'Criaturas': [],
            'Conjuros': [],
            'Instantaneos': [],
            'Artefactos': [],
            'Encantamientos': [],
            'Otras': []
        }
        
        for card_name in ramp_cards:
            card_info = self.cards_data.get(card_name, {})
            type_line = card_info.get('type_line', '')
            
            if 'Creature' in type_line:
                ramp_by_type['Criaturas'].append(card_name)
            elif 'Sorcery' in type_line:
                ramp_by_type['Conjuros'].append(card_name)
            elif 'Instant' in type_line:
                ramp_by_type['Instantaneos'].append(card_name)
            elif 'Artifact' in type_line:
                ramp_by_type['Artefactos'].append(card_name)
            elif 'Enchantment' in type_line:
                ramp_by_type['Encantamientos'].append(card_name)
            else:
                ramp_by_type['Otras'].append(card_name)
        
        # Mostrar
        total = len(ramp_cards)
        print(f"\nTotal: {total} cartas de ramp\n")
        
        for card_type, cards in ramp_by_type.items():
            if cards:
                counted = self._count_cards(cards)
                print(f"-- {card_type.upper()} ({len(cards)}) --")
                for card_name, count in sorted(counted.items()):
                    print(f"  {count}x {card_name}")
                print()
        
        print("=" * 60)
    
    def list_creatures(self):
        """Lista todas las criaturas agrupadas por raza/subtipo."""
        print("\n" + "=" * 60)
        print("CRIATURAS DEL MAZO")
        print("=" * 60)
        
        # Filtrar criaturas
        creatures = [name for name in self.deck_list 
                    if self.cards_data.get(name, {}).get('is_creature', False)]
        
        if not creatures:
            print("\nNo hay criaturas en el mazo.")
            return
        
        # Agrupar por subtipo/raza
        by_subtype = {}
        
        for creature_name in creatures:
            card_info = self.cards_data.get(creature_name, {})
            subtypes = card_info.get('subtypes', [])
            
            if not subtypes:
                # Sin subtipo específico
                if 'Sin subtipo' not in by_subtype:
                    by_subtype['Sin subtipo'] = []
                by_subtype['Sin subtipo'].append(creature_name)
            else:
                # Agrupar por cada subtipo (una criatura puede tener múltiples)
                for subtype in subtypes:
                    if subtype not in by_subtype:
                        by_subtype[subtype] = []
                    by_subtype[subtype].append(creature_name)
        
        # Mostrar
        total = len(creatures)
        print(f"\nTotal: {total} criaturas\n")
        
        # Ordenar por cantidad (más comunes primero)
        sorted_subtypes = sorted(by_subtype.items(), 
                                key=lambda x: len(x[1]), 
                                reverse=True)
        
        for subtype, cards in sorted_subtypes:
            counted = self._count_cards(cards)
            print(f"-- {subtype.upper()} ({len(cards)}) --")
            for card_name, count in sorted(counted.items()):
                print(f"  {count}x {card_name}")
            print()
        
        print("=" * 60)
    
    def list_interactions(self, removal: List[str], board_wipes: List[str], 
                         card_draw: List[str], counterspells: List[str]):
        """Lista todas las interacciones agrupadas por función."""
        print("\n" + "=" * 60)
        print("INTERACCIONES DEL MAZO")
        print("=" * 60)
        
        total = len(removal) + len(board_wipes) + len(card_draw) + len(counterspells)
        
        if total == 0:
            print("\nNo hay interacciones detectadas.")
            return
        
        print(f"\nTotal: {total} cartas de interaccion\n")
        
        # Board Wipes
        if board_wipes:
            counted = self._count_cards(board_wipes)
            print(f"-- BOARD WIPES ({len(board_wipes)}) --")
            for card_name, count in sorted(counted.items()):
                print(f"  {count}x {card_name}")
            print()
        
        # Removal Puntual
        if removal:
            counted = self._count_cards(removal)
            print(f"-- REMOVAL PUNTUAL ({len(removal)}) --")
            for card_name, count in sorted(counted.items()):
                print(f"  {count}x {card_name}")
            print()
        
        # Robo de cartas
        if card_draw:
            counted = self._count_cards(card_draw)
            print(f"-- ROBO DE CARTAS ({len(card_draw)}) --")
            for card_name, count in sorted(counted.items()):
                print(f"  {count}x {card_name}")
            print()
        
        # Counterspells
        if counterspells:
            counted = self._count_cards(counterspells)
            print(f"-- COUNTERSPELLS ({len(counterspells)}) --")
            for card_name, count in sorted(counted.items()):
                print(f"  {count}x {card_name}")
            print()
        
        print("=" * 60)
    
    def list_full_deck(self):
        """Lista el mazo completo agrupado por tipo de carta."""
        print("\n" + "=" * 60)
        print("MAZO COMPLETO")
        print("=" * 60)
        
        # Agrupar por tipo
        by_type = {
            'Tierras': [],
            'Criaturas': [],
            'Instantaneos': [],
            'Conjuros': [],
            'Artefactos': [],
            'Encantamientos': [],
            'Planeswalkers': [],
            'Otras': []
        }
        
        for card_name in self.deck_list:
            card_info = self.cards_data.get(card_name, {})
            
            if not card_info or 'error' in card_info:
                by_type['Otras'].append(card_name)
                continue
            
            type_line = card_info.get('type_line', '')
            card_type = self._get_card_type(type_line)
            
            if card_type == 'Land':
                by_type['Tierras'].append(card_name)
            elif card_type == 'Creature':
                by_type['Criaturas'].append(card_name)
            elif card_type == 'Instant':
                by_type['Instantaneos'].append(card_name)
            elif card_type == 'Sorcery':
                by_type['Conjuros'].append(card_name)
            elif card_type == 'Artifact':
                by_type['Artefactos'].append(card_name)
            elif card_type == 'Enchantment':
                by_type['Encantamientos'].append(card_name)
            elif card_type == 'Planeswalker':
                by_type['Planeswalkers'].append(card_name)
            else:
                by_type['Otras'].append(card_name)
        
        # Mostrar
        total = len(self.deck_list)
        print(f"\nTotal: {total} cartas\n")
        
        # Orden específico
        type_order = ['Tierras', 'Criaturas', 'Planeswalkers', 'Instantaneos', 
                     'Conjuros', 'Artefactos', 'Encantamientos', 'Otras']
        
        for card_type in type_order:
            cards = by_type[card_type]
            if cards:
                counted = self._count_cards(cards)
                print(f"-- {card_type.upper()} ({len(cards)}) --")
                for card_name, count in sorted(counted.items()):
                    print(f"  {count}x {card_name}")
                print()
        
        print("=" * 60)
