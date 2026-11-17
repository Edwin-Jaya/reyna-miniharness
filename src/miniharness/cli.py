import argparse
from llm import generate_answers

parser = argparse.ArgumentParser(description="Enter Question")
parser.add_argument("question", type=str, help="Question for the bots")

args = parser.parse_args()
ans = generate_answers(args.question)
print(ans)