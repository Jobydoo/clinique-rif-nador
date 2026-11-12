import { Router, Response } from 'express';
import prisma from '../prisma.js';
import { AuthenticatedRequest, authenticateToken } from '../middleware/auth.js';
import { recordAuditLog } from '../middleware/audit.js';

const router = Router();

// Génération du numéro patient unique (Format: CNR-2026-XXXX)
async function generatePatientNumber(): Promise<string> {
  const count = await prisma.patient.count();
  const year = new Date().getFullYear();
  const sequence = String(count + 1).padStart(4, '0');
  return `CNR-${year}-${sequence}`;
}

// Liste des patients (avec recherche multi-critères)
router.get('/', authenticateToken, async (req: AuthenticatedRequest, res: Response) => {
  try {
    const { search, mutuelle, neighborhood, includeArchived } = req.query;

    const whereClause: any = {
      isArchived: includeArchived === 'true' ? undefined : false,
    };

    if (mutuelle && typeof mutuelle === 'string' && mutuelle !== 'ALL') {
      whereClause.mutuelleType = mutuelle;
    }

    if (neighborhood && typeof neighborhood === 'string' && neighborhood !== 'ALL') {
      whereClause.neighborhood = neighborhood;
    }

    if (search && typeof search === 'string') {
      const q = search.trim();
      whereClause.OR = [
        { cin: { contains: q } },
        { firstNameFr: { contains: q } },
        { lastNameFr: { contains: q } },
        { firstNameAr: { contains: q } },
        { lastNameAr: { contains: q } },
        { phone: { contains: q } },
        { patientNumber: { contains: q } },
      ];
    }

    const patients = await prisma.patient.findMany({
      where: whereClause,
      orderBy: { createdAt: 'desc' },
      include: {
        vitalSigns: {
          take: 1,
          orderBy: { createdAt: 'desc' },
        },
        waitingQueue: {
          where: { status: { not: 'COMPLETED' } },
          take: 1,
        },
      },
    });

    res.json(patients);
  } catch (error: any) {
    console.error('Erreur liste patients:', error);
    res.status(500).json({ error: 'Erreur lors de la récupération des patients' });
  }
});

// Fiche patient complète (DME)
router.get('/:id', authenticateToken, async (req: AuthenticatedRequest, res: Response) => {
  try {
    const patient = await prisma.patient.findUnique({
      where: { id: req.params.id },
      include: {
        vitalSigns: { orderBy: { createdAt: 'desc' } },
        consultations: {
          orderBy: { date: 'desc' },
          include: {
            doctor: { select: { id: true, name: true, specialty: true } },
            prescriptions: { include: { items: true } },
          },
        },
        admissions: {
          orderBy: { admissionDate: 'desc' },
          include: {
            bed: { include: { room: true } },
            doctor: { select: { id: true, name: true, specialty: true } },
          },
        },
        invoices: {
          orderBy: { date: 'desc' },
          include: { items: true, payments: true },
        },
        documents: {
          orderBy: { createdAt: 'desc' },
        },
        appointments: {
          orderBy: { date: 'desc' },
        },
        waitingQueue: {
          orderBy: { arrivalTime: 'desc' },
          take: 5,
        },
      },
    });

    if (!patient) {
      return res.status(404).json({ error: 'Patient introuvable' });
    }

    // Enregistrement d'audit CNDP
    await recordAuditLog({
      userId: req.user?.id,
      userName: req.user?.name || 'Inconnu',
      userRole: req.user?.role || 'USER',
      action: 'VIEW',
      entityType: 'PATIENT',
      entityId: patient.id,
      details: `Consultation dossier médical du patient ${patient.firstNameFr} ${patient.lastNameFr} (CIN: ${patient.cin})`,
      ipAddress: req.ip,
    });

    res.json(patient);
  } catch (error) {
    res.status(500).json({ error: 'Erreur récupération dossier patient' });
  }
});

