# 🛠️ Universal File Editor CLI - Instrukcja użytkowania

## 📦 Instalacja wymaganych bibliotek

```bash
pip install lxml beautifulsoup4
```

## 🚀 Sposób użycia

### 1. Podstawowe komendy CLI

```bash
# Załaduj plik
python file_editor.py load example.svg

# Zapytanie XPath - pobierz tekst
python file_editor.py query "//text[@id='text1']" --type text

# Zapytanie XPath - pobierz atrybut
python file_editor.py query "//rect[@id='square1']" --type attribute --attr fill

# Ustaw tekst elementu
python file_editor.py set "//text[@id='text1']" "New Text Content" --type text

# Ustaw atrybut elementu
python file_editor.py set "//rect[@id='square1']" "green" --type attribute --attr fill

# Wylistuj wszystkie elementy
python file_editor.py list

# Wylistuj elementy z filtrem XPath
python file_editor.py list --xpath "//text"

# Zapisz zmiany
python file_editor.py save

# Zapisz do nowego pliku
python file_editor.py save --output modified_file.svg
```

### 2. Tryb interaktywny (Shell)

```bash
python file_editor.py shell
```

W trybie shell możesz używać komend:
```
📝 > load example.svg
✅ Loaded example.svg (svg)

📝 > query //text[@id='text1']
Result: Hello World

📝 > set //text[@id='text1'] "Updated Text"
✅ Updated

📝 > save
✅ Saved

📝 > exit
```

### 3. Serwer HTTP

```bash
python file_editor.py server --port 8080
```

Następnie otwórz http://localhost:8080 w przeglądarce.

## 📝 Przykłady XPath dla różnych typów plików

### SVG Files

```bash
# Znajdź wszystkie elementy text
//text

# Znajdź element po ID
//*[@id='circle1']

# Znajdź wszystkie prostokąty
//rect

# Znajdź elementy w metadata
//metadata/title

# Znajdź elementy po atrybucie
//rect[@fill='red']

# Znajdź elementy po pozycji
//rect[@x='10']
```

### XML Files

```bash
# Znajdź wszystkie rekordy
//record

# Znajdź rekord po ID
//record[@id='1']

# Znajdź wszystkie nazwy
//record/name

# Znajdź email konkretnej osoby
//record[name='John Doe']/email

# Znajdź metadane
//metadata/title
```

### HTML Files

```bash
# Znajdź element po ID
//*[@id='main-title']

# Znajdź elementy po klasie CSS
//*[@class='item']

# Znajdź wszystkie linki
//a

# Znajdź elementy w meta
//meta[@name='description']

# Znajdź tekst w paragrafie
//p[@id='intro']
```

## 🌐 API Serwera HTTP

### Załaduj plik
```bash
curl -X POST http://localhost:8080/api/load \
  -H "Content-Type: application/json" \
  -d '{"file_path": "example.svg"}'
```

### Wykonaj zapytanie XPath
```bash
curl -X POST http://localhost:8080/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "//text[@id=\"text1\"]", "type": "xpath"}'
```

### Aktualizuj element
```bash
curl -X POST http://localhost:8080/api/update \
  -H "Content-Type: application/json" \
  -d '{"xpath": "//text[@id=\"text1\"]", "type": "text", "value": "New Content"}'
```

### Zapisz plik
```bash
curl -X POST http://localhost:8080/api/save \
  -H "Content-Type: application/json" \
  -d '{"output_path": "modified.svg"}'
```

## 🔧 Przykłady praktycznego użycia

### 1. Aktualizacja metadanych SVG
```bash
# Załaduj plik SVG
python file_editor.py load chart.svg

# Zmień tytuł
python file_editor.py set "//metadata/title" "Updated Chart Title"

# Zmień opis
python file_editor.py set "//metadata/description" "Modified chart data"

# Zapisz
python file_editor.py save
```

### 2. Modyfikacja danych w HTML
```bash
# Załaduj HTML
python file_editor.py load report.html

# Zmień tytuł strony
python file_editor.py set "//title" "Updated Report"

# Zmień tekst nagłówka
python file_editor.py set "//h1[@id='main-title']" "New Report Title"

# Zmień meta description
python file_editor.py set "//meta[@name='description']" "Updated description" --type attribute --attr content

# Zapisz
python file_editor.py save --output updated_report.html
```

### 3. Batch processing z skryptem
```bash
#!/bin/bash
# Przykład batch processing

files=("data1.xml" "data2.xml" "data3.xml")

for file in "${files[@]}"; do
    echo "Processing $file..."
    
    # Załaduj plik
    python file_editor.py load "$file"
    
    # Aktualizuj wersję
    python file_editor.py set "//metadata/version" "2.0"
    
    # Aktualizuj datę
    python file_editor.py set "//metadata/updated" "$(date)"
    
    # Zapisz
    python file_editor.py save
    
    echo "✅ Updated $file"
done
```

### 4. Analiza i reporting
```bash
# Skrypt do analizy plików XML/SVG
python file_editor.py shell << EOF
load sales_data.xml
query //record
list --xpath "//record[sales>1000]"
exit
EOF
```

## 🎯 Zaawansowane funkcje

### XPath Expressions
- `//element` - znajdź wszystkie elementy o nazwie "element"
- `//*[@id='myid']` - znajdź element o konkretnym ID
- `//element[@attr='value']` - znajdź elementy z konkretną wartością atrybutu
- `//element[position()=1]` - pierwszy element
- `//element[last()]` - ostatni element
- `//element[text()='content']` - element z konkretnym tekstem

### CSS Selectors (tylko HTML)
- `#myid` - element o ID
- `.myclass` - elementy o klasie
- `div p` - paragrafy wewnątrz div
- `input[type="text"]` - inputy typu text

## ⚠️ Uwagi i ograniczenia

1. **XPath wymaga biblioteki lxml** - bez niej tylko podstawowe funkcje ElementTree
2. **CSS selectors działają tylko z HTML** - wymagają BeautifulSoup4
3. **Backup** - narzędzie automatycznie tworzy kopie zapasowe (.backup)
4. **Encoding** - domyślnie UTF-8, może wymagać dostosowania dla innych kodowań
5. **Namespaces** - SVG i XML z namespace mogą wymagać prefiksów w XPath

## 🐛 Rozwiązywanie problemów

### Brak lxml
```bash
pip install lxml
# lub na Ubuntu/Debian:
sudo apt-get install python3-lxml
```

### Błędy XPath
- Sprawdź składnię XPath w debuggerze przeglądarki
- Użyj `list` aby zobaczyć dostępne elementy
- Pamiętaj o namespace w SVG (`xmlns`)

### Problemy z zapisem
- Sprawdź uprawnienia do zapisu
- Użyj `--output` aby zapisać do nowego pliku
- Sprawdź czy plik nie jest używany przez inną aplikację

## 📚 Dodatkowe zasoby

- [XPath Tutorial](https://www.w3schools.com/xml/xpath_intro.asp)
- [CSS Selectors Reference](https://www.w3schools.com/cssref/css_selectors.asp)
- [SVG Elements Reference](https://developer.mozilla.org/en-US/docs/Web/SVG/Element)
- [lxml Documentation](https://lxml.de/)