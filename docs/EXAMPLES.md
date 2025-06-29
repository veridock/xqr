# XQR Examples

This document provides practical examples of using XQR for various tasks.

## Basic Examples

### Querying Elements

Find all paragraph elements:

```bash
xqr query document.html "//p"
```

Get elements by class name:

```bash
xqr query styles.css ".button"
```

### Modifying Content

Update text content:

```bash
xqr set document.html "//h1" "New Title"
```

Update an attribute:

```bash
xqr set document.html "//img[@id='logo']" "new-logo.png" --attr src
```

## Real-world Use Cases

### Batch Update Copyright Year

```bash
# Update copyright year in all HTML files
for file in **/*.html; do
    echo "Updating $file..."
    xqr set "$file" "//span[@class='copyright']" "© 2025 Company Name"
    xqr save "$file"
done
```

### Extract Data to CSV

Extract product information to a CSV file:

```bash
echo "Name,Price,Stock" > products.csv
xqr query products.html "//div[contains(@class,'product')]" | while read -r product; do
    name=$(echo "$product" | xqr query - "//h3" | tr -d '\n' | tr ',' ';')
    price=$(echo "$product" | xqr query - "//span[@class='price']" | tr -d '\n')
    stock=$(echo "$product" | xqr query - "//span[@class='stock']" | tr -d '\n')
    echo "$name,$price,$stock" >> products.csv
done
```

### Convert Multiple SVGs to PDF

```bash
# Convert all SVGs in current directory to PDF
for svg in *.svg; do
    xqr convert "$svg" "${svg%.svg}.pdf"
done
```

## Integration Examples

### With Makefiles

```makefile
.PHONY: update-version
update-version:
	xqr set package.json "//version" "$(VERSION)"
	xqr save package.json
```

### With CI/CD Pipelines

```yaml
# .gitlab-ci.yml
stages:
  - deploy

deploy:
  stage: deploy
  script:
    - pip install xqr
    - xqr set config.xml "//version" "${CI_COMMIT_TAG}"
    - xqr save config.xml
    - scp config.xml user@example.com:/var/www/config.xml
```

### With Python Scripts

```python
from xqr import FileEditor

# Load and edit file
editor = FileEditor('config.xml')

version = editor.query("//version")[0].text
print(f"Current version: {version}")

# Make changes
editor.set("//version", "2.0.0")
editor.save()
```

## Advanced Examples

### Conditional Updates

Update only if condition is met:

```bash
# Only update if current version is less than 2.0.0
current_version=$(xqr query config.xml "//version" | head -1)
if [ "$(printf '%s\n' "2.0.0" "$current_version" | sort -V | head -n1)" = "$current_version" ]; then
    xqr set config.xml "//version" "2.0.0"
    xqr save config.xml
fi
```

### Bulk Rename Attributes

```bash
# Change all 'class' attributes to 'className'
xqr query file.html "//@class" | while read -r element; do
    value=$(xqr query - "string($element)")
    xqr set - "$element" "" --attr class  # Remove old attribute
    xqr set - "${element%/@class}" "$value" --attr className  # Add new attribute
    xqr save file.html
done
```

### Extract and Process Data

Extract and process table data:

```bash
# Extract table data to TSV
xqr query data.html "//tr[position()>1]" | while read -r row; do
    echo -n "$row" | xqr query - "string(./td[1])" | tr -d '\n'
    echo -ne "\t"
    echo -n "$row" | xqr query - "string(./td[2])" | tr -d '\n'
    echo

done > data.tsv
```

## Troubleshooting Examples

### Debugging XPath Queries

```bash
# Show detailed information about matching elements
xqr query -v document.html "//div[contains(@class, 'product')]"
```

### Handling Namespaces

```bash
# Register namespaces for XPath queries
xqr query --ns x=http://www.w3.org/1999/xhtml document.xhtml "//x:div/x:p"
```

### Working with Large Files

```bash
# Process large files in chunks
xqr process large.xml --chunk-size 1000 "//record" process_record.sh
```
