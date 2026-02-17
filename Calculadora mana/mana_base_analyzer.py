"""
Módulo para analizar y recomendar base de maná para mazos de Commander.
Calcula requisitos de color y sugiere distribución de tierras.
"""

from typing import Dict, List, Tuple
from collections import Counter
import re
from colorama import Fore, Style


class ManaBaseAnalyzer:
    
    def __init__(self, cards_data: Dict[str, Dict], deck_list: List[str]):
        """
        Inicializa el analizador de base de maná.
        
        Args:
            cards_data: Diccionario {nombre_carta: info_scryfall}
            deck_list: Lista completa del mazo
        """
        self.cards_data = cards_data
        self.deck_list = deck_list
        self.color_requirements = self._calculate_color_requirements()
    
    def _parse_mana_cost(self, mana_cost: str) -> Dict[str, int]:
        """
        Parsea un costo de maná y cuenta símbolos de cada color.
        Ejemplo: "{2}{G}{G}{U}" -> {'G': 2, 'U': 1}
        
        Args:
            mana_cost: String del costo de maná
        
        Returns:
            Diccionario {color: cantidad}
        """
        color_counts = Counter()
        
        # Extraer todos los símbolos entre llaves
        symbols = re.findall(r'\{([^}]+)\}', mana_cost)
        
        for symbol in symbols:
            # Símbolos de un solo color
            if symbol in ['W', 'U', 'B', 'R', 'G']:
                color_counts[symbol] += 1
            
            # Símbolos híbridos (ej: {G/U})
            elif '/' in symbol:
                colors = symbol.split('/')
                for color in colors:
                    if color in ['W', 'U', 'B', 'R', 'G']:
                        color_counts[color] += 0.5  # Contar como medio símbolo cada uno
            
            # Símbolos de Phyrexian (ej: {G/P})
            elif '/P' in symbol:
                color = symbol.replace('/P', '')
                if color in ['W', 'U', 'B', 'R', 'G']:
                    color_counts[color] += 1
        
        return dict(color_counts)
    
    def _calculate_color_requirements(self) -> Dict[str, float]:
        """
        Calcula los requisitos totales de color del mazo.
        
        Returns:
            Diccionario {color: total_símbolos}
        """
        total_requirements = Counter()
        
        for card_name in self.deck_list:
            card_info = self.cards_data.get(card_name, {})
            
            # Solo contar cartas que no son tierras
            if card_info.get('is_land', False):
                continue
            
            mana_cost = card_info.get('mana_cost', '')
            if mana_cost:
                color_counts = self._parse_mana_cost(mana_cost)
                for color, count in color_counts.items():
                    total_requirements[color] += count
        
        return dict(total_requirements)
    
    def get_color_percentages(self) -> Dict[str, float]:
        """
        Calcula el porcentaje de cada color en el mazo.
        
        Returns:
            Diccionario {color: porcentaje}
        """
        total_symbols = sum(self.color_requirements.values())
        
        if total_symbols == 0:
            return {}
        
        percentages = {}
        for color, count in self.color_requirements.items():
            percentages[color] = (count / total_symbols) * 100
        
        return percentages
    
    def recommend_land_distribution(self, total_lands: int = 37) -> Dict[str, any]:
        """
        Recomienda distribución de tierras basada en requisitos de color.
        
        Args:
            total_lands: Número total de tierras en el mazo (default 37 para Commander)
        
        Returns:
            Diccionario con recomendaciones
        """
        percentages = self.get_color_percentages()
        
        if not percentages:
            return {
                'error': 'No se pudieron calcular requisitos de color'
            }
        
        # Reservar espacio para tierras de utilidad (aprox 10-12 en Commander)
        utility_lands = 10
        colored_lands = total_lands - utility_lands
        
        # Calcular tierras básicas según porcentaje
        basic_lands = {}
        for color, percentage in percentages.items():
            count = round((percentage / 100) * colored_lands)
            basic_lands[color] = count
        
        # Ajustar si la suma no da exacta
        total_allocated = sum(basic_lands.values())
        difference = colored_lands - total_allocated
        
        if difference != 0 and basic_lands:
            # Agregar/quitar del color dominante
            dominant_color = max(basic_lands, key=basic_lands.get)
            basic_lands[dominant_color] += difference
        
        # Recomendaciones de tierras duales
        dual_recommendations = self._recommend_dual_lands()
        
        return {
            'total_lands': total_lands,
            'utility_lands': utility_lands,
            'colored_lands': colored_lands,
            'basic_lands': basic_lands,
            'dual_recommendations': dual_recommendations,
            'color_requirements': self.color_requirements,
            'color_percentages': percentages
        }
    
    def _recommend_dual_lands(self) -> Dict[str, List[str]]:
        """
        Recomienda tierras duales según los colores del mazo.
        
        Returns:
            Diccionario con tipos de duales y ejemplos
        """
        colors = sorted(self.color_requirements.keys())
        
        recommendations = {
            'shock_lands': [],
            'fetch_lands': [],
            'fast_lands': [],
            'check_lands': [],
            'pain_lands': [],
            'bounce_lands': [],
            'tri_lands': []
        }
        
        # Mapeo de pares de colores a nombres de tierras
        shock_lands_map = {
            ('G', 'R'): 'Stomping Ground',
            ('G', 'U'): 'Breeding Pool',
            ('R', 'U'): 'Steam Vents',
            ('G', 'W'): 'Temple Garden',
            ('R', 'W'): 'Sacred Foundry',
            ('U', 'W'): 'Hallowed Fountain',
            ('B', 'G'): 'Overgrown Tomb',
            ('B', 'R'): 'Blood Crypt',
            ('B', 'U'): 'Watery Grave',
            ('B', 'W'): 'Godless Shrine'
        }
        
        fetch_lands_map = {
            ('G', 'R'): 'Wooded Foothills',
            ('G', 'U'): 'Misty Rainforest',
            ('R', 'U'): 'Scalding Tarn',
        }
        
        # Recomendar shocks y fetches para cada par de colores
        for i, color1 in enumerate(colors):
            for color2 in colors[i+1:]:
                pair = tuple(sorted([color1, color2]))
                
                if pair in shock_lands_map:
                    recommendations['shock_lands'].append(shock_lands_map[pair])
                
                if pair in fetch_lands_map:
                    recommendations['fetch_lands'].append(fetch_lands_map[pair])
        
        # Tierras tricolor para mazos de 3 colores
        if len(colors) == 3:
            if set(colors) == {'G', 'R', 'U'}:
                recommendations['tri_lands'] = ['Frontier Bivouac', 'Ketria Triome']
        
        return recommendations
    
    def _calculate_current_lands(self) -> Dict:
        """Calcula las tierras actuales en el mazo."""
        total = 0
        colored = Counter()
        dual_lands = 0
        
        for card_name in self.deck_list:
            card_info = self.cards_data.get(card_name, {})
            if card_info.get('is_land', False):
                total += 1
                # Contar tierras de color
                type_line = card_info.get('type_line', '').lower()
                if any(basic in type_line for basic in ['forest', 'island', 'mountain', 'plains', 'swamp']):
                    if 'forest' in type_line:
                        colored['G'] += 1
                    if 'island' in type_line:
                        colored['U'] += 1
                    if 'mountain' in type_line:
                        colored['R'] += 1
                    if 'plains' in type_line:
                        colored['W'] += 1
                    if 'swamp' in type_line:
                        colored['B'] += 1
                # Contar duales (tierras que producen 2+ colores)
                colors = card_info.get('color_identity', [])
                if len(colors) >= 2:
                    dual_lands += 1
        
        return {'total': total, 'colored': dict(colored), 'dual_lands': dual_lands}
    
    def _calculate_avg_cmc(self) -> float:
        """Calcula el CMC promedio del mazo (sin tierras)."""
        cmcs = []
        for card_name in self.deck_list:
            card_info = self.cards_data.get(card_name, {})
            if not card_info.get('is_land', False):
                cmcs.append(card_info.get('cmc', 0))
        return sum(cmcs) / len(cmcs) if cmcs else 0
    
    def _count_ramp_cards(self) -> int:
        """Cuenta cartas de ramp en el mazo."""
        ramp_count = 0
        for card_name in self.deck_list:
            card_info = self.cards_data.get(card_name, {})
            if card_info.get('is_ramp', False):
                ramp_count += 1
        return ramp_count
    
    def _analyze_color_pips(self) -> Dict[str, int]:
        """Analiza cartas con múltiples símbolos del mismo color (pips)."""
        demanding_cards = Counter()
        
        for card_name in self.deck_list:
            card_info = self.cards_data.get(card_name, {})
            if card_info.get('is_land', False):
                continue
            
            mana_cost = card_info.get('mana_cost', '')
            color_counts = self._parse_mana_cost(mana_cost)
            
            # Detectar cartas exigentes (2+ símbolos del mismo color)
            for color, count in color_counts.items():
                if count >= 2:
                    demanding_cards[color] += 1
        
        return dict(demanding_cards)
    
    def _analyze_early_game(self) -> Dict:
        """Analiza la curva temprana del mazo."""
        early_cards = 0  # CMC 1-2
        
        for card_name in self.deck_list:
            card_info = self.cards_data.get(card_name, {})
            if not card_info.get('is_land', False):
                cmc = card_info.get('cmc', 0)
                if cmc <= 2:
                    early_cards += 1
        
        return {'early_cards': early_cards}
    
    def _calculate_land_probabilities(self, land_count: int) -> Dict[str, float]:
        """Calcula probabilidades de tierras con hipergeométrica."""
        from hypergeometric import probability_at_least, probability_between
        
        deck_size = 99  # Commander sin comandante
        hand_size = 7
        
        # P(0-1 tierras) = Mana Screw
        mana_screw = probability_at_least(deck_size, land_count, hand_size, 0) - probability_at_least(deck_size, land_count, hand_size, 2)
        
        # P(2-4 tierras) = Keepable
        keepable = probability_between(deck_size, land_count, hand_size, 2, 4)
        
        # P(5+ tierras) = Mana Flood
        mana_flood = probability_at_least(deck_size, land_count, hand_size, 5)
        
        return {
            'mana_screw': mana_screw * 100,
            'keepable': keepable * 100,
            'mana_flood': mana_flood * 100
        }
    
    def print_recommendations(self):
        """
        Análisis completo de base de maná basado en CMC y probabilidades.
        """
        # Recolectar datos
        current_lands = self._calculate_current_lands()
        avg_cmc = self._calculate_avg_cmc()
        ramp_count = self._count_ramp_cards()
        percentages = self.get_color_percentages()
        num_colors = len(percentages)
        
        # Calcular tierras óptimas basado en CMC
        if avg_cmc >= 3.5:
            optimal_lands = 38
        elif avg_cmc >= 3.0:
            optimal_lands = 37
        else:
            optimal_lands = 36
        
        # Ajustar por ramp
        ramp_adjustment = 0
        if ramp_count >= 12:
            ramp_adjustment = -2
            optimal_lands -= 2
        elif ramp_count >= 8:
            ramp_adjustment = -1
            optimal_lands -= 1
        elif ramp_count <= 3:
            ramp_adjustment = 1
            optimal_lands += 1
        
        current_total = current_lands['total']
        difference = optimal_lands - current_total
        
        # ═══════════════════════════════════════════════════════
        # HEADER PRINCIPAL
        # ═══════════════════════════════════════════════════════
        print(Fore.CYAN + "\n╔" + "═" * 58 + "╗")
        print(f"║ {'📊 ANÁLISIS DE BASE DE MANÁ':^56} ║")
        print("╚" + "═" * 58 + "╝" + Style.RESET_ALL)
        
        # ═══════════════════════════════════════════════════════
        # 1. ESTADO ACTUAL
        # ═══════════════════════════════════════════════════════
        print(Fore.YELLOW + "\n┌─ 🏞️  ESTADO ACTUAL" + " " * 38 + "┐" + Style.RESET_ALL)
        print(f"{Fore.CYAN}│ Tierras totales: {Fore.WHITE}{current_total}{Fore.CYAN}")
        print(f"│ Tierras duales/fetches: {Fore.WHITE}{current_lands['dual_lands']}{Fore.CYAN}")
        print(f"│ Número de colores: {Fore.WHITE}{num_colors}{Fore.CYAN}")
        print(Fore.YELLOW + "└" + "─" * 59 + "┘" + Style.RESET_ALL)
        
        # ═══════════════════════════════════════════════════════
        # 2. RECOMENDACIÓN ÓPTIMA
        # ═══════════════════════════════════════════════════════
        print(Fore.YELLOW + "\n┌─ 🎯 RECOMENDACIÓN ÓPTIMA" + " " * 33 + "┐" + Style.RESET_ALL)
        
        # Calcular distribución ideal basada en porcentajes de color
        recommendations = self.recommend_land_distribution(optimal_lands)
        land_names = {'G': 'Forest', 'U': 'Island', 'R': 'Mountain', 'W': 'Plains', 'B': 'Swamp'}
        current_colored = current_lands['colored']
        
        if difference > 0:
            print(f"{Fore.RED}│ ⚠️  AÑADIR {Fore.WHITE}{difference} TIERRAS{Fore.RED} ({current_total} → {optimal_lands})")
            print(f"{Fore.CYAN}│")
            
            # Calcular déficit por color
            color_deficits = []
            for color in sorted(percentages.keys(), key=lambda c: percentages[c], reverse=True):
                current = current_colored.get(color, 0)
                recommended = recommendations['basic_lands'].get(color, 0)
                deficit = recommended - current
                
                if deficit > 0:
                    color_deficits.append((color, deficit, percentages[color]))
            
            # Distribuir tierras faltantes proporcionalmente
            lands_to_add = []
            remaining = difference
            
            for color, deficit, percent in color_deficits:
                if remaining <= 0:
                    break
                to_add = min(deficit, remaining)
                if to_add > 0:
                    land_name = land_names.get(color, color)
                    lands_to_add.append(f"{to_add}x {land_name}")
                    remaining -= to_add
            
            if lands_to_add:
                print(f"│ 📋 {Fore.WHITE}" + ", ".join(lands_to_add) + Fore.CYAN)
            else:
                # Si no hay déficit de básicas, recomendar duales
                dual_count = current_lands['dual_lands']
                if dual_count < 8:
                    print(f"│ 📋 {Fore.WHITE}Tierras duales (tienes {dual_count}, necesitas ~8){Fore.CYAN}")
                else:
                    print(f"│ 📋 {Fore.WHITE}Tierras de utilidad o duales{Fore.CYAN}")
                    
        elif difference < 0:
            print(f"{Fore.YELLOW}│ ⚠️  QUITAR {Fore.WHITE}{abs(difference)} TIERRAS{Fore.YELLOW} ({current_total} → {optimal_lands})")
            print(f"{Fore.CYAN}│")
            
            # Calcular exceso por color
            color_surplus = []
            for color in sorted(percentages.keys(), key=lambda c: percentages[c]):
                current = current_colored.get(color, 0)
                recommended = recommendations['basic_lands'].get(color, 0)
                surplus = current - recommended
                
                if surplus > 0:
                    color_surplus.append((color, surplus, percentages[color]))
            
            # Distribuir tierras a quitar
            lands_to_remove = []
            remaining = abs(difference)
            
            for color, surplus, percent in color_surplus:
                if remaining <= 0:
                    break
                to_remove = min(surplus, remaining)
                if to_remove > 0:
                    land_name = land_names.get(color, color)
                    lands_to_remove.append(f"{to_remove}x {land_name}")
                    remaining -= to_remove
            
            if lands_to_remove:
                print(f"│ 📋 {Fore.WHITE}" + ", ".join(lands_to_remove) + Fore.CYAN)
            else:
                print(f"│ 📋 {Fore.WHITE}Tierras de utilidad o excedentes{Fore.CYAN}")
        else:
            print(f"{Fore.GREEN}│ ✅ CANTIDAD PERFECTA ({current_total} tierras)")
        
        print(f"{Fore.CYAN}│")
        print(f"│ 📈 CMC Promedio: {Fore.WHITE}{avg_cmc:.2f}{Fore.CYAN}")
        
        # Explicar por qué esta cantidad
        if avg_cmc >= 3.5:
            print(f"│    → CMC alto (≥3.5) requiere {Fore.WHITE}38 tierras base{Fore.CYAN}")
        elif avg_cmc >= 3.0:
            print(f"│    → CMC medio (≥3.0) requiere {Fore.WHITE}37 tierras base{Fore.CYAN}")
        else:
            print(f"│    → CMC bajo (<3.0) requiere {Fore.WHITE}36 tierras base{Fore.CYAN}")
        
        if ramp_adjustment != 0:
            sign = "+" if ramp_adjustment > 0 else ""
            print(f"│    → Ajuste por ramp: {Fore.WHITE}{sign}{ramp_adjustment} tierras{Fore.CYAN}")
        
        print(Fore.YELLOW + "└" + "─" * 59 + "┘" + Style.RESET_ALL)
        
        # ═══════════════════════════════════════════════════════
        # 3. PROBABILIDADES (HIPERGEOMÉTRICA)
        # ═══════════════════════════════════════════════════════
        print(Fore.YELLOW + "\n┌─ 🎲 PROBABILIDADES (Mano Inicial)" + " " * 22 + "┐" + Style.RESET_ALL)
        
        if current_total > 0:
            current_probs = self._calculate_land_probabilities(current_total)
            
            print(f"{Fore.CYAN}│ Con {Fore.WHITE}{current_total} tierras{Fore.CYAN}:")
            print(f"│   {Fore.RED}Mana Screw (0-1): {current_probs['mana_screw']:>5.1f}%{Fore.CYAN}")
            print(f"│   {Fore.GREEN}Keepable (2-4):   {current_probs['keepable']:>5.1f}%{Fore.CYAN}")
            print(f"│   {Fore.YELLOW}Mana Flood (5+):  {current_probs['mana_flood']:>5.1f}%{Fore.CYAN}")
            
            # Comparar con óptimo si es diferente
            if difference != 0:
                optimal_probs = self._calculate_land_probabilities(optimal_lands)
                print(f"{Fore.CYAN}│")
                print(f"│ Con {Fore.WHITE}{optimal_lands} tierras{Fore.CYAN} (recomendado):")
                print(f"│   {Fore.RED}Mana Screw (0-1): {optimal_probs['mana_screw']:>5.1f}%{Fore.CYAN}")
                print(f"│   {Fore.GREEN}Keepable (2-4):   {optimal_probs['keepable']:>5.1f}%{Fore.CYAN}")
                print(f"│   {Fore.YELLOW}Mana Flood (5+):  {optimal_probs['mana_flood']:>5.1f}%{Fore.CYAN}")
                
                # Mostrar mejora
                screw_diff = current_probs['mana_screw'] - optimal_probs['mana_screw']
                keepable_diff = optimal_probs['keepable'] - current_probs['keepable']
                
                print(f"{Fore.CYAN}│")
                if difference > 0:  # Necesita añadir tierras
                    print(f"│ 💡 {Fore.GREEN}Mejora: {abs(screw_diff):.1f}% menos mana screw{Fore.CYAN}")
                else:  # Necesita quitar tierras
                    print(f"│ 💡 {Fore.GREEN}Mejora: {abs(keepable_diff):.1f}% más keepable{Fore.CYAN}")
        
        print(Fore.YELLOW + "└" + "─" * 59 + "┘" + Style.RESET_ALL)
        
        # ═══════════════════════════════════════════════════════
        # 4. COLOR FIXING
        # ═══════════════════════════════════════════════════════
        print(Fore.YELLOW + "\n┌─ 🌈 COLOR FIXING" + " " * 41 + "┐" + Style.RESET_ALL)
        
        dual_count = current_lands['dual_lands']
        
        if num_colors == 1:
            print(f"{Fore.GREEN}│ ✅ Mazo monocolor - No necesitas tierras duales")
        elif num_colors == 2:
            if dual_count >= 8:
                print(f"{Fore.GREEN}│ ✅ {dual_count} duales - Excelente para 2 colores")
            elif dual_count >= 5:
                print(f"{Fore.YELLOW}│ ⚠️  {dual_count} duales - Decente (objetivo: 8-10)")
            else:
                print(f"{Fore.RED}│ ❌ {dual_count} duales - INSUFICIENTE para 2 colores")
                print(f"{Fore.CYAN}│    💡 Añade {Fore.WHITE}{8 - dual_count} duales más{Fore.CYAN} (objetivo: 8-10)")
        elif num_colors >= 3:
            if dual_count >= 12:
                print(f"{Fore.GREEN}│ ✅ {dual_count} duales - Excelente para {num_colors} colores")
            elif dual_count >= 8:
                print(f"{Fore.YELLOW}│ ⚠️  {dual_count} duales - Justo (objetivo: 12-15)")
            else:
                print(f"{Fore.RED}│ ❌ {dual_count} duales - MUY POCO para {num_colors} colores")
                print(f"{Fore.CYAN}│    💡 Añade {Fore.WHITE}{12 - dual_count} duales más{Fore.CYAN} (objetivo: 12-15)")
        
        print(Fore.YELLOW + "└" + "─" * 59 + "┘" + Style.RESET_ALL)
        
        # ═══════════════════════════════════════════════════════
        # 5. ANÁLISIS DE RAMP
        # ═══════════════════════════════════════════════════════
        print(Fore.YELLOW + "\n┌─ 💎 ANÁLISIS DE RAMP" + " " * 37 + "┐" + Style.RESET_ALL)
        
        print(f"{Fore.CYAN}│ Cartas de ramp: {Fore.WHITE}{ramp_count}{Fore.CYAN}")
        
        if ramp_count >= 12:
            print(f"│ {Fore.GREEN}✅ Excelente aceleración (≥12)")
            print(f"{Fore.CYAN}│    💡 Alto ramp permite {Fore.WHITE}-2 tierras{Fore.CYAN}")
        elif ramp_count >= 8:
            print(f"│ {Fore.GREEN}✅ Cantidad estándar (8-11)")
            print(f"{Fore.CYAN}│    💡 Buen ramp permite {Fore.WHITE}-1 tierra{Fore.CYAN}")
        elif ramp_count >= 5:
            print(f"│ {Fore.YELLOW}⚠️  Un poco bajo (5-7)")
            print(f"{Fore.CYAN}│    💡 Sin ajuste de tierras")
        else:
            print(f"│ {Fore.RED}❌ MUY BAJO (<5)")
            print(f"{Fore.CYAN}│    💡 Poco ramp requiere {Fore.WHITE}+1 tierra{Fore.CYAN}")
            print(f"│    💡 O añade {Fore.WHITE}{8 - ramp_count} ramps más{Fore.CYAN}")
        
        print(Fore.YELLOW + "└" + "─" * 59 + "┘" + Style.RESET_ALL)
        
        print("\n" + Fore.CYAN + "═" * 60 + Style.RESET_ALL)
