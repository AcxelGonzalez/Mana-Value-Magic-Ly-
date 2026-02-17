"""
Script rápido para probar el mazo elemental.txt
"""

from moxfield_parser import MoxfieldParser
from scryfall_api import ScryfallAPI
from deck_analyzer import DeckAnalyzer
from colorama import init

# Inicializar colorama
init()

print("🔄 Cargando mazo desde elemental.txt...\n")

# Cargar archivo
cards = MoxfieldParser.load_deck("elemental.txt")

if not cards:
    print("❌ No se pudo cargar el mazo.")
    exit()

print(f"✅ Archivo parseado: {len(cards)} entradas encontradas\n")

# Obtener nombres únicos
unique_names = MoxfieldParser.get_unique_cards(cards)
print(f"📋 Cartas únicas en el mazo: {len(unique_names)}\n")

# Consultar Scryfall
api = ScryfallAPI()
cards_data = api.get_multiple_cards(unique_names)

# Crear lista expandida
deck_cards = MoxfieldParser.get_card_list(cards)
deck_size = len(deck_cards)

# Crear analizador con la lista completa
analyzer = DeckAnalyzer(cards_data, deck_cards)

print(f"\n✅ Mazo cargado exitosamente: {deck_size} cartas\n")

# Mostrar estadísticas
analyzer.print_statistics()

print("\n" + "="*60)
print("✅ ¡Mazo cargado correctamente!")
print("Ahora puedes usar python main.py para cálculos de probabilidad")
print("="*60)
