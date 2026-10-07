import io
from datetime import datetime
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.pdfgen import canvas


class PDFService:
    """
    Renders PDF certificates using ReportLab canvas primitives.
    """

    @staticmethod
    def generate_certificate_pdf(
        certificate_id: str,
        recipient_name: str,
        event_name: str,
        event_date: str,
        certificate_title: str,
    ) -> bytes:
        """
        Generates a formatted landscape PDF certificate and returns raw bytes.
        """
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=landscape(letter))
        width, height = landscape(letter)

        # Outer border
        c.setStrokeColor(colors.HexColor("#1A365D"))  # Dark Blue
        c.setLineWidth(5)
        c.rect(20, 20, width - 40, height - 40)

        # Inner border
        c.setLineWidth(1)
        c.rect(26, 26, width - 52, height - 52)

        # Certificate Title
        c.setFont("Helvetica-Bold", 32)
        c.setFillColor(colors.HexColor("#1A365D"))
        c.drawCentredString(width / 2, height - 100, certificate_title.upper())

        # Presentation Subheading
        c.setFont("Helvetica", 16)
        c.setFillColor(colors.HexColor("#4A5568"))
        c.drawCentredString(width / 2, height - 150, "This is proudly presented to")

        # Recipient Name
        c.setFont("Helvetica-Bold", 28)
        c.setFillColor(colors.HexColor("#2B6CB0"))
        c.drawCentredString(width / 2, height - 210, recipient_name)

        # Decorative line under name
        c.setStrokeColor(colors.HexColor("#CBD5E0"))
        c.setLineWidth(1)
        c.line(width / 2 - 150, height - 225, width / 2 + 150, height - 225)

        # Participation statement
        c.setFont("Helvetica", 15)
        c.setFillColor(colors.HexColor("#2D3748"))
        c.drawCentredString(width / 2, height - 270, f"for participating in {event_name}")

        # Event Date
        c.setFont("Helvetica-Oblique", 14)
        c.setFillColor(colors.HexColor("#718096"))
        c.drawCentredString(width / 2, height - 310, f"Date: {event_date}")

        # Footer details (Certificate ID & Issue Date)
        issue_date_str = datetime.utcnow().strftime("%Y-%m-%d")
        c.setFont("Helvetica", 10)
        c.setFillColor(colors.HexColor("#718096"))
        c.drawString(40, 50, f"Certificate ID: {certificate_id}")
        c.drawRightString(width - 40, 50, f"Issued Date: {issue_date_str}")

        c.showPage()
        c.save()

        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes
