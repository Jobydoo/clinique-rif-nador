import prisma from '../prisma.js';

export interface AuditParams {
  userId?: string;
  userName: string;
  userRole: string;
  action: 'VIEW' | 'CREATE' | 'UPDATE' | 'DELETE' | 'ARCHIVE' | 'RESTORE' | 'EXPORT' | 'LOGIN';
  entityType: 'PATIENT' | 'CONSULTATION' | 'INVOICE' | 'PRESCRIPTION' | 'STOCK' | 'BED' | 'DOCUMENT' | 'SYSTEM' | 'AUTH';
  entityId?: string;
  details: string;
  ipAddress?: string;
}

export async function recordAuditLog(params: AuditParams) {
  try {
    return await prisma.auditLog.create({
      data: {
        userId: params.userId || null,
        userName: params.userName,
        userRole: params.userRole,
        action: params.action,
        entityType: params.entityType,
        entityId: params.entityId || null,
        details: params.details,
        ipAddress: params.ipAddress || '127.0.0.1',
      },
    });
  } catch (error) {
    console.error('Erreur enregistrement audit log CNDP:', error);
  }
}
