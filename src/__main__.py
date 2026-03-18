"""CLI for sparktest."""
import sys, json, argparse
from .core import Sparktest

def main():
    parser = argparse.ArgumentParser(description="SparkTest — AI Creativity Tester. Benchmark for measuring AI creative capabilities across domains.")
    parser.add_argument("command", nargs="?", default="status", choices=["status", "run", "info"])
    parser.add_argument("--input", "-i", default="")
    args = parser.parse_args()
    instance = Sparktest()
    if args.command == "status":
        print(json.dumps(instance.get_stats(), indent=2))
    elif args.command == "run":
        print(json.dumps(instance.process(input=args.input or "test"), indent=2, default=str))
    elif args.command == "info":
        print(f"sparktest v0.1.0 — SparkTest — AI Creativity Tester. Benchmark for measuring AI creative capabilities across domains.")

if __name__ == "__main__":
    main()
