# Regex
<p align="center">
  <img src="https://img.shields.io/github/stars/peter-hunt/regex">
  <img src="https://img.shields.io/static/v1?label=Contributions&message=Welcome&color=0059b3">
  <img src="https://img.shields.io/github/repo-size/peter-hunt/regex">
  <img src="https://img.shields.io/github/languages/top/peter-hunt/regex">
  <img src="https://img.shields.io/github/license/peter-hunt/regex">
</p>
An attempt of recreating Regex with Python

# Installation
Use git to install Cocktail Lang.

```bash
git clone https://github.com/peter-hunt/regex.git
```

This project requires Python 3.8+

## Usage
```python
import regex
print(regex.match(r'\w+\d*?', 'peter_hunt123'))
```

## Known Issues
Removed param `start` and `end` from `Pattern._match` cause it kept bugging. It won't be friendly to groups later on.

## License
[MIT](LICENSE.txt)
