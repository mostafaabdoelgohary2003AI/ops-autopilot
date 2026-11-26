"""Publisher agent: export a report run to a real .docx document."""
from docx import Document
from docx.shared import RGBColor

TEAL = RGBColor(0x00, 0x60, 0x70)

def export_docx(result, path):
    doc = Document()
    h = doc.add_heading(f"Ops Autopilot Report: {result['topic']}", level=0)
    m = result["metrics"]
    doc.add_paragraph(
        f"{m['sources_found']}/{m['questions']} research questions answered from live Wikipedia sources. "
        f"Critic pass rate first try: {m['sections_passed_critic_first_try']}/{m['questions']}. "
        f"Generated in {m['run_seconds']}s by the planner/researcher/writer/critic pipeline.")
    for sec in result["sections"]:
        if not sec.get("draft"):
            continue
        doc.add_heading(sec["facet"], level=1)
        doc.add_paragraph(sec["draft"])
        if sec.get("url"):
            doc.add_paragraph(f"Source: {sec['url']}", style="Intense Quote")
    doc.add_heading("Pipeline metrics", level=1)
    for k, v in m.items():
        doc.add_paragraph(f"{k}: {v}", style="List Bullet")
    doc.save(path)
    return path
