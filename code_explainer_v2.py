#!/usr/bin/env python3
"""
Code Explainer Tool v2 - Enhanced version with file loading, markdown export, and model selection
Features:
- Load code from files (Python, JavaScript, Java, etc.)
- Save explanations to markdown files
- Choose between different Claude models
- Interactive CLI

Usage:
  python code_explainer_v2.py                    # Interactive mode
  python code_explainer_v2.py path/to/file.py   # Explain file directly
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from anthropic import Anthropic

# Available models with descriptions
MODELS = {
    "1": {
        "name": "claude-3-5-sonnet-20241022",
        "display": "Claude 3.5 Sonnet (Fast & Good)",
        "description": "Balanced speed and quality - recommended for most tasks"
    },
    "2": {
        "name": "claude-3-5-opus-20241022",
        "display": "Claude 3.5 Opus (Slower but Better)",
        "description": "More detailed explanations, handles complex code better"
    },
    "3": {
        "name": "claude-3-5-haiku-20241022",
        "display": "Claude 3.5 Haiku (Fastest)",
        "description": "Quick explanations, good for simple code"
    }
}

class CodeExplainer:
    def __init__(self):
        """Initialize the Code Explainer"""
        self.api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "❌ ANTHROPIC_API_KEY not set!\n"
                "Please set your API key: export ANTHROPIC_API_KEY='your-key'\n"
                "Get it from: https://console.anthropic.com/api_keys"
            )
        self.client = Anthropic(api_key=self.api_key)
        self.selected_model = MODELS["1"]["name"]  # Default model

    def display_models(self):
        """Show available models to user"""
        print("\n" + "="*60)
        print("📊 AVAILABLE MODELS")
        print("="*60)
        for key, model in MODELS.items():
            print(f"\n{key}. {model['display']}")
            print(f"   └─ {model['description']}")
        print("\n" + "="*60)

    def select_model(self) -> str:
        """Let user select a model"""
        self.display_models()
        while True:
            choice = input("\nSelect a model (1-3, default: 1): ").strip() or "1"
            if choice in MODELS:
                self.selected_model = MODELS[choice]["name"]
                print(f"✅ Using: {MODELS[choice]['display']}\n")
                return self.selected_model
            print("❌ Invalid choice. Please select 1, 2, or 3.")

    def load_code_from_file(self, file_path: str) -> tuple:
        """
        Load code from a file
        Returns: (code_content, language, file_name)
        """
        try:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            if not path.is_file():
                raise IsADirectoryError(f"This is a directory, not a file: {file_path}")

            # Read file
            with open(path, 'r', encoding='utf-8') as f:
                code = f.read()

            # Detect language from extension
            extension_to_language = {
                '.py': 'Python',
                '.js': 'JavaScript',
                '.ts': 'TypeScript',
                '.java': 'Java',
                '.cpp': 'C++',
                '.c': 'C',
                '.cs': 'C#',
                '.rb': 'Ruby',
                '.go': 'Go',
                '.rs': 'Rust',
                '.sql': 'SQL',
                '.html': 'HTML',
                '.css': 'CSS',
                '.php': 'PHP',
                '.swift': 'Swift',
                '.kt': 'Kotlin',
            }

            language = extension_to_language.get(path.suffix, 'unknown')

            print(f"\n✅ Loaded: {path.name}")
            print(f"   Language: {language}")
            print(f"   Lines: {len(code.splitlines())}")
            print(f"   Size: {len(code)} characters\n")

            return code, language, path.name

        except FileNotFoundError as e:
            print(f"❌ Error: {e}")
            return None, None, None
        except IsADirectoryError as e:
            print(f"❌ Error: {e}")
            return None, None, None
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return None, None, None

    def get_multiline_input(self, prompt: str) -> str:
        """Get multi-line code input from user"""
        print(prompt)
        print("(Type 'END' on a new line when done)")
        lines = []
        while True:
            line = input()
            if line.strip() == "END":
                break
            lines.append(line)
        return "\n".join(lines)

    def explain_code(self, code: str, language: str = "auto") -> str:
        """
        Send code to Claude and get an explanation

        Args:
            code: The code to explain
            language: Programming language

        Returns:
            Claude's explanation
        """

        system_prompt = """You are an expert code explainer. When given code, you should:

