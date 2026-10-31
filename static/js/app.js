/**
 * TAX_RAHISI - Main JS Fixed
 */

//==== 0. CORE UTILS ===
function getCSRF(){
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
           document.cookie.split('; ').find(r=>r.startsWith('csrftoken='))?.split('=')[1]; 
}

function formatTZS(num){
    return 'TZS ' + (num||0).toLocaleString('sw-TZ');
}

function isZanzibarRegion(region){
    return ['Mjini Magharibi', 'Kusini Unguja', 'Kaskazini Unguja', 'Kusini Pemba', 'Kaskazini Pemba'].includes(region);
}

document.addEventListener('DOMContentLoaded', () => {
    setTimeout(()=> document.querySelectorAll('.alert-auto').forEach(a=>a.remove()), 5000);
    initAccounts();
    initTaxpayers();
    initBusinesses();
    initTaxation();
    initSalesExpenses();
    initPayments();
    initReports();
    initNotifications();
});

// ===== 1. ACCOUNTS =======
function initAccounts(){
    const form = document.getElementById('registerForm');
    if (!form) return;
    form.addEventListener('submit', e => {
        const tin = document.getElementById('id_tin')?.value || '';
        if(tin && !/^\d{9}$/.test(tin.replace(/-/g,''))){
            e.preventDefault();
            alert('TIN si sahihi. Weka namba 9: mfano 123456789');
        }
    });
}

// ===== 2. TAXPAYERS ==========
function initTaxpayers(){
    const regionSelect = document.getElementById('id_region');
    if(!regionSelect) return;
    const toggleZRB = () => {
        const isZ = isZanzibarRegion(regionSelect.value);
        const badge = document.getElementById('region-badge');
        if(badge) badge.textContent = isZ ? 'ZRB - Zanzibar Revenue Board' : 'TRA - Tanzania Revenue Authority';
    };
    regionSelect.addEventListener('change', toggleZRB);
    toggleZRB();
}

async function searchTaxpayer(tin){
    const res = await fetch(`/taxpayers/api/search/?tin=${tin}`);
    return await res.json();
}

// ======== 3. BUSINESSES ==========
function initBusinesses(){
    const el = document.getElementById('annual-turnover');
    if(!el) return;
    const turnover = parseFloat(el.dataset.turnover || 0);
    if (turnover >= 100000000){
        const alertBox = document.getElementById('vat-alert');
        if(alertBox) alertBox.innerHTML = '<div class="alert alert-warning fw-bold">Biashara imevuka 100M - Lazima usajili VAT TRA/ZRB!</div>';
    }
}

//  ======= 4. TAXATION - Hesabu za TRA =========
const TaxTZ = {
    calcPAYE(salary){
        let brackets = [[270000,0],[520000,0.08],[760000,0.20],[1000000,0.25],[Infinity,0.30]];
        let tax=0, prev=0;
        for(let [upto, rate] of brackets){
            if(salary<=prev) break;
            let taxable = Math.min(salary, upto) - prev;
            if(taxable>0) tax += taxable*rate;
            prev=upto;
        }
        return Math.round(tax);
    },
    calcVAT(amount, inclusive=false){
        return inclusive ? (amount*18/118) : (amount*0.18);
    },
    calcCorporate(profit){
        return profit*0.30;
    },
    calcWithholding(amount, type){
        const rates = {rent:0.10, dividend:0.10, interest:0.10, professional:0.05, service:0.05};
        return amount * (rates[type] || 0.05);
    },
    calcPresumptive(turnover){
        if(turnover < 4000000) return 0;
        if(turnover <= 7000000) return 100000;
        if(turnover <= 11000000) return 250000;
        if(turnover <= 14000000) return 450000;
        if(turnover <= 18000000) return 650000;
        return 0;
    }
};

function initTaxation(){
    const grossInput = document.getElementById('id_gross');
    const payePreview = document.getElementById('paye-preview');
    if(grossInput && payePreview){
        grossInput.addEventListener('input', function(){
            let amt = parseFloat(this.value.replace(/,/g,''))||0;
            let paye = TaxTZ.calcPAYE(amt);
            payePreview.innerHTML = `PAYE: <b>${formatTZS(paye)}</b> | Net: <b>${formatTZS(amt-paye)}</b>`;
        });
    }
    const profitInput = document.getElementById('id_profit');
    const corpPreview = document.getElementById('corporate-preview');
    if(profitInput && corpPreview){
        profitInput.addEventListener('input', function(){
            let p = parseFloat(this.value)||0;
            corpPreview.innerText = `Corporate Tax (30%): ${formatTZS(TaxTZ.calcCorporate(p))}`;
        });
    }
}

