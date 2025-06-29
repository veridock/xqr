## Uniwersalne formaty kontenerowe

**JSON z JSON Schema** - najbardziej uniwersalny:
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "data": { /* twoje dane */ },
  "metadata": { /* opis struktury */ },
  "app": { /* konfiguracja aplikacji */ }
}
```

**SQLite jako przenośny kontener:**
- Pojedynczy plik zawierający dane + metadane + procedury
- Działa na każdym systemie bez instalacji
- Może zawierać aplikacje jako stored procedures lub triggers

**HDF5 dla danych naukowych:**
- Hierarchiczna struktura
- Wbudowane metadane
- Kompresja i chunking
- Biblioteki dla wszystkich języków

## Aplikacje niezależne od systemu

**Web-based (HTML+JS w jednym pliku):**
```html
<!DOCTYPE html>
<html>
<head><title>Aplikacja</title></head>
<body>
<script>
// Dane embedded w JS
const data = {...};
// Logika aplikacji
</script>
</body>
</html>
```

**Progressive Web Apps (PWA):**
- Działają offline
- Instalowalne na każdym systemie
- Dostęp do lokalnych plików

**Jupyter Notebooks:**
- Kod + dane + dokumentacja w jednym pliku
- Eksportowalne do HTML
- Uruchamialne w przeglądarce

## Praktyczne rozwiązania

**Data Package (Frictionless Data):**
```json
{
  "name": "my-dataset",
  "resources": [
    {
      "name": "data",
      "path": "data.csv",
      "schema": {...}
    }
  ],
  "views": [
    {
      "name": "chart",
      "type": "vega-lite",
      "spec": {...}
    }
  ]
}
```

**Observable Notebooks:**
- Dane + wizualizacje + interaktywność
- Eksport do różnych formatów
- Działają w każdej przeglądarce

Kluczowe jest wykorzystanie standardów web (HTML/CSS/JS) jako "maszyny wirtualnej" dostępnej wszędzie, w połączeniu z samopisującymi się formatami danych.

