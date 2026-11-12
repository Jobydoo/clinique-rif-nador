import os
import io
import qrcode
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from app.config import Config

def generate_qr_buffer(data_str):
    """Génère une image QR code en mémoire"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=5,
        border=2,
    )
    qr.add_data(data_str)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf

def create_official_header(styles):
    """En-tête officiel de la Clinique Médico-Chirurgicale du Rif - Nador"""
    header_data = [
        [
            Paragraph(f"<b>{Config.CLINIC_NAME}</b><br/><font size=8 color='#059669'><b>ROYAUME DU MAROC - NADOR</b></font><br/><font size=8 color='#4b5563'>{Config.CLINIC_ADDRESS}<br/>Tél: {Config.CLINIC_PHONE} | N° INPE: {Config.CLINIC_INPE}</font>", styles['Normal']),
            Paragraph(f"<para align=right><b>{Config.CLINIC_NAME_AR}</b><br/><font size=8 color='#059669'><b>المملكة المغربية - الناظور</b></font><br/><font size=8 color='#4b5563'>شارع الحسن الثاني، حي المطار، الناظور<br/>الهاتف: {Config.CLINIC_PHONE}</font></para>", styles['Normal'])
        ]
    ]
    t = Table(header_data, colWidths=[10*cm, 8.5*cm])
    t.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    return t

def generate_prescription_pdf(prescription, patient, doctor):
    """Génère l'ordonnance médicale officielle au format PDF avec QR code"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=1.5*cm, leftMargin=1.5*cm, topMargin=1.5*cm, bottomMargin=1.5*cm)
    story = []
    styles = getSampleStyleSheet()

    # Header
    story.append(create_official_header(styles))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#059669'), spaceBefore=8, spaceAfter=15))

    # Doctor & Patient Info Box
    date_str = prescription.date.strftime('%d/%m/%Y') if prescription.date else datetime.utcnow().strftime('%d/%m/%Y')
    info_data = [
        [
            Paragraph(f"<b>Praticien :</b> {doctor.name}<br/><b>Spécialité :</b> {doctor.specialty or 'Médecine Générale'}", styles['Normal']),
            Paragraph(f"<para align=right><b>Nador, le :</b> {date_str}</para>", styles['Normal'])
        ],
        [
            Paragraph(f"<b>Patient(e) :</b> {patient.first_name_fr} {patient.last_name_fr}<br/><b>CIN :</b> {patient.cin} | <b>Âge :</b> {patient.birth_date} | <b>Poids :</b> {patient.vital_signs[0].weight if patient.vital_signs else '--'} kg", styles['Normal']),
            Paragraph(f"<para align=right><b>N° Dossier :</b> {patient.patient_number}<br/><b>Mutuelle :</b> {patient.mutuelle_type}</para>", styles['Normal'])
        ]
    ]
    t_info = Table(info_data, colWidths=[11*cm, 7.5*cm])
    t_info.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_info)
    story.append(Spacer(1, 15))

    # Title
    title_style = ParagraphStyle(
        'PrescriptionTitle',
        parent=styles['Heading2'],
        alignment=1, # Center
        textColor=colors.HexColor('#065F46'),
        spaceAfter=15
    )
    story.append(Paragraph("ORDONNANCE MÉDICALE / وصفة طبية", title_style))

    # Medications Items
    meds_data = [["Médicament / Posologie & Durée", "Précautions"]]
    for item in prescription.items:
        med_desc = f"<b>• {item.medication_name}</b><br/><font color='#374151'>&nbsp;&nbsp;&nbsp;&nbsp;Posologie : {item.dosage} - {item.frequency}<br/>&nbsp;&nbsp;&nbsp;&nbsp;Durée du traitement : {item.duration}</font>"
        precautions = item.precautions or "Respecter les doses prescrites."
        if not item.allow_substitution:
            precautions += "<br/><font color='#dc2626'><b>[Non substituable]</b></font>"
        meds_data.append([Paragraph(med_desc, styles['Normal']), Paragraph(precautions, styles['Normal'])])

    t_meds = Table(meds_data, colWidths=[12.5*cm, 6*cm])
    t_meds.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#ECFDF5')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#065F46')),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_meds)
    story.append(Spacer(1, 20))

    if prescription.instructions:
        story.append(Paragraph(f"<b>Recommandations particulières :</b><br/>{prescription.instructions}", styles['Normal']))
        story.append(Spacer(1, 15))

    # QR Code & Stamp / Signature section
    qr_payload = f"CLINIQUE_DU_RIF_NADOR|PRESCRIPTION:{prescription.id}|PATIENT:{patient.cin}|DATE:{date_str}|DOCTOR:{doctor.name}"
    qr_buf = generate_qr_buffer(qr_payload)
    qr_img = Image(qr_buf, width=2.8*cm, height=2.8*cm)

    bottom_data = [
        [
            qr_img,
            Paragraph(f"<font size=8 color='#64748b'>Vérification d'authenticité électronique<br/>Clinique Médico-Chirurgicale du Rif - Nador<br/>Conformité CNDP & Ordre National des Médecins</font>", styles['Normal']),
            Paragraph(f"<para align=center><b>Cachet et Signature du Médecin :</b><br/><br/><font color='#065f46'><b>Dr. {doctor.name}</b></font><br/><font size=8>{doctor.specialty or ''}</font></para>", styles['Normal'])
        ]
    ]
    t_bottom = Table(bottom_data, colWidths=[3.2*cm, 7.5*cm, 7.8*cm])
    t_bottom.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOX', (2,0), (2,0), 1, colors.HexColor('#CBD5E1')),
        ('BACKGROUND', (2,0), (2,0), colors.HexColor('#FAFAFA')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(Spacer(1, 20))
    story.append(t_bottom)

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def generate_invoice_pdf(invoice, patient):
    """Génère la facture officielle avec calcul Tiers-Payant / Mutuelle Marocaine"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=1.5*cm, leftMargin=1.5*cm, topMargin=1.5*cm, bottomMargin=1.5*cm)
    story = []
    styles = getSampleStyleSheet()

    # Header
    story.append(create_official_header(styles))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0284c7'), spaceBefore=8, spaceAfter=15))

    # Invoice Metadata & Patient Box
    date_str = invoice.date.strftime('%d/%m/%Y %H:%M') if invoice.date else datetime.utcnow().strftime('%d/%m/%Y')
    info_data = [
        [
            Paragraph(f"<b>FACTURE OFFICIELLE N° :</b> <font color='#0284c7'><b>{invoice.invoice_number}</b></font><br/><b>Date d'émission :</b> {date_str}<br/><b>Mode de règlement :</b> {invoice.payment_method}", styles['Normal']),
            Paragraph(f"<para align=right><b>Patient :</b> {patient.first_name_fr} {patient.last_name_fr}<br/><b>CIN :</b> {patient.cin} | <b>N° Dossier :</b> {patient.patient_number}<br/><b>Organisme de prise en charge :</b> <b>{invoice.mutuelle_type}</b> ({patient.mutuelle_rate}%)<br/><b>N° Immatriculation Mutuelle :</b> {patient.mutuelle_number or 'N/A'}</para>", styles['Normal'])
        ]
    ]
    t_info = Table(info_data, colWidths=[9.5*cm, 9*cm])
    t_info.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F0F9FF')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#BAE6FD')),
        ('PADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_info)
    story.append(Spacer(1, 15))

    # Acts table
    table_data = [["Code NGAP", "Désignation de l'acte médical", "Qté", "P.U (MAD)", "Total (MAD)"]]
    for item in invoice.items:
        table_data.append([
            item.act_code,
            Paragraph(item.description, styles['Normal']),
            str(item.quantity),
            f"{item.unit_price:.2f}",
            f"{item.total:.2f}"
        ])

    t_acts = Table(table_data, colWidths=[2.5*cm, 9*cm, 1.5*cm, 2.5*cm, 3*cm])
    t_acts.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0284C7')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('ALIGN', (2,0), (-1,-1), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_acts)
    story.append(Spacer(1, 15))

    # Financial Summary (Total, Mutuelle Share, Patient Copay)
    summary_data = [
        ["Total Général des Prestations (TTC) :", f"{invoice.total_amount:.2f} MAD"],
        [f"Part Prise en Charge Mutuelle / Tiers-Payant ({invoice.mutuelle_type}) :", f"- {invoice.mutuelle_amount:.2f} MAD"],
        ["Part Patient / Ticket Modérateur à régler :", f"{invoice.patient_share:.2f} MAD"],
        ["Statut du Paiement :", f"{invoice.status}"]
    ]
    t_summary = Table(summary_data, colWidths=[12.5*cm, 6*cm])
    t_summary.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('FONTNAME', (0,2), (-1,2), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0,2), (-1,2), colors.HexColor('#059669')),
        ('FONTSIZE', (0,2), (-1,2), 11),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_summary)
    story.append(Spacer(1, 20))

    # QR Code & Legal footer
    qr_payload = f"CLINIQUE_DU_RIF_NADOR|INVOICE:{invoice.invoice_number}|PATIENT:{patient.cin}|TOTAL:{invoice.total_amount}|DATE:{date_str}"
    qr_buf = generate_qr_buffer(qr_payload)
    qr_img = Image(qr_buf, width=2.5*cm, height=2.5*cm)

    bottom_data = [
        [
            qr_img,
            Paragraph(f"<font size=8 color='#64748b'>Facture certifiée conforme pour déclaration CNSS / CNOPS / Assurances privées.<br/>ICE: {Config.CLINIC_ICE} | Patente: {Config.CLINIC_PATENTE}<br/>Clinique Médico-Chirurgicale du Rif - Nador</font>", styles['Normal']),
            Paragraph(f"<para align=center><b>Visa Caisse & Comptabilité :</b><br/><br/><font size=8 color='#0284c7'><b>ACQUITTÉ</b></font></para>", styles['Normal'])
        ]
    ]
    t_bottom = Table(bottom_data, colWidths=[3*cm, 10.5*cm, 5*cm])
    t_bottom.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOX', (2,0), (2,0), 1, colors.HexColor('#CBD5E1')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_bottom)

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def generate_medical_certificate_pdf(patient, doctor, certificate_type, days_rest, notes):
    """Génère un certificat médical officiel (repos, aptitude)"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    story = []
    styles = getSampleStyleSheet()

    story.append(create_official_header(styles))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#059669'), spaceBefore=8, spaceAfter=25))

    title_style = ParagraphStyle(
        'CertTitle',
        parent=styles['Heading1'],
        alignment=1,
        textColor=colors.HexColor('#065F46'),
        spaceAfter=25
    )
    story.append(Paragraph("CERTIFICAT MÉDICAL / شهادة طبية", title_style))

    body_text = f"""
    Je soussigné, <b>Dr. {doctor.name}</b>, médecin spécialiste en {doctor.specialty or 'Médecine Générale'} à la {Config.CLINIC_NAME} à Nador,
    certifie après avoir examiné ce jour :<br/><br/>
    M./Mme : <b>{patient.first_name_fr} {patient.last_name_fr}</b><br/>
    Titulaire de la CIN N° : <b>{patient.cin}</b><br/>
    Né(e) le : <b>{patient.birth_date}</b><br/>
    Demeurant à : <b>{patient.neighborhood}, Nador</b><br/><br/>
    Que son état de santé actuel nécessite un <b>repos médical de {days_rest} jour(s)</b>, sauf complications ultérieures.<br/><br/>
    <b>Observations cliniques :</b> {notes or 'Repos au domicile avec traitement prescrit.'}<br/><br/>
    <i>Certificat délivré à l'intéressé(e) en mains propres pour servir et valoir ce que de droit.</i>
    """
    story.append(Paragraph(body_text, styles['Normal']))
    story.append(Spacer(1, 40))

    date_str = datetime.utcnow().strftime('%d/%m/%Y')
    sign_data = [
        [
            Paragraph(f"Fait à Nador, le {date_str}", styles['Normal']),
            Paragraph(f"<para align=right><b>Signature et Cachet du Médecin :</b><br/><br/><br/><b>Dr. {doctor.name}</b></para>", styles['Normal'])
        ]
    ]
    t_sign = Table(sign_data, colWidths=[9*cm, 8*cm])
    story.append(t_sign)

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
