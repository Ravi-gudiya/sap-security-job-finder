// Initialize Lucide icons on page load
document.addEventListener('DOMContentLoaded', () => {
  lucide.createIcons();
});

// Configure PDF.js Worker
pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.16.105/pdf.worker.min.js';

// Application State
const state = {
  location: 'India',
  experience: 5,
  roleType: 'SAP Security',
  detectedSkills: [],
  scannedResumeText: ''
};

// DOM Elements
const preloader = document.getElementById('preloader');
const typingRole = document.getElementById('typing-role');
const particleCanvas = document.getElementById('particle-canvas');

const locationInput = document.getElementById('location-input');
const experienceInput = document.getElementById('experience-input');
const experienceVal = document.getElementById('experience-val');
const roleType = document.getElementById('role-type');
const searchBtn = document.getElementById('search-btn');

const resumeFileInput = document.getElementById('resume-file');
const uploadTrigger = document.getElementById('upload-trigger');
const fileNameDisplay = document.getElementById('file-name-display');
const resumeTextInput = document.getElementById('resume-input');
const scanResumeBtn = document.getElementById('scan-resume-btn');
const resumeResultsPanel = document.getElementById('resume-results-panel');
const avgMatchPct = document.getElementById('avg-match-pct');
const detectedSkillsChips = document.getElementById('detected-skills-chips');

const tabBtns = document.querySelectorAll('.tab-btn');
const tabContents = document.querySelectorAll('.tab-content');
const portalsCount = document.getElementById('portals-count');
const companiesCount = document.getElementById('companies-count');
const liveJobsCount = document.getElementById('live-jobs-count');

const copySearchBtn = document.getElementById('copy-search-string');
const downloadResumeBtn = document.getElementById('download-resume-btn');
const toast = document.getElementById('toast');
const toastMessage = document.getElementById('toast-message');

/* ==========================================================================
   1. Preloader Loading Control
   ========================================================================== */
window.addEventListener('load', () => {
  setTimeout(() => {
    preloader.classList.add('fade-out');
  }, 1200); // 1.2 second aesthetic buffer
});

/* ==========================================================================
   2. Typewriter Role Animation Loop
   ========================================================================== */
const roles = [
  "SAP Security Consultant",
  "SAP GRC Specialist",
  "Security Auditor",
  "Problem Solver"
];
let roleIndex = 0;
let charIndex = 0;
let isDeleting = false;
let typeDelay = 100;

function typeAnimation() {
  const currentRole = roles[roleIndex];
  
  if (isDeleting) {
    typingRole.textContent = currentRole.substring(0, charIndex - 1);
    charIndex--;
    typeDelay = 50;
  } else {
    typingRole.textContent = currentRole.substring(0, charIndex + 1);
    charIndex++;
    typeDelay = 120;
  }

  if (!isDeleting && charIndex === currentRole.length) {
    isDeleting = true;
    typeDelay = 2000; // Pause at full word
  } else if (isDeleting && charIndex === 0) {
    isDeleting = false;
    roleIndex = (roleIndex + 1) % roles.length;
    typeDelay = 500; // Pause before typing next word
  }

  setTimeout(typeAnimation, typeDelay);
}
setTimeout(typeAnimation, 1800); // Start typing after preloader fades

/* ==========================================================================
   3. Interactive Canvas Particle Constellation Backdrop
   ========================================================================== */
const ctx = particleCanvas.getContext('2d');
let particles = [];
const maxParticles = 65;
const connectionDistance = 110;

function resizeCanvas() {
  particleCanvas.width = window.innerWidth;
  particleCanvas.height = window.innerHeight;
}
window.addEventListener('resize', resizeCanvas);
resizeCanvas();

