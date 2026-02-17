"""
Módulo para interactuar con la API de Scryfall.
Obtiene información de cartas de Magic: The Gathering.
"""

import requests
import time
from typing import Dict, Optional


class ScryfallAPI:
    BASE_URL = "https://api.scryfall.com"
    
    def __init__(self):
        self.session = requests.Session()
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 100ms entre requests (Scryfall pide 50-100ms)
    
    def _rate_limit(self):
        """Respeta el rate limit de Scryfall."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        
        self.last_request_time = time.time()
    
    def get_card_by_name(self, card_name: str) -> Optional[Dict]:
        """
        Obtiene información de una carta por su nombre.
        
        Args:
            card_name: Nombre de la carta
        
        Returns:
            Diccionario con datos de la carta o None si no se encuentra
        """
        self._rate_limit()
        
        url = f"{self.BASE_URL}/cards/named"
        params = {"fuzzy": card_name}
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                print(f"⚠️  Carta no encontrada: {card_name}")
                return None
            else:
                print(f"⚠️  Error al buscar {card_name}: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"⚠️  Error de conexión al buscar {card_name}: {e}")
            return None
    
    def extract_card_info(self, card_data: Dict) -> Dict:
        """
        Extrae información relevante de los datos de Scryfall.
        
        Args:
            card_data: Datos de la carta de Scryfall
        
        Returns:
            Diccionario con información simplificada
        """
        # Manejo de cartas dobles (DFC, split, etc.)
        card_faces = card_data.get('card_faces', [])
        
        if card_faces:
            # Para cartas con múltiples caras, usar la primera cara
            face = card_faces[0]
            mana_cost = face.get('mana_cost', '')
            type_line = face.get('type_line', '')
        else:
            mana_cost = card_data.get('mana_cost', '')
            type_line = card_data.get('type_line', '')
        
        info = {
            'name': card_data.get('name', ''),
            'mana_cost': mana_cost,
            'cmc': card_data.get('cmc', 0),
            'type_line': type_line,
            'colors': card_data.get('colors', []),
            'color_identity': card_data.get('color_identity', []),
            'oracle_text': card_data.get('oracle_text', ''),
            'is_land': 'Land' in type_line,
            'is_creature': 'Creature' in type_line,
            'types': self._extract_types(type_line),
            'subtypes': self._extract_subtypes(type_line),
        }
        
        # Detectar si es ramp (produce o busca maná)
        oracle_text = card_data.get('oracle_text', '').lower()
        info['is_ramp'] = self._is_ramp_card(oracle_text, type_line)
        
        return info
    
    def _extract_types(self, type_line: str) -> list:
        """Extrae los tipos principales de una carta."""
        if '—' in type_line:
            main_types = type_line.split('—')[0].strip()
        else:
            main_types = type_line
        
        return [t.strip() for t in main_types.split() if t.strip()]
    
    def _extract_subtypes(self, type_line: str) -> list:
        """Extrae los subtipos de una carta."""
        if '—' in type_line:
            subtypes = type_line.split('—')[1].strip()
            return [s.strip() for s in subtypes.split() if s.strip()]
        return []
    
    def _is_ramp_card(self, oracle_text: str, type_line: str) -> bool:
        """
        Detecta si una carta es de ramp (acelera el maná).
        """
        if 'Land' in type_line:
            return False  # Las tierras no cuentan como ramp
        
        ramp_keywords = [
            'add {',
            'search your library for a land',
            'search your library for a basic land',
            'search your library for up to',
            'put a land card',
            'land card from your library',
            'untap target land',
            'lands you control',
        ]
        
        return any(keyword in oracle_text for keyword in ramp_keywords)
    
    def get_multiple_cards(self, card_names: list) -> Dict[str, Dict]:
        """
        Obtiene información de múltiples cartas.
        
        Args:
            card_names: Lista de nombres de cartas
        
        Returns:
            Diccionario {nombre: info_carta}
        """
        cards_info = {}
        total = len(card_names)
        
        print(f"\n🔍 Consultando Scryfall para {total} cartas...")
        
        for i, card_name in enumerate(card_names, 1):
            print(f"   [{i}/{total}] {card_name}...", end='\r')
            
            card_data = self.get_card_by_name(card_name)
            
            if card_data:
                cards_info[card_name] = self.extract_card_info(card_data)
            else:
                # Agregar entrada vacía para cartas no encontradas
                cards_info[card_name] = {
                    'name': card_name,
                    'error': 'No encontrada'
                }
        
        print(f"\n✅ Consulta completada: {len(cards_info)} cartas procesadas")
        return cards_info
