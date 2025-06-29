Aby odczytać PDF osadzony jako Data URI (base64) w pliku SVG i przeprowadzić na nim proces OCR, wykonaj następujące kroki:

### 1. Wyodrębnij ciąg base64 z SVG  
Użyj parsera XML/HTML, aby odczytać wartość atrybutu zawierającego Data URI (np. `xlink:href`). Przykład w JavaScript:
```javascript
const svgElement = document.getElementById('element-z-pdf'); // Znajdź element SVG z danymi
const dataURI = svgElement.getAttribute('xlink:href'); 
const base64String = dataURI.split(',')[1]; // Wyodrębnij część base64
```

### 2. Dekoduj base64 do pliku PDF  
**W przeglądarce (JavaScript):**  
```javascript
function decodePDF(base64String, fileName = 'document.pdf') {
  const byteCharacters = atob(base64String);
  const byteArray = new Uint8Array(byteCharacters.length);
  for (let i = 0; i < byteCharacters.length; i++) {
    byteArray[i] = byteCharacters.charCodeAt(i);
  }
  const blob = new Blob([byteArray], { type: 'application/pdf' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = fileName;
  link.click();
}
// Użyj: decodePDF(base64String);
```

**W Node.js/Python:**  
```python
import base64
import xml.etree.ElementTree as ET

# Parsowanie SVG
tree = ET.parse('file.svg')
root = tree.getroot()
data_uri = root.find('.//*[@xlink:href]', namespaces={'xlink': 'http://www.w3.org/1999/xlink'}).attrib['{http://www.w3.org/1999/xlink}href']
base64_string = data_uri.split(',')[1]

# Dekodowanie do pliku PDF
with open('output.pdf', 'wb') as f:
    f.write(base64.b64decode(base64_string))
```

