"""
Convert raw scraped text examples into JSONL training format.
Semi-automatic: Extracts code blocks and formats them as training examples.
"""

import json
import re
from pathlib import Path

def extract_code_blocks(text):
    """Extract code blocks marked with ``` or indented"""
    code_blocks = re.findall(r'```(?:python|sql)?\n(.*?)```', text, re.DOTALL)
    if not code_blocks:
        # Try indented code blocks (4+ spaces)
        code_blocks = re.findall(r'    (.+?)(?:\n\n|\Z)', text, re.DOTALL)
    return code_blocks

def extract_vulnerable_secure_pairs(text):
    """Extract vulnerable vs secure code pairs from OWASP-style docs"""
    pairs = []
    
    # Pattern: "Vulnerable:" followed by code, then "Secure:" followed by code
    pattern = r'[Vv]ulnerable[:\s]+(.*?)(?=[Ss]ecure[:\s]|$)([Ss]ecure[:\s]+)?(\S+.*?)(?=\n\n|\Z)'
    
    for match in re.finditer(pattern, text, re.DOTALL):
        vulnerable = match.group(1).strip()
        secure = match.group(3).strip() if match.group(3) else ""
        
        if vulnerable and secure:
            pairs.append({
                "vulnerable": vulnerable,
                "secure": secure
            })
    
    return pairs

def format_as_training_example(instruction, output, input="", source=""):
    """Format as JSONL training example"""
    return {
        "instruction": instruction,
        "input": input,
        "output": output,
        "source": source
    }

def process_owasp_file(filepath):
    """Process OWASP security examples"""
    print(f"[*] Processing {filepath}...")
    examples = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract vulnerable/secure pairs
    pairs = extract_vulnerable_secure_pairs(content)
    
    for pair in pairs:
        instruction = f"Fix this SQL injection vulnerability"
        output = f"VULNERABLE:\n{pair['vulnerable']}\n\nSECURE:\n{pair['secure']}"
        
        examples.append(format_as_training_example(
            instruction=instruction,
            output=output,
            source=filepath.stem
        ))
    
    # Extract standalone code blocks
    code_blocks = extract_code_blocks(content)
    for i, code in enumerate(code_blocks[:10]):  # Limit to first 10
        if code.strip():
            instruction = f"Write secure Python/SQL code (example {i+1})"
            examples.append(format_as_training_example(
                instruction=instruction,
                output=code.strip(),
                source=filepath.stem
            ))
    
    print(f"  ✓ Extracted {len(examples)} examples")
    return examples

def process_github_file(filepath):
    """Process GitHub README examples"""
    print(f"[*] Processing {filepath}...")
    examples = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract code blocks
    code_blocks = extract_code_blocks(content)
    
    for i, code in enumerate(code_blocks):
        if code.strip() and len(code) > 20:  # Only meaningful code blocks
            instruction = f"Secure Python code pattern (from {filepath.stem})"
            examples.append(format_as_training_example(
                instruction=instruction,
                output=code.strip(),
                source=filepath.stem
            ))
    
    print(f"  ✓ Extracted {len(examples)} examples")
    return examples

def process_stackoverflow_file(filepath):
    """Process StackOverflow Q&A"""
    print(f"[*] Processing {filepath}...")
    examples = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    current_question = None
    current_url = None
    
    for line in lines:
        if line.startswith("# Question:"):
            current_question = line.replace("# Question:", "").strip()
        elif line.startswith("URL:"):
            current_url = line.replace("URL:", "").strip()
        elif current_question and line.strip():
            # Add Q&A as training example
            examples.append(format_as_training_example(
                instruction=current_question,
                output=line.strip(),
                source=f"StackOverflow ({current_url})" if current_url else "StackOverflow"
            ))
    
    print(f"  ✓ Extracted {len(examples)} examples")
    return examples

def process_all_files():
    """Process all raw example files"""
    examples = []
    
    raw_dir = Path("raw-examples")
    if not raw_dir.exists():
        print("✗ raw-examples directory not found. Run scrape_training_data.py first.")
        return []
    
    # Process each file type
    for filepath in raw_dir.glob("*.txt"):
        filename = filepath.name
        
        try:
            if "owasp" in filename:
                examples.extend(process_owasp_file(filepath))
            elif "github" in filename:
                examples.extend(process_github_file(filepath))
            elif "stackoverflow" in filename:
                examples.extend(process_stackoverflow_file(filepath))
            else:
                # Generic processing
                examples.extend(process_github_file(filepath))
        
        except Exception as e:
            print(f"  ✗ Error processing {filename}: {e}")
    
    return examples

def save_jsonl(examples, output_file="python_sql_training_data.jsonl"):
    """Save examples to JSONL file"""
    print(f"\n[*] Saving {len(examples)} examples to {output_file}...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for example in examples:
            f.write(json.dumps(example) + "\n")
    
    print(f"✓ Saved to {output_file}")

def validate_jsonl(filepath="python_sql_training_data.jsonl"):
    """Validate JSONL file"""
    print(f"\n[*] Validating {filepath}...")
    
    valid_count = 0
    invalid_count = 0
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f, 1):
                try:
                    example = json.loads(line)
                    if "instruction" in example and "output" in example:
                        valid_count += 1
                    else:
                        print(f"  ⚠ Line {i}: Missing 'instruction' or 'output'")
                        invalid_count += 1
                except json.JSONDecodeError:
                    print(f"  ✗ Line {i}: Invalid JSON")
                    invalid_count += 1
        
        print(f"\n✓ Valid examples: {valid_count}")
        print(f"✗ Invalid examples: {invalid_count}")
        
        if valid_count > 0:
            print(f"\n📊 Dataset ready for fine-tuning! ({valid_count} examples)")
            return True
        else:
            print("\n⚠ No valid examples found")
            return False
    
    except FileNotFoundError:
        print(f"✗ {filepath} not found")
        return False

def main():
    print("=" * 60)
    print("Raw Text to JSONL Converter")
    print("=" * 60)
    
    # Process all raw files
    examples = process_all_files()
    
    if not examples:
        print("\n✗ No examples extracted. Check raw-examples directory.")
        return
    
    # Save to JSONL
    save_jsonl(examples)
    
    # Validate
    validate_jsonl()
    
    print("\n" + "=" * 60)
    print("Next step: Review python_sql_training_data.jsonl")
    print("If it looks good, you're ready for fine-tuning!")
    print("=" * 60)

if __name__ == "__main__":
    main()
