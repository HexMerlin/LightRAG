import tiktoken
import os
from dotenv import load_dotenv

# Load environment variables from 'env' file (not .env)
try:
    load_dotenv('env')
    # Get the embedding model from environment or use default
    embedding_model = os.getenv('EMBEDDING_MODEL', 'bge-m3:latest')
    print(f"Using embedding model reference: {embedding_model}")
except Exception as e:
    print(f"Could not load env file: {e}")
    embedding_model = "bge-m3:latest"

# Initialize the tokenizer with cl100k_base (used by many models including GPT-4 and similar to many embedding models)
encoding = tiktoken.get_encoding("cl100k_base")

# Sample texts of different lengths and content types
sample_texts = [
    "This is a short sample text.",
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla facilisi. Sed euismod, nisl eget ultricies ultricies, nunc nisl ultricies nisl, nec ultricies nisl nisl nec nisl.",
    "Technical content with code snippets: def calculate_ratio(text): tokens = encoding.encode(text); return len(text)/len(tokens)",
    "Document with multiple paragraphs.\nThis is paragraph 2.\nThis is paragraph 3 with some numbers 12345 and special characters !@#$%^&*().",
]

print("\nCharacter to Token Ratio Analysis\n")
print("| Text Sample | Characters | Tokens | Chars/Token |")
print("|-------------|------------|--------|------------|")

total_chars = 0
total_tokens = 0

for text in sample_texts:
    tokens = encoding.encode(text)
    char_count = len(text)
    token_count = len(tokens)
    ratio = char_count / token_count
    
    # Display truncated sample for readability
    display_text = text[:30] + "..." if len(text) > 30 else text
    
    print(f"| {display_text} | {char_count} | {token_count} | {ratio:.2f} |")
    
    total_chars += char_count
    total_tokens += token_count

# Calculate overall average
average_ratio = total_chars / total_tokens
print("\nOverall average characters per token:", f"{average_ratio:.2f}")

# Let's also analyze a very large text sample
large_text = "A" * 10000
large_tokens = encoding.encode(large_text)
large_ratio = len(large_text) / len(large_tokens)
print(f"\nFor a large repeating text (10000 'A's): {large_ratio:.2f} chars/token")

# Calculate token counts for our recommended chunk sizes
print("\nToken count for recommended chunk sizes:")
for char_size in [1024, 2048, 3000, 4096, 5000, 6000]:
    # Estimate with average ratio
    estimated_tokens = char_size / average_ratio
    # Verify with actual text of that length
    sample = "A" * char_size
    actual_tokens = len(encoding.encode(sample))
    print(f"{char_size} characters ≈ {estimated_tokens:.0f} tokens (estimate) / {actual_tokens} tokens (actual 'A's)")

print("\nNote: These calculations use tiktoken's 'cl100k_base' tokenizer which may differ slightly")
print(f"from {embedding_model}'s tokenization through Ollama, but provides a reasonable approximation.")
print("For most English text, a 3000-6000 character chunk will be around 800-1500 tokens,"
      " which aligns with LightRAG's default 1200 token chunks.") 