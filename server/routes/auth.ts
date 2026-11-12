import { Router, Response } from 'express';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import prisma from '../prisma.js';
import { AuthenticatedRequest, authenticateToken } from '../middleware/auth.js';
import { recordAuditLog } from '../middleware/audit.js';

const router = Router();
const JWT_SECRET = process.env.JWT_SECRET || 'nador-clinique-rif-secret-key-2026-cndp-secured';

// Comptes de test fonctionnels pour la démonstration
export const DEMO_ACCOUNTS = [
  {
    role: 'ADMIN',
    roleLabelFr: 'Directeur Général / Super Admin',
    roleLabelAr: 'المدير العام / المسؤول الرئيسي',
    email: 'admin@clinique-rif-nador.ma',
    name: 'Dr. Mohamed Amrani (Directeur)',
    specialty: 'Direction Médicale & Administration',
    badge: 'Accès Total',
  },
  {
    role: 'DOCTOR',
    roleLabelFr: 'Médecin Praticien',
    roleLabelAr: 'طبيب ممارس',
    email: 'medecin@clinique-rif-nador.ma',
    name: 'Dr. Youssef Benali',
    specialty: 'Cardiologie & Médecine Interne',
    badge: 'Consultations & DME',
  },
  {
    role: 'NURSE',
    roleLabelFr: 'Infirmier Major / Triage',
    roleLabelAr: 'ممرض رئيسي / الفرز الطبي',
    email: 'infirmier@clinique-rif-nador.ma',
    name: 'Fatima Zahra Mansouri',
    specialty: 'Soins Infirmiers & Triage Urgences',
    badge: 'Constantes & Soins',
  },
  {
    role: 'RECEPTIONIST',
    roleLabelFr: 'Accueil & Secrétariat Médical',
    roleLabelAr: 'الاستقبال وسكرتارية العيادة',
    email: 'reception@clinique-rif-nador.ma',
    name: 'Khadija El Idrissi',
    specialty: 'Accueil, RDV & Caisse',
    badge: 'Admissions & Facturation',
  },
  {
    role: 'PHARMACIST',
    roleLabelFr: 'Pharmacien & Responsable Stock',
    roleLabelAr: 'صيدلي ومسؤول المخزون الطبي',
    email: 'pharmacie@clinique-rif-nador.ma',
    name: 'Dr. Rachid Berrada',
    specialty: 'Pharmacie Hospitalière & Consommables',
    badge: 'Gestion des Stocks',
  },
  {
    role: 'LAB_TECH',
    roleLabelFr: 'Laborantin & Imagerie Médicale',
    roleLabelAr: 'مخبري وتقني أشعة طبية',
    email: 'labo@clinique-rif-nador.ma',
    name: 'Nadia Tazi',
    specialty: 'Analyses Biologiques & Radiologie',
    badge: 'Résultats & GED',
  },
];

// Route publique: liste des comptes démo
router.get('/demo-accounts', (req, res) => {
  res.json({
    accounts: DEMO_ACCOUNTS,
    defaultPassword: 'Password123!',
    clinic: {
      nameFr: process.env.CLINIC_NAME || 'Clinique Médico-Chirurgicale du Rif',
      nameAr: process.env.CLINIC_NAME_AR || 'مصحة الريف للطب والجراحة - الناظور',
      city: 'Nador',
      address: 'Boulevard Hassan II, Hay Al Matar, Nador',
      phone: '+212 536 60 44 20',
      inpe: '053421987',
    },
  });
});

// Connexion
router.post('/login', async (req, res) => {
  try {
    const { email, password } = req.body;
    if (!email) {
      return res.status(400).json({ error: 'Email requis' });
    }

    const user = await prisma.user.findUnique({
      where: { email: email.toLowerCase().trim() },
    });

    if (!user) {
      return res.status(401).json({ error: 'Identifiants incorrects' });
    }

    if (!user.isActive) {
      return res.status(403).json({ error: 'Compte désactivé. Contactez le Directeur de la Clinique.' });
    }

    // Vérification mot de passe (ou bypass pour démo si mot de passe démo)
    const isDemoPassword = password === 'Password123!' || password === 'Nador2026!';
    const isPasswordValid = isDemoPassword || await bcrypt.compare(password, user.passwordHash);

    if (!isPasswordValid) {
      return res.status(401).json({ error: 'Mot de passe incorrect' });
    }

    const token = jwt.sign(
      {
        id: user.id,
        email: user.email,
        name: user.name,
        role: user.role,
        specialty: user.specialty,
      },
      JWT_SECRET,
      { expiresIn: '24h' }
    );

    // Audit Log CNDP
    await recordAuditLog({
      userId: user.id,
      userName: user.name,
      userRole: user.role,
      action: 'LOGIN',
      entityType: 'AUTH',
      entityId: user.id,
      details: `Connexion réussie au SIH Clinique du Rif Nador (${user.role})`,
      ipAddress: req.ip,
    });

    res.json({
      token,
      user: {
        id: user.id,
        email: user.email,
        name: user.name,
        role: user.role,
        specialty: user.specialty,
        phone: user.phone,
        feeRate: user.feeRate,
      },
    });
  } catch (error: any) {
    console.error('Erreur Login:', error);
    res.status(500).json({ error: 'Erreur serveur lors de la connexion' });
  }
});

// Profil utilisateur actuel
router.get('/me', authenticateToken, async (req: AuthenticatedRequest, res: Response) => {
  try {
    const user = await prisma.user.findUnique({
      where: { id: req.user!.id },
      select: {
        id: true,
        email: true,
        name: true,
        role: true,
        specialty: true,
        phone: true,
        doctorType: true,
        feeRate: true,
        cndpConsent: true,
      },
    });

    if (!user) {
      return res.status(404).json({ error: 'Utilisateur introuvable' });
    }

    res.json(user);
  } catch (error) {
    res.status(500).json({ error: 'Erreur récupération profil' });
  }
});

// Liste de tous les utilisateurs (pour assignation médecin/personnel)
router.get('/users', authenticateToken, async (req: AuthenticatedRequest, res: Response) => {
  try {
    const users = await prisma.user.findMany({
      where: { isActive: true },
      select: {
        id: true,
        name: true,
        role: true,
        specialty: true,
        email: true,
        phone: true,
        doctorType: true,
        feeRate: true,
      },
      orderBy: { name: 'asc' },
    });
    res.json(users);
  } catch (error) {
    res.status(500).json({ error: 'Erreur liste utilisateurs' });
  }
});

export default router;
