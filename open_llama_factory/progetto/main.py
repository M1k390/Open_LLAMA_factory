import requests
import json
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

LLM_URL = "http://192.168.1.176:5001/v1/chat/completions"


# -------------------------
# LLM CLIENT
# -------------------------
def chiedi_a_llama(prompt: str) -> str:
    try:
        response = requests.post(
            LLM_URL,
            json={
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2
            }
        )
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"LLM error: {e}")
        return ""


# -------------------------
# UTILS
# -------------------------
def safe_json_parse(text: str):
    try:
        return json.loads(text)
    except:
        try:
            return json.loads(json.loads(text))
        except:
            return {"pages": []}


def ask_with_retry(prompt: str, retries=3):
    for _ in range(retries):
        output = chiedi_a_llama(prompt)
        if output:
            return output
    return ""


def pulisci_testo(text: str) -> str:
    return text.strip()


# -------------------------
# GENERATE STRUCTURE
# -------------------------
def generate_pages(topic: str) -> list:
    prompt = f"""
Generate a list of 5 book page titles about: {topic}

Return ONLY JSON:
{{ "pages": ["...", "..."] }}
"""

    output = ask_with_retry(prompt)
    data = safe_json_parse(output)

    return data.get("pages", [])


# -------------------------
# GENERATE CONTENT
# -------------------------
def generate_page_content(page: str, topic: str) -> str:
    prompt = f"""
Write a detailed book page.

Topic: {topic}
Page title: {page}

Write clear and structured content.
"""

    output = ask_with_retry(prompt)
    return pulisci_testo(output)


# -------------------------
# PDF GENERATION
# -------------------------
def combine_pages_into_pdf(pages: list, file_name="book.pdf"):
    doc = SimpleDocTemplate(file_name)
    styles = getSampleStyleSheet()

    elements = []

    for page in pages:
        elements.append(Paragraph(f"<b>{page['title']}</b>", styles["Heading2"]))
        elements.append(Spacer(1, 10))
        elements.append(Paragraph(page["content"], styles["Normal"]))
        elements.append(Spacer(1, 20))

    doc.build(elements)


# -------------------------
# ORCHESTRATOR
# -------------------------
class BookGenerator:

    def __init__(self):
        self.db = TinyDB(storage=MemoryStorage)
        self.cache = self.db.table("books")

    def run(self, topic: str):
        print(f"📘 Topic: {topic}")

        entry = self.cache.get(Query().topic == topic)

        if entry:
            print("📦 Loaded from cache")
            pages = entry["pages"]
        else:
            print("⚙️ Generating structure...")
            titles = generate_pages(topic)

            pages = []
            for title in titles:
                pages.append({
                    "title": title,
                    "content": None,
                    "status": "pending"
                })

            self.cache.insert({
                "topic": topic,
                "pages": pages
            })

        # GENERATE CONTENT (step-by-step)
        for page in pages:
            if page["status"] == "done":
                continue

            print(f"✍️ Generating: {page['title']}")

            content = generate_page_content(page["title"], topic)

            if content:
                page["content"] = content
                page["status"] = "done"
            else:
                page["status"] = "failed"

        # aggiorna cache
        self.cache.update({"pages": pages}, Query().topic == topic)

        # PDF finale
        print("📄 Building PDF...")
        completed_pages = [p for p in pages if p["status"] == "done"]

        combine_pages_into_pdf(completed_pages)

        print("✅ Book generated: book.pdf")


# -------------------------
# ENTRY POINT
# -------------------------
if __name__ == "__main__":
    generator = BookGenerator()
    generator.run("The Art of Python")