// Inscription d'un nouveau patient
router.post('/', authenticateToken, async (req: AuthenticatedRequest, res: Response) => {
  try {
    const data = req.body;

    if (!data.cin || !data.firstNameFr || !data.lastNameFr || !data.phone) {
      return res.status(400).json({ error: 'CIN, Nom, Prénom et Téléphone sont obligatoires' });
    }

    // Vérification unicité CIN
    const existing = await prisma.patient.findUnique({
      where: { cin: data.cin.trim().toUpperCase() },
    });

    if (existing) {
      return res.status(400).json({ error: `Un patient existe déjà avec la CIN ${data.cin.trim().toUpperCase()}` });
    }

    const patientNumber = await generatePatientNumber();

    const newPatient = await prisma.patient.create({
      data: {
        patientNumber,
        cin: data.cin.trim().toUpperCase(),
        firstNameFr: data.firstNameFr.trim(),
        lastNameFr: data.lastNameFr.trim(),
        firstNameAr: data.firstNameAr || null,
        lastNameAr: data.lastNameAr || null,
        birthDate: new Date(data.birthDate || '1990-01-01'),
        gender: data.gender || 'M',
        phone: data.phone.trim(),
        email: data.email || null,
        address: data.address || null,
        neighborhood: data.neighborhood || 'Hay Al Matar',
        bloodGroup: data.bloodGroup || null,
        allergies: data.allergies || null,
        medicalHistory: data.medicalHistory || null,
        surgicalHistory: data.surgicalHistory || null,
        mutuelleType: data.mutuelleType || 'PRIVE',
        mutuelleNumber: data.mutuelleNumber || null,
        mutuelleRate: parseFloat(data.mutuelleRate) || 0.0,
        emergencyContact: data.emergencyContact || null,
      },
    });

    await recordAuditLog({
      userId: req.user?.id,
      userName: req.user?.name || 'Inconnu',
      userRole: req.user?.role || 'USER',
      action: 'CREATE',
      entityType: 'PATIENT',
      entityId: newPatient.id,
      details: `Création nouveau patient ${newPatient.firstNameFr} ${newPatient.lastNameFr} (${newPatient.patientNumber})`,
      ipAddress: req.ip,
    });

    res.status(201).json(newPatient);
  } catch (error: any) {
    console.error('Erreur création patient:', error);
    res.status(500).json({ error: error.message || 'Erreur lors de la création du patient' });
  }
});

// Mise à jour dossier patient
router.put('/:id', authenticateToken, async (req: AuthenticatedRequest, res: Response) => {
  try {
    const data = req.body;
    const patient = await prisma.patient.update({
      where: { id: req.params.id },
      data: {
        firstNameFr: data.firstNameFr,
        lastNameFr: data.lastNameFr,
        firstNameAr: data.firstNameAr,
        lastNameAr: data.lastNameAr,
        birthDate: data.birthDate ? new Date(data.birthDate) : undefined,
        gender: data.gender,
        phone: data.phone,
        email: data.email,
        address: data.address,
        neighborhood: data.neighborhood,
        bloodGroup: data.bloodGroup,
        allergies: data.allergies,
        medicalHistory: data.medicalHistory,
        surgicalHistory: data.surgicalHistory,
        mutuelleType: data.mutuelleType,
        mutuelleNumber: data.mutuelleNumber,
        mutuelleRate: data.mutuelleRate !== undefined ? parseFloat(data.mutuelleRate) : undefined,
        emergencyContact: data.emergencyContact,
      },
    });

    await recordAuditLog({
      userId: req.user?.id,
      userName: req.user?.name || 'Inconnu',
      userRole: req.user?.role || 'USER',
      action: 'UPDATE',
      entityType: 'PATIENT',
      entityId: patient.id,
      details: `Mise à jour coordonnées / antécédents patient ${patient.firstNameFr} ${patient.lastNameFr}`,
      ipAddress: req.ip,
    });

    res.json(patient);
  } catch (error: any) {
    res.status(500).json({ error: error.message || 'Erreur mise à jour patient' });
  }
});

// Archivage sécurisé d'un patient (Soft Delete CNDP)
router.post('/:id/archive', authenticateToken, async (req: AuthenticatedRequest, res: Response) => {
  try {
    const { reason } = req.body;
    const patient = await prisma.patient.update({
      where: { id: req.params.id },
      data: {
        isArchived: true,
        archivedAt: new Date(),
        archivedReason: reason || 'Clôture administrative du dossier patient',
      },
    });

    await recordAuditLog({
      userId: req.user?.id,
      userName: req.user?.name || 'Inconnu',
      userRole: req.user?.role || 'USER',
      action: 'ARCHIVE',
      entityType: 'PATIENT',
      entityId: patient.id,
      details: `Transfert du dossier de ${patient.firstNameFr} ${patient.lastNameFr} dans les Archives Sécurisées (Motif: ${reason})`,
      ipAddress: req.ip,
    });

    res.json({ message: 'Patient archivé avec succès', patient });
  } catch (error) {
    res.status(500).json({ error: 'Erreur archivage patient' });
  }
});

// Restauration d'un dossier patient depuis les archives
router.post('/:id/restore', authenticateToken, async (req: AuthenticatedRequest, res: Response) => {
  try {
    const patient = await prisma.patient.update({
      where: { id: req.params.id },
      data: {
        isArchived: false,
        archivedAt: null,
        archivedReason: null,
      },
    });

    await recordAuditLog({
      userId: req.user?.id,
      userName: req.user?.name || 'Inconnu',
      userRole: req.user?.role || 'USER',
      action: 'RESTORE',
      entityType: 'PATIENT',
      entityId: patient.id,
      details: `Restauration du dossier patient ${patient.firstNameFr} ${patient.lastNameFr} depuis les Archives`,
      ipAddress: req.ip,
    });

    res.json({ message: 'Patient restauré dans la base active', patient });
  } catch (error) {
    res.status(500).json({ error: 'Erreur restauration patient' });
  }
});

export default router;