class Particle {
  constructor() {
    this.x = Math.random() * particleCanvas.width;
    this.y = Math.random() * particleCanvas.height;
    this.vx = (Math.random() - 0.5) * 0.45;
    this.vy = (Math.random() - 0.5) * 0.45;
    this.radius = Math.random() * 2.5 + 1.2;
    this.alpha = Math.random() * 0.5 + 0.4;
    
    // Choose random color from the user's custom palette
    const colors = ['#51e2f5', '#9df9ef', '#ffa8B6', '#edf756'];
    this.color = colors[Math.floor(Math.random() * colors.length)];
  }

  update() {
    this.x += this.vx;
    this.y += this.vy;

    // Boundary bounces
    if (this.x < 0 || this.x > particleCanvas.width) this.vx = -this.vx;
    if (this.y < 0 || this.y > particleCanvas.height) this.vy = -this.vy;
  }

  draw() {
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
    ctx.fillStyle = this.color;
    ctx.globalAlpha = this.alpha;
    ctx.fill();
    ctx.globalAlpha = 1.0;
  }
}

function initParticles() {
  particles = [];
  for (let i = 0; i < maxParticles; i++) {
    particles.push(new Particle());
  }
}

function animateParticles() {
  ctx.clearRect(0, 0, particleCanvas.width, particleCanvas.height);
  
  particles.forEach(p => {
    p.update();
    p.draw();
  });

  // Link proximal particles
  for (let i = 0; i < particles.length; i++) {
    for (let j = i + 1; j < particles.length; j++) {
      const dx = particles[i].x - particles[j].x;
      const dy = particles[i].y - particles[j].y;
      const dist = Math.sqrt(dx * dx + dy * dy);

      if (dist < connectionDistance) {
        ctx.beginPath();
        ctx.moveTo(particles[i].x, particles[i].y);
        ctx.lineTo(particles[j].x, particles[j].y);
        const linkAlpha = (1 - dist / connectionDistance) * 0.16;
        ctx.strokeStyle = `rgba(255, 168, 182, ${linkAlpha})`;
        ctx.lineWidth = 1;
        ctx.stroke();
      }
    }
  }
  requestAnimationFrame(animateParticles);
}
initParticles();
animateParticles();

/* ==========================================================================
   4. Search Panel & Keyword Systems
   ========================================================================== */

// Sync sliders
experienceInput.addEventListener('input', (e) => {
  state.experience = parseInt(e.target.value);
  experienceVal.textContent = `${state.experience} Year${state.experience > 1 ? 's' : ''}`;
  renderLiveJobs();
});

// Update location state on key input for immediate reactive filtering
locationInput.addEventListener('input', (e) => {
  state.location = e.target.value.trim() || 'India';
  renderLiveJobs();
});

// Quick selection chips
const chips = document.querySelectorAll('.quick-chips .chip');
chips.forEach(c => {
  // Highlight default
  if (c.getAttribute('data-val') === state.location) {
    c.classList.add('active');
  }

  c.addEventListener('click', () => {
    chips.forEach(x => x.classList.remove('active'));
    c.classList.add('active');
    const val = c.getAttribute('data-val');
    locationInput.value = val;
    state.location = val;
    generateLinks();
    renderLiveJobs();
  });
});

// Sync role subspecialty
roleType.addEventListener('change', (e) => {
  state.roleType = e.target.value;
  generateLinks();
  renderLiveJobs();
});

