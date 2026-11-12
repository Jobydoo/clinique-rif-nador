import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';

const JWT_SECRET = process.env.JWT_SECRET || 'nador-clinique-rif-secret-key-2026-cndp-secured';

export interface AuthUser {
  id: string;
  email: string;
  name: string;
  role: string;
  specialty?: string;
}

export interface AuthenticatedRequest extends Request {
  user?: AuthUser;
}

export function authenticateToken(req: AuthenticatedRequest, res: Response, next: NextFunction) {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    // Demo / fallback mode for local testing if needed
    const demoRole = req.headers['x-demo-role'] as string;
    const demoUser = req.headers['x-demo-user'] as string;
    if (demoRole && demoUser) {
      req.user = {
        id: 'demo-user-id',
        email: `${demoRole.toLowerCase()}@clinique-rif-nador.ma`,
        name: demoUser,
        role: demoRole.toUpperCase(),
      };
      return next();
    }
    return res.status(401).json({ error: 'Accès non autorisé : Token manquant' });
  }

  jwt.verify(token, JWT_SECRET, (err, user) => {
    if (err) {
      return res.status(403).json({ error: 'Token invalide ou expiré' });
    }
    req.user = user as AuthUser;
    next();
  });
}
