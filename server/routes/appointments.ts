import { Router, Response } from 'express';
import prisma from '../prisma.js';
import { AuthenticatedRequest, authenticateToken } from '../middleware/auth.js';
import { recordAuditLog } from '../middleware/audit.js';

const router = Router();

// Liste des rendez-vous
router.get('/', authenticateToken, async (req: AuthenticatedRequest, res: Response) => {
  try {
    const { date, doctorId, specialty, status } = req.query;

    const whereClause: any = {};
    if (doctorId && doctorId !== 'ALL') whereClause.doctorId = doctorId;
    if (specialty && specialty !== 'ALL') whereClause.specialty = specialty;
    if (status && status !== 'ALL') whereClause.status = status;

    if (date && typeof date === 'string') {
      const searchDate = new Date(date);
      const startOfDay = new Date(searchDate.setHours(0, 0, 0, 0));
      const endOfDay = new Date(searchDate.setHours(23, 59, 59, 999));
      whereClause.date = {
        gte: startOfDay,
        lte: endOfDay,
      };
    }

    const appointments = await prisma.appointment.findMany({
      where: whereClause,
      include: {
        patient: {
          select: {
            id: true,
            cin: true,
            firstNameFr: true,
            lastNameFr: true,
            firstNameAr: true,
            lastNameAr: true,
            phone: true,
            mutuelleType: true,
            neighborhood: true,
          },
        },
      },
      orderBy: [{ date: 'asc' }, { timeSlot: 'asc' }],
    });

    res.json(appointments);
  } catch (error) {
    res.status(500).json({ error: 'Erreur récupération rendez-vous' });
  }
});

// Création d'un rendez-vous
router.post('/', authenticateToken, async (req: AuthenticatedRequest, res: Response) => {
  try {
    const { patientId, doctorId, doctorName, specialty, date, timeSlot, reason, notes } = req.body;

    if (!patientId || !doctorId || !date || !timeSlot) {
      return res.status(400).json({ error: 'Patient, Médecin, Date et Créneau horaire sont obligatoires' });
    }

    const newAppointment = await prisma.appointment.create({
      data: {
        patientId,
        doctorId,
        doctorName: doctorName || 'Praticien Spécialiste',
        specialty: specialty || 'Médecine Générale',
        date: new Date(date),
        timeSlot,
        reason: reason || 'Consultation de suivi',
        notes: notes || null,
        status: 'SCHEDULED',
      },
      include: { patient: true },
    });

    await recordAuditLog({
      userId: req.user?.id,
      userName: req.user?.name || 'Inconnu',
      userRole: req.user?.role || 'USER',
      action: 'CREATE',
      entityType: 'PATIENT',
      entityId: patientId,
      details: `Prise de RDV le ${timeSlot} avec ${doctorName} pour ${newAppointment.patient.firstNameFr} ${newAppointment.patient.lastNameFr}`,
      ipAddress: req.ip,
    });

    res.status(201).json(newAppointment);
  } catch (error: any) {
    res.status(500).json({ error: error.message || 'Erreur création RDV' });
  }
});

// Mise à jour statut RDV
router.put('/:id/status', authenticateToken, async (req: AuthenticatedRequest, res: Response) => {
  try {
    const { status } = req.body;
    const appointment = await prisma.appointment.update({
      where: { id: req.params.id },
      data: { status },
      include: { patient: true },
    });

    res.json(appointment);
  } catch (error) {
    res.status(500).json({ error: 'Erreur mise à jour statut RDV' });
  }
});

// Générateur du lien de rappel WhatsApp (1-Clic)
router.get('/:id/whatsapp', authenticateToken, async (req: AuthenticatedRequest, res: Response) => {
  try {
    const appointment = await prisma.appointment.findUnique({
      where: { id: req.params.id },
      include: { patient: true },
    });

    if (!appointment) {
      return res.status(404).json({ error: 'Rendez-vous introuvable' });
    }

    // Formater le numéro de téléphone marocain (+212)
    let phone = appointment.patient.phone.replace(/[^0-9]/g, '');
    if (phone.startsWith('0')) {
      phone = '212' + phone.substring(1);
    } else if (!phone.startsWith('212')) {
      phone = '212' + phone;
    }

    const dateFormatted = new Date(appointment.date).toLocaleDateString('fr-FR', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });

    const clinicName = process.env.CLINIC_NAME || 'Clinique Médico-Chirurgicale du Rif - Nador';
    const message = `Bonjour M./Mme *${appointment.patient.lastNameFr}*,\n\nNous vous rappelons votre rendez-vous médical à la *${clinicName}* (Nador):\n\n📅 Date: *${dateFormatted}*\n⏰ Heure: *${appointment.timeSlot}*\n👨‍⚕️ Médecin: *${appointment.doctorName}* (${appointment.specialty})\n📍 Adresse: Boulevard Hassan II, Hay Al Matar, Nador.\n\nEn cas d'empêchement, merci de nous contacter au +212 536 60 44 20.\n\nتذكير بموعدكم الطبي بمصحة الريف - الناظور. نتمنى لكم دوام الصحة والعافية.`;

    const encodedMessage = encodeURIComponent(message);
    const whatsappUrl = `https://wa.me/${phone}?text=${encodedMessage}`;

    // Mettre à jour l'indicateur d'envoi
    await prisma.appointment.update({
      where: { id: appointment.id },
      data: { whatsappSent: true },
    });

    res.json({
      phone,
      message,
      whatsappUrl,
    });
  } catch (error) {
    res.status(500).json({ error: 'Erreur génération rappel WhatsApp' });
  }
});

export default router;
