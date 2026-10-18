"""1. Hafta: terminalden ilk model istegi.

Calistir:  uv run python -m lessons.week01_first_request
"""

from tools.costs import format_cost
from tools.llm import LabError, chat


def main() -> None:
    try:
        result = chat(
            [
                {"role": "system", "content": "Kisa ve net cevap ver."},
                {"role": "user", "content": "Token ve context window arasindaki farki 2 cumlede anlat."},
            ],
            temperature=0.2,
        )
    except LabError as exc:
        print(f"HATA: {exc}")
        return

    print("--- YANIT ---")
    print(result.text)
    print("\n--- KULLANIM ---")
    print(f"model        : {result.model}")
    print(f"input token  : {result.input_tokens}")
    print(f"output token : {result.output_tokens}")
    print(f"toplam token : {result.total_tokens}")
    print(f"gecikme      : {result.latency_ms} ms")
    print(f"tahmini ucret: {format_cost(result.cost_usd)}")
    print("\nLog: logs/usage.jsonl")


if __name__ == "__main__":
    main()
