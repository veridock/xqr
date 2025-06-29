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

# PWA Integration with SVG Files: Embedding and Building Applications

The integration of Progressive Web Apps (PWAs) with SVG files represents two distinct but related approaches: embedding PWA functionality within SVG documents and building PWA applications that are based on or heavily utilize SVG content. Both approaches leverage the unique capabilities of SVG as a markup language that supports interactivity and scripting.

## PWA Inside SVG Files

### Understanding SVG's Scripting Capabilities

SVG files can contain JavaScript directly within their structure, making them capable of hosting web application functionality [1][2]. This capability stems from the fact that SVG explicitly uses JavaScript as its scripting language and includes a complete DOM structure [3]. The JavaScript embedded within SVG files has global scope across the entire document and can manipulate SVG elements dynamically [2].

### Embedding PWA Components in SVG

When creating a PWA inside an SVG file, developers can leverage several key features:

**Service Worker Integration**: While SVG files themselves cannot directly register service workers, they can communicate with parent documents that manage PWA functionality [4]. The SVG content can trigger events that the parent PWA application handles through its service worker.

**Interactive Elements**: SVG supports comprehensive interactivity through embedded JavaScript, allowing for complex user interfaces within the vector graphics format [1][5]. This includes event handling, DOM manipulation, and dynamic content updates.

**Web API Access**: SVG applications can access modern web APIs when embedded within a PWA context, including the File System Access API, Async Clipboard API, and other progressive web capabilities [6].

### Technical Implementation Considerations

Developers implementing PWA functionality within SVG files must consider several technical aspects:

**Security Implications**: SVG files containing JavaScript present security considerations, particularly when user-uploaded content is involved [2]. Embedding SVG as images or background images prevents JavaScript execution, while inline SVG allows full interactivity.

**Cross-Origin Restrictions**: SVG files loaded through `` or `` tags may face cross-origin restrictions that limit their ability to interact with the parent document [4][7].

## PWA Based on SVG Files

### SVG as Core Application Content

Progressive Web Apps built around SVG content utilize vector graphics as their primary interface and functionality delivery mechanism. This approach is particularly effective for applications requiring scalable, interactive graphics [8][9].

### Offline SVG Asset Management

PWAs that rely heavily on SVG content must carefully manage offline asset availability:

**Inline SVG Strategy**: The most reliable approach for ensuring SVG availability in offline PWAs is to inline SVG content directly in HTML [10][4]. This method guarantees that SVG assets remain accessible regardless of network connectivity.

**Caching Challenges**: SVG files loaded through `` or `` tags present unique caching challenges in PWAs [4][7]. The fetch algorithm for these elements bypasses service worker interception, making offline access problematic.

**Service Worker Optimization**: PWAs utilizing extensive SVG content benefit from optimized service worker strategies that prioritize SVG asset caching [8][9]. Tools like SVGJar for Ember applications provide efficient SVG management systems that scale with application complexity.

### Performance Optimization Strategies

PWAs based on SVG files can implement several performance optimization techniques:

**Asset Management**: Modern PWA development practices recommend using inline SVG management tools that inject SVG code directly into HTML, eliminating the need for separate network requests [8][9].

**Lazy Loading**: SVG-based PWAs can implement lazy loading strategies where SVG content is only cached when users actually install the PWA, rather than preemptively caching all assets for every visitor [11].

**Vector Graphics Advantages**: SVG-based PWAs benefit from vector graphics' inherent scalability, ensuring consistent visual quality across different device sizes and pixel densities [12][13].

### Manifest Configuration for SVG Icons

PWAs utilizing SVG extensively often configure their web app manifest to use SVG icons:

**Icon Sizing**: SVG icons in PWA manifests can be configured with multiple size declarations, though modern browsers increasingly support SVG-only configurations [14][15].

**Cross-Platform Compatibility**: While SVG icons provide excellent scalability, some platforms may require fallback PNG icons for complete compatibility [14].

## Development Best Practices

### Choosing the Right Approach

The choice between embedding PWA functionality in SVG files versus building SVG-based PWAs depends on specific use cases:

