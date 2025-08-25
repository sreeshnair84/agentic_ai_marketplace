import nltk
import ssl

# Handle SSL context for downloading
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# Download NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
    print('NLTK data downloaded successfully')
except Exception as e:
    print(f'NLTK download warning: {e}')

# Check for sentence_transformers
try:
    import sentence_transformers
    print('Sentence transformers available')
except ImportError:
    print('Sentence transformers not available')
