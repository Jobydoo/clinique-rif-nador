import { Router, Response } from 'express';
import prisma from '../prisma.js';
import { AuthenticatedRequest, authenticateToken } from '../middleware/auth.js';
import { recordAuditLog } from '../middleware/audit.js';

const router = Router();

// File d'attente en direct (avec calcul temps d'attente)
router.get('/', authenticateToken, async (req: AuthenticatedRequest, res: Response) => {
  try {
    const { status, doctorId } = req.query;

    const whereClause: any = {};
    if (status && status !== 'ALL') {
      whereClause.status = status;
    } else {
      whereClause.status = { not: 'COMPLETED' };
    }

    if (doctorId && doctorId !== 'ALL') {
      whereClause.doctorId = doctorId;
    }

    const queue = await prisma.waitingRoom.findMany({
      where: whereClause,
      include: {
        patient: {
          select: {
            id: true,
            patientNumber: true,
            cin: true,
            firstNameFr: true,
            lastNameFr: true,
            firstNameAr: true,
            lastNameAr: true,
            phone: true,
            mutuelleType: true,
            allergies: true,
            neighborhood: true,
            birthDate: true,
            gender: true,
          },
        },
      },
      orderBy: [
        { priority: 'desc' }, // URGENT first
        { arrivalTime: 'asc' }, // FIFO
      ],
    });

    const now = new Date();
    const enrichedQueue = queue.map((item, index) => {
      const waitMinutes = Math.floor((now.getTime() - new Date(item.arrivalTime).getTime()) / 60000);
      // Estimation temps d'attente restant (environ 15 min par patient en amont)
      const estimatedRemainingMinutes = Math.max(0, index * 15);

      return {
        ...item,
        waitMinutes,
        estimatedRemainingMinutes,
      };
    });

    res.json(enrichedQueue);
  } catch (error) {
    res.status(500).json({ error: 'Erreur récupération salle d’attente' });
  }
});

// Ajouter un patient à la salle d'attente
router.post('/enqueue', authenticateToken, async (req: AuthenticatedRequest, res: Response) => {
  try {
    const { patientId, doctorId, priority, notes } = req.body;

    if (!patientId) {
      return res.status(400).json({ error: 'Patient requis' });
    }

    // Vérifier si le patient est déjà dans la file active
    const active = await prisma.waitingRoom.findFirst({
      where: {
        patientId,
        status: { not: 'COMPLETED' },
      },
    });

    if (active) {
      return res.status(400).json({ error: 'Le patient est déjà présent dans la salle d’attente' });
    }

    const entry = await prisma.waitingRoom.create({
      data: {
        patientId,
        doctorId: doctorId || null,
        priority: priority || 'NORMAL',
        notes: notes || null,
        status: 'WAITING',
      },
      include: {
        patient: true,
      },
    });

    await recordAuditLog({
      userId: req.user?.id,
      userName: req.user?.name || 'Inconnu',
      userRole: req.user?.role || 'USER',
      action: 'CREATE',
      entityType: 'PATIENT',
      entityId: patientId,
      details: `Admission en salle d'attente pour ${entry.patient.firstNameFr} ${entry.patient.lastNameFr} (Priorité: ${entry.priority})`,
      ipAddress: req.ip,
    });

    res.status(201).json(entry);
  } catch (error) {
    res.status(500).json({ error: 'Erreur ajout en salle d’attente' });
  }
});

// Changer le statut (Triage, En consultation, En examen, Terminé)
router.put('/:id/status', authenticateToken, async (req: AuthenticatedRequest, res: Response) => {
  try {
    const { status, doctorId } = req.body;
    const now = new Date();

    const updateData: any = { status };
    if (doctorId) updateData.doctorId = doctorId;

    if (status === 'TRIAGE') {
      updateData.triageTime = now;
    } else if (status === 'IN_CONSULTATION') {
      updateData.consultStartTime = now;
    } else if (status === 'COMPLETED') {
      updateData.completedTime = now;
    }

    const updated = await prisma.waitingRoom.update({
      where: { id: req.params.id },
      data: updateData,
      include: { patient: true },
    });

    await recordAuditLog({
      userId: req.user?.id,
      userName: req.user?.name || 'Inconnu',
      userRole: req.user?.role || 'USER',
      action: 'UPDATE',
      entityType: 'PATIENT',
      entityId: updated.patientId,
      details: `Changement statut file d'attente vers: ${status} pour ${updated.patient.firstNameFr} ${updated.patient.lastNameFr}`,
      ipAddress: req.ip,
    });

    res.json(updated);
  } catch (error) {
    res.status(500).json({ error: 'Erreur mise à jour statut file d’attente' });
  }
});

// Appel du patient (Notification visuelle & sonore)
router.post('/:id/call', authenticateToken, async (req: AuthenticatedRequest, res: Response) => {
  try {
    const { roomNumber } = req.body;
    const entry = await prisma.waitingRoom.findUnique({
      where: { id: req.params.id },
      include: { patient: true },
    });

    if (!entry) {
      return res.status(404).json({ error: 'Entrée introuvable' });
    }

    const callPayload = {
      messageFr: `Le patient ${entry.patient.firstNameFr} ${entry.patient.lastNameFr} est appelé en ${roomNumber || 'Salle de consultation'}`,
      messageAr: `المريض(ة) ${entry.patient.firstNameAr || entry.patient.firstNameFr} ${entry.patient.lastNameAr || entry.patient.lastNameFr}، يرجى التوجه إلى ${roomNumber || 'قاعة الفحص'}`,
      timestamp: new Date().toISOString(),
      patientName: `${entry.patient.firstNameFr} ${entry.patient.lastNameFr}`,
      room: roomNumber || 'Cabinet 1',
    };

    res.json({
      success: true,
      call: callPayload,
    });
  } catch (error) {
    res.status(500).json({ error: 'Erreur appel patient' });
  }
});

export default router;