**SVG-Embedded PWAs**: Best suited for applications where the SVG content itself is the primary interface, such as interactive diagrams, games, or specialized visualization tools [16].

**SVG-Based PWAs**: More appropriate for applications that use SVG as a significant component but require broader web platform features and traditional HTML structure [8][17].

### Technical Implementation Guidelines

**DOM Integration**: Developers should leverage SVG's DOM compatibility to create seamless interactions between SVG content and PWA functionality [5][18].

**Framework Integration**: Modern JavaScript frameworks like React provide robust SVG integration capabilities, allowing developers to treat SVG content as reusable components within PWA applications [19][17].

**Progressive Enhancement**: Both approaches benefit from progressive enhancement strategies that ensure basic functionality works without JavaScript while providing enhanced experiences when scripting is available [13][18].

The integration of PWAs with SVG files offers powerful possibilities for creating engaging, scalable web applications that work effectively across different devices and network conditions. Success depends on careful consideration of technical requirements, performance implications, and user experience goals.

[1] https://stackoverflow.com/questions/5378559/including-javascript-in-svg
[2] https://davidwalsh.name/javascript-in-svgs
[3] https://news.ycombinator.com/item?id=39079943
[4] https://stackoverflow.com/questions/56854918/how-to-interact-with-an-svg-asset-in-an-offline-progressive-web-app
[5] https://www.petercollingridge.co.uk/tutorials/svg/interactive/javascript/
[6] https://web.dev/case-studies/svgcode
[7] https://github.com/GoogleChrome/workbox/issues/1569
[8] https://dev.to/ctannerweb/how-inline-svg-s-improve-performance-4k37
[9] https://dockyard.com/blog/2017/08/01/svg-assets-in-pwas
[10] https://stackoverflow.com/questions/56854918/how-to-interact-with-an-svg-asset-in-an-offline-progressive-web-app/56927409
[11] https://www.reddit.com/r/PWA/comments/ulbsq7/how_to_create_a_pwa_service_worker_that_only/
[12] https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/How_to/Define_app_icons
[13] https://daily.dev/blog/svg-basics-for-web-developers
[14] https://stackoverflow.com/questions/61446452/whether-all-icon-sizes-can-be-used-when-using-svg-in-pwa-manifest
[15] https://stackoverflow.com/questions/62825490/svg-icon-in-pwa-manifest-json-how-to-set-it-for-all-sizes
[16] https://www.svgator.com/interactive-svg-animation
[17] https://blog.logrocket.com/guide-svgs-react/
[18] https://developer.mozilla.org/en-US/docs/Web/SVG
[19] https://www.telerik.com/blogs/how-to-use-svg-react
[20] https://uxwing.com/pwa-icon/
[21] https://www.svgrepo.com/svg/354234/pwa
[22] https://stackoverflow.com/questions/64427667/how-to-use-svg-as-pwa-icon
[23] https://github.com/QasimTalkin/Progressive-Web-App
[24] https://www.bram.us/2021/11/29/svgcode-a-pwa-to-convert-raster-images-to-svg-vector-graphics/
[25] https://github.com/antonmedv/svg-embed
[26] https://flourish.studio/blog/interactive-svg-template/
[27] https://www.svgrepo.com/vectors/web-application-framework/
[28] http://www.w3schools.com/Html/html5_svg.asp
[29] https://dev.w3.org/SVG/tools/svgweb/docs/QuickStart.html
[30] https://github.com/101yogeshsharma/svg.init
[31] https://xmlgraphics.apache.org/batik/using/dom-api.html
[32] https://xmlgraphics.apache.org/batik/
[33] https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Tutorials/CycleTracker/Service_workers
[34] https://www.youtube.com/watch?v=liZcrjHAOww
[35] https://www.youtube.com/watch?v=lie7_DVxNBY
[36] https://www.w3.org/2021/10/TPAC/demos/pwa.html
[37] https://www.w3schools.com/graphics/svg_scripting.asp
[38] https://svgjs.dev
[39] https://www.intelegain.com/scalable-vector-graphics/

