// Dictionnaire Bilingue Français / Arabe (Maroc) avec support RTL complet
const I18N = {
  fr: {
    // Clinique Info
    clinic_name: "Clinique Médico-Chirurgicale du Rif",
    clinic_city: "Nador (Maroc)",
    clinic_subtitle: "Système d'Information Hospitalier & Dossier Médical Électronique (DME)",
    cndp_badge: "Conformité CNDP Loi 09-08 Maroc",
    
    // Navigation
    nav_dashboard: "Tableau de Bord",
    nav_waiting_room: "Salle d'Attente",
    nav_patients: "Dossiers Patients (DME)",
    nav_consultations: "Consultations & Constantes",
    nav_inpatient: "Hospitalisation & Lits",
    nav_billing: "Facturation & Mutuelles",
    nav_pharmacy: "Pharmacie & Stocks",
    nav_staff: "Personnel & Gardes",
    nav_archive: "Coffre-fort Archives",
    nav_audit: "Audit CNDP & Sauvegardes",

    // Rôles
    role_admin: "Directeur / Admin",
    role_doctor: "Médecin Praticien",
    role_nurse: "Infirmier(ère)",
    role_receptionist: "Accueil / Secrétariat",
    role_pharmacist: "Pharmacien",
    role_lab: "Laborantin / Radio",

    // Statuts Salle d'Attente
    status_waiting: "En attente",
    status_triage: "Au triage",
    status_in_consultation: "En consultation",
    status_in_exam: "En examen",
    status_completed: "Terminé",

    // Priorités
    priority_normal: "Normal",
    priority_urgent: "Urgence médicale",
    priority_elderly: "Personne âgée",
    priority_pregnant: "Femme enceinte",

    // Statuts Lits
    bed_available: "Disponible",
    bed_occupied: "Occupé",
    bed_cleaning: "En désinfection",
    bed_reserved: "Réservé",

    // Boutons & Actions
    btn_login: "Se connecter",
    btn_logout: "Déconnexion",
    btn_new_patient: "+ Nouveau Patient",
    btn_add_to_queue: "Ajouter en Salle d'Attente",
    btn_call_patient: "Appeler le Patient",
    btn_take_vitals: "Prendre les Constantes",
    btn_new_consultation: "Nouvelle Consultation",
    btn_create_prescription: "Éditer Ordonnance",
    btn_create_certificate: "Certificat Médical",
    btn_new_invoice: "Créer Facture",
    btn_daily_closure: "Clôture de Caisse",
    btn_add_stock: "Entrée Stock",
    btn_restore: "Restaurer le Dossier",
    btn_archive: "Transférer aux Archives",
    btn_export_dossier: "Exporter Dossier Complet",
    btn_backup: "Créer Sauvegarde Système",
    btn_whatsapp_reminder: "Rappel WhatsApp (1-Clic)",
    btn_print: "Imprimer",
    btn_save: "Enregistrer",
    btn_cancel: "Annuler",
    btn_search: "Rechercher...",
    btn_filter: "Filtrer",

    // Constantes Vitales
    bp: "Tension Artérielle",
    pulse: "Pouls",
    temp: "Température",
    weight: "Poids",
    height: "Taille",
    bmi: "IMC (Indice de Masse)",
    spo2: "SpO2 (Oxygène)",
    glucose: "Glycémie",
    pain: "Échelle de douleur",

    // Mutuelles
    mutuelle: "Organisme Mutuelle",
    mutuelle_cnops: "CNOPS (AMO Public)",
    mutuelle_cnss: "CNSS (AMO Salariés)",
    mutuelle_far: "FAR (Mutuelle Militaire)",
    mutuelle_mgpap: "MGPAP",
    mutuelle_saham: "Saham / Sanlam",
    mutuelle_wafa: "Wafa Assurance",
    mutuelle_atlanta: "AtlantaSanad",
    mutuelle_rma: "RMA Watanya",
    mutuelle_prive: "Privé (Sans Mutuelle)",

    // Quartiers Nador
    quartier: "Quartier (Nador & Environs)",
    
    // Facturation
    total_ttc: "Total Général (TTC)",
    mutuelle_share: "Part Prise en Charge Mutuelle",
    patient_copay: "Ticket Modérateur (Part Patient)",
    payment_method: "Mode de Paiement",
    cash: "Espèces",
    card: "Carte Bancaire (TPE)",
    check: "Chèque",
    transfer: "Virement"
  },

  ar: {
    // Clinique Info
    clinic_name: "مصحة الريف للطب والجراحة",
    clinic_city: "الناظور (المملكة المغربية)",
    clinic_subtitle: "نظام المعلوميات الاستشفائية والملف الطبي الإلكتروني المتكامل",
    cndp_badge: "مطابق لمعايير اللجنة الوطنية لحماية المعطيات CNDP",

    // Navigation
    nav_dashboard: "لوحة القيادة",
    nav_waiting_room: "قاعة الانتظار الذكية",
    nav_patients: "ملفات المرضى (DME)",
    nav_consultations: "الفحوصات والمؤشرات الحيوية",
    nav_inpatient: "الاستشفاء والأسرة",
    nav_billing: "الفواتير والتأمين الصحي",
    nav_pharmacy: "الصيدلية والمخزون",
    nav_staff: "الأطر الطبية والمناوبة",
    nav_archive: "خزينة الأرشيف الآمنة",
    nav_audit: "سجل المراقبة والنسخ الاحتياطي",

    // Rôles
    role_admin: "المدير العام / مسؤول",
    role_doctor: "طبيب ممارس",
    role_nurse: "ممرض(ة) رئيسي(ة)",
    role_receptionist: "الاستقبال والسكرتارية",
    role_pharmacist: "صيدلي ومسؤول المخزون",
    role_lab: "تقني مخبر وأشعة",

    // Statuts Salle d'Attente
    status_waiting: "في الانتظار",
    status_triage: "قيد الفرز والقياس",
    status_in_consultation: "في قاعة الفحص",
    status_in_exam: "قيد إجراء تحاليل/أشعة",
    status_completed: "انتهى الفحص",

    // Priorités
    priority_normal: "عادي",
    priority_urgent: "حالة استعجالية",
    priority_elderly: "مسن / كبار السن",
    priority_pregnant: "سيدة حامل",

    // Statuts Lits
    bed_available: "شاغر",
    bed_occupied: "مشغول",
    bed_cleaning: "قيد التعقيم",
    bed_reserved: "محجوز",

    // Boutons & Actions
    btn_login: "تسجيل الدخول",
    btn_logout: "تسجيل الخروج",
    btn_new_patient: "+ تسجيل مريض جديد",
    btn_add_to_queue: "إضافة إلى قاعة الانتظار",
    btn_call_patient: "مناداة المريض صوتياً",
    btn_take_vitals: "تسجيل القياسات الحيوية",
    btn_new_consultation: "بدء فحص طبي",
    btn_create_prescription: "تحرير وصفة طبية",
    btn_create_certificate: "شهادة طبية",
    btn_new_invoice: "إصدار فاتورة",
    btn_daily_closure: "إغلاق صندوق الحسابات",
    btn_add_stock: "إدخال شحنة أدوية",
    btn_restore: "استرجاع من الأرشيف",
    btn_archive: "نقل إلى الأرشيف الآمن",
    btn_export_dossier: "تصدير الملف الطبي كاملاً",
    btn_backup: "إنشاء نسخة احتياطية",
    btn_whatsapp_reminder: "تذكير عبر واتساب (نقرة واحدة)",
    btn_print: "طباعة",
    btn_save: "حفظ",
    btn_cancel: "إلغاء",
    btn_search: "بحث متعدد المعايير...",
    btn_filter: "تصفية",

    // Constantes Vitales
    bp: "ضغط الدم",
    pulse: "النبض",
    temp: "درجة الحرارة",
    weight: "الوزن",
    height: "الطول",
    bmi: "مؤشر كتلة الجسم (IMC)",
    spo2: "تشبع الأكسجين (SpO2)",
    glucose: "نسبة السكر في الدم",
    pain: "مستوى الألم",

    // Mutuelles
    mutuelle: "هيئة التغطية الصحية",
    mutuelle_cnops: "كنوبس CNOPS (القطاع العام)",
    mutuelle_cnss: "الضمان الاجتماعي CNSS",
    mutuelle_far: "التعاضدية العسكرية FAR",
    mutuelle_mgpap: "التعاضدية العامة MGPAP",
    mutuelle_saham: "سهام للتأمين Saham",
    mutuelle_wafa: "وفا للتأمين Wafa",
    mutuelle_atlanta: "أطلنطا سند AtlantaSanad",
    mutuelle_rma: "الملكية المغربية RMA",
    mutuelle_prive: "خاص (بدون تأمين)",

    // Quartiers Nador
    quartier: "الحي / المنطقة (الناظور والنواحي)",

    // Facturation
    total_ttc: "المبلغ الإجمالي (درهم)",
    mutuelle_share: "حصة التأمين الصحي",
    patient_copay: "المبلغ المتبقي على المريض",
    payment_method: "طريقة الأداء",
    cash: "نقداً (درهم)",
    card: "بطاقة بنكية",
    check: "شيك بنكي",
    transfer: "تحويل بنكي"
  }
};

let CURRENT_LANG = 'fr';

function getLang() {
  return CURRENT_LANG;
}

function setLang(lang) {
  CURRENT_LANG = lang;
  const isRtl = lang === 'ar';
  document.documentElement.dir = isRtl ? 'rtl' : 'ltr';
  document.documentElement.lang = lang;
  localStorage.setItem('clinique_rif_lang', lang);
  window.dispatchEvent(new CustomEvent('language_changed', { detail: { lang, isRtl } }));
}

function t(key) {
  if (I18N[CURRENT_LANG] && I18N[CURRENT_LANG][key]) {
    return I18N[CURRENT_LANG][key];
  }
  if (I18N['fr'][key]) {
    return I18N['fr'][key];
  }
  return key;
}

// Initialisation au chargement
(function() {
  const saved = localStorage.getItem('clinique_rif_lang');
  if (saved && (saved === 'fr' || saved === 'ar')) {
    CURRENT_LANG = saved;
    document.documentElement.dir = saved === 'ar' ? 'rtl' : 'ltr';
    document.documentElement.lang = saved;
  }
})();
