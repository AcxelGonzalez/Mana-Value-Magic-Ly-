"""
Módulo para analizar mazos de MTG Commander.
Categoriza cartas y calcula estadísticas.
"""

from typing import Dict, List
from collections import Counter


class DeckAnalyzer:
    
    def __init__(self, cards_data: Dict[str, Dict], deck_list: List[str] = None):
        """
        Inicializa el analizador con datos de cartas.
        
        Args:
            cards_data: Diccionario {nombre_carta: info_scryfall}
            deck_list: Lista expandida con todas las cartas (incluyendo duplicados)
        """
        self.cards_data = cards_data
        self.deck_list = deck_list or []
        self.categories = self._categorize_cards()
    
    def _categorize_cards(self) -> Dict[str, List[str]]:
        """
        Categoriza las cartas en diferentes grupos.
        Cuenta cada carta según las veces que aparece en el deck_list.
        
        Returns:
            Diccionario con categorías y listas de nombres de cartas (con duplicados)
        """
        categories = {
            'lands': [],
            'ramp': [],
            'creatures': [],
            'elementals': [],
            'removal': [],
            'board_wipes': [],
            'card_draw': [],
            'counterspells': [],
            'other': []
        }
        
        # Si no hay deck_list, usar cards_data directamente
        if not self.deck_list:
            cards_to_process = list(self.cards_data.keys())
        else:
            cards_to_process = self.deck_list
        
        for card_name in cards_to_process:
            card_info = self.cards_data.get(card_name, {})
            # Si la carta no está en Scryfall data, agregar a "other"
            if not card_info or 'error' in card_info:
                categories['other'].append(card_name)
                continue
            
            # Tierras
            if card_info.get('is_land', False):
                categories['lands'].append(card_name)
            
            # Ramp (no tierras)
            elif card_info.get('is_ramp', False):
                categories['ramp'].append(card_name)
            
            # Criaturas
            if card_info.get('is_creature', False):
                categories['creatures'].append(card_name)
                
                # Elementales
                subtypes = card_info.get('subtypes', [])
                if 'Elemental' in subtypes:
                    categories['elementals'].append(card_name)
            
            # Removal
            oracle_text = card_info.get('oracle_text', '').lower()
            type_line = card_info.get('type_line', '')
            
            # Board wipes (detectar primero antes que removal puntual)
            if self._is_board_wipe(oracle_text, card_name):
                categories['board_wipes'].append(card_name)
            # Removal puntual
            elif self._is_removal(oracle_text, type_line):
                categories['removal'].append(card_name)
            
            # Card draw
            if self._is_card_draw(oracle_text, card_name):
                categories['card_draw'].append(card_name)
            
            # Counterspells
            if self._is_counterspell(oracle_text):
                categories['counterspells'].append(card_name)
            
            # Si no encaja en ninguna categoría específica (y no es tierra ni criatura)
            if not any([
                card_info.get('is_land', False),
                card_info.get('is_ramp', False),
                card_name in categories['removal'],
                card_name in categories['board_wipes'],
                card_name in categories['card_draw'],
                card_name in categories['counterspells']
            ]):
                if not card_info.get('is_creature', False):
                    categories['other'].append(card_name)
        
        return categories
    
    def _is_removal(self, oracle_text: str, type_line: str) -> bool:
        """Detecta si una carta es removal puntual."""
        removal_keywords = [
            'destroy target',
            'exile target',
            'return target',
            'put target',
            'sacrifice target',
            'tap target',
            '-x/-x',
            'damage to target',
            'damage to any target',
            'deals damage',
            'fight',
            'return up to one target',
            'return another target',
        ]
        
        # Excluir criaturas (salvo algunas con habilidades de removal claras)
        if 'Creature' in type_line:
            # Permitir criaturas con removal en ETB o habilidades activadas
            if 'when' in oracle_text or 'enters' in oracle_text or '{t}:' in oracle_text:
                pass
            else:
                return False
        
        return any(keyword in oracle_text for keyword in removal_keywords)
    
    def _is_board_wipe(self, oracle_text: str, card_name: str) -> bool:
        """Detecta si una carta es un board wipe (limpieza masiva)."""
        board_wipe_keywords = [
            'destroy all',
            'exile all',
            'return all',
            'each creature',
            'all creatures',
            'each permanent',
            'all permanents',
            'each opponent sacrifices',
            'wrath',
        ]
        
        # Nombres comunes de board wipes
        wipe_names = [
            'evacuation',
            'cyclone summoner',
            'in garruk\'s wake',
            'necromantic selection',
            'blustersquall',
            'succumb to the cold',
            'dead drop',
        ]
        
        card_name_lower = card_name.lower()
        if any(name in card_name_lower for name in wipe_names):
            return True
        
        return any(keyword in oracle_text for keyword in board_wipe_keywords)
    
    def _is_counterspell(self, oracle_text: str) -> bool:
        """Detecta contrahechizos."""
        counter_keywords = [
            'counter target',
            'counter that',
            'counter up to',
            'exile it instead of putting it into a graveyard',  # Misdirection type
        ]
        
        return any(keyword in oracle_text for keyword in counter_keywords)
    
    def _is_card_draw(self, oracle_text: str, card_name: str = '') -> bool:
        """Detecta si una carta genera ventaja de cartas (robo, scry, etc)."""
        draw_keywords = [
            'draw a card',
            'draw cards',
            'draw two',
            'draw three',
            'draw that many',
            'draws a card',
            'scry',
            'surveil',
            'look at the top',
            'reveal cards',
            'whenever you draw',
            'you may draw',
            'draw equal',
        ]
        
        # Nombres específicos de cartas de ventaja
        advantage_cards = [
            'sensei\'s divining top',
            'mystic remora',
            'the temporal anchor',
            'prying eyes',
            'halimar depths',
        ]
        
        card_name_lower = card_name.lower()
        if any(name in card_name_lower for name in advantage_cards):
            return True
        
        return any(keyword in oracle_text for keyword in draw_keywords)
    
    def get_mana_curve(self) -> Dict[int, int]:
        """
        Calcula la curva de maná del mazo (excluyendo tierras).
        Cuenta cada carta según aparece en el deck_list.
        
        Returns:
            Diccionario {cmc: cantidad_de_cartas}
        """
        cmc_counts = Counter()
        
        # Usar deck_list para contar correctamente
        cards_to_count = self.deck_list if self.deck_list else list(self.cards_data.keys())
        
        for card_name in cards_to_count:
            card_info = self.cards_data.get(card_name, {})
            
            if 'error' in card_info or not card_info:
                continue
            
            # Excluir tierras de la curva de maná
            if not card_info.get('is_land', False):
                cmc = int(card_info.get('cmc', 0))
                cmc_counts[cmc] += 1
        
        return dict(cmc_counts)
    
    def get_color_distribution(self) -> Dict[str, int]:
        """
        Calcula la distribución de colores en el mazo.
        Cuenta cada carta según aparece en el deck_list.
        
        Returns:
            Diccionario {color: cantidad}
        """
        color_counts = Counter()
        
        # Usar deck_list para contar correctamente
        cards_to_count = self.deck_list if self.deck_list else list(self.cards_data.keys())
        
        for card_name in cards_to_count:
            card_info = self.cards_data.get(card_name, {})
            
            if 'error' in card_info or not card_info:
                continue
            
            colors = card_info.get('color_identity', [])
            
            if not colors:
                color_counts['Colorless'] += 1
            else:
                for color in colors:
                    color_counts[color] += 1
        
        return dict(color_counts)
    
    def get_statistics(self) -> Dict:
        """
        Genera estadísticas completas del mazo.
        
        Returns:
            Diccionario con estadísticas
        """
        total_cards = len(self.deck_list) if self.deck_list else len(self.cards_data)
        mana_curve = self.get_mana_curve()
        
        # Calcular CMC promedio (sin tierras)
        total_cmc = sum(cmc * count for cmc, count in mana_curve.items())
        non_land_cards = sum(mana_curve.values())
        avg_cmc = total_cmc / non_land_cards if non_land_cards > 0 else 0
        
        stats = {
            'total_cards': total_cards,
            'lands': len(self.categories['lands']),
            'ramp': len(self.categories['ramp']),
            'creatures': len(self.categories['creatures']),
            'elementals': len(self.categories['elementals']),
            'removal': len(self.categories['removal']),
            'board_wipes': len(self.categories['board_wipes']),
            'card_draw': len(self.categories['card_draw']),
            'counterspells': len(self.categories['counterspells']),
            'other': len(self.categories['other']),
            'avg_cmc': avg_cmc,
            'mana_curve': mana_curve,
            'color_distribution': self.get_color_distribution(),
        }
        
        return stats
    
    def print_statistics(self):
        """Imprime las estadísticas del mazo de forma legible."""
        stats = self.get_statistics()
        
        print("\n" + "=" * 60)
        print("📊 ANÁLISIS DEL MAZO")
        print("=" * 60)
        
        print(f"\n📦 Total de cartas: {stats['total_cards']}")
        print(f"🏔️  Tierras: {stats['lands']}")
        print(f"💎 Ramp: {stats['ramp']}")
        print(f"🐉 Criaturas: {stats['creatures']}")
        print(f"   └─ 🔥 Elementales: {stats['elementals']}")
        print(f"⚔️  Removal puntual: {stats['removal']}")
        print(f"💥 Board Wipes: {stats['board_wipes']}")
        print(f"📖 Robo de cartas: {stats['card_draw']}")
        print(f"🚫 Contrahechizos: {stats['counterspells']}")
        print(f"❓ Otras: {stats['other']}")
        
        print(f"\n📈 CMC Promedio (sin tierras): {stats['avg_cmc']:.2f}")
        
        # Curva de maná visual
        print("\n📊 CURVA DE MANÁ:")
        mana_curve = stats['mana_curve']
        max_count = max(mana_curve.values()) if mana_curve else 1
        
        for cmc in sorted(mana_curve.keys()):
            count = mana_curve[cmc]
            bar_length = int((count / max_count) * 30)
            bar = '█' * bar_length
            print(f"   CMC {cmc:2d}: {bar} ({count})")
        
        # Distribución de colores
        print("\n🎨 DISTRIBUCIÓN DE COLORES:")
        colors = stats['color_distribution']
        color_symbols = {
            'W': '☀️ Blanco',
            'U': '💧 Azul',
            'B': '💀 Negro',
            'R': '🔥 Rojo',
            'G': '🌳 Verde',
            'Colorless': '◇ Incoloro'
        }
        
        for color, count in sorted(colors.items(), key=lambda x: x[1], reverse=True):
            symbol = color_symbols.get(color, color)
            print(f"   {symbol}: {count}")
        
        print("=" * 60)
    
    def get_category(self, category_name: str) -> List[str]:
        """
        Obtiene la lista de cartas de una categoría específica.
        
        Args:
            category_name: Nombre de la categoría
        
        Returns:
            Lista de nombres de cartas
        """
        return self.categories.get(category_name, [])
