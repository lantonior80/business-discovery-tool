"""Build handout/Business_Discovery_Start_Here.pdf: the beginner start steps plus a tap-to-select box
holding the one-line setup command.

Needs reportlab and pymupdf (not used by the tool itself):
  pip install reportlab pymupdf
  python tools/build_start_pdf.py
"""
from pathlib import Path

import pymupdf
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Flowable, Paragraph, SimpleDocTemplate, Spacer

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "handout" / "Business_Discovery_Start_Here.pdf"
COMMAND = ("Set me up with the Business Discovery Tool by following this guide step by step: "
           "https://raw.githubusercontent.com/lantonior80/business-discovery-tool/main/SETUP.md")
FIELD = "setup_command"
INK, MUTED, ACCENT, PALE = colors.HexColor("#1F2328"), colors.HexColor("#57606A"), colors.HexColor("#0B5CAD"), colors.HexColor("#EEF5FC")

FONTS = Path("C:/Windows/Fonts")
pdfmetrics.registerFont(TTFont("Body", str(FONTS / "segoeui.ttf")))
pdfmetrics.registerFont(TTFont("Body-Bold", str(FONTS / "segoeuib.ttf")))
pdfmetrics.registerFont(TTFont("Sym", str(FONTS / "seguisym.ttf")))
pdfmetrics.registerFontFamily("Body", normal="Body", bold="Body-Bold", italic="Body", boldItalic="Body-Bold")

title = ParagraphStyle("t", fontName="Body-Bold", fontSize=24, leading=29, textColor=INK)
sub = ParagraphStyle("s", fontName="Body", fontSize=12, leading=16, textColor=MUTED, spaceAfter=8)
h = ParagraphStyle("h", fontName="Body-Bold", fontSize=14.5, leading=19, textColor=ACCENT, spaceBefore=11, spaceAfter=3)
body = ParagraphStyle("b", fontName="Body", fontSize=12, leading=16.5, textColor=INK, leftIndent=18, firstLineIndent=-14, spaceAfter=2.5)
plain = ParagraphStyle("p", parent=body, leftIndent=0, firstLineIndent=0)
small = ParagraphStyle("sm", fontName="Body", fontSize=10.5, leading=14, textColor=MUTED, alignment=TA_CENTER)


class CommandBox(Flowable):
    """Shaded panel; records where the tap-to-select field goes (added afterwards with PyMuPDF)."""
    def __init__(self, width, height=58):
        super().__init__()
        self.width, self.height, self.rect = width, height, None

    def draw(self):
        c = self.canv
        c.setFillColor(PALE); c.setStrokeColor(ACCENT); c.setLineWidth(1.6)
        c.roundRect(0, 0, self.width, self.height, 8, stroke=1, fill=1)
        x, y = c.absolutePosition(0, 0)
        self.rect = (x, y, self.width, self.height)


def steps(items):
    return [Paragraph(f"<b>{i}.</b>&nbsp; {t}", body) for i, t in enumerate(items, 1)]


def build():
    OUT.parent.mkdir(exist_ok=True)
    tmp = OUT.with_suffix(".tmp.pdf")
    doc = SimpleDocTemplate(str(tmp), pagesize=letter, leftMargin=0.8 * inch, rightMargin=0.8 * inch,
                            topMargin=0.6 * inch, bottomMargin=0.5 * inch,
                            title="Business Discovery Tool — Start Here", author="Business Discovery Tool")
    box = CommandBox(doc.width)
    sym = '<font name="Sym">\u2630</font>'
    story = [
        Paragraph("Business Discovery Tool", title),
        Paragraph("Start here. It takes about 2 minutes on a phone or a computer.", sub),

        Paragraph("Step 1 — Open ChatGPT", h),
        Paragraph("Open the <b>ChatGPT app</b> or go to <b>chatgpt.com</b>. Sign in, or <b>sign up</b> (it's free) "
                  "if you don't have an account yet.", plain),

        Paragraph("Step 2 — Make a new Project", h),
        *steps([f"Tap the <b>three-line menu ({sym})</b> on the left to open the side menu.",
                "Find <b>Projects</b> and tap <b>+</b> next to it to create a new project.",
                "Type the name: <b>Business Discovery</b>",
                "Tap <b>Create project</b>."]),

        Paragraph("Step 3 — Switch to Work mode", h),
        *steps(["You're now on the Project's page, with its name at the top.",
                "Tap the word <b>Chat</b> under the Project's name and choose <b>Work</b> (not Chat)."]),

        Paragraph("Step 4 — Start the setup", h),
        *steps(["There's <b>no \u201cNew chat\u201d button</b> here. Just tap the <b>message box</b> at the bottom of this page.",
                "<b>Copy the sentence in the blue box below:</b> tap inside the box, press and hold, tap "
                "<b>Select all</b>, then tap <b>Copy</b>.",
                "Go back to ChatGPT. Press and hold in the message box, tap <b>Paste</b>, then tap the "
                "<b>send arrow</b>."]),
        Spacer(1, 7), box, Spacer(1, 4),
        Paragraph("Tip: if the box doesn't highlight, press and hold on the words and drag to select all of them.", small),

        Paragraph("What happens next", h),
        Paragraph("ChatGPT asks how you'd like to set it up:", plain),
        Paragraph("<b>A. Manual:</b> you download 5 files and upload them into the Project. ChatGPT tells you exactly what to tap.", body),
        Paragraph("<b>B. Automated:</b> ChatGPT does the files for you. You only sign in to ChatGPT in the browser window it "
                  "opens, with your email, password and a verification code (it can text one to your phone).", body),
        Spacer(1, 3),
        Paragraph("Either way, do what it says, one step at a time, and type <b>done</b> after each step.", plain),
    ]
    doc.build(story)

    pdf = pymupdf.open(str(tmp))
    page = pdf[0]
    x, y, w, hgt = box.rect
    top = page.rect.height - (y + hgt)          # reportlab measures from the bottom, PyMuPDF from the top
    pad = 8
    wd = pymupdf.Widget()
    wd.field_type = pymupdf.PDF_WIDGET_TYPE_TEXT
    wd.field_name = FIELD
    wd.field_label = "Setup sentence to copy"
    wd.field_value = COMMAND
    wd.field_flags = pymupdf.PDF_TX_FIELD_IS_MULTILINE
    wd.rect = pymupdf.Rect(x + pad, top + pad, x + w - pad, top + hgt - pad)
    wd.text_font, wd.text_fontsize = "Helv", 10.5   # small enough for the whole link to fit on one line
    wd.text_color, wd.border_width = (0.12, 0.14, 0.16), 0
    wd.fill_color = (0.933, 0.961, 0.988)
    # Acrobat: select the whole sentence when the box is tapped/clicked, and ignore typing so it can't be changed.
    wd.script_focus = "event.target.setFocus(); event.selStart = 0; event.selEnd = -1;"
    wd.script_stroke = "if (!event.willCommit) event.rc = false;"
    widget = page.add_widget(wd)
    # PyMuPDF stores the actions on the parent field; the focus trigger belongs on the widget itself.
    parent = int(pdf.xref_get_key(widget.xref, "Parent")[1].split()[0])
    fo = pdf.xref_get_key(parent, "AA/Fo")[1]
    pdf.xref_set_key(widget.xref, "AA", f"<</Fo {fo}>>")
    pdf.save(str(OUT), garbage=3, deflate=True)
    pdf.close()
    tmp.unlink()
    print(OUT)


if __name__ == "__main__":
    build()