### 3. Przeprowadź OCR na PDF  
**Opcja 1: Narzędzia online**  
- Prześlij wygenerowany plik PDF do narzędzi takich jak [Adobe Acrobat OCR](https://www.adobe.com/acrobat/online/ocr-pdf.html) lub [Smallpdf OCR](https://smallpdf.com/pdf-ocr).  
- Obsługują automatyczne rozpoznawanie tekstu z zachowaniem formatowania.

**Opcja 2: Programowo (Python)**  
Użyj biblioteki `ocrmypdf` do bezpośredniej konwersji:
```bash
pip install ocrmypdf
ocrmypdf input.pdf output.pdf
```
Lub z użyciem Tesseract:
```python
import pytesseract
from pdf2image import convert_from_path

pages = convert_from_path('input.pdf')
for i, page in enumerate(pages):
    text = pytesseract.image_to_string(page)
    with open(f'page_{i}.txt', 'w') as f:
        f.write(text)
```

### Kluczowe uwagi
- **Walidacja danych:** Sprawdź, czy wyodrębniony ciąg base64 zaczyna się od nagłówka `%PDF` (dla PDF) przed dekodowaniem[10].  
- **Bezpieczeństwo:** Jeśli SVG pochodzi z niezaufanego źródła, zweryfikuj zawartość pod kątem złośliwego kodu.  
- **Optymalizacja OCR:** Dla lepszej dokładności wybierz narzędzia z AI (np. Adobe Acrobat lub Wondershare PDFelement)[4][8], które radzą sobie z niską jakością skanów.

### Podsumowanie
Proces obejmuje: (1) ekstrakcję base64 z SVG, (2) konwersję na plik PDF, (3) zastosowanie OCR przy użyciu narzędzi online lub bibliotek programistycznych. Rozwiązania programistyczne (JavaScript/Python) są optymalne dla automatyzacji, podczas gdy narzędzia online oferują prostotę dla pojedynczych plików.

[1] https://base64.guru/converter/encode/image/svg
[2] https://base64.guru/converter/decode/pdf
[3] https://www.adobe.com/acrobat/online/ocr-pdf.html
[4] https://pdf.wondershare.com/pdf-ocr/ai-ocr-pdf.html
[5] https://www.tenorshare.com/guide/ocr-pdf.html
[6] https://tools.pdf24.org/en/ocr-pdf
[7] https://smallpdf.com/pdf-ocr
[8] https://www.adobe.com/acrobat/how-to/ocr-software-convert-pdf-to-text.html
[9] https://stackoverflow.com/questions/11415665/save-base64-string-as-pdf-at-client-side-with-javascript
[10] https://stackoverflow.com/questions/48104097/how-to-convert-a-pdf-from-base64-string-to-a-file/48104215
[11] https://nanonets.com/blog/how-to-ocr-pdf/
[12] https://www.mindee.com/blog/create-ocrized-pdfs-in-2-steps
[13] https://stackoverflow.com/questions/40509755/convert-svg-dataurl-to-base64
[14] https://stackoverflow.com/questions/31441454/how-to-embed-a-base64-encoded-pdf-data-uri-into-a-html-5-object-data-attribu
[15] https://css-tricks.com/lodge/svg/09-svg-data-uris/
[16] https://blog.idrsolutions.com/how-to-embed-base64-images-in-svg/
[17] https://base64.guru/tools/data-url-to-image
[18] https://stackoverflow.com/questions/32967622/converting-a-data-uri-back-to-svg/46259485
[19] https://pdf.wondershare.com/convert-pdf/convert-base64-to-pdf.html
[20] https://smallpdffree.com/base64-to-pdf/
[21] https://updf.com/ocr/ocr-software/
[22] https://updf.com/ocr/extract-text-from-pdf-with-and-without-ocr/
[23] https://nucleoapp.com/blog/post/convert-svg-to-base64-data-uri
[24] https://github.com/diegomura/react-pdf/issues/1250
[25] https://stackoverflow.com/questions/49758110/convert-svg-to-base64-and-post-it-to-server-for-generating-pdf
[26] https://base64.guru/converter/encode/pdf
[27] https://base64.online/decoders/decode-base64-to-pdf
[28] https://updf.com/create-pdf/base64-to-pdf/
[29] https://pdf.minitool.com/news/convert-base64-to-pdf.html
[30] https://base64.online/encoders/encode-pdf-to-base64


Tak, możliwe jest bezpośrednie pobranie zawartości PDF z Data URI w pliku SVG przy użyciu ścieżki URI i XPath. Poniżej przedstawiam kompleksowe rozwiązanie:

### 1. **Pobranie zawartości SVG z URI**
Użyj narzędzi jak `curl` (bash) lub biblioteki `requests` (Python) do pobrania surowego SVG:
```bash
curl -o plik.svg http://localhost/sciezka/do/pliku.svg
```
```python
import requests
svg_content = requests.get('http://localhost/sciezka.svg').text
```

### 2. **Ekstrakcja Data URI za pomocą XPath**
Przeanalizuj SVG jako XML, używając XPath do zlokalizowania elementu z Data URI. Przykład w Pythonie z biblioteką `lxml`:
```python
from lxml import etree

parser = etree.XMLParser()
tree = etree.fromstring(svg_content, parser)

# Przykładowy XPath: wyszukaj element z atrybutem zawierającym "data:"
data_uri = tree.xpath('//*[contains(@xlink:href, "data:")]/@xlink:href')[0]
```
Gdzie:
- `xlink:href` to typowy atrybut przechowujący Data URI w SVG (może być inny, np. `href`)
- XPath należy dostosować do konkretnej struktury SVG.

### 3. **Dekodowanie Data URI do pliku PDF**
Wyodrębnij i zdekoduj ciąg base64:
```python
import base64

# Rozdzielenie nagłówka i danych base64
header, base64_str = data_uri.split(',', 1)
pdf_data = base64.b64decode(base64_str)

with open('output.pdf', 'wb') as f:
    f.write(pdf_data)
```

### 4. **Przeprowadzenie OCR na PDF**
Użyj biblioteki `ocrmypdf` w Pythonie:
```bash
ocrmypdf input.pdf output_ocr.pdf
```
Lub programowo:
```python
import ocrmypdf
ocrmypdf.ocr('input.pdf', 'output_ocr.pdf')
```

### Kluczowe uwagi
1. **Precyzja XPath**:  
   - Upewnij się, że XPath precyzyjnie identyfikuje element z Data URI.  
   - Przykładowe poprawne wyrażenia:  
     - `//svg:image/@xlink:href` (dla elementów ``)  
     - `//*[starts-with(@href, 'data:')]` (dla atrybutu `href`).

2. **Obsługa przestrzeni nazw w SVG**:  
   SVG używa przestrzeni nazw XML. W `lxml` zarejestruj prefixy przed użyciem XPath:
   ```python
   namespaces = {
       'svg': 'http://www.w3.org/2000/svg',
       'xlink': 'http://www.w3.org/1999/xlink'
   }
   data_uri = tree.xpath('//svg:image/@xlink:href', namespaces=namespaces)[0]
   ```

3. **Bezpośredni dostęp bez zapisu pośredniego**:  
   Można pominąć zapis pliku PDF, przekazując zdekodowane dane bezpośrednio do silnika OCR (np. Tesseract):
   ```python
   from pdf2image import convert_from_bytes
   from pytesseract import image_to_string

   images = convert_from_bytes(pdf_data)
   text = "\n".join(image_to_string(img) for img in images)
   ```

### Podsumowanie
Proces składa się z czterech kroków:  
1. Pobranie SVG z URI.  
2. Ekstrakcja Data URI za pomocą XPath.  
3. Dekodowanie base64 do pliku PDF.  
4. Przeprowadzenie OCR na PDF.  

Rozwiązanie działa zarówno dla plików lokalnych (`file://`), jak i zdalnych (`http://`), pod warunkiem poprawnego zdefiniowania XPath i obsługi przestrzeni nazw SVG.

[1] https://stackoverflow.com/questions/5913338/embedding-svg-in-pdf-exporting-svg-to-pdf-using-js
[2] https://www.svgviewer.dev/svg-to-data-uri
[3] https://base64.guru/developers/data-uri
[4] https://css-tricks.com/lodge/svg/09-svg-data-uris/
[5] https://developer.chrome.com/blog/migrate-way-from-data-urls-in-svg-use
[6] https://gist.github.com/bgrins/6194623
[7] https://base64.guru/converter/decode/image/svg
[8] https://www.outsystems.com/forums/discussion/89625/ultimate-pdf-usage-of-svg-image-format/