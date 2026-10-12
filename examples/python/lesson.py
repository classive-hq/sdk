"""Quote-only by default; --submit explicitly starts paid generation."""
import os
import sys
from classive import Classive
from classive.types import CreateLesson

def run_lesson(client: Classive, submit: bool = False):
    input: CreateLesson = {"type": "lesson", "prompt": "Teach adding fractions with unlike denominators.",
                           "audience": {"band": "primary", "grade": "Year 5"}, "outputs": ["notes", "quiz"]}
    quote = client.jobs.quote(input)
    print("Quoted credits:", quote["credits"])
    if not submit: return quote
    job = client.jobs.create({**input, "quoteId": quote["id"]}, options={"idempotency_key": f"fractions-{quote['id']}"})
    completed = client.jobs.wait(job["id"])
    print("Delivered job:", completed["id"])
    return completed

if __name__ == "__main__":
    with Classive(base_url=os.getenv("CLASSIVE_BASE_URL", "https://api.classive.app")) as client:
        run_lesson(client, "--submit" in sys.argv)