// Dynamic Search Link Generator
function generateLinks() {
  const location = state.location;
  const role = state.roleType;
  const expTerm = getExperienceKeywords();
  const locLower = location.toLowerCase();

  // Indeed domain router
  let indeedDomain = 'www.indeed.com';
  if (locLower.includes('india') || locLower.includes('bengaluru') || locLower.includes('hyderabad') || locLower.includes('mumbai') || locLower.includes('pune')) {
    indeedDomain = 'in.indeed.com';
  } else if (locLower.includes('germany') || locLower.includes('munich') || locLower.includes('walldorf')) {
    indeedDomain = 'de.indeed.com';
  } else if (locLower.includes('uk') || locLower.includes('london')) {
    indeedDomain = 'uk.indeed.com';
  }

  const isRemote = locLower === 'remote';
  const remoteParam = isRemote ? '&f_WT=2' : '';

  // 1. Portals Tab Links
  const portals = [
    {
      name: 'LinkedIn Jobs',
      description: 'Deep link query matching your security specialty and target region.',
      badge: 'Portal',
      url: `https://www.linkedin.com/jobs/search/?keywords=${encodeURIComponent(`"${role}" AND (${expTerm})`)}&location=${encodeURIComponent(location)}${remoteParam}&f_TPR=r2592000`,
      rawQuery: `keywords="${role}" AND (${expTerm}) & location=${location}`
    },
    {
      name: 'Indeed Search',
      description: 'General indeed search pre-populated with role terms and geo filters.',
      badge: 'Portal',
      url: `https://${indeedDomain}/jobs?q=${encodeURIComponent(`"${role}" (${expTerm})`)}&l=${encodeURIComponent(location)}&fromage=30`,
      rawQuery: `q="${role}" (${expTerm}) & l=${location}`
    },
    {
      name: 'Glassdoor',
      description: 'Search active portal openings including salary approximations.',
      badge: 'Portal',
      url: `https://www.glassdoor.com/Job/jobs.htm?sc.keyword=${encodeURIComponent(`"${role}" ${expTerm}`)}&locN=${encodeURIComponent(location)}`,
      rawQuery: `sc.keyword="${role}" (${expTerm})`
    },
    {
      name: 'Google Jobs',
      description: 'Aggregates listings indexed over minor boards and corporate ATS registries.',
      badge: 'Portal',
      url: `https://www.google.com/search?q=${encodeURIComponent(`"${role}" (${expTerm}) jobs in ${location}`)}&ibp=htl;jobs`,
      rawQuery: `"${role}" (${expTerm}) jobs in ${location}`
    },
    {
      name: 'Dice Tech',
      description: 'Targeted tech job site search. Best for contract roles in US.',
      badge: 'Portal',
      url: `https://www.dice.com/jobs?q=${encodeURIComponent(`"${role}" ${expTerm}`)}&location=${encodeURIComponent(location)}`,
      rawQuery: `q="${role}" & location=${location}`
    },
    {
      name: 'ZipRecruiter',
      description: 'Aggregator featuring rapid applications and quick apply overlays.',
      badge: 'Portal',
      url: `https://www.ziprecruiter.com/candidate/search?search=${encodeURIComponent(`"${role}" ${expTerm}`)}&location=${encodeURIComponent(location)}`,
      rawQuery: `search="${role}"`
    }
  ];

  // 2. Company Portals Tab Links (Direct search engines - no Google search redirects)
  const companies = [
    {
      name: 'SAP Careers',
      description: 'Direct SuccessFactors search engine for official SAP global and local openings.',
      badge: 'Company',
      url: `https://jobs.sap.com/search/?q=${encodeURIComponent(role)}&locationsearch=${encodeURIComponent(location)}`,
      rawQuery: `jobs.sap.com -> keyword="${role}", location="${location}"`
    },
    {
      name: 'Accenture Careers',
      description: 'Direct candidate search portal on Accenture\'s official career board.',
      badge: 'Company',
      url: `https://www.accenture.com/in-en/careers/jobsearch?jk=${encodeURIComponent(role)}`,
      rawQuery: `accenture.com/careers -> keyword="${role}"`
    },
    {
      name: 'Deloitte Jobs',
      description: 'Direct search portal for Deloitte\'s global and regional consulting positions.',
      badge: 'Company',
      url: `https://careers.deloitte.com/jobs`,
      rawQuery: `deloitte.com/careers -> keyword="${role}"`
    },
    {
      name: 'EY Careers',
      description: 'Direct SuccessFactors application search for EY client risk & security practice roles.',
      badge: 'Company',
      url: `https://careers.ey.com/search/?q=${encodeURIComponent(role)}&location=${encodeURIComponent(location)}`,
      rawQuery: `ey.com/careers -> keyword="${role}", location="${location}"`
    },
    {
      name: 'PwC Portal',
      description: 'Direct search engine for PricewaterhouseCoopers audit, risk and cybersecurity openings.',
      badge: 'Company',
      url: `https://jobs.us.pwc.com/search-jobs/${encodeURIComponent(role)}`,
      rawQuery: `pwc.com/careers -> keyword="${role}"`
    },
    {
      name: 'IBM Security',
      description: 'IBM direct careers portal for enterprise cybersecurity and SAP consulting positions.',
      badge: 'Company',
      url: `https://careers.ibm.com/search/?keyword=${encodeURIComponent(role)}&location=${encodeURIComponent(location)}`,
      rawQuery: `ibm.com/careers -> keyword="${role}", location="${location}"`
    },
    {
      name: 'TCS iBegin',
      description: 'Direct search engine on Tata Consultancy Services (TCS) job portal.',
      badge: 'Company',
      url: `https://ibegin.tcs.com/iBegin/jobs/search`,
      rawQuery: `ibegin.tcs.com -> search portal`
    },
    {
      name: 'Infosys Careers',
      description: 'Direct candidate search engine on Infosys official career board.',
      badge: 'Company',
      url: `https://career.infosys.com/joblist?keyword=${encodeURIComponent(role)}`,
      rawQuery: `career.infosys.com -> keyword="${role}"`
    },
    {
      name: 'Capgemini Portal',
      description: 'Direct job search engine on Capgemini corporate consulting directories.',
      badge: 'Company',
      url: `https://www.capgemini.com/in-en/careers/job-search/?q=${encodeURIComponent(role)}`,
      rawQuery: `capgemini.com/careers -> keyword="${role}"`
    }
  ];

  renderPortalCards(portals);
  renderCompanyCards(companies);
  
  portalsCount.textContent = portals.length;
  companiesCount.textContent = companies.length;
}

