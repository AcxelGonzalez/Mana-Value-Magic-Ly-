"""
Módulo para parsear archivos exportados desde Moxfield.
Soporta formatos CSV y texto plano.
"""

import csv
from typing import List, Dict
import os


class MoxfieldParser:
    
    @staticmethod
    def parse_csv(filepath: str) -> List[Dict]:
        """
        Parsea un archivo CSV exportado desde Moxfield.
        
        Args:
            filepath: Ruta al archivo CSV
        
        Returns:
            Lista de diccionarios con información de las cartas
        """
        cards = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                # Moxfield CSV tiene headers
                reader = csv.DictReader(file)
                
                for row in reader:
                    # Moxfield exporta con estas columnas principales
                    card = {
                        'quantity': int(row.get('Count', row.get('Quantity', 1))),
                        'name': row.get('Name', '').strip(),
                        'type': row.get('Type', ''),
                        'set': row.get('Edition', ''),
                        'mana_cost': row.get('Cost', ''),
                        'cmc': row.get('CMC', 0),
                        'color': row.get('Color', ''),
                        'board': row.get('Board', 'mainboard'),  # mainboard, sideboard, commander
                    }
                    
                    # Filtrar solo las del mainboard y commander
                    if card['board'].lower() in ['mainboard', 'commander', '']:
                        cards.append(card)
        
        except FileNotFoundError:
            print(f"❌ Archivo no encontrado: {filepath}")
            return []
        except Exception as e:
            print(f"❌ Error al leer archivo CSV: {e}")
            return []
        
        return cards
    
    @staticmethod
    def parse_text(filepath: str) -> List[Dict]:
        """
        Parsea un archivo de texto plano con formato "Cantidad Nombre".
        Ejemplo:
        1 Omnath, Locus of the Roil
        37 Island
        
        Args:
            filepath: Ruta al archivo de texto
        
        Returns:
            Lista de diccionarios con información de las cartas
        """
        cards = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                for line in file:
                    line = line.strip()
                    
                    # Ignorar líneas vacías y comentarios
                    if not line or line.startswith('#') or line.startswith('//'):
                        continue
                    
                    # Formato: "Cantidad Nombre de la Carta"
                    parts = line.split(maxsplit=1)
                    
                    if len(parts) >= 2:
                        try:
                            quantity = int(parts[0])
                            name = parts[1].strip()
                            
                            card = {
                                'quantity': quantity,
                                'name': name,
                                'type': '',
                                'set': '',
                                'mana_cost': '',
                                'cmc': 0,
                                'color': '',
                                'board': 'mainboard',
                            }
                            
                            cards.append(card)
                        except ValueError:
                            # Si la primera parte no es un número, asumir cantidad 1
                            card = {
                                'quantity': 1,
                                'name': line,
                                'type': '',
                                'set': '',
                                'mana_cost': '',
                                'cmc': 0,
                                'color': '',
                                'board': 'mainboard',
                            }
                            cards.append(card)
        
        except FileNotFoundError:
            print(f"❌ Archivo no encontrado: {filepath}")
            return []
        except Exception as e:
            print(f"❌ Error al leer archivo de texto: {e}")
            return []
        
        return cards
    
    @staticmethod
    def load_deck(filepath: str) -> List[Dict]:
        """
        Carga un mazo desde un archivo (detecta automáticamente el formato).
        
        Args:
            filepath: Ruta al archivo
        
        Returns:
            Lista de diccionarios con información de las cartas
        """
        if not os.path.exists(filepath):
            print(f"❌ Archivo no encontrado: {filepath}")
            return []
        
        # Detectar formato por extensión
        _, ext = os.path.splitext(filepath)
        ext = ext.lower()
        
        if ext == '.csv':
            return MoxfieldParser.parse_csv(filepath)
        elif ext in ['.txt', '.dec', '.mwdeck']:
            return MoxfieldParser.parse_text(filepath)
        else:
            # Intentar como texto por defecto
            print(f"⚠️  Extensión desconocida '{ext}', intentando como texto plano...")
            return MoxfieldParser.parse_text(filepath)
    
    @staticmethod
    def get_card_list(cards: List[Dict]) -> List[str]:
        """
        Extrae una lista de nombres de cartas (expandiendo cantidades).
        
        Args:
            cards: Lista de diccionarios de cartas
        
        Returns:
            Lista de nombres de cartas individuales
        """
        card_list = []
        
        for card in cards:
            quantity = card.get('quantity', 1)
            name = card.get('name', '')
            
            for _ in range(quantity):
                card_list.append(name)
        
        return card_list
    
    @staticmethod
    def get_unique_cards(cards: List[Dict]) -> List[str]:
        """
        Obtiene lista de nombres únicos de cartas (sin duplicados).
        
        Args:
            cards: Lista de diccionarios de cartas
        
        Returns:
            Lista de nombres únicos
        """
        unique_names = set()
        
        for card in cards:
            name = card.get('name', '')
            if name:
                unique_names.add(name)
        
        return list(unique_names)
