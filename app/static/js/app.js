// Application Principale - Clinique Médico-Chirurgicale du Rif - Nador
// Front-End React 18 Ultra-Rapide, Responsive et Installable en PWA

const { useState, useEffect, createElement: h } = React;

function App() {
  const [lang, setLangState] = useState(getLang());
  const [currentUser, setCurrentUser] = useState(null);
  const [demoAccounts, setDemoAccounts] = useState([]);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [loading, setLoading] = useState(true);
  const [toast, setToast] = useState(null);

  // Données des modules
  const [dashboardStats, setDashboardStats] = useState(null);
  const [patients, setPatients] = useState([]);
  const [waitingQueue, setWaitingQueue] = useState([]);
  const [appointments, setAppointments] = useState([]);
  const [rooms, setRooms] = useState([]);
  const [invoices, setInvoices] = useState([]);
  const [stockItems, setStockItems] = useState([]);
  const [staffMembers, setStaffMembers] = useState([]);
  const [feeReport, setFeeReport] = useState([]);
  const [shifts, setShifts] = useState([]);
  const [archives, setArchives] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [backups, setBackups] = useState([]);
  const [cim10List, setCim10List] = useState([]);
  const [actsCatalog, setActsCatalog] = useState([]);

  // États des modales
  const [activeModal, setActiveModal] = useState(null); // 'new_patient', 'patient_dme', 'vitals', 'consultation', 'invoice', 'closure', 'call', 'admit', 'backup'
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [selectedEntry, setSelectedEntry] = useState(null);
  const [selectedBed, setSelectedBed] = useState(null);

  // Recherche & Filtres
  const [patientSearch, setPatientSearch] = useState('');
  const [patientMutuelleFilter, setPatientMutuelleFilter] = useState('ALL');
  const [archiveSearch, setArchiveSearch] = useState('');
  const [stockSearch, setStockSearch] = useState('');
  const [stockCategoryFilter, setStockCategoryFilter] = useState('ALL');
  const [stockAlertFilter, setStockAlertFilter] = useState('ALL');

  // Formulaires
  const [formData, setFormData] = useState({});

  // Notification Toast Helper
  const showToast = (message, type = 'success') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 4000);
  };

  // Chargement initial
  useEffect(() => {
    const handleLangChange = (e) => setLangState(e.detail.lang);
    window.addEventListener('language_changed', handleLangChange);

    fetch('/api/auth/demo-accounts')
      .then(res => res.json())
      .then(data => {
        setDemoAccounts(data.accounts || []);
      });

    fetch('/api/auth/me')
      .then(res => res.json())
      .then(user => {
        if (!user.error) {
          setCurrentUser(user);
        }
      })
      .catch(() => {})
      .finally(() => {
        setLoading(false);
      });

    return () => window.removeEventListener('language_changed', handleLangChange);
  }, []);

  // Rechargement des données selon l'onglet actif
  const loadModuleData = () => {
    if (activeTab === 'dashboard') {
      fetch('/api/stats/dashboard').then(res => res.json()).then(setDashboardStats);
      fetch('/api/waiting-room').then(res => res.json()).then(setWaitingQueue);
      fetch('/api/appointments').then(res => res.json()).then(setAppointments);
    } else if (activeTab === 'waiting_room') {
      fetch('/api/waiting-room').then(res => res.json()).then(setWaitingQueue);
      fetch('/api/patients').then(res => res.json()).then(setPatients);
    } else if (activeTab === 'patients') {
      const url = `/api/patients?search=${encodeURIComponent(patientSearch)}&mutuelle=${patientMutuelleFilter}`;
      fetch(url).then(res => res.json()).then(setPatients);
    } else if (activeTab === 'consultations') {
      fetch('/api/patients').then(res => res.json()).then(setPatients);
      fetch('/api/medical/cim10').then(res => res.json()).then(setCim10List);
    } else if (activeTab === 'inpatient') {
      fetch('/api/inpatient/rooms').then(res => res.json()).then(setRooms);
      fetch('/api/patients').then(res => res.json()).then(setPatients);
    } else if (activeTab === 'billing') {
      fetch('/api/billing/invoices').then(res => res.json()).then(setInvoices);
      fetch('/api/billing/acts-catalog').then(res => res.json()).then(setActsCatalog);
      fetch('/api/patients').then(res => res.json()).then(setPatients);
    } else if (activeTab === 'pharmacy') {
      const url = `/api/pharmacy/stock?category=${stockCategoryFilter}&alert=${stockAlertFilter}&search=${encodeURIComponent(stockSearch)}`;
      fetch(url).then(res => res.json()).then(setStockItems);
    } else if (activeTab === 'staff') {
      fetch('/api/staff').then(res => res.json()).then(setStaffMembers);
      fetch('/api/staff/fees-calculator').then(res => res.json()).then(setFeeReport);
      fetch('/api/staff/shifts').then(res => res.json()).then(setShifts);
    } else if (activeTab === 'archive') {
      fetch(`/api/archive?search=${encodeURIComponent(archiveSearch)}`).then(res => res.json()).then(setArchives);
    } else if (activeTab === 'audit') {
      fetch('/api/audit/logs').then(res => res.json()).then(setAuditLogs);
      fetch('/api/audit/backups').then(res => res.json()).then(setBackups);
    }
  };

  useEffect(() => {
    loadModuleData();
  }, [activeTab, patientSearch, patientMutuelleFilter, archiveSearch, stockCategoryFilter, stockAlertFilter, stockSearch]);

  // Connexion rapide par rôle démo
  const switchRole = (account) => {
    fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: account.email, password: 'Password123!' })
    })
    .then(res => res.json())
    .then(data => {
      if (data.user) {
        setCurrentUser(data.user);
        showToast(`Connecté en tant que : ${account.name} (${account.role})`);
        loadModuleData();
      }
    });
  };

  const handleLogout = () => {
    fetch('/api/auth/logout', { method: 'POST' }).then(() => {
      setCurrentUser(null);
      showToast('Déconnexion effectuée');
    });
  };

  const toggleLanguage = () => {
    const nextLang = lang === 'fr' ? 'ar' : 'fr';
    setLang(nextLang);
  };

  // Sonnerie / Chime synthétisé pour appel patient
  const playChime = () => {
    try {
      const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(587.33, audioCtx.currentTime); // D5
      osc.frequency.setValueAtTime(880, audioCtx.currentTime + 0.15); // A5
      gain.gain.setValueAtTime(0.2, audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.8);
      osc.connect(gain);
      gain.connect(audioCtx.destination);
      osc.start();
      osc.stop(audioCtx.currentTime + 0.8);
    } catch (e) {
      console.log('Audio chime simulated');
    }
  };

  // ---------------- RENDU PRINCIPAL ----------------
  return h('div', { className: 'min-h-screen bg-slate-50 text-slate-900 flex flex-col' },
    // 1. Toast Notification
    toast && h('div', {
      className: `fixed bottom-5 right-5 z-50 px-5 py-3 rounded-lg shadow-xl text-white font-medium flex items-center space-x-3 fade-in ${
        toast.type === 'error' ? 'bg-rose-600' : 'bg-emerald-600'
      }`
    }, [
      h('span', { key: 'msg' }, toast.message)
    ]),

    // 2. Barre d'en-tête supérieure (Header & Navbar)
    h('header', { className: 'bg-white border-b border-slate-200 sticky top-0 z-30 shadow-sm' },
      h('div', { className: 'max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3 flex flex-wrap items-center justify-between gap-3' },
        // Logo & Identité Clinique Nador
        h('div', { className: 'flex items-center space-x-3 rtl:space-x-reverse cursor-pointer', onClick: () => setActiveTab('dashboard') },
          h('div', { className: 'w-10 h-10 rounded-xl bg-emerald-600 flex items-center justify-center text-white shadow-md font-bold text-xl' }, '✚'),
          h('div', {},
            h('h1', { className: 'text-lg font-bold text-slate-900 leading-tight' }, t('clinic_name')),
            h('p', { className: 'text-xs text-emerald-700 font-medium' }, `${t('clinic_city')} • ${t('cndp_badge')}`)
          )
        ),

        // Sélecteur rapide de Rôle / Démo Comptes (RBAC 1-Clic)
        h('div', { className: 'flex items-center flex-wrap gap-1.5 bg-slate-100 p-1.5 rounded-xl border border-slate-200' },
          h('span', { className: 'text-xs font-semibold text-slate-500 px-2' }, 'Rôle Démo :'),
          demoAccounts.map(acc => {
            const isCurrent = currentUser && currentUser.role === acc.role;
            return h('button', {
              key: acc.role,
              onClick: () => switchRole(acc),
              title: `${acc.name} - ${acc.specialty}`,
              className: `px-2.5 py-1 text-xs font-medium rounded-lg transition-all ${
                isCurrent
                  ? 'bg-emerald-600 text-white shadow-sm font-bold'
                  : 'bg-white text-slate-700 hover:bg-slate-200'
              }`
            }, acc.role);
          })
        ),

        // Actions droites : Langue, Profil, Déconnexion
        h('div', { className: 'flex items-center space-x-3 rtl:space-x-reverse' },
          // Sélecteur de langue bilingue FR / AR
          h('button', {
            onClick: toggleLanguage,
            className: 'px-3 py-1.5 text-xs font-bold rounded-lg border border-slate-300 bg-white hover:bg-slate-50 text-slate-700 flex items-center gap-1 shadow-sm'
          }, lang === 'fr' ? 'العربية (AR) 🇲🇦' : 'Français (FR) 🇫🇷'),

          // Badge Utilisateur Connecté
          currentUser && h('div', { className: 'hidden sm:flex flex-col text-right rtl:text-left' },
            h('span', { className: 'text-xs font-bold text-slate-800' }, currentUser.name),
            h('span', { className: 'text-[10px] text-emerald-600 font-semibold' }, currentUser.role)
          ),

          // Déconnexion
          currentUser && h('button', {
            onClick: handleLogout,
            title: t('btn_logout'),
            className: 'p-2 text-xs rounded-lg text-slate-500 hover:text-rose-600 hover:bg-rose-50 border border-transparent'
          }, '🚪')
        )
      ),

      // 3. Barre de Navigation des 10 Modules Fonctionnels
      h('nav', { className: 'bg-slate-900 text-slate-300 px-4 overflow-x-auto shadow-inner' },
        h('div', { className: 'max-w-7xl mx-auto flex space-x-1 rtl:space-x-reverse py-2 whitespace-nowrap text-xs font-medium' },
          [
            { id: 'dashboard', label: t('nav_dashboard'), icon: '📊' },
            { id: 'waiting_room', label: t('nav_waiting_room'), icon: '⏳' },
            { id: 'patients', label: t('nav_patients'), icon: '🗂️' },
            { id: 'consultations', label: t('nav_consultations'), icon: '🩺' },
            { id: 'inpatient', label: t('nav_inpatient'), icon: '🛏️' },
            { id: 'billing', label: t('nav_billing'), icon: '💳' },
            { id: 'pharmacy', label: t('nav_pharmacy'), icon: '💊' },
            { id: 'staff', label: t('nav_staff'), icon: '👨‍⚕️' },
            { id: 'archive', label: t('nav_archive'), icon: '🗄️' },
            { id: 'audit', label: t('nav_audit'), icon: '🛡️' }
          ].map(tab => {
            const isActive = activeTab === tab.id;
            return h('button', {
              key: tab.id,
              onClick: () => setActiveTab(tab.id),
              className: `px-3 py-2 rounded-lg flex items-center gap-1.5 transition-colors ${
                isActive
                  ? 'bg-emerald-600 text-white font-bold shadow-md'
                  : 'hover:bg-slate-800 text-slate-300'
              }`
            }, [
              h('span', { key: 'i' }, tab.icon),
              h('span', { key: 't' }, tab.label)
            ]);
          })
        )
      )
    ),

    // 4. Contenu Principal de l'Application
    h('main', { className: 'flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8 fade-in' },
      activeTab === 'dashboard' && renderDashboard(),
      activeTab === 'waiting_room' && renderWaitingRoom(),
      activeTab === 'patients' && renderPatients(),
      activeTab === 'consultations' && renderConsultations(),
      activeTab === 'inpatient' && renderInpatient(),
      activeTab === 'billing' && renderBilling(),
      activeTab === 'pharmacy' && renderPharmacy(),
      activeTab === 'staff' && renderStaff(),
      activeTab === 'archive' && renderArchive(),
      activeTab === 'audit' && renderAudit()
    ),

    // 5. Modales contextuelles
    renderActiveModal(),

    // 6. Pied de page officiel
    h('footer', { className: 'bg-white border-t border-slate-200 py-4 px-6 text-center text-xs text-slate-500' },
      `${t('clinic_name')} — ${t('clinic_city')} • N° INPE: 053421987 • ICE: 002391823000045 • Tél: +212 536 60 44 20 • ${t('cndp_badge')}`
    )
  );

  // ================= MODULE 1 : DASHBOARD =================
  function renderDashboard() {
    const kpis = dashboardStats ? dashboardStats.kpis : {};
    return h('div', { className: 'space-y-6' },
      // En-tête de bienvenue & Actions rapides
      h('div', { className: 'bg-gradient-to-r from-emerald-800 to-teal-900 rounded-2xl p-6 text-white shadow-lg flex flex-wrap justify-between items-center gap-4' },
        h('div', {},
          h('h2', { className: 'text-2xl font-black mb-1' }, `Bienvenue au SIH • ${t('clinic_name')}`),
          h('p', { className: 'text-emerald-200 text-sm' }, `Clinique multidisciplinaire à Nador • Gestion intégrée et conforme CNDP`)
        ),
        h('div', { className: 'flex flex-wrap gap-2' },
          h('button', {
            onClick: () => { setFormData({}); setActiveModal('new_patient'); },
            className: 'bg-white text-emerald-900 hover:bg-emerald-50 px-4 py-2 rounded-xl text-xs font-bold shadow-md transition-all'
          }, t('btn_new_patient')),
          h('button', {
            onClick: () => setActiveTab('waiting_room'),
            className: 'bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-2 rounded-xl text-xs font-bold shadow-md transition-all'
          }, '⏳ ' + t('nav_waiting_room')),
          h('button', {
            onClick: () => setActiveTab('billing'),
            className: 'bg-teal-700 hover:bg-teal-600 text-white px-4 py-2 rounded-xl text-xs font-bold shadow-md transition-all'
          }, '💳 ' + t('nav_billing'))
        )
      ),

      // Cartes KPIs
      h('div', { className: 'grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4' },
        [
          { label: 'File d’Attente Active', val: kpis.waiting_active || 0, badge: 'En cours', color: 'bg-amber-500', icon: '⏳' },
          { label: 'Taux Occupation Lits', val: `${kpis.occupancy_rate || 0}%`, badge: `${kpis.occupied_beds || 0}/${kpis.total_beds || 0} Lits`, color: 'bg-blue-600', icon: '🛏️' },
          { label: 'Patients Inscrits', val: kpis.total_patients || 0, badge: `${kpis.active_patients || 0} Actifs`, color: 'bg-emerald-600', icon: '👥' },
          { label: 'Recettes du Jour (TTC)', val: `${kpis.today_revenue || 0} DH`, badge: `${kpis.today_collected || 0} DH Encaissés`, color: 'bg-indigo-600', icon: '💰' },
          { label: 'Alertes Pharmacie', val: (kpis.low_stock_count || 0) + (kpis.near_expiry_count || 0), badge: `${kpis.low_stock_count || 0} Stock mini`, color: 'bg-rose-600', icon: '⚠️' },
          { label: 'Archives Sécurisées', val: kpis.archived_patients || 0, badge: 'Coffre-fort', color: 'bg-slate-700', icon: '🗄️' }
        ].map((card, i) =>
          h('div', { key: i, className: 'bg-white p-4 rounded-xl border border-slate-200 shadow-sm relative overflow-hidden' },
            h('div', { className: `w-1.5 h-full absolute left-0 top-0 ${card.color}` }),
            h('div', { className: 'flex justify-between items-start mb-2' },
              h('span', { className: 'text-2xl' }, card.icon),
              h('span', { className: 'text-[10px] font-bold px-2 py-0.5 rounded bg-slate-100 text-slate-600' }, card.badge)
            ),
            h('p', { className: 'text-xs text-slate-500 font-medium' }, card.label),
            h('h3', { className: 'text-xl font-black text-slate-900 mt-1' }, card.val)
          )
        )
      ),

      // Deux colonnes : File d'attente en direct & Rendez-vous du jour
      h('div', { className: 'grid grid-cols-1 lg:grid-cols-2 gap-6' },
        // File d'attente
        h('div', { className: 'bg-white p-5 rounded-2xl border border-slate-200 shadow-sm' },
          h('div', { className: 'flex justify-between items-center mb-4' },
            h('h3', { className: 'font-bold text-slate-900 text-base flex items-center gap-2' }, '⏳ File d’Attente en Temps Réel'),
            h('button', {
              onClick: () => setActiveTab('waiting_room'),
              className: 'text-xs text-emerald-600 font-bold hover:underline'
            }, 'Voir toute la salle →')
          ),
          waitingQueue.length === 0
            ? h('p', { className: 'text-xs text-slate-400 py-6 text-center' }, 'Aucun patient en attente actuellement')
            : h('div', { className: 'space-y-3' },
                waitingQueue.slice(0, 5).map(item =>
                  h('div', { key: item.id, className: 'flex items-center justify-between p-3 rounded-xl bg-slate-50 border border-slate-100' },
                    h('div', {},
                      h('p', { className: 'font-bold text-sm text-slate-800' }, `${item.patient.first_name_fr} ${item.patient.last_name_fr}`),
                      h('p', { className: 'text-xs text-slate-500' }, `CIN: ${item.patient.cin} • Quartier: ${item.patient.neighborhood}`)
                    ),
                    h('div', { className: 'text-right' },
                      h('span', { className: `text-xs font-bold px-2.5 py-1 rounded-full ${
                        item.status === 'IN_CONSULTATION' ? 'bg-emerald-100 text-emerald-800' :
                        item.status === 'TRIAGE' ? 'bg-blue-100 text-blue-800' : 'bg-amber-100 text-amber-800'
                      }` }, item.status),
                      h('p', { className: 'text-[11px] text-slate-400 mt-1' }, `Attente: ~${item.wait_minutes || 0} min`)
                    )
                  )
                )
              )
        ),

        // Rendez-vous du jour avec bouton WhatsApp
        h('div', { className: 'bg-white p-5 rounded-2xl border border-slate-200 shadow-sm' },
          h('div', { className: 'flex justify-between items-center mb-4' },
            h('h3', { className: 'font-bold text-slate-900 text-base flex items-center gap-2' }, '📅 Rendez-vous Médicaux'),
            h('span', { className: 'text-xs bg-slate-100 font-bold px-2.5 py-1 rounded-lg text-slate-600' }, `Aujourd'hui`)
          ),
          appointments.length === 0
            ? h('p', { className: 'text-xs text-slate-400 py-6 text-center' }, 'Aucun rendez-vous prévu pour aujourd’hui')
            : h('div', { className: 'space-y-3' },
                appointments.slice(0, 5).map(app =>
                  h('div', { key: app.id, className: 'flex items-center justify-between p-3 rounded-xl bg-slate-50 border border-slate-100' },
                    h('div', {},
                      h('p', { className: 'font-bold text-sm text-slate-800' }, `${app.patient ? app.patient.first_name_fr + ' ' + app.patient.last_name_fr : 'Patient'}`),
                      h('p', { className: 'text-xs text-slate-500' }, `Dr. ${app.doctor_name} (${app.specialty}) • ${app.time_slot}`)
                    ),
                    h('button', {
                      onClick: () => {
                        fetch(`/api/appointments/${app.id}/whatsapp`)
                          .then(res => res.json())
                          .then(data => {
                            window.open(data.whatsapp_url, '_blank');
                            showToast('Rappel WhatsApp ouvert !');
                          });
                      },
                      className: 'bg-emerald-50 hover:bg-emerald-100 text-emerald-700 border border-emerald-300 text-xs font-bold px-3 py-1.5 rounded-lg flex items-center gap-1 transition-all'
                    }, '💬 WhatsApp')
                  )
                )
              )
        )
      )
    );
  }

  // ================= MODULE 2 : SALLE D'ATTENTE INTELLIGENTE =================
  function renderWaitingRoom() {
    return h('div', { className: 'space-y-6' },
      h('div', { className: 'flex flex-wrap justify-between items-center gap-3 bg-white p-4 rounded-xl border border-slate-200' },
        h('div', {},
          h('h2', { className: 'text-xl font-bold text-slate-900' }, t('nav_waiting_room')),
          h('p', { className: 'text-xs text-slate-500' }, 'Gestion intelligente des flux, priorités d’urgence et appel patient avec carillon sonore')
        ),
        h('button', {
          onClick: () => {
            setFormData({});
            setActiveModal('enqueue_patient');
          },
          className: 'bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs px-4 py-2.5 rounded-xl shadow'
        }, t('btn_add_to_queue'))
      ),

      // Liste des patients dans la file d'attente
      h('div', { className: 'bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm' },
        h('div', { className: 'overflow-x-auto' },
          h('table', { className: 'w-full text-left rtl:text-right border-collapse text-xs' },
            h('thead', { className: 'bg-slate-50 text-slate-500 font-bold border-b border-slate-200 uppercase' },
              h('tr', {}, [
                h('th', { key: 'pos', className: 'p-3 text-center' }, '#'),
                h('th', { key: 'name', className: 'p-3' }, 'Patient (Identité & CIN)'),
                h('th', { key: 'prior', className: 'p-3' }, 'Priorité'),
                h('th', { key: 'status', className: 'p-3' }, 'Statut / Étape'),
                h('th', { key: 'wait', className: 'p-3 text-center' }, 'Temps d’attente'),
                h('th', { key: 'est', className: 'p-3 text-center' }, 'Temps estimé'),
                h('th', { key: 'actions', className: 'p-3 text-center' }, 'Actions / Appel')
              ])
            ),
            h('tbody', { className: 'divide-y divide-slate-100' },
              waitingQueue.length === 0
                ? h('tr', {}, h('td', { colSpan: 7, className: 'p-8 text-center text-slate-400' }, 'Salle d’attente vide'))
                : waitingQueue.map((entry, idx) =>
                    h('tr', { key: entry.id, className: 'hover:bg-slate-50/80 transition-colors' }, [
                      h('td', { key: 'num', className: 'p-3 font-bold text-center text-slate-400' }, idx + 1),
                      h('td', { key: 'pat', className: 'p-3' }, [
                        h('p', { key: 'fn', className: 'font-bold text-slate-800' }, `${entry.patient.first_name_fr} ${entry.patient.last_name_fr}`),
                        h('p', { key: 'cin', className: 'text-[11px] text-slate-500' }, `CIN: ${entry.patient.cin} • Tél: ${entry.patient.phone} • ${entry.patient.neighborhood}`)
                      ]),
                      h('td', { key: 'prio', className: 'p-3' },
                        h('span', { className: `px-2 py-0.5 rounded-full font-bold text-[10px] ${
                          entry.priority === 'URGENT' ? 'bg-rose-100 text-rose-800 animate-pulse' :
                          entry.priority === 'PREGNANT' ? 'bg-purple-100 text-purple-800' :
                          entry.priority === 'ELDERLY' ? 'bg-blue-100 text-blue-800' : 'bg-slate-100 text-slate-600'
                        }` }, entry.priority)
                      ),
                      h('td', { key: 'st', className: 'p-3' },
                        h('select', {
                          value: entry.status,
                          onChange: (e) => {
                            fetch(`/api/waiting-room/${entry.id}/status`, {
                              method: 'PUT',
                              headers: { 'Content-Type': 'application/json' },
                              body: JSON.stringify({ status: e.target.value })
                            }).then(() => {
                              showToast('Statut mis à jour');
                              loadModuleData();
                            });
                          },
                          className: 'border border-slate-300 rounded px-2 py-1 text-xs font-semibold bg-white'
                        }, [
                          h('option', { key: 'W', value: 'WAITING' }, 'En attente'),
                          h('option', { key: 'T', value: 'TRIAGE' }, 'Au triage'),
                          h('option', { key: 'C', value: 'IN_CONSULTATION' }, 'En consultation'),
                          h('option', { key: 'E', value: 'IN_EXAM' }, 'En examen'),
                          h('option', { key: 'D', value: 'COMPLETED' }, 'Terminé / Sortie')
                        ])
                      ),
                      h('td', { key: 'wmin', className: 'p-3 text-center font-bold text-amber-600' }, `${entry.wait_minutes || 0} min`),
                      h('td', { key: 'estmin', className: 'p-3 text-center text-slate-500' }, `~${entry.estimated_remaining_minutes || 0} min`),
                      h('td', { key: 'acts', className: 'p-3 text-center space-x-1 rtl:space-x-reverse' }, [
                        // Bouton Appel Patient (Carillon + Pop-up)
                        h('button', {
                          key: 'call',
                          onClick: () => {
                            playChime();
                            fetch(`/api/waiting-room/${entry.id}/call`, {
                              method: 'POST',
                              headers: { 'Content-Type': 'application/json' },
                              body: JSON.stringify({ cabinet: 'Cabinet de Consultation N° 1' })
                            })
                            .then(res => res.json())
                            .then(data => {
                              setSelectedEntry(data.call);
                              setActiveModal('call_patient_announcement');
                            });
                          },
                          className: 'bg-emerald-50 text-emerald-700 hover:bg-emerald-100 border border-emerald-300 px-2 py-1 rounded text-xs font-bold'
                        }, '📢 Appeler'),
                        // Prise de Constantes
                        h('button', {
                          key: 'vit',
                          onClick: () => {
                            setSelectedPatient(entry.patient);
                            setFormData({ patient_id: entry.patient.id });
                            setActiveModal('take_vitals');
                          },
                          className: 'bg-blue-50 text-blue-700 hover:bg-blue-100 border border-blue-300 px-2 py-1 rounded text-xs font-bold'
                        }, '🩺 Constantes')
                      ])
                    ])
                  )
            )
          )
        )
      )
    );
  }

  // ================= MODULE 3 : DOSSIERS PATIENTS (DME) =================
  function renderPatients() {
    return h('div', { className: 'space-y-6' },
      // Barre de recherche et filtres
      h('div', { className: 'bg-white p-4 rounded-xl border border-slate-200 flex flex-wrap justify-between items-center gap-3' },
        h('div', { className: 'flex flex-wrap items-center gap-2 flex-1 max-w-2xl' },
          h('input', {
            type: 'text',
            placeholder: 'Recherche par Nom, CIN, N° Dossier, Tél...',
            value: patientSearch,
            onChange: (e) => setPatientSearch(e.target.value),
            className: 'border border-slate-300 rounded-lg px-3 py-2 text-xs flex-1 min-w-[200px]'
          }),
          h('select', {
            value: patientMutuelleFilter,
            onChange: (e) => setPatientMutuelleFilter(e.target.value),
            className: 'border border-slate-300 rounded-lg px-3 py-2 text-xs font-semibold bg-white'
          }, [
            h('option', { key: 'ALL', value: 'ALL' }, 'Toutes les mutuelles'),
            h('option', { key: 'CNOPS', value: 'CNOPS' }, 'CNOPS (Public)'),
            h('option', { key: 'CNSS', value: 'CNSS' }, 'CNSS (Salariés)'),
            h('option', { key: 'FAR', value: 'FAR' }, 'FAR (Militaire)'),
            h('option', { key: 'MGPAP', value: 'MGPAP' }, 'MGPAP'),
            h('option', { key: 'SAHAM', value: 'SAHAM' }, 'Saham'),
            h('option', { key: 'WAFA', value: 'WAFA' }, 'Wafa Assurance'),
            h('option', { key: 'PRIVE', value: 'PRIVE' }, 'Privé (Sans Mutuelle)')
          ])
        ),
        h('button', {
          onClick: () => { setFormData({}); setActiveModal('new_patient'); },
          className: 'bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs px-4 py-2.5 rounded-xl shadow'
        }, t('btn_new_patient'))
      ),

      // Tableau des patients
      h('div', { className: 'bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm' },
        h('div', { className: 'overflow-x-auto' },
          h('table', { className: 'w-full text-left rtl:text-right border-collapse text-xs' },
            h('thead', { className: 'bg-slate-50 text-slate-500 font-bold border-b border-slate-200 uppercase' },
              h('tr', {}, [
                h('th', { key: 'num', className: 'p-3' }, 'N° Dossier'),
                h('th', { key: 'cin', className: 'p-3' }, 'CIN'),
                h('th', { key: 'name', className: 'p-3' }, 'Nom & Prénom (FR / AR)'),
                h('th', { key: 'tel', className: 'p-3' }, 'Téléphone'),
                h('th', { key: 'quartier', className: 'p-3' }, 'Quartier (Nador)'),
                h('th', { key: 'mut', className: 'p-3' }, 'Mutuelle / Taux'),
                h('th', { key: 'acts', className: 'p-3 text-center' }, 'Actions Dossier')
              ])
            ),
            h('tbody', { className: 'divide-y divide-slate-100' },
              patients.map(p =>
                h('tr', { key: p.id, className: 'hover:bg-slate-50 transition-colors' }, [
                  h('td', { key: 'pnum', className: 'p-3 font-mono font-bold text-emerald-700' }, p.patient_number),
                  h('td', { key: 'cin', className: 'p-3 font-bold text-slate-800' }, p.cin),
                  h('td', { key: 'pname', className: 'p-3' }, [
                    h('p', { key: 'fr', className: 'font-bold text-slate-900' }, `${p.first_name_fr} ${p.last_name_fr}`),
                    p.first_name_ar && h('p', { key: 'ar', className: 'text-[11px] text-slate-500 font-arabic' }, `${p.first_name_ar} ${p.last_name_ar || ''}`)
                  ]),
                  h('td', { key: 'ptel', className: 'p-3 text-slate-600' }, p.phone),
                  h('td', { key: 'pqt', className: 'p-3 text-slate-600' }, p.neighborhood),
                  h('td', { key: 'pmut', className: 'p-3' },
                    h('span', { className: `px-2 py-0.5 rounded text-[11px] font-bold ${
                      p.mutuelle_type === 'CNOPS' ? 'bg-blue-100 text-blue-800' :
                      p.mutuelle_type === 'CNSS' ? 'bg-teal-100 text-teal-800' :
                      p.mutuelle_type === 'FAR' ? 'bg-amber-100 text-amber-800' : 'bg-slate-100 text-slate-700'
                    }` }, `${p.mutuelle_type} (${p.mutuelle_rate || 0}%)`)
                  ),
                  h('td', { key: 'pacts', className: 'p-3 text-center space-x-1 rtl:space-x-reverse' }, [
                    // Ouvrir Dossier Complet DME
                    h('button', {
                      key: 'view',
                      onClick: () => {
                        fetch(`/api/patients/${p.id}`)
                          .then(res => res.json())
                          .then(fullPatient => {
                            setSelectedPatient(fullPatient);
                            setActiveModal('patient_dme');
                          });
                      },
                      className: 'bg-emerald-50 text-emerald-700 hover:bg-emerald-100 border border-emerald-300 px-2.5 py-1 rounded text-xs font-bold'
                    }, '📂 Ouvrir DME'),
                    // Ajouter en Salle d'Attente
                    h('button', {
                      key: 'queue',
                      onClick: () => {
                        fetch('/api/waiting-room/enqueue', {
                          method: 'POST',
                          headers: { 'Content-Type': 'application/json' },
                          body: JSON.stringify({ patient_id: p.id, priority: 'NORMAL' })
                        })
                        .then(res => res.json())
                        .then(res => {
                          if (res.error) showToast(res.error, 'error');
                          else showToast('Patient ajouté à la salle d’attente');
                        });
                      },
                      className: 'bg-slate-100 text-slate-700 hover:bg-slate-200 border border-slate-300 px-2 py-1 rounded text-xs font-bold'
                    }, '⏳ Attente'),
                    // Archiver (Soft-delete CNDP)
                    h('button', {
                      key: 'arch',
                      onClick: () => {
                        const reason = prompt('Motif d’archivage du dossier (Conformité CNDP) :', 'Clôture médicale du suivi patient');
                        if (reason) {
                          fetch(`/api/patients/${p.id}/archive`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ reason })
                          })
                          .then(() => {
                            showToast('Dossier transféré aux archives sécurisées');
                            loadModuleData();
                          });
                        }
                      },
                      className: 'text-slate-400 hover:text-amber-600 px-1 py-1 text-xs'
                    }, '🗄️')
                  ])
                ])
              )
            )
          )
        )
      )
    );
  }

  // ================= MODULE 4 : CONSULTATIONS & CONSTANTES =================
  function renderConsultations() {
    return h('div', { className: 'space-y-6' },
      h('div', { className: 'bg-white p-5 rounded-xl border border-slate-200 flex justify-between items-center' },
        h('div', {},
          h('h2', { className: 'text-xl font-bold text-slate-900' }, t('nav_consultations')),
          h('p', { className: 'text-xs text-slate-500' }, 'Prise de constantes vitales, codification diagnostique CIM-10 et génération ordonnances officielles')
        ),
        h('button', {
          onClick: () => {
            setFormData({
              fee_amount: 250,
              medications: [{ name: '', dosage: '', frequency: '', duration: '' }]
            });
            setActiveModal('new_consultation');
          },
          className: 'bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs px-4 py-2.5 rounded-xl shadow'
        }, t('btn_new_consultation'))
      ),

      // Liste des patients avec accès direct aux constantes & consultations
      h('div', { className: 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4' },
        patients.slice(0, 9).map(p =>
          h('div', { key: p.id, className: 'bg-white p-4 rounded-xl border border-slate-200 shadow-sm space-y-3' },
            h('div', { className: 'flex justify-between items-start' },
              h('div', {},
                h('h4', { className: 'font-bold text-sm text-slate-900' }, `${p.first_name_fr} ${p.last_name_fr}`),
                h('p', { className: 'text-xs text-slate-500' }, `CIN: ${p.cin} • ${p.neighborhood}`)
              ),
              h('span', { className: 'text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-100 text-emerald-800' }, p.mutuelle_type)
            ),
            h('div', { className: 'bg-slate-50 p-2.5 rounded-lg text-xs space-y-1' },
              h('p', {}, h('strong', {}, 'Groupe sanguin : '), p.blood_group || '--'),
              h('p', {}, h('strong', {}, 'Allergies : '), h('span', { className: 'text-rose-600 font-semibold' }, p.allergies || 'Aucune')),
              h('p', {}, h('strong', {}, 'Antécédents : '), p.medical_history || 'Aucun')
            ),
            h('div', { className: 'flex gap-2 pt-1' },
              h('button', {
                onClick: () => {
                  setSelectedPatient(p);
                  setFormData({ patient_id: p.id });
                  setActiveModal('take_vitals');
                },
                className: 'flex-1 bg-blue-50 text-blue-700 hover:bg-blue-100 border border-blue-200 text-xs font-bold py-1.5 rounded-lg'
              }, '🩺 Constantes'),
              h('button', {
                onClick: () => {
                  setSelectedPatient(p);
                  setFormData({
                    patient_id: p.id,
                    fee_amount: 250,
                    medications: [{ name: '', dosage: '', frequency: '', duration: '' }]
                  });
                  setActiveModal('new_consultation');
                },
                className: 'flex-1 bg-emerald-600 text-white hover:bg-emerald-700 text-xs font-bold py-1.5 rounded-lg'
              }, '✍️ Consulter')
            )
          )
        )
      )
    );
  }

  // ================= MODULE 5 : HOSPITALISATION & LITS =================
  function renderInpatient() {
    return h('div', { className: 'space-y-6' },
      h('div', { className: 'bg-white p-5 rounded-xl border border-slate-200 flex flex-wrap justify-between items-center gap-3' },
        h('div', {},
          h('h2', { className: 'text-xl font-bold text-slate-900' }, t('nav_inpatient')),
          h('p', { className: 'text-xs text-slate-500' }, 'Plan interactif des chambres et lits par service (USI, Chirurgie, Médecine, Maternité)')
        ),
        // Légende des statuts
        h('div', { className: 'flex flex-wrap items-center gap-3 text-xs font-semibold' },
          h('span', { className: 'flex items-center gap-1.5' }, h('span', { className: 'w-3 h-3 rounded-full bg-emerald-500' }), t('bed_available')),
          h('span', { className: 'flex items-center gap-1.5' }, h('span', { className: 'w-3 h-3 rounded-full bg-rose-500' }), t('bed_occupied')),
          h('span', { className: 'flex items-center gap-1.5' }, h('span', { className: 'w-3 h-3 rounded-full bg-amber-400' }), t('bed_cleaning')),
          h('span', { className: 'flex items-center gap-1.5' }, h('span', { className: 'w-3 h-3 rounded-full bg-blue-500' }), t('bed_reserved'))
        )
      ),

      // Plan interactif des chambres & lits
      h('div', { className: 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6' },
        rooms.map(room =>
          h('div', { key: room.id, className: 'bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4' },
            h('div', { className: 'flex justify-between items-center border-b border-slate-100 pb-3' },
              h('div', {},
                h('h4', { className: 'font-bold text-base text-slate-900' }, room.room_number),
                h('p', { className: 'text-xs text-slate-400 font-medium' }, `Étage ${room.floor} • ${room.department}`)
              ),
              h('span', { className: 'text-xs font-bold text-emerald-700 bg-emerald-50 px-2 py-1 rounded-md' }, `${room.daily_rate} MAD/j`)
            ),
            h('div', { className: 'grid grid-cols-2 gap-3' },
              room.beds.map(bed => {
                const colorClass =
                  bed.status === 'AVAILABLE' ? 'border-emerald-300 bg-emerald-50/50 hover:bg-emerald-100' :
                  bed.status === 'OCCUPIED' ? 'border-rose-300 bg-rose-50/50 hover:bg-rose-100' :
                  bed.status === 'CLEANING' ? 'border-amber-300 bg-amber-50/50 hover:bg-amber-100' :
                  'border-blue-300 bg-blue-50/50 hover:bg-blue-100';

                return h('div', {
                  key: bed.id,
                  onClick: () => {
                    setSelectedBed(bed);
                    if (bed.status === 'AVAILABLE') {
                      setFormData({ bed_id: bed.id });
                      setActiveModal('admit_patient');
                    } else if (bed.status === 'OCCUPIED' && bed.active_admission_id) {
                      if (confirm(`Libérer le lit ${bed.bed_number} et autoriser la sortie du patient ?`)) {
                        fetch(`/api/inpatient/admissions/${bed.active_admission_id}/discharge`, {
                          method: 'POST',
                          headers: { 'Content-Type': 'application/json' },
                          body: JSON.stringify({ discharge_summary: 'Sortie d’hospitalisation avec ordonnance de sortie.' })
                        }).then(() => {
                          showToast('Sortie enregistrée. Lit basculé en désinfection.');
                          loadModuleData();
                        });
                      }
                    } else if (bed.status === 'CLEANING') {
                      fetch(`/api/inpatient/beds/${bed.id}/status`, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ status: 'AVAILABLE' })
                      }).then(() => {
                        showToast('Désinfection terminée. Lit désormais disponible.');
                        loadModuleData();
                      });
                    }
                  },
                  className: `cursor-pointer p-3 rounded-xl border-2 transition-all flex flex-col justify-between ${colorClass}`
                }, [
                  h('div', { key: 'top', className: 'flex justify-between items-center' },
                    h('span', { className: 'font-bold text-xs text-slate-800' }, bed.bed_number),
                    h('span', { className: 'text-[10px] font-bold uppercase' }, bed.status)
                  ),
                  bed.active_patient && h('div', { key: 'pat', className: 'mt-2 text-[11px]' },
                    h('p', { className: 'font-bold text-slate-900 truncate' }, `${bed.active_patient.first_name_fr} ${bed.active_patient.last_name_fr}`),
                    h('p', { className: 'text-slate-500' }, bed.active_patient.cin)
                  ),
                  h('span', { key: 'tip', className: 'text-[9px] text-slate-400 mt-2' },
                    bed.status === 'AVAILABLE' ? 'Cliquez pour admettre' :
                    bed.status === 'OCCUPIED' ? 'Cliquez pour sortie' : 'Cliquez pour valider désinfection'
                  )
                ]);
              })
            )
          )
        )
      )
    );
  }

  // ================= MODULE 6 : FACTURATION & MUTUELLES =================
  function renderBilling() {
    return h('div', { className: 'space-y-6' },
      h('div', { className: 'bg-white p-5 rounded-xl border border-slate-200 flex flex-wrap justify-between items-center gap-3' },
        h('div', {},
          h('h2', { className: 'text-xl font-bold text-slate-900' }, t('nav_billing')),
          h('p', { className: 'text-xs text-slate-500' }, 'Tarification NGAP, calcul automatique Tiers-Payant / Mutuelle vs Ticket modérateur et clôture de caisse')
        ),
        h('div', { className: 'flex gap-2' },
          h('button', {
            onClick: () => {
              setFormData({ items: [{ act_code: 'CS', description: 'Consultation Spécialiste', quantity: 1, unit_price: 250 }] });
              setActiveModal('new_invoice');
            },
            className: 'bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs px-4 py-2.5 rounded-xl shadow'
          }, t('btn_new_invoice')),
          h('button', {
            onClick: () => {
              setFormData({ opening_amount: 1000, actual_cash: 1000 });
              setActiveModal('daily_closure');
            },
            className: 'bg-slate-800 hover:bg-slate-900 text-white font-bold text-xs px-4 py-2.5 rounded-xl shadow'
          }, '🔒 ' + t('btn_daily_closure'))
        )
      ),

      // Liste des factures émises
      h('div', { className: 'bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm' },
        h('div', { className: 'overflow-x-auto' },
          h('table', { className: 'w-full text-left rtl:text-right border-collapse text-xs' },
            h('thead', { className: 'bg-slate-50 text-slate-500 font-bold border-b border-slate-200 uppercase' },
              h('tr', {}, [
                h('th', { key: 'num', className: 'p-3' }, 'N° Facture'),
                h('th', { key: 'date', className: 'p-3' }, 'Date'),
                h('th', { key: 'pat', className: 'p-3' }, 'Patient'),
                h('th', { key: 'mut', className: 'p-3' }, 'Mutuelle'),
                h('th', { key: 'tot', className: 'p-3 text-right' }, 'Total TTC'),
                h('th', { key: 'mshare', className: 'p-3 text-right' }, 'Part Mutuelle'),
                h('th', { key: 'pshare', className: 'p-3 text-right' }, 'Part Patient'),
                h('th', { key: 'st', className: 'p-3 text-center' }, 'Statut'),
                h('th', { key: 'act', className: 'p-3 text-center' }, 'PDF Officiel')
              ])
            ),
            h('tbody', { className: 'divide-y divide-slate-100' },
              invoices.map(inv =>
                h('tr', { key: inv.id, className: 'hover:bg-slate-50 transition-colors' }, [
                  h('td', { key: 'num', className: 'p-3 font-mono font-bold text-blue-700' }, inv.invoice_number),
                  h('td', { key: 'date', className: 'p-3 text-slate-500' }, inv.date),
                  h('td', { key: 'pat', className: 'p-3 font-bold text-slate-900' }, inv.patient ? `${inv.patient.first_name_fr} ${inv.patient.last_name_fr}` : 'Inconnu'),
                  h('td', { key: 'mut', className: 'p-3' },
                    h('span', { className: 'px-2 py-0.5 rounded font-bold text-[10px] bg-slate-100 text-slate-700' }, inv.mutuelle_type)
                  ),
                  h('td', { key: 'tot', className: 'p-3 text-right font-bold text-slate-900' }, `${inv.total_amount.toFixed(2)} MAD`),
                  h('td', { key: 'msh', className: 'p-3 text-right text-emerald-600 font-medium' }, `${inv.mutuelle_amount.toFixed(2)} MAD`),
                  h('td', { key: 'psh', className: 'p-3 text-right font-bold text-blue-600' }, `${inv.patient_share.toFixed(2)} MAD`),
                  h('td', { key: 'st', className: 'p-3 text-center' },
                    h('span', { className: 'px-2 py-0.5 rounded-full font-bold text-[10px] bg-emerald-100 text-emerald-800' }, inv.status)
                  ),
                  h('td', { key: 'pdf', className: 'p-3 text-center' },
                    h('button', {
                      onClick: () => window.open(`/api/billing/invoices/${inv.id}/pdf`, '_blank'),
                      className: 'bg-blue-50 text-blue-700 hover:bg-blue-100 border border-blue-300 px-2 py-1 rounded text-xs font-bold'
                    }, '📄 Facture PDF')
                  )
                ])
              )
            )
          )
        )
      )
    );
  }

  // ================= MODULE 7 : PHARMACIE & GESTION DES STOCKS =================
  function renderPharmacy() {
    return h('div', { className: 'space-y-6' },
      h('div', { className: 'bg-white p-5 rounded-xl border border-slate-200 flex flex-wrap justify-between items-center gap-3' },
        h('div', {},
          h('h2', { className: 'text-xl font-bold text-slate-900' }, t('nav_pharmacy')),
          h('p', { className: 'text-xs text-slate-500' }, 'Inventaire en temps réel, alertes stock minimum et péremption proche')
        ),
        h('button', {
          onClick: () => {
            setFormData({ category: 'MEDICAMENT', min_quantity_alert: 10, current_quantity: 20 });
            setActiveModal('add_stock');
          },
          className: 'bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs px-4 py-2.5 rounded-xl shadow'
        }, t('btn_add_stock'))
      ),

      // Filtres catégories et alertes
      h('div', { className: 'flex flex-wrap items-center gap-2' },
        ['ALL', 'LOW', 'EXPIRING', 'EXPIRED'].map(alt =>
          h('button', {
            key: alt,
            onClick: () => setStockAlertFilter(alt),
            className: `px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
              stockAlertFilter === alt
                ? 'bg-emerald-600 text-white shadow-sm'
                : 'bg-white border border-slate-300 text-slate-600 hover:bg-slate-50'
            }`
          }, alt === 'ALL' ? 'Tous les articles' : alt === 'LOW' ? '⚠️ Stock Faible' : alt === 'EXPIRING' ? '⏳ Péremption < 60j' : '🚫 Périmés')
        )
      ),

      // Tableau des stocks
      h('div', { className: 'bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm' },
        h('div', { className: 'overflow-x-auto' },
          h('table', { className: 'w-full text-left rtl:text-right border-collapse text-xs' },
            h('thead', { className: 'bg-slate-50 text-slate-500 font-bold border-b border-slate-200 uppercase' },
              h('tr', {}, [
                h('th', { key: 'code', className: 'p-3' }, 'Code'),
                h('th', { key: 'name', className: 'p-3' }, 'Désignation / DCI'),
                h('th', { key: 'cat', className: 'p-3' }, 'Catégorie'),
                h('th', { key: 'qte', className: 'p-3 text-center' }, 'Quantité en Stock'),
                h('th', { key: 'exp', className: 'p-3' }, 'Date Péremption'),
                h('th', { key: 'st', className: 'p-3 text-center' }, 'Alerte'),
                h('th', { key: 'acts', className: 'p-3 text-center' }, 'Mouvement')
              ])
            ),
            h('tbody', { className: 'divide-y divide-slate-100' },
              stockItems.map(item =>
                h('tr', { key: item.id, className: 'hover:bg-slate-50 transition-colors' }, [
                  h('td', { key: 'code', className: 'p-3 font-mono font-bold text-slate-700' }, item.code),
                  h('td', { key: 'name', className: 'p-3' }, [
                    h('p', { key: 'n', className: 'font-bold text-slate-900' }, item.name),
                    item.dci && h('p', { key: 'dci', className: 'text-[11px] text-slate-400' }, item.dci)
                  ]),
                  h('td', { key: 'cat', className: 'p-3' },
                    h('span', { className: 'px-2 py-0.5 rounded text-[10px] font-bold bg-slate-100 text-slate-600' }, item.category)
                  ),
                  h('td', { key: 'qte', className: `p-3 text-center font-bold text-sm ${item.is_low_stock ? 'text-rose-600' : 'text-slate-900'}` }, `${item.current_quantity} ${item.unit}`),
                  h('td', { key: 'exp', className: 'p-3' }, item.expiration_date),
                  h('td', { key: 'st', className: 'p-3 text-center' },
                    item.is_expired ? h('span', { className: 'px-2 py-0.5 rounded-full font-bold text-[10px] bg-rose-600 text-white' }, 'PÉRIMÉ') :
                    item.is_near_expiry ? h('span', { className: 'px-2 py-0.5 rounded-full font-bold text-[10px] bg-amber-100 text-amber-800' }, 'Péremption proche') :
                    item.is_low_stock ? h('span', { className: 'px-2 py-0.5 rounded-full font-bold text-[10px] bg-rose-100 text-rose-800' }, 'Stock mini') :
                    h('span', { className: 'px-2 py-0.5 rounded-full font-bold text-[10px] bg-emerald-100 text-emerald-800' }, 'Normal')
                  ),
                  h('td', { key: 'acts', className: 'p-3 text-center space-x-1 rtl:space-x-reverse' }, [
                    h('button', {
                      key: 'in',
                      onClick: () => {
                        const qty = prompt(`Quantité à ajouter au stock de ${item.name} :`, '10');
                        if (qty && parseInt(qty) > 0) {
                          fetch(`/api/pharmacy/stock/${item.id}/movement`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ type: 'IN', quantity: parseInt(qty), reason: 'Réception commande' })
                          }).then(() => {
                            showToast('Entrée en stock enregistrée');
                            loadModuleData();
                          });
                        }
                      },
                      className: 'bg-emerald-50 text-emerald-700 hover:bg-emerald-100 border border-emerald-300 px-2 py-1 rounded text-xs font-bold'
                    }, '+ Entrée'),
                    h('button', {
                      key: 'out',
                      onClick: () => {
                        const qty = prompt(`Quantité à déstocker pour ${item.name} :`, '1');
                        if (qty && parseInt(qty) > 0) {
                          fetch(`/api/pharmacy/stock/${item.id}/movement`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ type: 'OUT', quantity: parseInt(qty), reason: 'Prescription / Service' })
                          })
                          .then(res => res.json())
                          .then(res => {
                            if (res.error) showToast(res.error, 'error');
                            else {
                              showToast('Sortie de stock enregistrée');
                              loadModuleData();
                            }
                          });
                        }
                      },
                      className: 'bg-slate-100 text-slate-700 hover:bg-slate-200 border border-slate-300 px-2 py-1 rounded text-xs font-bold'
                    }, '- Sortie')
                  ])
                ])
              )
            )
          )
        )
      )
    );
  }

  // ================= MODULE 8 : PERSONNEL & HONORAIRES =================
  function renderStaff() {
    return h('div', { className: 'space-y-6' },
      h('div', { className: 'bg-white p-5 rounded-xl border border-slate-200' },
        h('h2', { className: 'text-xl font-bold text-slate-900' }, t('nav_staff')),
        h('p', { className: 'text-xs text-slate-500' }, 'Fiches du personnel, planning des gardes et calcul automatique des honoraires / rétrocessions médecins')
      ),

      // Calcul des honoraires médecins (70% médecin / 30% clinique)
      h('div', { className: 'bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4' },
        h('h3', { className: 'font-bold text-slate-900 text-base flex items-center gap-2' }, '📊 Calcul des Rétrocessions & Honoraires Médecins'),
        h('div', { className: 'overflow-x-auto' },
          h('table', { className: 'w-full text-left rtl:text-right border-collapse text-xs' },
            h('thead', { className: 'bg-slate-50 text-slate-500 font-bold border-b border-slate-200 uppercase' },
              h('tr', {}, [
                h('th', { key: 'doc', className: 'p-3' }, 'Médecin Praticien'),
                h('th', { key: 'spec', className: 'p-3' }, 'Spécialité'),
                h('th', { key: 'type', className: 'p-3' }, 'Statut'),
                h('th', { key: 'cnum', className: 'p-3 text-center' }, 'Consultations'),
                h('th', { key: 'grand', className: 'p-3 text-right' }, 'CA Généré (MAD)'),
                h('th', { key: 'dshare', className: 'p-3 text-right font-bold text-emerald-700' }, 'Part Médecin (Honoraires)'),
                h('th', { key: 'cshare', className: 'p-3 text-right font-bold text-blue-700' }, 'Part Clinique')
              ])
            ),
            h('tbody', { className: 'divide-y divide-slate-100' },
              feeReport.map(f =>
                h('tr', { key: f.doctor_id, className: 'hover:bg-slate-50' }, [
                  h('td', { key: 'doc', className: 'p-3 font-bold text-slate-900' }, f.doctor_name),
                  h('td', { key: 'spec', className: 'p-3 text-slate-500' }, f.specialty),
                  h('td', { key: 'type', className: 'p-3' },
                    h('span', { className: 'px-2 py-0.5 rounded font-bold text-[10px] bg-slate-100 text-slate-700' }, f.doctor_type)
                  ),
                  h('td', { key: 'cnum', className: 'p-3 text-center font-bold' }, f.consultations_count),
                  h('td', { key: 'grand', className: 'p-3 text-right font-bold text-slate-900' }, `${f.grand_total_ca.toFixed(2)} MAD`),
                  h('td', { key: 'dshare', className: 'p-3 text-right font-bold text-emerald-600' }, `${f.doctor_share.toFixed(2)} MAD (${f.fee_rate}%)`),
                  h('td', { key: 'cshare', className: 'p-3 text-right font-bold text-blue-600' }, `${f.clinic_share.toFixed(2)} MAD`)
                ])
              )
            )
          )
        )
      ),

      // Planning des gardes et astreintes
      h('div', { className: 'bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4' },
        h('h3', { className: 'font-bold text-slate-900 text-base flex items-center gap-2' }, '🌙 Planning des Gardes de Nuit & Astreintes'),
        h('div', { className: 'grid grid-cols-1 md:grid-cols-3 gap-4' },
          shifts.map(s =>
            h('div', { key: s.id, className: 'p-4 rounded-xl border border-slate-200 bg-slate-50 space-y-2' },
              h('div', { className: 'flex justify-between items-center' },
                h('span', { className: 'text-xs font-bold text-slate-500' }, s.shift_date),
                h('span', { className: 'px-2 py-0.5 rounded text-[10px] font-bold bg-indigo-100 text-indigo-800' }, s.shift_type)
              ),
              h('h4', { className: 'font-bold text-sm text-slate-900' }, s.user_name),
              h('p', { className: 'text-xs text-slate-600' }, s.specialty || s.user_role),
              h('p', { className: 'text-[11px] text-slate-400 italic' }, s.notes || 'Service d’astreinte standard')
            )
          )
        )
      )
    );
  }

  // ================= MODULE 9 : COFFRE-FORT ARCHIVES (SOFT DELETE) =================
  function renderArchive() {
    return h('div', { className: 'space-y-6' },
      h('div', { className: 'bg-white p-5 rounded-xl border border-slate-200 flex flex-wrap justify-between items-center gap-3' },
        h('div', {},
          h('h2', { className: 'text-xl font-bold text-slate-900' }, t('nav_archive')),
          h('p', { className: 'text-xs text-slate-500' }, 'Recherche multicritères et coffre-fort historique (Soft Delete CNDP). Aucun dossier n’est jamais détruit.')
        ),
        h('input', {
          type: 'text',
          placeholder: 'Recherche archives par Nom, CIN, N°...',
          value: archiveSearch,
          onChange: (e) => setArchiveSearch(e.target.value),
          className: 'border border-slate-300 rounded-lg px-3 py-2 text-xs min-w-[240px]'
        })
      ),

      // Tableau des archives
      h('div', { className: 'bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm' },
        h('div', { className: 'overflow-x-auto' },
          h('table', { className: 'w-full text-left rtl:text-right border-collapse text-xs' },
            h('thead', { className: 'bg-slate-50 text-slate-500 font-bold border-b border-slate-200 uppercase' },
              h('tr', {}, [
                h('th', { key: 'type', className: 'p-3' }, 'Type'),
                h('th', { key: 'title', className: 'p-3' }, 'Élément Archivé'),
                h('th', { key: 'cin', className: 'p-3' }, 'CIN / Réf'),
                h('th', { key: 'date', className: 'p-3' }, 'Date d’Archivage'),
                h('th', { key: 'reason', className: 'p-3' }, 'Motif Légal (CNDP)'),
                h('th', { key: 'acts', className: 'p-3 text-center' }, 'Actions')
              ])
            ),
            h('tbody', { className: 'divide-y divide-slate-100' },
              archives.length === 0
                ? h('tr', {}, h('td', { colSpan: 6, className: 'p-8 text-center text-slate-400' }, 'Aucun élément trouvé dans les archives'))
                : archives.map((item, idx) =>
                    h('tr', { key: idx, className: 'hover:bg-slate-50' }, [
                      h('td', { key: 'type', className: 'p-3' },
                        h('span', { className: 'px-2 py-0.5 rounded font-bold text-[10px] bg-slate-200 text-slate-700' }, item.entity_type)
                      ),
                      h('td', { key: 'title', className: 'p-3 font-bold text-slate-900' }, item.title),
                      h('td', { key: 'cin', className: 'p-3 font-mono font-bold text-slate-700' }, item.cin),
                      h('td', { key: 'date', className: 'p-3 text-slate-500' }, item.archived_at),
                      h('td', { key: 'reason', className: 'p-3 text-slate-600 italic' }, item.reason),
                      h('td', { key: 'acts', className: 'p-3 text-center space-x-1 rtl:space-x-reverse' }, [
                        // Restauration 1-Clic vers la base active
                        h('button', {
                          key: 'rest',
                          onClick: () => {
                            fetch(`/api/archive/${item.entity_type}/${item.entity_id}/restore`, { method: 'POST' })
                              .then(res => res.json())
                              .then(data => {
                                showToast(data.message || 'Élément restauré');
                                loadModuleData();
                              });
                          },
                          className: 'bg-emerald-50 text-emerald-700 hover:bg-emerald-100 border border-emerald-300 px-2 py-1 rounded text-xs font-bold'
                        }, '🔄 Restaurer'),
                        // Si patient : Export numérique complet du dossier
                        item.entity_type === 'PATIENT' && h('button', {
                          key: 'exp',
                          onClick: () => window.open(`/api/archive/patients/${item.entity_id}/export`, '_blank'),
                          className: 'bg-blue-50 text-blue-700 hover:bg-blue-100 border border-blue-300 px-2 py-1 rounded text-xs font-bold'
                        }, '📥 Export JSON')
                      ])
                    ])
                  )
            )
          )
        )
      )
    );
  }

  // ================= MODULE 10 : AUDIT CNDP & SAUVEGARDES =================
  function renderAudit() {
    return h('div', { className: 'space-y-6' },
      h('div', { className: 'bg-white p-5 rounded-xl border border-slate-200 flex flex-wrap justify-between items-center gap-3' },
        h('div', {},
          h('h2', { className: 'text-xl font-bold text-slate-900' }, t('nav_audit')),
          h('p', { className: 'text-xs text-slate-500' }, 'Traçabilité inaltérable selon la loi marocaine CNDP 09-08 et sauvegardes automatiques de la base')
        ),
        h('button', {
          onClick: () => {
            fetch('/api/audit/backups/create', { method: 'POST' })
              .then(res => res.json())
              .then(data => {
                showToast(`Sauvegarde créée : ${data.filename} (${data.size_kb} KB)`);
                loadModuleData();
              });
          },
          className: 'bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs px-4 py-2.5 rounded-xl shadow'
        }, '💾 ' + t('btn_backup'))
      ),

      // Journal d'audit CNDP
      h('div', { className: 'bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm' },
        h('div', { className: 'overflow-x-auto max-h-[500px]' },
          h('table', { className: 'w-full text-left rtl:text-right border-collapse text-xs' },
            h('thead', { className: 'bg-slate-50 text-slate-500 font-bold border-b border-slate-200 uppercase sticky top-0' },
              h('tr', {}, [
                h('th', { key: 'time', className: 'p-3' }, 'Horodatage'),
                h('th', { key: 'user', className: 'p-3' }, 'Utilisateur / Rôle'),
                h('th', { key: 'act', className: 'p-3' }, 'Action CNDP'),
                h('th', { key: 'det', className: 'p-3' }, 'Détail de l’Opération'),
                h('th', { key: 'ip', className: 'p-3' }, 'Adresse IP')
              ])
            ),
            h('tbody', { className: 'divide-y divide-slate-100' },
              auditLogs.map(log =>
                h('tr', { key: log.id, className: 'hover:bg-slate-50' }, [
                  h('td', { key: 'time', className: 'p-3 font-mono text-slate-500' }, log.timestamp),
                  h('td', { key: 'user', className: 'p-3' }, [
                    h('p', { key: 'n', className: 'font-bold text-slate-900' }, log.user_name),
                    h('p', { key: 'r', className: 'text-[10px] text-slate-500' }, log.user_role)
                  ]),
                  h('td', { key: 'act', className: 'p-3' },
                    h('span', { className: `px-2 py-0.5 rounded font-bold text-[10px] ${
                      log.action === 'CREATE' ? 'bg-emerald-100 text-emerald-800' :
                      log.action === 'ARCHIVE' ? 'bg-amber-100 text-amber-800' :
                      log.action === 'EXPORT' ? 'bg-blue-100 text-blue-800' : 'bg-slate-100 text-slate-700'
                    }` }, log.action)
                  ),
                  h('td', { key: 'det', className: 'p-3 text-slate-700 font-medium' }, log.details),
                  h('td', { key: 'ip', className: 'p-3 font-mono text-[11px] text-slate-400' }, log.ip_address)
                ])
              )
            )
          )
        )
      )
    );
  }

  // ================= MODALES CONTEXTUELLES =================
  function renderActiveModal() {
    if (!activeModal) return null;

    return h('div', { className: 'fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4 fade-in overflow-y-auto' },
      h('div', { className: 'bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto border border-slate-200' },
        // Header de la modale
        h('div', { className: 'px-6 py-4 border-b border-slate-200 flex justify-between items-center sticky top-0 bg-white z-10' },
          h('h3', { className: 'font-bold text-base text-slate-900' },
            activeModal === 'new_patient' ? 'Inscription d’un Nouveau Patient' :
            activeModal === 'patient_dme' ? `Dossier Médical Électronique (DME) • ${selectedPatient ? selectedPatient.first_name_fr + ' ' + selectedPatient.last_name_fr : ''}` :
            activeModal === 'take_vitals' ? `Prise des Constantes Vitales • ${selectedPatient ? selectedPatient.first_name_fr : ''}` :
            activeModal === 'new_consultation' ? 'Consultation Médicale & Diagnostic CIM-10' :
            activeModal === 'new_invoice' ? 'Émission Facture Médicale (Dirhams MAD)' :
            activeModal === 'daily_closure' ? 'Clôture Journalière de Caisse' :
            activeModal === 'call_patient_announcement' ? '📢 Annonce Appel Patient' :
            activeModal === 'admit_patient' ? 'Admission Hospitalière & Affectation de Lit' :
            activeModal === 'add_stock' ? 'Entrée de Stock Médicaments' : 'Formulaire'
          ),
          h('button', {
            onClick: () => setActiveModal(null),
            className: 'text-slate-400 hover:text-slate-700 text-lg font-bold'
          }, '✕')
        ),

        // Corps de la modale
        h('div', { className: 'p-6' },
          activeModal === 'new_patient' && renderNewPatientForm(),
          activeModal === 'patient_dme' && renderPatientDMEView(),
          activeModal === 'take_vitals' && renderTakeVitalsForm(),
          activeModal === 'new_consultation' && renderNewConsultationForm(),
          activeModal === 'new_invoice' && renderNewInvoiceForm(),
          activeModal === 'daily_closure' && renderDailyClosureForm(),
          activeModal === 'call_patient_announcement' && renderCallPatientAnnouncement(),
          activeModal === 'admit_patient' && renderAdmitPatientForm(),
          activeModal === 'add_stock' && renderAddStockForm()
        )
      )
    );
  }

  // Modale : Inscription Patient
  function renderNewPatientForm() {
    return h('form', {
      onSubmit: (e) => {
        e.preventDefault();
        fetch('/api/patients', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(formData)
        })
        .then(res => res.json())
        .then(res => {
          if (res.error) showToast(res.error, 'error');
          else {
            showToast('Patient inscrit avec succès');
            setActiveModal(null);
            loadModuleData();
          }
        });
      },
      className: 'space-y-4 text-xs'
    }, [
      h('div', { key: 'r1', className: 'grid grid-cols-2 gap-3' }, [
        h('div', { key: 'cin' }, [
          h('label', { className: 'font-bold block mb-1' }, 'CIN (Carte Nationale) *'),
          h('input', {
            type: 'text',
            required: true,
            placeholder: 'Ex: S612345',
            value: formData.cin || '',
            onChange: (e) => setFormData({ ...formData, cin: e.target.value.toUpperCase() }),
            className: 'w-full border p-2 rounded'
          })
        ]),
        h('div', { key: 'phone' }, [
          h('label', { className: 'font-bold block mb-1' }, 'Téléphone Portable *'),
          h('input', {
            type: 'text',
            required: true,
            placeholder: '0661...',
            value: formData.phone || '',
            onChange: (e) => setFormData({ ...formData, phone: e.target.value }),
            className: 'w-full border p-2 rounded'
          })
        ])
      ]),
      h('div', { key: 'r2', className: 'grid grid-cols-2 gap-3' }, [
        h('div', { key: 'fnfr' }, [
          h('label', { className: 'font-bold block mb-1' }, 'Prénom (Français) *'),
          h('input', {
            type: 'text',
            required: true,
            value: formData.first_name_fr || '',
            onChange: (e) => setFormData({ ...formData, first_name_fr: e.target.value }),
            className: 'w-full border p-2 rounded'
          })
        ]),
        h('div', { key: 'lnfr' }, [
          h('label', { className: 'font-bold block mb-1' }, 'Nom (Français) *'),
          h('input', {
            type: 'text',
            required: true,
            value: formData.last_name_fr || '',
            onChange: (e) => setFormData({ ...formData, last_name_fr: e.target.value }),
            className: 'w-full border p-2 rounded'
          })
        ])
      ]),
      h('div', { key: 'r3', className: 'grid grid-cols-2 gap-3' }, [
        h('div', { key: 'fnar' }, [
          h('label', { className: 'font-bold block mb-1 font-arabic' }, 'الاسم الشخصي (بالعربية)'),
          h('input', {
            type: 'text',
            value: formData.first_name_ar || '',
            onChange: (e) => setFormData({ ...formData, first_name_ar: e.target.value }),
            className: 'w-full border p-2 rounded text-right font-arabic'
          })
        ]),
        h('div', { key: 'lnar' }, [
          h('label', { className: 'font-bold block mb-1 font-arabic' }, 'الاسم العائلي (بالعربية)'),
          h('input', {
            type: 'text',
            value: formData.last_name_ar || '',
            onChange: (e) => setFormData({ ...formData, last_name_ar: e.target.value }),
            className: 'w-full border p-2 rounded text-right font-arabic'
          })
        ])
      ]),
      h('div', { key: 'r4', className: 'grid grid-cols-3 gap-3' }, [
        h('div', { key: 'bdate' }, [
          h('label', { className: 'font-bold block mb-1' }, 'Date de Naissance'),
          h('input', {
            type: 'date',
            value: formData.birth_date || '1990-01-01',
            onChange: (e) => setFormData({ ...formData, birth_date: e.target.value }),
            className: 'w-full border p-2 rounded'
          })
        ]),
        h('div', { key: 'gender' }, [
          h('label', { className: 'font-bold block mb-1' }, 'Sexe'),
          h('select', {
            value: formData.gender || 'M',
            onChange: (e) => setFormData({ ...formData, gender: e.target.value }),
            className: 'w-full border p-2 rounded bg-white'
          }, [
            h('option', { key: 'M', value: 'M' }, 'Masculin (M)'),
            h('option', { key: 'F', value: 'F' }, 'Féminin (F)')
          ])
        ]),
        h('div', { key: 'quartier' }, [
          h('label', { className: 'font-bold block mb-1' }, 'Quartier (Nador)'),
          h('select', {
            value: formData.neighborhood || 'Hay Al Matar',
            onChange: (e) => setFormData({ ...formData, neighborhood: e.target.value }),
            className: 'w-full border p-2 rounded bg-white'
          }, [
            'Hay Al Matar', 'Bouizazarène', 'Selouane', 'Beni Ansar',
            'Hay Al Qods', 'Ulad Mimoun', 'Al Aroui', 'Zeghanghane', 'Zaio', 'Driouch'
          ].map(q => h('option', { key: q, value: q }, q)))
        ])
      ]),
      h('div', { key: 'r5', className: 'grid grid-cols-2 gap-3' }, [
        h('div', { key: 'mut' }, [
          h('label', { className: 'font-bold block mb-1' }, 'Organisme Mutuelle Marocaine'),
          h('select', {
            value: formData.mutuelle_type || 'CNOPS',
            onChange: (e) => {
              const val = e.target.value;
              const rate = val === 'CNOPS' ? 80 : val === 'CNSS' ? 70 : val === 'FAR' ? 90 : val === 'PRIVE' ? 0 : 80;
              setFormData({ ...formData, mutuelle_type: val, mutuelle_rate: rate });
            },
            className: 'w-full border p-2 rounded bg-white'
          }, [
            h('option', { key: 'CNOPS', value: 'CNOPS' }, 'CNOPS (AMO Public - 80%)'),
            h('option', { key: 'CNSS', value: 'CNSS' }, 'CNSS (AMO Salariés - 70%)'),
            h('option', { key: 'FAR', value: 'FAR' }, 'FAR (Forces Armées - 90%)'),
            h('option', { key: 'MGPAP', value: 'MGPAP' }, 'MGPAP (80%)'),
            h('option', { key: 'SAHAM', value: 'SAHAM' }, 'Saham / Sanlam'),
            h('option', { key: 'WAFA', value: 'WAFA' }, 'Wafa Assurance'),
            h('option', { key: 'PRIVE', value: 'PRIVE' }, 'Privé (Sans Mutuelle)')
          ])
        ]),
        h('div', { key: 'mutnum' }, [
          h('label', { className: 'font-bold block mb-1' }, 'N° Immatriculation Mutuelle'),
          h('input', {
            type: 'text',
            placeholder: 'N° Affiliation...',
            value: formData.mutuelle_number || '',
            onChange: (e) => setFormData({ ...formData, mutuelle_number: e.target.value }),
            className: 'w-full border p-2 rounded'
          })
        ])
      ]),
      h('div', { key: 'actions', className: 'flex justify-end gap-2 pt-4 border-t' }, [
        h('button', {
          type: 'button',
          onClick: () => setActiveModal(null),
          className: 'px-4 py-2 border rounded font-bold'
        }, t('btn_cancel')),
        h('button', {
          type: 'submit',
          className: 'px-4 py-2 bg-emerald-600 text-white rounded font-bold shadow'
        }, t('btn_save'))
      ])
    ]);
  }

  // Modale : Fiche Patient DME Complète
  function renderPatientDMEView() {
    if (!selectedPatient) return null;
    return h('div', { className: 'space-y-4 text-xs' },
      h('div', { className: 'bg-emerald-50 p-4 rounded-xl border border-emerald-200 flex justify-between items-center' },
        h('div', {},
          h('h4', { className: 'text-base font-bold text-emerald-950' }, `${selectedPatient.first_name_fr} ${selectedPatient.last_name_fr}`),
          h('p', { className: 'text-emerald-700' }, `CIN: ${selectedPatient.cin} • N° Dossier: ${selectedPatient.patient_number} • Tél: ${selectedPatient.phone}`)
        ),
        h('div', { className: 'text-right' },
          h('span', { className: 'font-bold px-2.5 py-1 rounded-full bg-emerald-200 text-emerald-900 text-xs' }, `${selectedPatient.mutuelle_type} (${selectedPatient.mutuelle_rate}%)`),
          h('p', { className: 'text-slate-500 text-[11px] mt-1' }, selectedPatient.neighborhood)
        )
      ),

      // Antécédents & Allergies
      h('div', { className: 'grid grid-cols-2 gap-3 bg-slate-50 p-3 rounded-lg border' },
        h('div', {},
          h('strong', { className: 'text-slate-700 block mb-1' }, 'Allergies Connues :'),
          h('span', { className: selectedPatient.allergies ? 'text-rose-600 font-bold' : 'text-slate-500' }, selectedPatient.allergies || 'Aucune allergie signalée')
        ),
        h('div', {},
          h('strong', { className: 'text-slate-700 block mb-1' }, 'Antécédents Médicaux :'),
          h('span', { className: 'text-slate-700' }, selectedPatient.medical_history || 'Aucun antécédent particulier')
        )
      ),

      // Historique des consultations & ordonnances
      h('div', { className: 'space-y-2' },
        h('h5', { className: 'font-bold text-slate-800 uppercase text-[11px]' }, 'Historique des Consultations & Prescriptions :'),
        selectedPatient.consultations && selectedPatient.consultations.length > 0
          ? selectedPatient.consultations.map(c =>
              h('div', { key: c.id, className: 'p-3 rounded-lg border bg-white space-y-1' }, [
                h('div', { key: 'top', className: 'flex justify-between items-center font-bold text-slate-900' },
                  h('span', {}, `${c.date} • Dr. ${c.doctor_name}`),
                  c.cim10_code && h('span', { className: 'px-2 py-0.5 rounded bg-blue-100 text-blue-800 text-[10px]' }, `CIM-10: ${c.cim10_code}`)
                ),
                h('p', { key: 'diag', className: 'text-emerald-800 font-semibold' }, `Diagnostic : ${c.diagnosis}`),
                c.clinical_notes && h('p', { key: 'notes', className: 'text-slate-600' }, `Notes : ${c.clinical_notes}`),
                c.prescriptions && c.prescriptions.length > 0 && h('div', { key: 'presc', className: 'mt-2 pt-2 border-t flex items-center justify-between' },
                  h('span', { className: 'text-[11px] font-bold text-slate-600' }, `Ordonnance (${c.prescriptions[0].items ? c.prescriptions[0].items.length : 0} médicaments)`),
                  h('button', {
                    onClick: () => window.open(`/api/medical/prescriptions/${c.prescriptions[0].id}/pdf`, '_blank'),
                    className: 'bg-emerald-50 text-emerald-700 border border-emerald-300 font-bold px-2 py-1 rounded text-xs hover:bg-emerald-100'
                  }, '📄 Imprimer Ordonnance PDF')
                )
              ])
            )
          : h('p', { className: 'text-slate-400 py-3 text-center' }, 'Aucune consultation enregistrée pour l’instant')
      ),

      // Bouton export dossier complet
      h('div', { className: 'flex justify-end pt-3 border-t' },
        h('button', {
          onClick: () => window.open(`/api/archive/patients/${selectedPatient.id}/export`, '_blank'),
          className: 'bg-blue-600 text-white font-bold px-4 py-2 rounded-lg text-xs shadow hover:bg-blue-700'
        }, '📥 Exporter Dossier Patient Complet (JSON/CNDP)')
      )
    );
  }

  // Modale : Prise des Constantes Vitales
  function renderTakeVitalsForm() {
    return h('form', {
      onSubmit: (e) => {
        e.preventDefault();
        fetch('/api/medical/vitals', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(formData)
        })
        .then(res => res.json())
        .then(() => {
          showToast('Constantes vitales enregistrées avec succès');
          setActiveModal(null);
          loadModuleData();
        });
      },
      className: 'space-y-4 text-xs'
    }, [
      h('div', { key: 'r1', className: 'grid grid-cols-2 gap-3' }, [
        h('div', { key: 'bp' }, [
          h('label', { className: 'font-bold block mb-1' }, 'Tension Artérielle (Systolique / Diastolique)'),
          h('div', { className: 'flex gap-2' }, [
            h('input', {
              type: 'number',
              placeholder: '120',
              value: formData.systolic_bp || '',
              onChange: (e) => setFormData({ ...formData, systolic_bp: e.target.value }),
              className: 'w-1/2 border p-2 rounded'
            }),
            h('input', {
              type: 'number',
              placeholder: '80',
              value: formData.diastolic_bp || '',
              onChange: (e) => setFormData({ ...formData, diastolic_bp: e.target.value }),
              className: 'w-1/2 border p-2 rounded'
            })
          ])
        ]),
        h('div', { key: 'hr' }, [
          h('label', { className: 'font-bold block mb-1' }, 'Pouls (bpm)'),
          h('input', {
            type: 'number',
            placeholder: '72',
            value: formData.heart_rate || '',
            onChange: (e) => setFormData({ ...formData, heart_rate: e.target.value }),
            className: 'w-full border p-2 rounded'
          })
        ])
      ]),
      h('div', { key: 'r2', className: 'grid grid-cols-3 gap-3' }, [
        h('div', { key: 'w' }, [
          h('label', { className: 'font-bold block mb-1' }, 'Poids (kg)'),
          h('input', {
            type: 'number',
            step: '0.1',
            placeholder: '75.0',
            value: formData.weight || '',
            onChange: (e) => setFormData({ ...formData, weight: e.target.value }),
            className: 'w-full border p-2 rounded'
          })
        ]),
        h('div', { key: 'h' }, [
          h('label', { className: 'font-bold block mb-1' }, 'Taille (cm)'),
          h('input', {
            type: 'number',
            placeholder: '175',
            value: formData.height || '',
            onChange: (e) => setFormData({ ...formData, height: e.target.value }),
            className: 'w-full border p-2 rounded'
          })
        ]),
        h('div', { key: 'temp' }, [
          h('label', { className: 'font-bold block mb-1' }, 'Température (°C)'),
          h('input', {
            type: 'number',
            step: '0.1',
            placeholder: '37.0',
            value: formData.temperature || '',
            onChange: (e) => setFormData({ ...formData, temperature: e.target.value }),
            className: 'w-full border p-2 rounded'
          })
        ])
      ]),
      h('div', { key: 'r3', className: 'grid grid-cols-2 gap-3' }, [
        h('div', { key: 'spo2' }, [
          h('label', { className: 'font-bold block mb-1' }, 'SpO2 (% Oxygène)'),
          h('input', {
            type: 'number',
            placeholder: '98',
            value: formData.spo2 || '',
            onChange: (e) => setFormData({ ...formData, spo2: e.target.value }),
            className: 'w-full border p-2 rounded'
          })
        ]),
        h('div', { key: 'gly' }, [
          h('label', { className: 'font-bold block mb-1' }, 'Glycémie (g/L)'),
          h('input', {
            type: 'number',
            step: '0.01',
            placeholder: '1.05',
            value: formData.blood_glucose || '',
            onChange: (e) => setFormData({ ...formData, blood_glucose: e.target.value }),
            className: 'w-full border p-2 rounded'
          })
        ])
      ]),
      h('div', { key: 'actions', className: 'flex justify-end gap-2 pt-3 border-t' }, [
        h('button', {
          type: 'button',
          onClick: () => setActiveModal(null),
          className: 'px-4 py-2 border rounded font-bold'
        }, t('btn_cancel')),
        h('button', {
          type: 'submit',
          className: 'px-4 py-2 bg-emerald-600 text-white rounded font-bold shadow'
        }, t('btn_save'))
      ])
    ]);
  }

  // Modale : Nouvelle Consultation Médicale
  function renderNewConsultationForm() {
    return h('form', {
      onSubmit: (e) => {
        e.preventDefault();
        fetch('/api/medical/consultations', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(formData)
        })
        .then(res => res.json())
        .then(res => {
          showToast('Consultation enregistrée avec succès');
          setActiveModal(null);
          loadModuleData();
        });
      },
      className: 'space-y-4 text-xs'
    }, [
      h('div', { key: 'pat' }, [
        h('label', { className: 'font-bold block mb-1' }, 'Patient *'),
        h('select', {
          required: true,
          value: formData.patient_id || '',
          onChange: (e) => setFormData({ ...formData, patient_id: e.target.value }),
          className: 'w-full border p-2 rounded bg-white'
        }, [
          h('option', { key: '', value: '' }, '-- Sélectionner un patient --'),
          patients.map(p => h('option', { key: p.id, value: p.id }, `${p.first_name_fr} ${p.last_name_fr} (CIN: ${p.cin})`))
        ])
      ]),
      h('div', { key: 'cim10' }, [
        h('label', { className: 'font-bold block mb-1' }, 'Codification Diagnostique CIM-10 (OMS)'),
        h('select', {
          value: formData.cim10_code || '',
          onChange: (e) => {
            const found = cim10List.find(c => c.code === e.target.value);
            setFormData({
              ...formData,
              cim10_code: e.target.value,
              cim10_description: found ? found.description : '',
              diagnosis: found ? found.description : formData.diagnosis
            });
          },
          className: 'w-full border p-2 rounded bg-white'
        }, [
          h('option', { key: '', value: '' }, '-- Choisir un code CIM-10 fréquent au Maroc --'),
          cim10List.map(c => h('option', { key: c.code, value: c.code }, `${c.code} - ${c.description}`))
        ])
      ]),
      h('div', { key: 'diag' }, [
        h('label', { className: 'font-bold block mb-1' }, 'Diagnostic Médical Établi *'),
        h('input', {
          type: 'text',
          required: true,
          placeholder: 'Ex: Hypertension artérielle modérée, angine...',
          value: formData.diagnosis || '',
          onChange: (e) => setFormData({ ...formData, diagnosis: e.target.value }),
          className: 'w-full border p-2 rounded'
        })
      ]),
      h('div', { key: 'notes' }, [
        h('label', { className: 'font-bold block mb-1' }, 'Notes Cliniques & Conseils'),
        h('textarea', {
          rows: 2,
          placeholder: 'Observations cliniques...',
          value: formData.clinical_notes || '',
          onChange: (e) => setFormData({ ...formData, clinical_notes: e.target.value }),
          className: 'w-full border p-2 rounded'
        })
      ]),
      h('div', { key: 'meds', className: 'space-y-2 border-t pt-3' }, [
        h('div', { className: 'flex justify-between items-center' },
          h('span', { className: 'font-bold text-slate-800' }, 'Prescription Médicamenteuse :'),
          h('button', {
            type: 'button',
            onClick: () => {
              const cur = formData.medications || [];
              setFormData({ ...formData, medications: [...cur, { name: '', dosage: '', frequency: '', duration: '' }] });
            },
            className: 'text-xs text-emerald-600 font-bold'
          }, '+ Ajouter médicament')
        ),
        (formData.medications || []).map((med, idx) =>
          h('div', { key: idx, className: 'grid grid-cols-4 gap-2 bg-slate-50 p-2 rounded' }, [
            h('input', {
              key: 'n',
              placeholder: 'Médicament (ex: Amoxicilline 1g)',
              value: med.name || '',
              onChange: (e) => {
                const arr = [...formData.medications];
                arr[idx].name = e.target.value;
                setFormData({ ...formData, medications: arr });
              },
              className: 'border p-1 rounded text-xs'
            }),
            h('input', {
              key: 'd',
              placeholder: 'Posologie (1 cp)',
              value: med.dosage || '',
              onChange: (e) => {
                const arr = [...formData.medications];
                arr[idx].dosage = e.target.value;
                setFormData({ ...formData, medications: arr });
              },
              className: 'border p-1 rounded text-xs'
            }),
            h('input', {
              key: 'f',
              placeholder: 'Fréquence (3x/j)',
              value: med.frequency || '',
              onChange: (e) => {
                const arr = [...formData.medications];
                arr[idx].frequency = e.target.value;
                setFormData({ ...formData, medications: arr });
              },
              className: 'border p-1 rounded text-xs'
            }),
            h('input', {
              key: 'dur',
              placeholder: 'Durée (7j)',
              value: med.duration || '',
              onChange: (e) => {
                const arr = [...formData.medications];
                arr[idx].duration = e.target.value;
                setFormData({ ...formData, medications: arr });
              },
              className: 'border p-1 rounded text-xs'
            })
          ])
        )
      ]),
      h('div', { key: 'actions', className: 'flex justify-end gap-2 pt-3 border-t' }, [
        h('button', {
          type: 'button',
          onClick: () => setActiveModal(null),
          className: 'px-4 py-2 border rounded font-bold'
        }, t('btn_cancel')),
        h('button', {
          type: 'submit',
          className: 'px-4 py-2 bg-emerald-600 text-white rounded font-bold shadow'
        }, 'Valider & Créer Consultation')
      ])
    ]);
  }

  // Modale : Nouvelle Facture
  function renderNewInvoiceForm() {
    return h('form', {
      onSubmit: (e) => {
        e.preventDefault();
        fetch('/api/billing/invoices', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(formData)
        })
        .then(res => res.json())
        .then(res => {
          showToast('Facture médicale émise avec succès');
          setActiveModal(null);
          loadModuleData();
        });
      },
      className: 'space-y-4 text-xs'
    }, [
      h('div', { key: 'pat' }, [
        h('label', { className: 'font-bold block mb-1' }, 'Patient à facturer *'),
        h('select', {
          required: true,
          value: formData.patient_id || '',
          onChange: (e) => setFormData({ ...formData, patient_id: e.target.value }),
          className: 'w-full border p-2 rounded bg-white'
        }, [
          h('option', { key: '', value: '' }, '-- Sélectionner un patient --'),
          patients.map(p => h('option', { key: p.id, value: p.id }, `${p.first_name_fr} ${p.last_name_fr} (${p.mutuelle_type})`))
        ])
      ]),
      h('div', { key: 'act' }, [
        h('label', { className: 'font-bold block mb-1' }, 'Acte Médical (Nomenclature NGAP Maroc) *'),
        h('select', {
          onChange: (e) => {
            const found = actsCatalog.find(a => a.code === e.target.value);
            if (found) {
              setFormData({
                ...formData,
                items: [{ act_code: found.code, description: found.description, quantity: 1, unit_price: found.unit_price }]
              });
            }
          },
          className: 'w-full border p-2 rounded bg-white'
        }, [
          h('option', { key: '', value: '' }, '-- Choisir un acte dans la nomenclature --'),
          actsCatalog.map(a => h('option', { key: a.code, value: a.code }, `${a.code} - ${a.description} (${a.unit_price} MAD)`))
        ])
      ]),
      h('div', { key: 'pm' }, [
        h('label', { className: 'font-bold block mb-1' }, 'Mode de Règlement'),
        h('select', {
          value: formData.payment_method || 'CASH',
          onChange: (e) => setFormData({ ...formData, payment_method: e.target.value }),
          className: 'w-full border p-2 rounded bg-white'
        }, [
          h('option', { key: 'CASH', value: 'CASH' }, 'Espèces (Cash)'),
          h('option', { key: 'CARD', value: 'CARD' }, 'Carte Bancaire (TPE)'),
          h('option', { key: 'CHECK', value: 'CHECK' }, 'Chèque bancaire'),
          h('option', { key: 'TRANSFER', value: 'TRANSFER' }, 'Virement bancaire')
        ])
      ]),
      h('div', { key: 'actions', className: 'flex justify-end gap-2 pt-3 border-t' }, [
        h('button', {
          type: 'button',
          onClick: () => setActiveModal(null),
          className: 'px-4 py-2 border rounded font-bold'
        }, t('btn_cancel')),
        h('button', {
          type: 'submit',
          className: 'px-4 py-2 bg-emerald-600 text-white rounded font-bold shadow'
        }, 'Émettre Facture')
      ])
    ]);
  }

  // Modale : Clôture de Caisse Journalière
  function renderDailyClosureForm() {
    return h('form', {
      onSubmit: (e) => {
        e.preventDefault();
        fetch('/api/billing/cash-closures', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(formData)
        })
        .then(res => res.json())
        .then(res => {
          showToast('Caisse journalière clôturée et archivée');
          setActiveModal(null);
          loadModuleData();
        });
      },
      className: 'space-y-4 text-xs'
    }, [
      h('div', { key: 'open' }, [
        h('label', { className: 'font-bold block mb-1' }, 'Fond de Caisse Initial (MAD)'),
        h('input', {
          type: 'number',
          value: formData.opening_amount || 1000,
          onChange: (e) => setFormData({ ...formData, opening_amount: e.target.value }),
          className: 'w-full border p-2 rounded'
        })
      ]),
      h('div', { key: 'act' }, [
        h('label', { className: 'font-bold block mb-1' }, 'Montant Réel en Espèces Présent dans le Tiroir-Caisse (MAD) *'),
        h('input', {
          type: 'number',
          required: true,
          value: formData.actual_cash || '',
          onChange: (e) => setFormData({ ...formData, actual_cash: e.target.value }),
          className: 'w-full border p-2 rounded text-base font-bold text-emerald-800'
        })
      ]),
      h('div', { key: 'notes' }, [
        h('label', { className: 'font-bold block mb-1' }, 'Remarques ou Justificatifs d’Écart éventuel'),
        h('textarea', {
          rows: 2,
          value: formData.notes || '',
          onChange: (e) => setFormData({ ...formData, notes: e.target.value }),
          className: 'w-full border p-2 rounded'
        })
      ]),
      h('div', { key: 'actions', className: 'flex justify-end gap-2 pt-3 border-t' }, [
        h('button', {
          type: 'button',
          onClick: () => setActiveModal(null),
          className: 'px-4 py-2 border rounded font-bold'
        }, t('btn_cancel')),
        h('button', {
          type: 'submit',
          className: 'px-4 py-2 bg-slate-900 text-white rounded font-bold shadow'
        }, 'Valider Clôture de Caisse')
      ])
    ]);
  }

  // Modale : Annonce Appel Patient
  function renderCallPatientAnnouncement() {
    if (!selectedEntry) return null;
    return h('div', { className: 'text-center space-y-4 py-4' },
      h('div', { className: 'text-5xl mb-2 animate-bounce' }, '📢'),
      h('h3', { className: 'text-lg font-bold text-slate-900' }, selectedEntry.announcement_fr),
      h('h3', { className: 'text-lg font-bold text-emerald-700 font-arabic mt-2' }, selectedEntry.announcement_ar),
      h('div', { className: 'bg-emerald-50 border border-emerald-200 p-3 rounded-xl max-w-sm mx-auto mt-4' },
        h('p', { className: 'text-xs text-slate-600' }, 'Lieu d’accueil :'),
        h('p', { className: 'text-sm font-bold text-emerald-900' }, selectedEntry.cabinet)
      ),
      h('button', {
        onClick: () => setActiveModal(null),
        className: 'mt-6 bg-emerald-600 text-white font-bold px-6 py-2 rounded-xl text-xs shadow'
      }, 'Fermer')
    );
  }

  // Modale : Admission Hospitalière
  function renderAdmitPatientForm() {
    return h('form', {
      onSubmit: (e) => {
        e.preventDefault();
        fetch('/api/inpatient/admissions', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(formData)
        })
        .then(res => res.json())
        .then(res => {
          if (res.error) showToast(res.error, 'error');
          else {
            showToast('Patient admis en hospitalisation');
            setActiveModal(null);
            loadModuleData();
          }
        });
      },
      className: 'space-y-4 text-xs'
    }, [
      h('div', { key: 'pat' }, [
        h('label', { className: 'font-bold block mb-1' }, 'Patient à admettre *'),
        h('select', {
          required: true,
          value: formData.patient_id || '',
          onChange: (e) => setFormData({ ...formData, patient_id: e.target.value }),
          className: 'w-full border p-2 rounded bg-white'
        }, [
          h('option', { key: '', value: '' }, '-- Sélectionner un patient --'),
          patients.map(p => h('option', { key: p.id, value: p.id }, `${p.first_name_fr} ${p.last_name_fr} (CIN: ${p.cin})`))
        ])
      ]),
      h('div', { key: 'reason' }, [
        h('label', { className: 'font-bold block mb-1' }, 'Motif d’Hospitalisation *'),
        h('input', {
          type: 'text',
          required: true,
          placeholder: 'Ex: Surveillance post-opératoire, crise hypertensive...',
          value: formData.reason || '',
          onChange: (e) => setFormData({ ...formData, reason: e.target.value }),
          className: 'w-full border p-2 rounded'
        })
      ]),
      h('div', { key: 'acts' }, [
        h('label', { className: 'font-bold block mb-1' }, 'Actes Chirurgicaux / Soins programmés'),
        h('input', {
          type: 'text',
          placeholder: 'Ex: Appendicectomie sous cœlioscopie',
          value: formData.surgical_acts || '',
          onChange: (e) => setFormData({ ...formData, surgical_acts: e.target.value }),
          className: 'w-full border p-2 rounded'
        })
      ]),
      h('div', { key: 'actions', className: 'flex justify-end gap-2 pt-3 border-t' }, [
        h('button', {
          type: 'button',
          onClick: () => setActiveModal(null),
          className: 'px-4 py-2 border rounded font-bold'
        }, t('btn_cancel')),
        h('button', {
          type: 'submit',
          className: 'px-4 py-2 bg-emerald-600 text-white rounded font-bold shadow'
        }, 'Confirmer l’Admission')
      ])
    ]);
  }

  // Modale : Entrée de Stock Pharmacie
  function renderAddStockForm() {
    return h('form', {
      onSubmit: (e) => {
        e.preventDefault();
        fetch('/api/pharmacy/stock', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(formData)
        })
        .then(res => res.json())
        .then(res => {
          showToast('Article ajouté au stock');
          setActiveModal(null);
          loadModuleData();
        });
      },
      className: 'space-y-4 text-xs'
    }, [
      h('div', { key: 'r1', className: 'grid grid-cols-2 gap-3' }, [
        h('div', { key: 'c' }, [
          h('label', { className: 'font-bold block mb-1' }, 'Code Article / Référence *'),
          h('input', {
            type: 'text',
            required: true,
            placeholder: 'MED-AMOX-1G',
            value: formData.code || '',
            onChange: (e) => setFormData({ ...formData, code: e.target.value.toUpperCase() }),
            className: 'w-full border p-2 rounded'
          })
        ]),
        h('div', { key: 'n' }, [
          h('label', { className: 'font-bold block mb-1' }, 'Désignation Commerciale *'),
          h('input', {
            type: 'text',
            required: true,
            placeholder: 'Ex: Amoxicilline 1g',
            value: formData.name || '',
            onChange: (e) => setFormData({ ...formData, name: e.target.value }),
            className: 'w-full border p-2 rounded'
          })
        ])
      ]),
      h('div', { key: 'r2', className: 'grid grid-cols-3 gap-3' }, [
        h('div', { key: 'cat' }, [
          h('label', { className: 'font-bold block mb-1' }, 'Catégorie'),
          h('select', {
            value: formData.category || 'MEDICAMENT',
            onChange: (e) => setFormData({ ...formData, category: e.target.value }),
            className: 'w-full border p-2 rounded bg-white'
          }, [
            h('option', { key: 'MEDICAMENT', value: 'MEDICAMENT' }, 'Médicament'),
            h('option', { key: 'CONSOMMABLE', value: 'CONSOMMABLE' }, 'Consommable'),
            h('option', { key: 'URGENCE', value: 'URGENCE' }, 'Urgence'),
            h('option', { key: 'MATERIEL', value: 'MATERIEL' }, 'Matériel')
          ])
        ]),
        h('div', { key: 'q' }, [
          h('label', { className: 'font-bold block mb-1' }, 'Quantité'),
          h('input', {
            type: 'number',
            value: formData.current_quantity || 20,
            onChange: (e) => setFormData({ ...formData, current_quantity: e.target.value }),
            className: 'w-full border p-2 rounded'
          })
        ]),
        h('div', { key: 'exp' }, [
          h('label', { className: 'font-bold block mb-1' }, 'Date Péremption *'),
          h('input', {
            type: 'date',
            required: true,
            value: formData.expiration_date || '2027-12-31',
            onChange: (e) => setFormData({ ...formData, expiration_date: e.target.value }),
            className: 'w-full border p-2 rounded'
          })
        ])
      ]),
      h('div', { key: 'actions', className: 'flex justify-end gap-2 pt-3 border-t' }, [
        h('button', {
          type: 'button',
          onClick: () => setActiveModal(null),
          className: 'px-4 py-2 border rounded font-bold'
        }, t('btn_cancel')),
        h('button', {
          type: 'submit',
          className: 'px-4 py-2 bg-emerald-600 text-white rounded font-bold shadow'
        }, 'Enregistrer en Stock')
      ])
    ]);
  }
}

// Montage de l'application React
document.addEventListener('DOMContentLoaded', () => {
  const rootElement = document.getElementById('root');
  if (rootElement) {
    const root = ReactDOM.createRoot(rootElement);
    root.render(h(App));
  }
});
