Nastąpiło przesunięcie w myśleniu. Dawniej mieliśmy wyraźny podział:
- **Aplikacja** (program wykonujący funkcje)
- **Dane** (pliki z informacjami)
- **Metadane** (informacje o danych)

Dziś wszystko "stało się bazą danych" głównie z powodów:
- **Wydajności** - bazy danych szybciej wyszukują i indeksują
- **Skalowania** - łatwiej zarządzać milionami rekordów
- **Integracji** - jedna baza może obsługiwać wiele aplikacji
- **Monetyzacji** - zamknięte formaty utrudniają migrację danych

## Separation of concerns w praktyce

**Formaty plików mogące służyć jako aplikacje:**
- **JSON/YAML** - konfiguracje aplikacji, ale też logika workflows
- **Markdown** - dokumenty z osadzoną logiką (np. Jupyter notebooks)
- **XML/HTML** - znaczniki + embedded JavaScript
- **SQLite** - baza danych w jednym pliku, może zawierać procedury składowane

**Kontenery danych:**
- **Parquet** - kolumnowy format z metadanymi
- **HDF5** - hierarchiczny format naukowy
- **JSON-LD** - JSON z linked data
- **CSV** z zewnętrznymi schematami

**Kontenery metadanych:**
- **JSON Schema** - opisuje strukturę danych JSON
- **Dublin Core** - standard metadanych
- **DCAT** - katalogowanie zbiorów danych
- **Data Package** - format Frictionless Data

## Dlaczego o tym się nie mówi?

1. **Kompleksność techniczna** - łatwiej mówić o "ochronie" niż o formatach
2. **Interesy biznesowe** - vendor lock-in jest opłacalny
3. **Brak świadomości** - prawników nie uczą formatów plików
4. **Szybkość rozwoju** - technologie zmieniają się szybciej niż regulacje

**Praktyczne podejście do separacji:**
- Używaj otwartych formatów (JSON, CSV, XML)
- Separuj dane od logiki aplikacji
- Dokumentuj schematy danych
- Stosuj standardy metadanych
- Rozważ formaty samo-opisujące się (JSON-LD, RDF)

Cloud zatarł granice - SaaS to aplikacja+dane+infrastruktura w pakiecie, co utrudnia kontrolę nad własnymi informacjami.