function getExperienceKeywords() {
  const years = state.experience;
  if (years <= 2) return '"Junior" OR "Associate"';
  if (years <= 6) return '"Consultant" OR "Analyst" OR "Specialist"';
  if (years <= 10) return '"Senior" OR "Lead" OR "Architect"';
  return '"Principal" OR "Architect" OR "Manager"';
}

// Render Card loops
function renderPortalCards(arr) {
  const grid = document.getElementById('portals-grid');
  grid.innerHTML = '';
  arr.forEach(p => {
    const card = document.createElement('div');
    card.className = 'glass-card link-card';
    card.innerHTML = `
      <div>
        <div class="card-header-row">
          <div class="card-logo-placeholder">
            <i data-lucide="globe"></i>
          </div>
          <span class="card-badge badge-portal">${p.badge}</span>
        </div>
        <h3>${p.name}</h3>
        <p>${p.description}</p>
        <div class="search-query-preview" title="Constructed search parameter block">${p.rawQuery}</div>
      </div>
      <div class="card-actions">
        <a href="${p.url}" target="_blank" class="btn btn-primary btn-sm">
          <i data-lucide="external-link"></i> Launch Search
        </a>
      </div>
    `;
    grid.appendChild(card);
  });
  lucide.createIcons();
}

function renderCompanyCards(arr) {
  const grid = document.getElementById('companies-grid');
  grid.innerHTML = '';
  arr.forEach(c => {
    const card = document.createElement('div');
    card.className = 'glass-card link-card';
    card.innerHTML = `
      <div>
        <div class="card-header-row">
          <div class="card-logo-placeholder">
            <i data-lucide="building-2"></i>
          </div>
          <span class="card-badge badge-company">${c.badge}</span>
        </div>
        <h3>${c.name}</h3>
        <p>${c.description}</p>
        <div class="search-query-preview" title="SuccessFactors/Workday direct mapping">${c.rawQuery}</div>
      </div>
      <div class="card-actions">
        <a href="${c.url}" target="_blank" class="btn btn-secondary btn-sm">
          <i data-lucide="shield-check"></i> Open Portal
        </a>
      </div>
    `;
    grid.appendChild(card);
  });
  lucide.createIcons();
}

