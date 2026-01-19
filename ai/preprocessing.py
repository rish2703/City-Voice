import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import re

# Initialize tools
stop_words = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()

def preprocess_text(text):
    # 1. Lowercase
    text = text.lower()
    
    # 2. Remove special characters and numbers
    text = re.sub(r"[^a-zA-Z\s]", "", text)
    
    # 3. Tokenize
    words = nltk.word_tokenize(text)
    
    # 4. Remove stopwords
    filtered_words = [word for word in words if word not in stop_words]
    
    # 5. Lemmatize (convert words to base form)
    lemmatized_words = [lemmatizer.lemmatize(word) for word in filtered_words]
    
    # 6. Join back to string
    clean_text = " ".join(lemmatized_words)
    
    return clean_text
