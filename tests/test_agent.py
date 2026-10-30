
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

load_dotenv(BASE_DIR / ".env")


def test_datasets():
    from tools.data_query import (
        get_energy_summary,
        get_traffic_summary
    )

    energy = get_energy_summary()
    traffic = get_traffic_summary()

    assert energy["valid_readings"] == 8760
    assert traffic["total_records"] == 48204

    print("PASS: Energy dataset - 8760 readings")
    print("PASS: Traffic dataset - 48204 records")


def test_calculator():
    from tools.calculator import (
        calculate_statistics,
        percentage_change
    )

    result = calculate_statistics([10, 20, 30, 40, 50])
    assert result["average"] == 30

    change = percentage_change(100, 80)
    assert change["percentage_change"] == -20

    print("PASS: Calculator")
    print("PASS: Percentage change")


def test_ai_agent():
    from groq import Groq

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        print("SKIP: Groq API key not configured")
        return

    client = Groq(api_key=api_key)

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are NUNVIZHI, an AI-powered "
                    "campus energy and traffic assistant."
                )
            },
            {
                "role": "user",
                "content": (
                    "Explain in two short sentences how "
                    "AI can support campus energy management."
                )
            }
        ],
        max_tokens=150
    )

    answer = response.choices[0].message.content

    assert answer, "AI returned an empty response"

    print("PASS: Groq AI Agent")
    print(answer.encode("ascii", errors="replace").decode())


def main():
    print("=" * 45)
    print("NUNVIZHI - AI AGENT TEST")
    print("=" * 45)

    test_calculator()
    test_datasets()
    test_ai_agent()

    print("\nAll executed tests passed!")


if __name__ == "__main__":
    main()