// Copy keyword block helper
copySearchBtn.addEventListener('click', () => {
  const role = state.roleType;
  const exp = getExperienceKeywords();
  const loc = state.location;
  const searchString = `"${role}" AND (${exp}) AND "${loc}"`;
  
  navigator.clipboard.writeText(searchString)
    .then(() => showToast('Search keywords copied to clipboard!'))
    .catch(() => showToast('Failed to copy keywords', false));
});

// Download resume placeholder button
downloadResumeBtn.addEventListener('click', (e) => {
  e.preventDefault();
  showToast('Generating resume package download...', true);
});

// Toast Notifications helper
function showToast(message, isSuccess = true) {
  toastMessage.textContent = message;
  const icon = toast.querySelector('.toast-icon');
  if (isSuccess) {
    icon.setAttribute('data-lucide', 'check-circle');
    icon.style.color = 'var(--success)';
  } else {
    icon.setAttribute('data-lucide', 'alert-circle');
    icon.style.color = 'var(--secondary)';
  }
  lucide.createIcons();

  toast.classList.add('show');
  setTimeout(() => {
    toast.classList.remove('show');
  }, 3000);
}

/* ==========================================================================
   5. Resume Parser & Card Analyzer Engine (Local Parsing)
   ========================================================================== */

// Trigger file input
uploadTrigger.addEventListener('click', () => resumeFileInput.click());

resumeFileInput.addEventListener('change', (e) => {
  const file = e.target.files[0];
  if (!file) return;

  fileNameDisplay.textContent = file.name;
  
  const reader = new FileReader();
  if (file.type === 'text/plain') {
    reader.onload = function(evt) {
      resumeTextInput.value = evt.target.result;
      showToast('TXT Resume text loaded. Click Analyze Match.');
    };
    reader.readAsText(file);
  } else if (file.type === 'application/pdf') {
    reader.onload = function(evt) {
      const typedarray = new Uint8Array(evt.target.result);
      parsePDFText(typedarray);
    };
    reader.readAsArrayBuffer(file);
  } else {
    showToast('Unsupported file format. Please upload PDF or TXT.', false);
  }
});

// Read and extract text from local PDF using PDF.js
function parsePDFText(data) {
  showToast('Reading local PDF stream...');
  pdfjsLib.getDocument(data).promise.then(pdf => {
    let maxPages = pdf.numPages;
    let countPromises = [];
    
    for (let j = 1; j <= maxPages; j++) {
      let page = pdf.getPage(j);
      countPromises.push(page.then(p => {
        return p.getTextContent().then(textContent => {
          return textContent.items.map(item => item.str).join(' ');
        });
      }));
    }
    
    Promise.all(countPromises).then(pagesText => {
      const fullText = pagesText.join('\n');
      resumeTextInput.value = fullText;
      showToast('PDF content extracted. Click Analyze Match!');
    });
  }).catch(err => {
    console.error(err);
    showToast('Failed to parse PDF file.', false);
  });
}

// Analyze Match Action
scanResumeBtn.addEventListener('click', () => {
  const text = resumeTextInput.value.trim();
  if (!text) {
    showToast('Please upload a file or paste your resume text first.', false);
    return;
  }

  state.scannedResumeText = text;
  analyzeResumeSkills(text);
});

// Vocabulary mapping of standard SAP keywords
const SKILLS_VOCAB = [
  'S/4HANA Security', 'SAP Fiori', 'PFCG', 'Role Design',
  'SAP GRC', 'Access Control', 'User Administration', 'SoD',
  'SAP GRC AC 12.0', 'Segregation of Duties', 'Emergency Access Management',
  'SAP Basis Security', 'Fiori Catalogs', 'Audit Trails', 'UI Masking',
  'Security Architecture', 'SoD Remediation', 'BTP Security',
  'SAP Security Audit', 'SOX Compliance', 'GRC Process Control',
  'IAM', 'Client Facing', 'Project Management', 'SAP Security Architecture',
  'SOX Control', 'GRC 12.0', 'Vulnerability Management',
  'ABAP Security Code Scan', 'SAP ETD', 'SAP BTP Security',
  'SAP IAS/IPS', 'Cloud ALM', 'German Language', 'Client Management',
  'SAP Security', 'SAP Basis', 'Basis Security'
];

