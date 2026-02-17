"""
Sistema de filtros avanzados para cartas.
Interfaz profesional con colores y símbolos.
"""

from typing import Dict, List, Set
from collections import Counter
from colorama import Fore, Style, Back


class CardFilter:
    
    def __init__(self, cards_data: Dict[str, Dict], deck_list: List[str]):
        """
        Inicializa el sistema de filtros.
        
        Args:
            cards_data: Diccionario {nombre_carta: info_scryfall}
            deck_list: Lista completa del mazo
        """
        self.cards_data = cards_data
        self.deck_list = deck_list
        
        # Filtros activos
        self.active_filters = {
            'colors': set(),
            'color_mode': 'OR',  # OR = al menos uno, AND = todos
            'types': set(),
            'search_text': '',
            'sort_by': 'name'  # name, cmc_asc, cmc_desc, color, type
        }
    
    def _print_header(self, title: str):
        """Imprime un header bonito."""
        print("\n" + Fore.CYAN + "╔" + "═" * 58 + "╗")
        print(f"║ {title:^56} ║")
        print("╚" + "═" * 58 + "╝" + Style.RESET_ALL)
    
    def _print_section(self, title: str):
        """Imprime un separador de sección."""
        print("\n" + Fore.YELLOW + "─" * 60)
        print(f"  {title}")
        print("─" * 60 + Style.RESET_ALL)
    
    def _get_color_symbol(self, color: str) -> str:
        """Retorna símbolo y color para cada tipo de maná."""
        symbols = {
            'W': f'{Fore.LIGHTYELLOW_EX}☀️  Blanco{Style.RESET_ALL}',
            'U': f'{Fore.BLUE}💧 Azul{Style.RESET_ALL}',
            'B': f'{Fore.LIGHTBLACK_EX}💀 Negro{Style.RESET_ALL}',
            'R': f'{Fore.RED}🔥 Rojo{Style.RESET_ALL}',
            'G': f'{Fore.GREEN}🌳 Verde{Style.RESET_ALL}',
            'C': f'{Fore.WHITE}◇  Incoloro{Style.RESET_ALL}'
        }
        return symbols.get(color, color)
    
    def _get_type_icon(self, card_type: str) -> str:
        """Retorna icono para cada tipo de carta."""
        icons = {
            'Land': '🏔️ ',
            'Creature': '🐉',
            'Instant': '⚡',
            'Sorcery': '📜',
            'Artifact': '⚙️ ',
            'Enchantment': '✨',
            'Planeswalker': '👤'
        }
        return icons.get(card_type, '📄')
    
    def show_active_filters(self):
        """Muestra los filtros actualmente activos."""
        print(Fore.CYAN + "\n┌─ FILTROS ACTIVOS " + "─" * 41 + "┐" + Style.RESET_ALL)
        
        has_filters = False
        
        # Colores
        if self.active_filters['colors']:
            has_filters = True
            colors_str = ', '.join([c for c in self.active_filters['colors']])
            mode = self.active_filters['color_mode']
            print(f"{Fore.YELLOW}│{Style.RESET_ALL} 🎨 Colores: {colors_str} ({mode})")
        
        # Tipos
        if self.active_filters['types']:
            has_filters = True
            types_str = ', '.join(self.active_filters['types'])
            print(f"{Fore.YELLOW}│{Style.RESET_ALL} 📦 Tipos: {types_str}")
        
        # Búsqueda
        if self.active_filters['search_text']:
            has_filters = True
            print(f"{Fore.YELLOW}│{Style.RESET_ALL} 🔍 Búsqueda: '{self.active_filters['search_text']}'")
        
        # Orden
        sort_names = {
            'name': 'Nombre (A-Z)',
            'cmc_asc': 'CMC (menor a mayor)',
            'cmc_desc': 'CMC (mayor a menor)',
            'color': 'Color',
            'type': 'Tipo'
        }
        print(f"{Fore.YELLOW}│{Style.RESET_ALL} 📊 Orden: {sort_names[self.active_filters['sort_by']]}")
        
        if not has_filters:
            print(f"{Fore.YELLOW}│{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}(Sin filtros aplicados){Style.RESET_ALL}")
        
        print(Fore.CYAN + "└" + "─" * 59 + "┘" + Style.RESET_ALL)
    
    def filter_by_colors(self):
        """Menú para filtrar por colores."""
        self._print_section("🎨 FILTRAR POR COLOR")
        
        print("\nSelecciona colores (puedes elegir varios):")
        print(f"  {Fore.LIGHTYELLOW_EX}[W]{Style.RESET_ALL} ☀️  Blanco")
        print(f"  {Fore.BLUE}[U]{Style.RESET_ALL} 💧 Azul")
        print(f"  {Fore.LIGHTBLACK_EX}[B]{Style.RESET_ALL} 💀 Negro")
        print(f"  {Fore.RED}[R]{Style.RESET_ALL} 🔥 Rojo")
        print(f"  {Fore.GREEN}[G]{Style.RESET_ALL} 🌳 Verde")
        print(f"  {Fore.WHITE}[C]{Style.RESET_ALL} ◇  Incoloro")
        
        colors_input = input("\nIngresa letras separadas por coma (ej: U,B,R) o ENTER para saltar: ").strip().upper()
        
        if colors_input:
            colors = set([c.strip() for c in colors_input.split(',') if c.strip() in ['W', 'U', 'B', 'R', 'G', 'C']])
            self.active_filters['colors'] = colors
            
            if len(colors) > 1:
                mode = input("\n¿Modo? [1] Tiene TODOS estos colores (AND) / [2] Tiene AL MENOS UNO (OR): ").strip()
                self.active_filters['color_mode'] = 'AND' if mode == '1' else 'OR'
            
            print(Fore.GREEN + f"\n✅ Filtro de color aplicado: {', '.join(colors)}" + Style.RESET_ALL)
        else:
            self.active_filters['colors'] = set()
            print(Fore.YELLOW + "\n⚠️  Filtro de color eliminado" + Style.RESET_ALL)
    
    def filter_by_type(self):
        """Menú para filtrar por tipo de carta."""
        self._print_section("📦 FILTRAR POR TIPO DE CARTA")
        
        print("\nSelecciona tipos (puedes elegir varios):")
        print(f"  [1] 🏔️  Tierras")
        print(f"  [2] 🐉 Criaturas")
        print(f"  [3] ⚡ Instantáneos")
        print(f"  [4] 📜 Conjuros")
        print(f"  [5] ⚙️  Artefactos")
        print(f"  [6] ✨ Encantamientos")
        print(f"  [7] 👤 Planeswalkers")
        
        types_input = input("\nIngresa números separados por coma (ej: 1,2,5) o ENTER para saltar: ").strip()
        
        type_map = {
            '1': 'Land',
            '2': 'Creature',
            '3': 'Instant',
            '4': 'Sorcery',
            '5': 'Artifact',
            '6': 'Enchantment',
            '7': 'Planeswalker'
        }
        
        if types_input:
            selected = set()
            for num in types_input.split(','):
                num = num.strip()
                if num in type_map:
                    selected.add(type_map[num])
            
            self.active_filters['types'] = selected
            print(Fore.GREEN + f"\n✅ Filtro de tipo aplicado: {', '.join(selected)}" + Style.RESET_ALL)
        else:
            self.active_filters['types'] = set()
            print(Fore.YELLOW + "\n⚠️  Filtro de tipo eliminado" + Style.RESET_ALL)
    
    def search_by_name(self):
        """Búsqueda fuzzy por nombre."""
        self._print_section("🔍 BUSCAR POR NOMBRE")
        
        search = input("\nIngresa texto a buscar (búsqueda flexible) o ENTER para saltar: ").strip()
        
        if search:
            self.active_filters['search_text'] = search.lower()
            print(Fore.GREEN + f"\n✅ Búsqueda aplicada: '{search}'" + Style.RESET_ALL)
        else:
            self.active_filters['search_text'] = ''
            print(Fore.YELLOW + "\n⚠️  Búsqueda eliminada" + Style.RESET_ALL)
    
    def set_sort_order(self):
        """Establece el orden de los resultados."""
        self._print_section("📊 ORDENAR RESULTADOS")
        
        print("\n¿Cómo quieres ordenar?")
        print("  [1] 📝 Nombre (A-Z)")
        print("  [2] 📈 CMC (menor a mayor)")
        print("  [3] 📉 CMC (mayor a menor)")
        print("  [4] 🎨 Por color")
        print("  [5] 📦 Por tipo")
        
        choice = input("\nElige opción: ").strip()
        
        sort_map = {
            '1': 'name',
            '2': 'cmc_asc',
            '3': 'cmc_desc',
            '4': 'color',
            '5': 'type'
        }
        
        if choice in sort_map:
            self.active_filters['sort_by'] = sort_map[choice]
            print(Fore.GREEN + "\n✅ Orden actualizado" + Style.RESET_ALL)
        else:
            print(Fore.RED + "\n❌ Opción inválida" + Style.RESET_ALL)
    
    def _apply_filters(self) -> List[str]:
        """Aplica todos los filtros activos y retorna lista de cartas."""
        filtered_cards = []
        
        for card_name in self.deck_list:
            card_info = self.cards_data.get(card_name, {})
            
            if not card_info or 'error' in card_info:
                continue
            
            # Filtro de colores
            if self.active_filters['colors']:
                card_colors = set(card_info.get('color_identity', []))
                if not card_colors:
                    card_colors = {'C'}  # Incoloro
                
                filter_colors = self.active_filters['colors']
                
                if self.active_filters['color_mode'] == 'AND':
                    # Debe tener TODOS los colores
                    if not filter_colors.issubset(card_colors):
                        continue
                else:  # OR
                    # Debe tener AL MENOS UNO
                    if not filter_colors.intersection(card_colors):
                        continue
            
            # Filtro de tipos
            if self.active_filters['types']:
                type_line = card_info.get('type_line', '')
                card_matches_type = False
                
                for filter_type in self.active_filters['types']:
                    if filter_type in type_line:
                        card_matches_type = True
                        break
                
                if not card_matches_type:
                    continue
            
            # Búsqueda por texto
            if self.active_filters['search_text']:
                search_text = self.active_filters['search_text']
                card_name_lower = card_name.lower()
                
                if search_text not in card_name_lower:
                    continue
            
            # Si pasó todos los filtros, agregar
            filtered_cards.append(card_name)
        
        return filtered_cards
    
    def _sort_cards(self, cards: List[str]) -> List[str]:
        """Ordena las cartas según el criterio seleccionado."""
        sort_by = self.active_filters['sort_by']
        
        if sort_by == 'name':
            return sorted(cards)
        
        elif sort_by == 'cmc_asc':
            return sorted(cards, key=lambda c: self.cards_data.get(c, {}).get('cmc', 0))
        
        elif sort_by == 'cmc_desc':
            return sorted(cards, key=lambda c: self.cards_data.get(c, {}).get('cmc', 0), reverse=True)
        
        elif sort_by == 'color':
            def color_key(card):
                colors = self.cards_data.get(card, {}).get('color_identity', [])
                return ''.join(sorted(colors)) if colors else 'Z'
            return sorted(cards, key=color_key)
        
        elif sort_by == 'type':
            def type_key(card):
                type_line = self.cards_data.get(card, {}).get('type_line', '')
                for t in ['Land', 'Creature', 'Planeswalker', 'Artifact', 'Enchantment', 'Instant', 'Sorcery']:
                    if t in type_line:
                        return t
                return 'ZZZ'
            return sorted(cards, key=type_key)
        
        return cards
    
    def apply_and_show_results(self):
        """Aplica filtros y muestra resultados bonitos."""
        self._print_header("📋 RESULTADOS DE BÚSQUEDA")
        
        # Aplicar filtros
        filtered = self._apply_filters()
        
        if not filtered:
            print(Fore.RED + "\n❌ No se encontraron cartas con estos filtros." + Style.RESET_ALL)
            return
        
        # Ordenar
        sorted_cards = self._sort_cards(filtered)
        
        # Contar repeticiones
        card_counts = Counter(sorted_cards)
        
        # Calcular estadísticas
        total_cards = len(sorted_cards)
        unique_cards = len(card_counts)
        
        cmcs = [self.cards_data.get(c, {}).get('cmc', 0) for c in sorted_cards 
                if not self.cards_data.get(c, {}).get('is_land', False)]
        avg_cmc = sum(cmcs) / len(cmcs) if cmcs else 0
        
        # Mostrar estadísticas
        print(Fore.CYAN + "\n┌─ ESTADÍSTICAS " + "─" * 43 + "┐")
        print(f"│ {Fore.GREEN}✓{Fore.CYAN} Total de cartas: {Fore.WHITE}{total_cards}{Fore.CYAN}")
        print(f"│ {Fore.GREEN}✓{Fore.CYAN} Cartas únicas: {Fore.WHITE}{unique_cards}{Fore.CYAN}")
        print(f"│ {Fore.GREEN}✓{Fore.CYAN} CMC promedio (sin tierras): {Fore.WHITE}{avg_cmc:.2f}{Fore.CYAN}")
        print("└" + "─" * 59 + "┘" + Style.RESET_ALL)
        
        # Mostrar cartas
        print(Fore.YELLOW + "\n╔═ CARTAS ENCONTRADAS " + "═" * 37 + "╗" + Style.RESET_ALL)
        
        for card_name in card_counts.keys():
            count = card_counts[card_name]
            card_info = self.cards_data.get(card_name, {})
            
            # Info de la carta
            cmc = card_info.get('cmc', 0)
            type_line = card_info.get('type_line', '')
            colors = card_info.get('color_identity', [])
            
            # Icono de tipo
            icon = ''
            for t in ['Land', 'Creature', 'Planeswalker', 'Artifact', 'Enchantment', 'Instant', 'Sorcery']:
                if t in type_line:
                    icon = self._get_type_icon(t)
                    break
            
            # Símbolos de color
            color_str = ''.join(colors) if colors else 'C'
            
            # Formato bonito
            print(f"{Fore.WHITE}║{Style.RESET_ALL} {icon} {Fore.CYAN}{count}x{Style.RESET_ALL} {Fore.WHITE}{card_name:<40}{Style.RESET_ALL} "
                  f"{Fore.YELLOW}CMC:{cmc}{Style.RESET_ALL} {Fore.MAGENTA}{color_str}{Style.RESET_ALL}")
        
        print(Fore.YELLOW + "╚" + "═" * 59 + "╝" + Style.RESET_ALL)
    
    def clear_filters(self):
        """Limpia todos los filtros."""
        self.active_filters = {
            'colors': set(),
            'color_mode': 'OR',
            'types': set(),
            'search_text': '',
            'sort_by': 'name'
        }
        print(Fore.GREEN + "\n✅ Todos los filtros han sido eliminados" + Style.RESET_ALL)
    
    def show_menu(self):
        """Muestra el menú principal de filtros."""
        while True:
            self._print_header("🔍 FILTROS AVANZADOS - SISTEMA PRO")
            self.show_active_filters()
            
            print(Fore.YELLOW + "\n┌─ OPCIONES " + "─" * 47 + "┐" + Style.RESET_ALL)
            print(f"{Fore.YELLOW}│{Style.RESET_ALL} [1] 🎨 Filtrar por color(es)")
            print(f"{Fore.YELLOW}│{Style.RESET_ALL} [2] 📦 Filtrar por tipo de carta")
            print(f"{Fore.YELLOW}│{Style.RESET_ALL} [3] 🔍 Buscar por nombre/texto")
            print(f"{Fore.YELLOW}│{Style.RESET_ALL} [4] 📊 Ordenar resultados")
            print(f"{Fore.YELLOW}│{Style.RESET_ALL} {Fore.GREEN}[5] ✅ APLICAR FILTROS Y MOSTRAR{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}│{Style.RESET_ALL} [6] 🔄 Limpiar filtros")
            print(f"{Fore.YELLOW}│{Style.RESET_ALL} [7] ⬅️  Volver al menú anterior")
            print(Fore.YELLOW + "└" + "─" * 59 + "┘" + Style.RESET_ALL)
            
            choice = input(f"\n{Fore.CYAN}➤{Style.RESET_ALL} Elige una opción: ").strip()
            
            if choice == '1':
                self.filter_by_colors()
            elif choice == '2':
                self.filter_by_type()
            elif choice == '3':
                self.search_by_name()
            elif choice == '4':
                self.set_sort_order()
            elif choice == '5':
                self.apply_and_show_results()
            elif choice == '6':
                self.clear_filters()
            elif choice == '7':
                break
            else:
                print(Fore.RED + "\n❌ Opción inválida" + Style.RESET_ALL)
