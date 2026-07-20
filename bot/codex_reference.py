import os
import re

CODEX_PATH = "/home/karun777/futuresky/docs/developer_codex_v2.0_full.md"

# Parse the Codex into a dictionary of sections
def load_codex():
    if not os.path.exists(CODEX_PATH):
        return {}
    with open(CODEX_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    sections = {}
    # Match headings like "## 5. Title", "## 5 Title", "### 4.1 Something"
    matches = re.finditer(r"^#{2,3}\s*(\d+(\.\d+)*)(?:\s*\.\s*)?\s*(.+)", content, re.MULTILINE)

    positions = [(m.start(), m.group(1), m.group(3).strip()) for m in matches]

    for i, (pos, sec_num, sec_title) in enumerate(positions):
        # Clean title (remove stray leading/trailing spaces or dots)
        clean_title = sec_title.lstrip(". ").strip()
        start = pos
        end = positions[i+1][0] if i+1 < len(positions) else len(content)
        section_text = content[start:end].strip()
        sections[sec_num] = {
            "title": clean_title,
            "text": section_text
        }
    return sections


CODEX_SECTIONS = load_codex()

def get_codex_section(section_number):
    """Return full section text by number."""
    return CODEX_SECTIONS.get(section_number, {}).get("text", "Section not found.")

def get_codex_index():
    """Return a list of available sections."""
    return [
        f"{num} — {data['title']}"
        for num, data in CODEX_SECTIONS.items()
    ]

def get_codex_tasks(section_number):
    """Return bullet points from a section that look like tasks."""
    section_text = get_codex_section(section_number)
    if section_text == "Section not found.":
        return section_text
    tasks = re.findall(r"^[\-\*]\s+.+", section_text, re.MULTILINE)
    return tasks if tasks else ["No explicit tasks found."]
