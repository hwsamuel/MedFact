# MedFact Dependency Issues Analysis

## Summary
The MedFact project was originally developed for **Python 2.7.15** (as stated in README.md) but the current environment is running **Python 3.12.11**. This creates multiple compatibility issues that need to be addressed.

## Critical Issues

### 1. Python Version Compatibility
- **Original**: Python 2.7.15 (2018)
- **Current**: Python 3.12.11 (2024)
- **Impact**: Major breaking changes between Python 2 and 3

### 2. Package Version Issues

#### Severely Outdated Packages (5+ years old):
- `spacy==2.0.11` (2018) - **CRITICAL**: Fails to install on Python 3.12
- `Flask==1.0.2` (2018) - Security vulnerabilities, missing features
- `requests==2.21.0` (2019) - Security vulnerabilities
- `scikit_learn==0.21.3` (2019) - Missing modern features
- `gensim==3.4.0` (2019) - API changes in newer versions
- `beautifulsoup4==4.8.1` (2019) - Missing bug fixes

#### Moderately Outdated Packages:
- `nltk==3.6.6` (2021) - Should work but newer versions available
- `numpy==1.22.0` (2022) - May have compatibility issues with other packages
- `lxml==4.9.1` (2022) - Should work but newer versions available

### 3. Python 2 vs Python 3 Code Issues

#### Import Issues:
```python
# In scraper.py line 1:
from urllib import urlopen  # Python 2 syntax
# Should be:
from urllib.request import urlopen  # Python 3 syntax
```

#### Print Statement Issues:
Multiple files use Python 2 print statements without parentheses:
- `medfact.py` lines 210-212: `print 'Veracity', v_score`
- `trip.py` lines 110-113: `print 'Quality', ndcg_at_k(r1, 5)`
- `readability.py` lines 74-76: `print 'Flesch-Kincaid', fk, fk_label`

## Recommended Solutions

### Option 1: Minimal Updates (Recommended)
Update to compatible versions while maintaining similar functionality:

```txt
# Updated requirements.txt
nltk>=3.8.1
textblob>=0.17.1
lxml>=4.9.3
spacy>=3.7.0
Flask-HTTPAuth>=4.8.0
requests>=2.31.0
Flask>=3.0.0
gensim>=4.3.0
textstat>=0.7.3
numpy>=1.24.0
beautifulsoup4>=4.12.0
scikit-learn>=1.3.0
```

### Option 2: Full Modernization
- Upgrade to latest versions of all packages
- Refactor code to use modern Python 3 idioms
- Add type hints and modern error handling
- Update to use current best practices

### Option 3: Python 2.7 Environment
- Use Python 2.7 environment (NOT RECOMMENDED due to security and support issues)
- Python 2.7 reached end-of-life in January 2020

## Required Code Changes

### 1. Fix Import Statements
```python
# Change in scraper.py:
from urllib.request import urlopen
```

### 2. Fix Print Statements
Convert all print statements to function calls:
```python
# Change from:
print 'Veracity', v_score
# To:
print('Veracity', v_score)
```

### 3. Handle API Changes
- **spaCy**: Major API changes from 2.x to 3.x
- **gensim**: KeyedVectors API changes
- **scikit-learn**: Some parameter names changed

## Security Considerations
- `requests==2.21.0` has known security vulnerabilities
- `Flask==1.0.2` has security issues
- Old packages may have unpatched vulnerabilities

## Installation Priority
1. Fix Python 2/3 compatibility issues in code
2. Update requirements.txt with compatible versions
3. Test core functionality
4. Address any API breaking changes

## Estimated Effort
- **Minimal Updates**: 2-4 hours
- **Full Modernization**: 1-2 days
- **Testing and Validation**: Additional 1-2 hours

## Next Steps
1. Create updated requirements.txt
2. Fix Python 2/3 compatibility issues
3. Test installation and basic functionality
4. Address any API breaking changes
5. Update documentation