function analyzeResumeSkills(resumeText) {
  const textLower = resumeText.toLowerCase();
  state.detectedSkills = [];

  SKILLS_VOCAB.forEach(skill => {
    if (textLower.includes(skill.toLowerCase())) {
      state.detectedSkills.push(skill);
    }
  });

  // Render detected chips
  detectedSkillsChips.innerHTML = '';
  if (state.detectedSkills.length === 0) {
    detectedSkillsChips.innerHTML = '<span class="file-name-text">No SAP Security key-skills detected in text.</span>';
  } else {
    state.detectedSkills.forEach(s => {
      const chip = document.createElement('span');
      chip.className = 'detected-chip';
      chip.textContent = s;
      detectedSkillsChips.appendChild(chip);
    });
  }

  resumeResultsPanel.style.display = 'flex';
  
  // Recalculate match ratios and re-render live postings
  renderLiveJobs();
  
  // Transition to dynamic openings list
  const liveTab = Array.from(tabBtns).find(b => b.getAttribute('data-tab') === 'live-jobs');
  if (liveTab) liveTab.click();
  
  showToast('Analysis complete! Matching openings prioritized.');
}

// Filter helpers
function matchesLocation(jobLoc, targetLoc) {
  const jl = jobLoc.toLowerCase();
  const tl = targetLoc.toLowerCase().trim();
  if (!tl) return true;
  
  // Standardize common synonymous terms (e.g., Bangalore vs Bengaluru)
  const normalize = (str) => {
    return str
      .replace(/bangalore/g, 'bengaluru')
      .replace(/bombay/g, 'mumbai')
      .replace(/madras/g, 'chennai');
  };
  
  const normJl = normalize(jl);
  const normTl = normalize(tl);
  
  if (normTl === 'remote') {
    return normJl.includes('remote');
  }
  if (normTl === 'india') {
    return normJl.includes('india') || normJl.includes('bengaluru') || normJl.includes('pune') || normJl.includes('hyderabad') || normJl.includes('mumbai') || normJl.includes('noida') || normJl.includes('chennai');
  }
  if (normTl === 'usa' || normTl === 'us') {
    return normJl.includes('usa') || normJl.includes('us') || normJl.includes('tx') || normJl.includes('il') || normJl.includes('chicago') || normJl.includes('dallas');
  }
  if (normTl === 'germany') {
    return normJl.includes('germany') || normJl.includes('deutschland') || normJl.includes('munich') || normJl.includes('walldorf');
  }
  return normJl.includes(normTl);
}

function matchesExperience(jobExp, targetExp) {
  // Matches if required experience is less than or equal to user's targeted experience (plus a 2-year stretch buffer)
  return jobExp <= (targetExp + 2);
}

