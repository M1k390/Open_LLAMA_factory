# SYSTEM GOAL
Build a simple Python system that generates a book using an LLM.

Flow:
topic → pages → content → PDF

---

# REQUIREMENTS

## 1. LLM usage
- Use the LLM only to:
  - generate page structure
  - generate page content

## 2. Cache
- Use a simple in-memory cache (dict or TinyDB)
- Store:
  - topic
  - pages
  - generated content

## 3. Steps

Step 1:
Generate a list of pages from a topic

Output:
{
  "pages": ["page 1", "page 2", ...]
}

Step 2:
For each page:
Generate content using the LLM

Step 3:
Combine all pages into a PDF

---

# DESIGN RULES

- Keep architecture simple
- No complex task system
- No file-based intermediate storage
- The system must be deterministic
- Each step must be clear and isolated

---

# FINAL OUTPUT

- A working Python script
- Generates a full book from a topic
- Outputs a PDF
