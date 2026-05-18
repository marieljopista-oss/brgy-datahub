/* ================================================
   BARANGAY DATAHUB — app.js
   Global JavaScript shared by ALL pages
   ================================================ */

'use strict';

/* ------------------------------------------------
   TOAST NOTIFICATIONS
   Usage: showToast('Saved!', 'success')
   Types: 'success' | 'error' | 'warning' | 'info'
   ------------------------------------------------ */
function showToast(message, type = 'success', duration = 3000) {
  // Create container if it doesn't exist
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }

  const icons = { success: '✅', error: '❌', warning: '⚠️', info: 'ℹ️' };

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `
    <span class="toast-icon">${icons[type] || '✅'}</span>
    <span class="toast-msg">${message}</span>
    <button class="toast-close" onclick="this.parentElement.remove()">✕</button>
  `;

  container.appendChild(toast);

  // Auto-remove after duration
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transition = 'opacity 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

/* ------------------------------------------------
   CONFIRM DIALOG
   Usage: showConfirm('Delete this?', 'Cannot undo.', () => doDelete())
   ------------------------------------------------ */
function showConfirm(title, message, onConfirm) {
  // Remove any existing confirm dialog
  const existing = document.getElementById('confirm-dialog');
  if (existing) existing.remove();

  const overlay = document.createElement('div');
  overlay.id = 'confirm-dialog';
  overlay.className = 'confirm-overlay open';
  overlay.innerHTML = `
    <div class="confirm-box">
      <div class="confirm-icon">🗑️</div>
      <div class="confirm-title">${title}</div>
      <div class="confirm-msg">${message}</div>
      <div class="confirm-actions">
        <button class="btn btn-outline" id="confirm-cancel">Cancel</button>
        <button class="btn btn-danger" id="confirm-ok">Yes, Delete</button>
      </div>
    </div>
  `;
  document.body.appendChild(overlay);

  document.getElementById('confirm-cancel').onclick = () => overlay.remove();
  document.getElementById('confirm-ok').onclick = () => {
    onConfirm();
    overlay.remove();
  };

  // Close on backdrop click
  overlay.addEventListener('click', (e) => { if (e.target === overlay) overlay.remove(); });
}

/* ------------------------------------------------
   MODAL HELPERS
   ------------------------------------------------ */
function openModal(id) {
  const el = document.getElementById(id);
  if (el) {
    el.classList.add('open');
    // Focus first input
    setTimeout(() => { const inp = el.querySelector('input, select, textarea'); if (inp) inp.focus(); }, 100);
  }
}
function closeModal(id) {
  const el = document.getElementById(id);
  if (el) el.classList.remove('open');
}

// Close modal on backdrop click — auto-applied to all .modal-overlay elements
document.addEventListener('click', function(e) {
  if (e.target.classList.contains('modal-overlay')) {
    e.target.classList.remove('open');
  }
});

// Close modal on Escape key
document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') {
    document.querySelectorAll('.modal-overlay.open').forEach(m => m.classList.remove('open'));
    const confirmDialog = document.getElementById('confirm-dialog');
    if (confirmDialog) confirmDialog.remove();
  }
});

/* ------------------------------------------------
   TAB SWITCHER
   Usage: initTabs('tab-bar-id') — auto-init on DOMContentLoaded
   ------------------------------------------------ */
function switchTab(tabName, clickedBtn, groupId) {
  // Hide all panels in this group
  const panels = document.querySelectorAll(`[data-group="${groupId}"]`);
  panels.forEach(p => p.classList.remove('active'));

  // Show the selected panel
  const target = document.getElementById('tab-' + tabName);
  if (target) target.classList.add('active');

  // Update active button
  const buttons = clickedBtn.parentElement.querySelectorAll('.tab-btn');
  buttons.forEach(b => b.classList.remove('active'));
  clickedBtn.classList.add('active');
}

/* ------------------------------------------------
   SEARCH / FILTER TABLE
   Usage: filterTable('tableId', 'searchInputId')
   ------------------------------------------------ */
function filterTable(tableId, searchValue) {
  const table = document.getElementById(tableId);
  if (!table) return;
  const rows = table.querySelectorAll('tbody tr');
  const val  = searchValue.toLowerCase().trim();

  rows.forEach(row => {
    const text = row.textContent.toLowerCase();
    row.style.display = text.includes(val) ? '' : 'none';
  });
}

/* ------------------------------------------------
   CALCULATE AGE from birth date string
   ------------------------------------------------ */
function calcAge(birthDateStr) {
  if (!birthDateStr) return '—';
  const today = new Date();
  const birth = new Date(birthDateStr);
  if (isNaN(birth)) return '—';
  let age = today.getFullYear() - birth.getFullYear();
  const m = today.getMonth() - birth.getMonth();
  if (m < 0 || (m === 0 && today.getDate() < birth.getDate())) age--;
  return age < 0 ? 0 : age;
}

/* ------------------------------------------------
   FORMAT DATE for display
   ------------------------------------------------ */
function formatDate(dateStr) {
  if (!dateStr) return '—';
  const d = new Date(dateStr);
  if (isNaN(d)) return '—';
  return d.toLocaleDateString('en-PH', { year: 'numeric', month: 'short', day: 'numeric' });
}

/* ------------------------------------------------
   FORM VALIDATION — checks required fields
   Usage: validateForm(formElement) → true/false
   ------------------------------------------------ */
function validateForm(form) {
  let valid = true;
  form.querySelectorAll('[required]').forEach(field => {
    field.style.borderColor = '';
    if (!field.value.trim()) {
      field.style.borderColor = '#e05252';
      field.style.boxShadow = '0 0 0 3px rgba(224,82,82,0.12)';
      valid = false;
    }
  });
  return valid;
}

/* ------------------------------------------------
   TOGGLE EMPTY STATE visibility
   Shows empty-state div when table has no rows
   ------------------------------------------------ */
function updateEmptyState(tableBodyId, emptyStateId) {
  const body  = document.getElementById(tableBodyId);
  const empty = document.getElementById(emptyStateId);
  if (!body || !empty) return;
  const hasRows = body.querySelectorAll('tr').length > 0;
  empty.style.display = hasRows ? 'none' : '';
}

/* ------------------------------------------------
   PRINT / EXPORT helpers
   ------------------------------------------------ */
function printPage() { window.print(); }

/* ------------------------------------------------
   ACTIVE NAV LINK highlight (for home menu)
   ------------------------------------------------ */
document.addEventListener('DOMContentLoaded', function() {
  // Mark current page link active if on home menu
  const links = document.querySelectorAll('.menu-btn');
  links.forEach(link => {
    if (link.href === window.location.href) {
      link.style.opacity = '0.7';
    }
  });
});