// Render dynamic postings matching skills
function renderLiveJobs() {
  const stack = document.getElementById('live-jobs-stack');
  stack.innerHTML = '';

  if (!window.JOBS_DATABASE || JOBS_DATABASE.length === 0) {
    stack.innerHTML = '<div class="glass-card"><p>No jobs found in the local database.</p></div>';
    liveJobsCount.textContent = '0';
    return;
  }

  // Filter jobs based on active search parameters (Location & Experience)
  const filteredJobs = JOBS_DATABASE.filter(job => {
    return matchesLocation(job.location, state.location) && matchesExperience(job.experience_years, state.experience);
  });

  if (filteredJobs.length === 0) {
    stack.innerHTML = '<div class="glass-card"><p style="text-align: center; color: var(--text-muted);">No active postings match your location and experience filters in the local database. Try expanding your search criteria.</p></div>';
    liveJobsCount.textContent = '0';
    return;
  }

  // Calculate scores for each filtered job based on detected skills
  const scoredJobs = filteredJobs.map(job => {
    let matches = 0;
    const totalSkills = job.skills.length;
    const matchedSkills = [];
    const missingSkills = [];

    job.skills.forEach(skill => {
      const isMatched = state.detectedSkills.some(s => s.toLowerCase() === skill.toLowerCase() || skill.toLowerCase().includes(s.toLowerCase()));
      if (isMatched || state.detectedSkills.length === 0) {
        matches++;
        matchedSkills.push(skill);
      } else {
        missingSkills.push(skill);
      }
    });

    const matchPct = totalSkills > 0 ? Math.round((matches / totalSkills) * 100) : 0;
    return { ...job, matchPct, matchedSkills, missingSkills };
  });

  // Sort by match percentage (descending)
  if (state.detectedSkills.length > 0) {
    scoredJobs.sort((a, b) => b.matchPct - a.matchPct);
  }

  // Calculate aggregate score
  if (state.detectedSkills.length > 0) {
    const totalMatchPct = scoredJobs.reduce((sum, j) => sum + j.matchPct, 0);
    const avgPct = Math.round(totalMatchPct / scoredJobs.length);
    avgMatchPct.textContent = `${avgPct}%`;
  } else {
    avgMatchPct.textContent = '0%';
  }

  // Render cards
  scoredJobs.forEach(job => {
    const isHighMatch = job.matchPct >= 70;
    const card = document.createElement('div');
    card.className = 'glass-card job-row-card';
    card.innerHTML = `
      ${state.detectedSkills.length > 0 ? `<div class="job-match-badge ${isHighMatch ? 'high-match' : ''}"><i data-lucide="shield-alert"></i> ${job.matchPct}% Match</div>` : ''}
      <div class="job-info-left">
        <div class="job-title-row">
          <h4>${job.title}</h4>
          <div class="job-meta-tags">
            <span class="meta-tag meta-tag-company"><i data-lucide="building-2"></i> ${job.company}</span>
            <span class="meta-tag"><i data-lucide="map-pin"></i> ${job.location}</span>
            <span class="meta-tag"><i data-lucide="award"></i> ${job.experience_years}+ Years</span>
            <span class="meta-tag"><i data-lucide="clock"></i> ${job.type}</span>
          </div>
        </div>
        <div class="job-skills">
          ${job.skills.map(s => {
            let cls = '';
            if (state.detectedSkills.length > 0) {
              const matched = job.matchedSkills.includes(s);
              cls = matched ? 'matched-skill' : 'missing-skill';
            }
            return `<span class="skill-tag ${cls}">${s}</span>`;
          }).join('')}
        </div>
      </div>
      <div class="job-action-right">
        <span class="posted-date"><i data-lucide="calendar"></i> ${job.posted_date}</span>
        <a href="${job.url}" target="_blank" class="btn btn-primary btn-sm">
          <i data-lucide="external-link"></i> Apply Directly
        </a>
      </div>
    `;
    stack.appendChild(card);
  });

  liveJobsCount.textContent = scoredJobs.length;
  lucide.createIcons();
}

/* ==========================================================================
   6. HUD Tab Control Switches
   ========================================================================== */
tabBtns.forEach(btn => {
  btn.addEventListener('click', () => {
    tabBtns.forEach(b => b.classList.remove('active'));
    tabContents.forEach(c => c.classList.remove('active'));

    btn.classList.add('active');
    const target = btn.getAttribute('data-tab');
    document.getElementById(target).classList.add('active');
  });
});

/* ==========================================================================
   7. Page Initialization
   ========================================================================== */
searchBtn.addEventListener('click', () => {
  generateLinks();
  showToast('Search filters updated!');
});

// Run default link population on startup
generateLinks();
renderLiveJobs();
