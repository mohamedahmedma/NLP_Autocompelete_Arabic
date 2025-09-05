from GloblaImport import *;
#  PREPROCESSING
class ArabicPreprocessor:
    def __init__(self):
        self.arabic_diacritics = re.compile(r'[\u064B-\u065F\u0670]')
        self.arabic_punctuations = re.compile(r'[\u0021-\u002F\u003A-\u0040\u005B-\u0060\u007B-\u007E\u060C\u061B\u061F\u066D\u06D4]')
        self.non_arabic_letters = re.compile(r'[^\u0621-\u063A\u0641-\u064A\s]')
        self.whitespace = re.compile(r'\s+')    #matches one or more white space

    def preprocess_text(self, text):
        # Remove diacritics (tashkeel)
        text = self.arabic_diacritics.sub('', text)
        
        # Remove punctuations
        text = self.arabic_punctuations.sub(' ', text)
        
        # Remove non-Arabic letters
        text = self.non_arabic_letters.sub(' ', text)
        
        # Normalize whitespace
        text = self.whitespace.sub(' ', text)   #replace more than one line space or new lines with one white space
        return text.strip()

    def tokenize(self, text):
        
        return text.split()

    def process_file(self, file_path):
       
        all_tokens = []
        sentence_count = 0
        
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return all_tokens
            
        print(f"Processing file: {file_path}...")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
                print(f"Successfully read file with {len(text)} characters")
        except Exception as e:
            print(f"Error reading file: {e}")
            # Try again with different encodings if UTF-8 fails
            try:
                with open(file_path, 'r', encoding='cp1256') as f:  # Arabic Windows encoding
                    text = f.read()
                    print(f"Successfully read file with cp1256 encoding, {len(text)} characters")
            except Exception as e2:
                print(f"Error reading file with alternative encoding: {e2}")
                return all_tokens
        
        # Split into sentences 
        sentences = re.split(r'[.!?؟!\n]+', text)
        print(f"Split text into {len(sentences)} sentences")

        # Process each sentence
        for sentence in sentences:
            if sentence.strip():  # Skip empty sentences
                processed_text = self.preprocess_text(sentence)
                tokens = self.tokenize(processed_text)
                
                if len(tokens) > 3:  # Only include sentences with at least 3 tokens
                    all_tokens.extend(tokens)
                    sentence_count += 1
        
        print(f"Completed processing with {sentence_count} valid sentences.")
        print(f"Total tokens collected: {len(all_tokens)}")
        return all_tokens

