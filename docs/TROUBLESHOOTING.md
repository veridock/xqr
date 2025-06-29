# Troubleshooting Guide

This guide provides solutions to common issues you might encounter while using XQR.

## Installation Issues

### Missing Dependencies

**Error**: `ModuleNotFoundError: No module named 'module_name'`

**Solution**: Install the required Python packages:

```bash
pip install -r requirements.txt
```

### System Dependencies

**Error**: `OSError: Failed to execute...` or similar system command errors

**Solution**: Ensure all system dependencies are installed:

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install -y poppler-utils tesseract-ocr pdf2svg python3-magic libmagic1
```

#### macOS
```bash
brew install poppler tesseract pdf2svg libmagic
```

## Runtime Errors

### File Not Found

**Error**: `FileNotFoundError: [Errno 2] No such file or directory`

**Solution**: Verify the file path is correct and the file exists:

```bash
ls -l /path/to/your/file
```

### Permission Denied

**Error**: `PermissionError: [Errno 13] Permission denied`

**Solution**: Check file permissions and ownership:

```bash
ls -l /path/to/file
chmod +x /path/to/file  # If executable permission is needed
chown youruser:yourgroup /path/to/file  # Change ownership if needed
```

## PDF Conversion Issues

### Corrupted PDF Output

**Symptom**: PDF files are generated but cannot be opened or are corrupted

**Solution**:
1. Ensure the input file is not corrupted
2. Try converting with a different DPI setting:
   ```bash
   xqr convert input.svg output.pdf --dpi 300
   ```
3. Check for error messages during conversion

### Text Extraction Problems

**Symptom**: Text is not being extracted correctly from PDFs

**Solution**:
1. Increase OCR DPI for better accuracy:
   ```bash
   xqr convert input.pdf output.svg --dpi 600
   ```
2. Check if the PDF contains actual text or just images
3. Try different OCR settings:
   ```bash
   xqr convert input.pdf output.svg --ocr-engine tesseract
   ```

## Performance Issues

### Slow Processing

**Symptom**: Operations take too long to complete

**Solutions**:
1. Process files in chunks:
   ```bash
   xqr process large.xml --chunk-size 100
   ```
2. Disable unnecessary features:
   ```bash
   xqr convert input.svg output.pdf --no-metadata
   ```
3. Use parallel processing:
   ```bash
   find . -name "*.svg" | parallel -j 4 "xqr convert {} {.}.pdf"
   ```

## Common Error Messages

### "Invalid XPath expression"

**Cause**: The XPath expression is not valid

**Solution**:
1. Check XPath syntax
2. Verify element names and attributes
3. Use `xqr query --debug file.xml "xpath"` for more details

### "Element not found"

**Cause**: No elements match the specified XPath

**Solution**:
1. Verify the XPath expression
2. Check if the element exists in the document
3. Try a simpler XPath query first

## Debugging Tips

### Enable Verbose Output

Use the `-v` or `--verbose` flag for more detailed output:

```bash
xqr -v convert input.svg output.pdf
```

### Save Intermediate Files

Use the `--keep-temp` flag to preserve temporary files for debugging:

```bash
xqr convert input.svg output.pdf --keep-temp
```

## Getting Help

If you're still experiencing issues:

1. Check the [GitHub Issues](https://github.com/veridock/xqr/issues) for similar problems
2. Create a new issue with:
   - Steps to reproduce
   - Expected vs actual behavior
   - Error messages
   - Environment details (OS, Python version, etc.)

## Known Issues

1. **Memory Usage with Large Files**: Very large files may cause high memory usage
   - Workaround: Process in smaller chunks

2. **Font Rendering**: Some fonts may not render correctly
   - Workaround: Install additional system fonts or specify font paths

3. **PDF/A Compatibility**: Some PDF features may not be fully compatible with PDF/A
   - Workaround: Use standard PDF format if possible

## Version Compatibility

| XQR Version | Python Versions | Notes                     |
|-------------|-----------------|---------------------------|
| 1.0.x      | 3.8+            | Initial release           |
| 2.0.x      | 3.9+            | Added parallel processing |


## Support

For additional support, please contact:
- Email: support@example.com
- GitHub: [https://github.com/veridock/xqr/issues](https://github.com/veridock/xqr/issues)