// ====== 5. SALES & EXPENSES ===========
function initSalesExpenses(){
    const excl = document.getElementById('id_amount_excl_vat');
    const vat = document.getElementById('id_vat_amount');
    const incl = document.getElementById('id_amount_incl_vat');
    if(excl){
        excl.addEventListener('input', function(){
            let v = parseFloat(this.value)||0;
            if(vat) vat.value = (v*0.18).toFixed(2);
            if(incl) incl.value = (v*1.18).toFixed(2);
        });
    }
    const hasEfd = document.getElementById('id_has_efd_receipt');
    const efdNo = document.getElementById('id_efd_receipt_no');
    if(hasEfd && efdNo){
        const toggle = () => {
            efdNo.closest('.form-group').style.display = hasEfd.checked ? 'block' : 'none';
        };
        hasEfd.addEventListener('change', toggle);
        toggle();
    }
    document.getElementById('expenseForm')?.addEventListener('submit', e=>{
        const cat = document.getElementById('id_category')?.value;
        const receipt = document.getElementById('id_receipt_number')?.value;
        if(cat==='CAPITAL' && !receipt){
            e.preventDefault();
            alert('Matumizi ya mtaji yanahitaji namba ya risiti!');
        }
    });
}

// ====== 6. PAYMENTS - GePG & ZanMalipo ========
function initPayments(){
    document.getElementById('copy-cn')?.addEventListener('click', function(){
        navigator.clipboard.writeText(this.dataset.cn);
        this.innerHTML = 'Imenakiliwa!';
        setTimeout(() => this.innerHTML = 'Copy Control Number', 2000);
    });
}

async function requestControlNumber(assessmentId){
    const btn = document.getElementById('btn-request-cn');
    if(btn) btn.innerHTML = 'Inaomba...';
    const res = await fetch(`/payments/create/${assessmentId}/`,{
        method:'POST', headers:{'X-CSRFToken': getCSRF()}
    });
    location.reload();    
}

function checkPaymentStatus(paymentId){
    let interval = setInterval(async () =>{
        try{
            let r = await fetch(`/payments/api/status/${paymentId}/`);
            let d = await r.json();
            if(d.status==='PAID'){
                clearInterval(interval);
                alert('Malipo yamefanikiwa! Rasiti: ' + d.receipt);
                location.reload();
            }
        }catch(e){}
    }, 3000);
}

// ===== 7. REPORTS - Chart.js =========
function initReports(){
    const businessId = document.getElementById('dashboard')?.dataset.businessId;
    const year = document.getElementById('dashboard')?.dataset.year;
    if(businessId) loadDashboardCharts(businessId, year);
}

async function loadDashboardCharts(businessId, year){
    try{
        const res = await fetch(`/reports/api/chart/${businessId}/?year=${year||new Date().getFullYear()}`);
        const monthly = await res.json();
        if(!monthly || !Array.isArray(monthly)) return;

        const salesCtx = document.getElementById('salesChart');
        if(salesCtx){
            new Chart(salesCtx, {
                type:'bar',
                data:{
                    labels:monthly.map(m=> 'Mwezi '+m.month),
                    datasets:[
                        {label: 'Mauzo', data: monthly.map(m=>m.sales), backgroundColor:'#0F172A'},
                        {label: 'Matumizi', data: monthly.map(m=>m.expenses), backgroundColor:'#EF4444'}
                    ]
                },
                options:{responsive:true, plugins:{legend:{position:'bottom'}}}
            });
        }
        const profitCtx = document.getElementById('profitChart');
        if(profitCtx){
            new Chart(profitCtx, {
                type: 'line',
                data:{
                    labels:['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],
                    datasets:[{
                        label: 'Faida',
                        data: monthly.map(m=> m.sales - m.expenses),
                        borderColor:'#10B981', backgroundColor:'rgba(16,185,129,0.2)', tension:0.4, fill:true
                    }]
                }
            });
        }
    }catch(e){console.log('Chart load error', e);}
} 

//  ====== 8. NOTIFICATIONS ===========
function initNotifications(){
    setInterval(async ()=>{
        try{
            let res = await fetch('/notifications/api/unread-count/');
            let d = await res.json();
            let badge = document.getElementById('notif-badge');
            if(badge){
                badge.innerText = d.count;
                badge.style.display = d.count>0 ? 'inline' : 'none';
            }
        }catch(e){}
    }, 30000);
}

function markAsRead(notifId){
    fetch(`/notifications/read/${notifId}/`, {method:'POST', headers:{'X-CSRFToken': getCSRF()}})
    .then(()=> document.getElementById(`notif-${notifId}`)?.classList.remove('unread'));
}

window.TaxTZ = TaxTZ;
window.requestControlNumber = requestControlNumber;
window.checkPaymentStatus = checkPaymentStatus;
window.markAsRead = markAsRead;
window.loadDashboardCharts = loadDashboardCharts;