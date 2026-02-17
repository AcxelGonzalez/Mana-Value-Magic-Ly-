"""
Script simple para ver qué hay en elemental.txt
"""

# Leer archivo línea por línea
with open("elemental.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()

print(f"Total de líneas en el archivo: {len(lines)}")
print(f"\nPrimeras 5 líneas:")
for i, line in enumerate(lines[:5], 1):
    print(f"{i}. {line.strip()}")

print(f"\nÚltimas 5 líneas:")
for i, line in enumerate(lines[-5:], len(lines)-4):
    print(f"{i}. {line.strip()}")

# Contar cartas
total_cards = 0
for line in lines:
    line = line.strip()
    if line and not line.startswith('#'):
        parts = line.split(maxsplit=1)
        if parts:
            try:
                quantity = int(parts[0])
                total_cards += quantity
            except:
                pass

print(f"\n📦 Total de cartas contadas: {total_cards}")
print(f"⚠️  Nota: Un mazo de Commander debe tener 100 cartas (99 + comandante)")
