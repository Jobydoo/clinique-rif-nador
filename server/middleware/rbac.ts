import { Response, NextFunction } from 'express';
import { AuthenticatedRequest } from './auth.js';

export function authorizeRoles(...allowedRoles: string[]) {
  return (req: AuthenticatedRequest, res: Response, next: NextFunction) => {
    if (!req.user) {
      return res.status(401).json({ error: 'Utilisateur non authentifié' });
    }

    // Le DIRECTEUR / ADMIN a accès à l'ensemble du système
    if (req.user.role === 'ADMIN' || allowedRoles.includes(req.user.role)) {
      return next();
    }

    return res.status(403).json({
      error: `Accès refusé. Rôle requis: [${allowedRoles.join(', ')}]. Votre rôle: ${req.user.role}`,
    });
  };
}