1. **Identify the language** (if not obvious)
2. **Explain what it does** - High-level overview first
3. **Break it down** - Explain key functions, loops, conditionals
4. **Highlight important parts** - What's clever, what might be confusing
5. **Spot issues** - Any bugs, inefficiencies, or improvements
6. **Give examples** - If helpful, show how the code would execute with sample input

Keep explanations clear and suitable for someone learning programming. Use simple language but be technically accurate."""

        user_message = f"""Please explain this {language} code:

```
{code}
```"""

        try:
            message = self.client.messages.create(
                model=self.selected_model,
                max_tokens=1024,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )

            return message.content[0].text
        except Exception as e:
            raise Exception(f"API Error: {e}")

    def save_to_markdown(self, code: str, language: str, explanation: str, file_name: str = None) -> str:
        """
        Save code and explanation to a markdown file

        Args:
            code: Original code
            language: Programming language
            explanation: Claude's explanation
            file_name: Original file name (optional)

        Returns:
            Path to saved file
        """
        try:
            # Create filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if file_name:
                base_name = Path(file_name).stem
                output_file = f"explanation_{base_name}_{timestamp}.md"
            else:
                output_file = f"explanation_{timestamp}.md"

            # Create markdown content
            markdown_content = f"""# Code Explanation
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Language
{language}

{"## Original File" + chr(10) + f"{file_name}" + chr(10) if file_name else ""}

## Code
```{language.lower() if language != 'unknown' else ''}
{code}
```

## Explanation
{explanation}

---
*Generated by Code Explainer Tool*
"""

            # Save file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)

            print(f"\n✅ Saved to: {output_file}")
            print(f"   Location: {Path(output_file).absolute()}\n")

            return output_file

        except Exception as e:
            print(f"❌ Error saving file: {e}")
            return None

    def main(self):
        """Main interactive loop"""
        print("\n" + "="*60)
        print("🔍 CODE EXPLAINER TOOL v2")
        print("="*60)
        print("\nEnhanced features:")
        print("✅ Load code from files")
        print("✅ Save explanations to markdown")
        print("✅ Choose different Claude models")
        print()

        try:
            self.client
        except ValueError as e:
            print(f"❌ {e}")
            return

        print("✅ Connected to Claude API!\n")

        # Check if file was provided as argument
        if len(sys.argv) > 1:
            file_path = sys.argv[1]
            code, language, file_name = self.load_code_from_file(file_path)
            if code:
                self.select_model()
                print("⏳ Analyzing code...")
                print("-" * 60)

                try:
                    explanation = self.explain_code(code, language)
                    print(explanation)
                    print("-" * 60)

                    # Ask to save
                    save_choice = input("\nSave explanation to markdown? (y/n): ").strip().lower()
                    if save_choice == 'y':
                        self.save_to_markdown(code, language, explanation, file_name)

                except Exception as e:
                    print(f"❌ Error: {e}")
            return

        # Interactive mode
        self.select_model()

        while True:
            print("\n" + "="*60)
            print("OPTIONS")
            print("="*60)
            print("1. Explain code from input")
            print("2. Explain code from file")
            print("3. Change model")
            print("4. Exit")
            print("="*60)

            choice = input("\nChoose (1-4): ").strip()

            if choice == "4":
                print("\n👋 Goodbye!")
                break

            elif choice == "3":
                self.select_model()
                continue

            elif choice not in ["1", "2"]:
                print("❌ Invalid choice. Please select 1-4.")
                continue

            # Get code (from input or file)
            if choice == "2":
                file_path = input("\nEnter file path: ").strip()
                code, language, file_name = self.load_code_from_file(file_path)
                if not code:
                    continue
            else:
                language = input("Programming language (default: auto): ").strip() or "auto"
                code = self.get_multiline_input("\nPaste your code below:")
                file_name = None

                if not code.strip():
                    print("❌ No code provided!")
                    continue

            # Explain code
            print("\n⏳ Analyzing code...")
            print("-" * 60)

            try:
                explanation = self.explain_code(code, language)
                print(explanation)
            except Exception as e:
                print(f"❌ Error: {e}")
                continue

            print("-" * 60)

            # Ask to save
            save_choice = input("\nSave explanation to markdown? (y/n): ").strip().lower()
            if save_choice == 'y':
                self.save_to_markdown(code, language, explanation, file_name)

            print("\n✨ Done!")

if __name__ == "__main__":
    try:
        explainer = CodeExplainer()
        explainer.main()
    except ValueError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user. Goodbye!")
        sys.exit(0)