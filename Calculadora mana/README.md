## 📋 Descripción

Calcula probabilidades para Magic: The Gathering formato Commander usando **Distribución Hipergeométrica**. Ideal para analizar mazos, optimizar construcción y calcular probabilidades de robo.

## ✨ Características

### 🔢 Cálculos de Probabilidad
- **Distribución Hipergeométrica**: Matemática precisa para probabilidades sin reemplazo
- Cálculos de "al menos X cartas", "exactamente X", "entre X e Y"
- Escenarios predefinidos para manos iniciales y turnos específicos

### 📊 Análisis de Mazo
- **Importación desde Moxfield**: Soporte para CSV y TXT
- **Integración con Scryfall API**: Datos automáticos de todas las cartas
- Categorización automática:
  - Tierras
  - Ramp (aceleradores de maná)
  - Elementales (y otros tribales)
  - Removal/Interacción
  - Contrahechizos
  - Robo de cartas
  
### 📈 Visualización
- Curva de maná
- Distribución de colores
- Estadísticas completas del mazo
- Tablas formateadas

## 🚀 Instalación

### Requisitos
- Python 3.8 o superior
- pip

### Pasos

1. **Clonar o descargar** este proyecto

2. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

3. **Ejecutar**:
```bash
python main.py
```

## 📖 Cómo Usar

### 1. Exportar tu mazo desde Moxfield

1. Ve a [Moxfield.com](https://www.moxfield.com/)
2. Abre tu mazo de Commander
3. Click en **"Export"**
4. Selecciona **"CSV"** o **"Text"**
5. Descarga el archivo


**¿Por qué hipergeométrica?**
Porque MTG roba cartas **sin reemplazo** de un conjunto **finito**. No es como lanzar un dado (donde cada evento es independiente), sino como sacar bolas de una urna sin devolverlas.

## 📁 Estructura del Proyecto

```
Calculadora mana/
├── main.py                 # Aplicación CLI principal
├── hypergeometric.py       # Cálculos de probabilidad
├── moxfield_parser.py      # Parser para archivos de Moxfield
├── scryfall_api.py         # Cliente para API de Scryfall
├── deck_analyzer.py        # Análisis y categorización de mazos
├── requirements.txt        # Dependencias Python
└── README.md              # Este archivo
```

## 🐛 Solución de Problemas

**Error al cargar archivo**:
- Verifica que la ruta sea correcta
- En Windows usa `\\` o `/` en rutas
- Ejemplo: `C:/Users/Orion/Desktop/mi_mazo.csv`

**Carta no encontrada en Scryfall**:
- Verifica el nombre exacto de la carta
- Scryfall usa nombres en inglés
- Usa "fuzzy search" automático

**Rate limit de Scryfall**:
- La app respeta automáticamente el rate limit (100ms entre requests)
- Para mazos grandes puede tomar 1-2 minutos

## 📚 Recursos

- [Moxfield](https://www.moxfield.com/) - Constructor de mazos
- [Scryfall](https://scryfall.com/) - Base de datos de cartas MTG
- [Distribución Hipergeométrica](https://en.wikipedia.org/wiki/Hypergeometric_distribution) - Teoría matemática
- [EDHREC](https://edhrec.com/) - Recomendaciones para Commander

## 🎮 Ejemplo de Sesión

```
🎴  CALCULADORA DE PROBABILIDADES MTG COMMANDER
📊 Distribución Hipergeométrica
⚡ Optimizada para Omnath, Locus of the Roil
===================================================================

🎮 MENÚ PRINCIPAL
1. Cargar mazo
2. Calcular probabilidades
3. Ver estadísticas del mazo
4. Salir

Elige una opción: 1

📁 CARGAR MAZO
1. Cargar desde archivo (Moxfield CSV/TXT)
2. Cargar mazo de ejemplo (Omnath)
3. Volver

Elige una opción: 1
Ingresa la ruta del archivo: C:/Users/Orion/Desktop/omnath_deck.csv

🔄 Cargando mazo desde: C:/Users/Orion/Desktop/omnath_deck.csv
✅ Archivo parseado: 100 entradas encontradas

🔍 Consultando Scryfall para 100 cartas...
✅ Consulta completada: 100 cartas procesadas

✅ Mazo cargado exitosamente: 100 cartas

📊 ANÁLISIS DEL MAZO
===============================================================
📦 Total de cartas: 100
🏔️  Tierras: 37
💎 Ramp: 12
🐉 Criaturas: 28
   └─ 🔥 Elementales: 15
⚔️  Removal: 8
📖 Robo de cartas: 6
🚫 Contrahechizos: 4
❓ Otras: 5

📈 CMC Promedio (sin tierras): 3.42

📊 CURVA DE MANÁ:
   CMC  0: █ (1)
   CMC  1: ████ (5)
   CMC  2: ███████████ (12)
   CMC  3: ████████████████ (18)
   CMC  4: ██████████████████████████████ (15)
   CMC  5: ████████████ (8)
   CMC  6: ████████ (4)
   CMC  7+: █████ (3)

🎨 DISTRIBUCIÓN DE COLORES:
   🌳 Verde: 45
   💧 Azul: 38
   🔥 Rojo: 32
   ◇ Incoloro: 8
===============================================================
```

## 📄 Licencia

Proyecto personal educativo. Úsalo libremente para tus mazos de Commander.
---





