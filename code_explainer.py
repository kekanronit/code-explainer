#!/usr/bin/env python3
"""
Code Explainer Tool - Paste code and get AI explanations
Usage: python code_explainer.py
"""

import os
from anthropic import Anthropic

def create_explainer():
    """Initialize the Anthropic client"""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError(
            "Please set your ANTHROPIC_API_KEY environment variable.\n"
            "Get it from: https://console.anthropic.com/api_keys"
        )
    return Anthropic(api_key=api_key)

def explain_code(client, code: str, language: str = "auto") -> str:
    """
    Send code to Claude and get an explanation

    Args:
        client: Anthropic client
        code: The code to explain
        language: Programming language (auto-detected if "auto")

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

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        system=system_prompt,
        messages=[
            {"role": "user", "content": user_message}
        ]
    )

    return message.content[0].text

def get_multiline_input(prompt: str) -> str:
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

def main():
    """Main interactive loop"""
    print("=" * 60)
    print("🔍 CODE EXPLAINER TOOL")
    print("=" * 60)
    print()

    # Initialize client
    try:
        client = create_explainer()
    except ValueError as e:
        print(f"❌ Error: {e}")
        return

    print("✅ Connected to Claude API!\n")

    while True:
        print("\nOptions:")
        print("1. Explain code from clipboard/input")
        print("2. Exit")
        choice = input("\nChoose (1 or 2): ").strip()

        if choice == "2":
            print("Goodbye! 👋")
            break
        elif choice != "1":
            print("Invalid choice. Please try again.")
            continue

        # Get programming language
        language = input("Programming language (default: auto): ").strip() or "auto"

        # Get code to explain
        code = get_multiline_input("\nPaste your code below:")

        if not code.strip():
            print("❌ No code provided!")
            continue

        print("\n⏳ Analyzing code...")
        print("-" * 60)

        try:
            explanation = explain_code(client, code, language)
            print(explanation)
        except Exception as e:
            print(f"❌ Error: {e}")

        print("-" * 60)
        print("\n✨ Explanation complete!")

if __name__ == "__main__":
    main()