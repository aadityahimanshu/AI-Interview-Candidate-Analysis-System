from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


def generate_pdf_report(results, filename="candidate_report.pdf"):

    styles = getSampleStyleSheet()

    story = []

    story.append(Paragraph("AI Interview Candidate Report", styles['Title']))
    story.append(Spacer(1,20))

    for key,value in results.items():

        line = f"{key}: {value}"

        story.append(Paragraph(line, styles['Normal']))
        story.append(Spacer(1,10))

    pdf = SimpleDocTemplate(filename)

    pdf.build(story)

    return filename