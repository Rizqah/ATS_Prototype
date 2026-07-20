import { useEffect, useMemo, useRef, useState } from "react";
import {
  ArrowRight,
  BarChart3,
  BriefcaseBusiness,
  Check,
  ChevronRight,
  CircleUserRound,
  FileText,
  LayoutDashboard,
  ListFilter,
  LogOut,
  Mail,
  Menu,
  Search,
  ShieldCheck,
  Sparkles,
  Target,
  Upload,
  Users,
  X,
} from "lucide-react";
import { api } from "./api";

const sampleCandidates = [
  { name: "Avery Morgan", role: "Senior Frontend Engineer", score: 92, status: "Shortlist", skills: ["React", "TypeScript", "Accessibility"], resume: "React TypeScript accessibility testing frontend engineer with measurable dashboard delivery." },
  { name: "Maya Patel", role: "Frontend Engineer", score: 84, status: "Reviewing", skills: ["React", "Testing", "GraphQL"], resume: "Frontend engineer with React, testing, GraphQL, design systems and product analytics experience." },
  { name: "Jordan Lee", role: "Product Engineer", score: 78, status: "Reviewing", skills: ["TypeScript", "CSS", "REST"], resume: "Product engineer with TypeScript, CSS architecture, REST APIs and user-facing product launches." },
  { name: "Sam Rivera", role: "UI Engineer", score: 66, status: "New", skills: ["React", "CSS Architecture"], resume: "UI engineer focused on React components, responsive CSS and marketing site delivery." },
];

const sampleApplications = [
  { company: "Northwind Labs", role: "Senior Frontend Engineer", status: "Screening", score: 82 },
  { company: "Orbit Systems", role: "Product Engineer", status: "Interview", score: 76 },
  { company: "Brightline", role: "Frontend Developer", status: "Applied", score: 69 },
];

const DEFAULT_SCREENING_JD = "Senior Frontend Engineer\n\nWe need strong React, TypeScript, accessibility, testing, CSS architecture, and API integration experience.";

function getJobTitle(jobDescription) {
  return jobDescription.split(/\r?\n/).map((line) => line.trim()).find(Boolean) || "New screening";
}

function Logo({ onClick }) {
  return (
    <button className="logo" onClick={onClick} aria-label="TrueFit home">
      <span className="logo-mark"><Target size={17} /></span>
      <span>TrueFit</span>
    </button>
  );
}

function Button({ children, variant = "primary", icon: Icon, className = "", ...props }) {
  return (
    <button className={`button button-${variant} ${className}`} {...props}>
      {Icon && <Icon size={17} />}
      <span>{children}</span>
    </button>
  );
}

function Score({ value, compact = false }) {
  const tone = value >= 80 ? "excellent" : value >= 65 ? "good" : "fair";
  return <span className={`score score-${tone} ${compact ? "score-compact" : ""}`}>{value}%</span>;
}

function downloadFile(contents, filename, type) {
  const url = URL.createObjectURL(new Blob([contents], { type }));
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

function downloadCsv(rows, filename) {
  const csv = rows
    .map((row) => row.map((value) => `"${String(value ?? "").replace(/"/g, '""')}"`).join(","))
    .join("\r\n");
  downloadFile(`\uFEFF${csv}`, filename, "text/csv;charset=utf-8");
}

function downloadTextPdf(lines, filename) {
  const safeLines = lines.map((line) => String(line).normalize("NFKD").replace(/[^\x20-\x7E]/g, "-").slice(0, 96));
  const chunks = [];
  for (let index = 0; index < safeLines.length; index += 43) chunks.push(safeLines.slice(index, index + 43));

  const pageCount = Math.max(chunks.length, 1);
  const objects = ["", "", "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"];
  const pageIds = [];
  for (let pageIndex = 0; pageIndex < pageCount; pageIndex += 1) {
    const pageId = objects.length + 1;
    const contentId = pageId + 1;
    pageIds.push(pageId);
    const content = ["BT", "/F1 11 Tf", "50 790 Td", "14 TL", ...(chunks[pageIndex] || []).map((line) => `(${line.replace(/([\\()])/g, "\\$1")}) Tj T*`), "ET"].join("\n");
    objects.push(`<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 842] /Resources << /Font << /F1 3 0 R >> >> /Contents ${contentId} 0 R >>`);
    objects.push(`<< /Length ${content.length} >>\nstream\n${content}\nendstream`);
  }
  objects[0] = "<< /Type /Catalog /Pages 2 0 R >>";
  objects[1] = `<< /Type /Pages /Kids [${pageIds.map((id) => `${id} 0 R`).join(" ")}] /Count ${pageCount} >>`;

  let pdf = "%PDF-1.4\n";
  const offsets = [0];
  objects.forEach((object, index) => {
    offsets.push(pdf.length);
    pdf += `${index + 1} 0 obj\n${object}\nendobj\n`;
  });
  const xrefOffset = pdf.length;
  pdf += `xref\n0 ${objects.length + 1}\n0000000000 65535 f \n`;
  pdf += offsets.slice(1).map((offset) => `${String(offset).padStart(10, "0")} 00000 n \n`).join("");
  pdf += `trailer\n<< /Size ${objects.length + 1} /Root 1 0 R >>\nstartxref\n${xrefOffset}\n%%EOF`;
  downloadFile(pdf, filename, "application/pdf");
}

function TopNav({ page, setPage, role, onLogout }) {
  const candidateLinks = [
    ["candidate", "Dashboard", LayoutDashboard],
    ["optimizer", "CV Optimizer", Target],
    ["profile", "Profile", CircleUserRound],
    ["applications", "Applications", BriefcaseBusiness],
  ];
  const recruiterLinks = [
    ["recruiter", "Workspace", Users],
    ["feedback", "Feedback", Mail],
    ["jobs", "Jobs", BriefcaseBusiness],
    ["candidates", "Candidates", CircleUserRound],
    ["reports", "Reports", BarChart3],
  ];
  const links = role === "recruiter" ? recruiterLinks : candidateLinks;

  return (
    <header className="top-nav">
      <div className="nav-inner">
        <Logo onClick={() => setPage(role === "recruiter" ? "recruiter" : "candidate")} />
        <nav className="nav-links">
          {links.map(([target, label, Icon]) => (
            <button key={label} className={page === target ? "nav-link active" : "nav-link"} onClick={() => setPage(target)}>
              <Icon size={15} /> {label}
            </button>
          ))}
        </nav>
        <div className="nav-spacer" />
        <span className="api-status"><span className="status-dot" /> API connected</span>
        <button className="icon-button" onClick={onLogout} title="Log out"><LogOut size={18} /></button>
      </div>
    </header>
  );
}

function Landing({ setPage, setRole, onStartScreening }) {
  const openAuth = (role) => {
    setRole(role);
    setPage("auth");
  };
  return (
    <main>
      <header className="public-nav">
        <Logo onClick={() => setPage("landing")} />
        <div className="public-actions">
          <Button variant="ghost" onClick={() => openAuth("candidate")}>Sign in</Button>
          <Button onClick={onStartScreening}>Start screening</Button>
        </div>
      </header>
      <section className="hero">
        <div className="hero-copy">
          <span className="eyebrow">Explainable AI hiring</span>
          <h1>Find the right fit.<br /><span>Show people why.</span></h1>
          <p>TrueFit ranks resumes against the real requirements of a role and turns every score into clear, useful next steps.</p>
          <div className="hero-actions">
            <Button icon={Users} onClick={onStartScreening}>Start screening</Button>
            <Button variant="secondary" icon={CircleUserRound} onClick={() => openAuth("candidate")}>Optimize my CV</Button>
          </div>
          <div className="trust-row">
            <span><Check size={15} /> Semantic matching</span>
            <span><Check size={15} /> Explainable scores</span>
            <span><Check size={15} /> Candidate feedback</span>
          </div>
        </div>
        <div className="match-preview">
          <div className="preview-header">
            <div><span className="muted-label">Top match</span><h3>Avery Morgan</h3></div>
            <Score value={92} />
          </div>
          <div className="preview-role">Senior Frontend Engineer</div>
          <div className="skills">
            {["React", "TypeScript", "Accessibility", "Testing"].map((skill) => <span className="skill" key={skill}>{skill}</span>)}
          </div>
          <div className="insight"><Sparkles size={18} /><span><strong>Strong candidate</strong> Matches all core requirements and demonstrates measurable impact.</span></div>
        </div>
      </section>
      <section className="capabilities">
        {[
          [Target, "Semantic matching", "Score the meaning and depth of experience, not just keyword overlap."],
          [BarChart3, "Explainable decisions", "Understand strengths, gaps, and role-specific evidence behind each score."],
          [Mail, "Useful feedback", "Give every candidate a clear, personalised answer instead of silence."],
        ].map(([Icon, title, body]) => (
          <article className="capability" key={title}><Icon size={22} /><h3>{title}</h3><p>{body}</p></article>
        ))}
      </section>
    </main>
  );
}

function Auth({ role, setRole, onAuthenticated }) {
  const [mode, setMode] = useState("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(event) {
    event.preventDefault();
    setError("");
    setBusy(true);
    try {
      const result = mode === "login" ? await api.login(email, password) : await api.signup(email, password);
      onAuthenticated(result.user || email);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="auth-page">
      <div className="auth-message">
        <Logo />
        <span className="eyebrow">{role === "recruiter" ? "Recruiter workspace" : "Candidate workspace"}</span>
        <h1>{role === "recruiter" ? "Screen smarter. Shortlist with confidence." : "Stand out before you hit apply."}</h1>
        <p>{role === "recruiter" ? "Rank candidates, inspect the evidence, and generate constructive feedback." : "Benchmark your profile against each role and make every application stronger."}</p>
      </div>
      <form className="auth-form" onSubmit={submit}>
        <div className="segmented">
          <button type="button" className={role === "recruiter" ? "active" : ""} onClick={() => setRole("recruiter")}><Users size={16} /> Recruiter</button>
          <button type="button" className={role === "candidate" ? "active" : ""} onClick={() => setRole("candidate")}><CircleUserRound size={16} /> Candidate</button>
        </div>
        <div><span className="eyebrow">{mode === "login" ? "Welcome back" : "Create account"}</span><h2>{mode === "login" ? "Sign in to TrueFit" : "Start using TrueFit"}</h2></div>
        <label>Email<input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" required /></label>
        <label>Password<input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="At least 8 characters" required /></label>
        {error && <div className="form-error">{error}</div>}
        <Button type="submit" disabled={busy}>{busy ? "Working..." : mode === "login" ? "Sign in" : "Create account"}</Button>
        <button className="text-button" type="button" onClick={() => setMode(mode === "login" ? "signup" : "login")}>
          {mode === "login" ? "Need an account? Sign up" : "Already have an account? Sign in"}
        </button>
      </form>
    </main>
  );
}

function CandidateDashboard({ setPage, user }) {
  const displayName = user ? user.split("@")[0] : "Alex";
  const recentApplications = [
    { company: "Northwind Labs", role: "Senior Frontend Engineer", status: "Screening", score: 68, initials: "NL", age: "2 days ago" },
    { company: "Mapbox", role: "Frontend Engineer", status: "Interview", score: 82, initials: "MB", age: "1 week ago" },
    { company: "Klarna", role: "UI Engineer", status: "Applied", score: 74, initials: "KI", age: "3 days ago" },
    { company: "Pleo", role: "React Developer", status: "Offer", score: 90, initials: "PL", age: "2 weeks ago" },
  ];
  const actions = [
    [Target, "Optimise for a role", "Paste a JD, see your match, and tailor your CV.", "optimizer"],
    [CircleUserRound, "Build your profile", "Keep your career profile sharp for instant CVs.", "profile"],
    [BriefcaseBusiness, "Track applications", "Follow every role from saved to offer.", "applications"],
  ];

  return (
    <div className="page-shell">
      <section className="page-heading">
        <div><span className="eyebrow">Your job search</span><h1>Welcome back, {displayName}</h1><p>3 active applications - 1 offer on the table.</p></div>
        <Button icon={Target} onClick={() => setPage("optimizer")}>Match a new role</Button>
      </section>

      <section className="candidate-actions">
        {actions.map(([Icon, title, body, target]) => (
          <button className="panel candidate-action-card" key={title} onClick={() => setPage(target)}>
            <span className="action-icon"><Icon size={20} /></span>
            <strong>{title} <ArrowRight size={15} /></strong>
            <small>{body}</small>
          </button>
        ))}
      </section>

      <section className="candidate-home-grid">
        <article className="panel wide-panel">
          <div className="panel-head"><div><h2>Recent applications</h2></div><button className="text-button" onClick={() => setPage("applications")}>View all <ArrowRight size={15} /></button></div>
          <div className="application-list candidate-application-list">
            {recentApplications.map((item) => <button className="application-row candidate-app-row" key={item.company} onClick={() => setPage("applications")}><div className="company-mark">{item.initials}</div><div className="grow"><strong>{item.role}</strong><span>{item.company} - {item.age}</span></div><span className={`status-pill status-${item.status.toLowerCase()}`}>{item.status}</span><Score value={item.score} compact /></button>)}
          </div>
        </article>

        <div className="candidate-side-stack">
          <article className="panel profile-strength-card">
            <Score value={83} />
            <div><h2>Profile strength</h2><p>Add your portfolio link to reach 100%.</p><Button variant="secondary" icon={CircleUserRound} onClick={() => setPage("profile")}>Complete profile</Button></div>
          </article>
          <article className="panel next-move-card">
            <Sparkles size={19} />
            <div><h2>Next best move</h2><p>Your <strong>Northwind Labs</strong> application scored 68%. Closing 3 skill gaps could lift it into the shortlist.</p><Button icon={Target} onClick={() => setPage("optimizer")}>Optimise it now</Button></div>
          </article>
        </div>
      </section>
    </div>
  );
}

function Optimizer() {
  const [jd, setJd] = useState("Senior Frontend Engineer - Northwind Labs\n\nWe're building the data-visualization layer for a real-time analytics platform. You'll own complex, accessible UI and partner closely with design and backend.\n\nRequirements:\n- Expert-level React and modern JavaScript\n- Strong TypeScript across a large typed codebase\n- Deep CSS architecture skills and design-token systems\n- Accessibility - you build to WCAG AA standards by default\n- Solid testing discipline with Jest and React Testing Library\n- Comfortable consuming REST and GraphQL APIs");
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);
  const matched = ["React", "JavaScript", "CSS Architecture", "REST/GraphQL"];
  const missing = ["TypeScript", "Accessibility (WCAG)", "Testing (Jest/RTL)", "Next.js", "Design Systems", "Performance"];
  const suggestions = [
    ["TypeScript", "Convert a project to TypeScript and list it with typed-codebase experience."],
    ["Accessibility (WCAG)", "Add a line about WCAG AA, keyboard navigation, ARIA, or an audit you ran."],
    ["Testing (Jest/RTL)", "Quantify your testing: coverage owned, Jest, or React Testing Library in context."],
    ["Next.js", "Note any Next.js work, App Router, SSR, or a site you shipped with it."],
    ["Design Systems", "Mention design-system contributions, components owned, or adoption driven."],
    ["Performance", "Add a Lighthouse or Core Web Vitals improvement with a number."],
  ];

  async function renderPreview() {
    setBusy(true);
    try {
      const response = await api.renderCv({
        profile: { full_name: "Candidate Profile", professional_summary: "Frontend engineer focused on accessible product experiences." },
        work_experiences: [],
        achievements_by_experience: {},
        skills: [{ skill_name: "React" }, { skill_name: "TypeScript" }, { skill_name: "Testing" }],
        job_description: jd,
      });
      setResult(response.text);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="page-shell">
      <section className="page-heading"><div><span className="eyebrow">Per-role tailoring</span><h1>CV Optimizer</h1><p>Paste any job description. TrueFit matches it against your profile, scores the fit, and shows exactly what to add.</p></div><Button variant="secondary" icon={CircleUserRound}>Edit profile</Button></section>
      <section className="optimizer-grid">
        <article className="panel optimizer-input-panel">
          <div className="panel-head"><div><h2><FileText size={17} /> Job description</h2></div><div className="heading-actions"><Button variant="ghost" icon={Upload}>Upload</Button><button className="icon-button" onClick={() => setJd("")} title="Clear"><X size={17} /></button></div></div>
          <textarea value={jd} onChange={(e) => setJd(e.target.value)} />
          <div className="optimizer-input-footer"><Button icon={Target} onClick={renderPreview} disabled={busy || !jd.trim()}>{busy ? "Matching..." : "Match against my CV"}</Button><span>{matched.length + missing.length} requirements detected</span></div>
          <div className="parsed-requirements"><strong>Parsed requirements</strong><div className="skills">{[...matched, ...missing].map((skill) => <span className="skill" key={skill}>{skill}</span>)}</div></div>
        </article>

        <div className="optimizer-results">
          <article className="panel optimizer-score-card">
            <Score value={62} />
            <div><h2>Your match</h2><p>You match <strong>4/10</strong> requirements. Closing the 6 gaps below could lift you into the shortlist.</p><Button icon={Sparkles} onClick={renderPreview} disabled={busy || !jd.trim()}>{busy ? "Applying..." : "Apply all optimisations"}</Button></div>
          </article>

          <article className="panel">
            <SkillSection title="You match" items={matched} tone="match" />
            <SkillSection title="Missing" items={missing} tone="missing" />
          </article>

          <article className="panel optimisation-panel">
            <div className="panel-head"><div><h2>Optimisation suggestions</h2><p>Add each to your CV to raise your match score.</p></div></div>
            <div className="suggestion-list">{suggestions.map(([title, body]) => <div className="suggestion-row" key={title}><Sparkles size={16} /><div><strong>{title}</strong><p>{body}</p></div><Button variant="secondary" icon={Check}>Add</Button></div>)}</div>
          </article>
        </div>
      </section>
      {result && <section className="panel result-panel cv-preview-panel"><div className="panel-head"><div><h2>Tailored CV preview</h2><p>Generated through the FastAPI backend.</p></div><Score value={78} /></div><pre>{result}</pre></section>}
    </div>
  );
}

function RecruiterWorkspace({ onOpenReport, screening }) {
  const [query, setQuery] = useState("");
  const [showFilters, setShowFilters] = useState(false);
  const [statusFilter, setStatusFilter] = useState("All");
  const [minScore, setMinScore] = useState(0);
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const fileInputRef = useRef(null);
  const {
    jobDescription,
    setJobDescription,
    candidates,
    setCandidates,
    selectedCandidate,
    setSelectedCandidate,
    candidateMessages,
    setCandidateMessages,
    reviewedMessages,
    setReviewedMessages,
    sentMessages,
    setSentMessages,
    hasReviewed,
    setHasReviewed,
    threshold,
    setThreshold,
  } = screening;

  const reviewedCandidates = useMemo(() => candidates.filter((candidate) => typeof candidate.score === "number"), [candidates]);
  const rows = useMemo(() => reviewedCandidates.filter((candidate) => {
    const matchesQuery = `${candidate.name} ${candidate.role} ${(candidate.skills || []).join(" ")}`.toLowerCase().includes(query.toLowerCase());
    const matchesStatus = statusFilter === "All" || candidate.status === statusFilter;
    const matchesScore = (candidate.score || 0) >= minScore;
    return matchesQuery && matchesStatus && matchesScore;
  }), [reviewedCandidates, query, statusFilter, minScore]);
  const topScore = reviewedCandidates.length ? Math.max(...reviewedCandidates.map((candidate) => candidate.score || 0)) : 0;
  const averageScore = reviewedCandidates.length ? Math.round(reviewedCandidates.reduce((total, candidate) => total + (candidate.score || 0), 0) / reviewedCandidates.length) : 0;
  const shortlisted = reviewedCandidates.filter((candidate) => (candidate.score || 0) >= threshold).length;
  const belowThreshold = reviewedCandidates.filter((candidate) => (candidate.score || 0) < threshold).length;
  const selectedMessage = selectedCandidate ? candidateMessages[selectedCandidate.name] : null;
  const selectedReviewed = selectedCandidate ? Boolean(reviewedMessages[selectedCandidate.name]) : false;
  const selectedSent = selectedCandidate ? Boolean(sentMessages[selectedCandidate.name]) : false;
  const jobTitle = getJobTitle(jobDescription);

  function startNewScreening() {
    setJobDescription("");
    setCandidates([]);
    setSelectedCandidate(null);
    setCandidateMessages({});
    setReviewedMessages({});
    setSentMessages({});
    setHasReviewed(false);
    setQuery("");
    setShowFilters(false);
    setStatusFilter("All");
    setMinScore(0);
    setError("");
    setStatus("New screening started. Add the job description, upload resumes, then click Review CVs.");
  }

  async function processUploadedFiles(event) {
    const files = Array.from(event.target.files || []);
    if (!files.length) return;

    setBusy(true);
    setError("");
    setCandidateMessages({});
    setReviewedMessages({});
    setSentMessages({});
    setHasReviewed(false);
    setStatus(`Extracting ${files.length} resume${files.length === 1 ? "" : "s"}...`);

    try {
      const extracted = [];
      for (const file of files) {
        const result = await api.extractResume(file);
        extracted.push({
          name: file.name.replace(/\.pdf$/i, "").replace(/[_-]+/g, " "),
          resume: result.text,
        });
      }

      const nextCandidates = extracted.map((candidate) => ({
        name: candidate.name,
        role: "Uploaded resume",
        score: null,
        status: "Pending Review",
        skills: inferSkills(candidate.resume),
        resume: candidate.resume,
      }));

      setCandidates(nextCandidates);
      setSelectedCandidate(nextCandidates[0] || null);
      setStatus(`${nextCandidates.length} resume${nextCandidates.length === 1 ? "" : "s"} staged. Paste or confirm the JD, then click Review CVs to rank them.`);
    } catch (err) {
      setError(err.message);
      setStatus("");
    } finally {
      setBusy(false);
      event.target.value = "";
    }
  }

  async function reviewCVs() {
    if (!jobDescription.trim()) {
      setError("Paste a job description before reviewing CVs.");
      return;
    }
    if (!candidates.length) {
      setError("Upload or add candidates before reviewing CVs.");
      return;
    }

    setBusy(true);
    setError("");
    setCandidateMessages({});
    setReviewedMessages({});
    setSentMessages({});
    setStatus(`Reviewing ${candidates.length} CV${candidates.length === 1 ? "" : "s"} against the ${threshold}% threshold...`);

    try {
      const ranked = await api.matchBatch({
        job_description: jobDescription,
        candidates: candidates.map((candidate) => ({
          name: candidate.name,
          resume: candidate.resume || `${candidate.role} ${(candidate.skills || []).join(" ")}`,
        })),
      });
      const rankedCandidates = ranked.candidates.map((candidate, index) => ({
        name: candidate.candidate_name || candidate.name || candidates[index]?.name || `Candidate ${index + 1}`,
        role: getJobTitle(jobDescription),
        score: Math.round((candidate.score || 0) * 100),
        status: "Reviewing",
        skills: inferSkills(candidate.resume || candidates[index]?.resume),
        resume: candidate.resume || candidates[index]?.resume,
      }));
      const nextMessages = {};
      const nextCandidates = [];

      for (const candidate of rankedCandidates) {
        const payload = {
          job_description: jobDescription,
          candidate_resume: candidate.resume || `${candidate.role} ${(candidate.skills || []).join(" ")}`,
          candidate_name: candidate.name,
        };

        if ((candidate.score || 0) < threshold) {
          const result = await api.feedback(payload);
          nextMessages[candidate.name] = {
            type: "feedback",
            title: "Personalised rejection feedback",
            body: result.feedback,
          };
          nextCandidates.push({ ...candidate, status: "Reject" });
        } else {
          const result = await api.invite(payload);
          nextMessages[candidate.name] = {
            type: "invite",
            title: "Interview invite",
            subject: result.subject,
            body: result.invite,
          };
          nextCandidates.push({ ...candidate, status: "Shortlist" });
        }
      }

      setCandidates(nextCandidates);
      setSelectedCandidate(nextCandidates[0] || null);
      setCandidateMessages(nextMessages);
      setHasReviewed(true);
      const nextBelowThreshold = nextCandidates.filter((candidate) => candidate.score < threshold).length;
      setStatus(`${nextBelowThreshold} feedback email${nextBelowThreshold === 1 ? "" : "s"} and ${nextCandidates.length - nextBelowThreshold} interview invite${nextCandidates.length - nextBelowThreshold === 1 ? "" : "s"} generated.`);
    } catch (err) {
      setError(err.message);
      setStatus("");
    } finally {
      setBusy(false);
    }
  }

  function updateCandidateStatus(candidateName, nextStatus) {
    setCandidates((current) => current.map((candidate) => (
      candidate.name === candidateName ? { ...candidate, status: nextStatus } : candidate
    )));
    setSelectedCandidate((current) => (
      current?.name === candidateName ? { ...current, status: nextStatus } : current
    ));
  }

  function markFeedbackSent() {
    if (!selectedCandidate) return;
    if (!selectedReviewed) {
      setError("A human compliance check is required before this message can be sent.");
      return;
    }
    setSentMessages((current) => ({ ...current, [selectedCandidate.name]: true }));
    setError("");
    setStatus(`${selectedMessage?.type === "invite" ? "Interview invite" : "Feedback"} marked as sent to ${selectedCandidate.name}.`);
  }

  function setSelectedReviewed(checked) {
    if (!selectedCandidate) return;
    setReviewedMessages((current) => ({ ...current, [selectedCandidate.name]: checked }));
  }

  function inferSkills(resumeText = "") {
    const text = resumeText.toLowerCase();
    return ["React", "TypeScript", "Accessibility", "Testing", "GraphQL", "Python", "SQL", "CSS"].filter((skill) => text.includes(skill.toLowerCase())).slice(0, 5);
  }

  return (
    <div className="page-shell">
      <section className="page-heading"><div><span className="eyebrow">Recruiter workspace</span><h1>{jobTitle}</h1><p>Start with a job description, upload resumes, then review CVs when you are ready to rank them.</p></div><div className="heading-actions"><input ref={fileInputRef} className="hidden-input" type="file" accept="application/pdf" multiple onChange={processUploadedFiles} /><Button variant="secondary" icon={Sparkles} onClick={startNewScreening} disabled={busy}>Start screening</Button><Button variant="secondary" icon={Upload} onClick={() => fileInputRef.current?.click()} disabled={busy || !jobDescription.trim()}>Upload resumes</Button><Button icon={Sparkles} onClick={reviewCVs} disabled={busy || !candidates.length || !jobDescription.trim()}>Review CVs</Button></div></section>
      <section className="panel jd-panel">
        <div className="panel-head"><div><h2>Job description</h2><p>Resume ranking and feedback use this role description.</p></div></div>
        <textarea value={jobDescription} onChange={(event) => { setJobDescription(event.target.value); setHasReviewed(false); setCandidateMessages({}); setReviewedMessages({}); setSentMessages({}); }} placeholder="Paste the job title on the first line, then the full job description below." />
      </section>
      <section className="panel threshold-panel">
        <div><h2>Shortlist threshold</h2><p>Candidates below the line receive personalised rejection feedback; candidates at or above it receive interview invites.</p></div>
        <label className="threshold-control"><span>{threshold}%</span><input type="range" min="40" max="95" value={threshold} onChange={(event) => setThreshold(Number(event.target.value))} /></label>
        <div className="threshold-stats"><span>{hasReviewed ? belowThreshold : 0} need feedback</span><span>{hasReviewed ? reviewedCandidates.length - belowThreshold : 0} advancing</span></div>
      </section>
      {(status || error) && <div className={error ? "form-error workspace-message" : "success-message workspace-message"}>{error || status}</div>}
      {hasReviewed ? (
        <>
          <section className="metric-grid">
            {[["Candidates", String(reviewedCandidates.length), Users], ["Top match", `${topScore}%`, Target], ["Average match", `${averageScore}%`, BarChart3], ["Shortlisted", String(shortlisted), ShieldCheck]].map(([label, value, Icon]) => <article className="metric-card" key={label}><Icon size={20} /><span>{label}</span><strong>{value}</strong></article>)}
          </section>
          <section className="panel">
            <div className="workspace-toolbar"><div className="search-box"><Search size={17} /><input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search candidates or skills" /></div><Button variant="secondary" icon={ListFilter} onClick={() => setShowFilters((value) => !value)}>{showFilters ? "Hide filters" : "Filters"}</Button></div>
            {showFilters && <div className="filter-panel"><label>Status<select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}><option>All</option><option>Reviewing</option><option>Shortlist</option><option>Reject</option><option>New</option></select></label><label>Minimum match <strong>{minScore}%</strong><input type="range" min="0" max="100" value={minScore} onChange={(event) => setMinScore(Number(event.target.value))} /></label></div>}
            <div className="candidate-table">
              <div className="candidate-row candidate-header"><span>Candidate</span><span>Match</span><span>Evidence</span><span>Status</span><span /></div>
              {rows.map((candidate) => <div className={`candidate-row ${selectedCandidate?.name === candidate.name ? "selected-row" : ""}`} key={candidate.name} onClick={() => { setSelectedCandidate(candidate); onOpenReport(candidate, { jobDescription, message: candidateMessages[candidate.name] }); }}><div className="candidate-name"><span className="avatar">{candidate.name.split(" ").map((word) => word[0]).join("").slice(0, 2).toUpperCase()}</span><span><strong>{candidate.name}</strong><small>{candidate.role}</small></span></div><Score value={candidate.score} compact /><div className="skills">{(candidate.skills?.length ? candidate.skills : ["Resume parsed"]).map((skill) => <span className="skill" key={skill}>{skill}</span>)}</div><select className="status-select" value={candidate.status} onClick={(event) => event.stopPropagation()} onChange={(event) => updateCandidateStatus(candidate.name, event.target.value)} aria-label={`Status for ${candidate.name}`}><option>Reviewing</option><option>Shortlist</option><option>Reject</option></select><button className="icon-button" title="Open match report" onClick={(event) => { event.stopPropagation(); setSelectedCandidate(candidate); onOpenReport(candidate, { jobDescription, message: candidateMessages[candidate.name] }); }}><ArrowRight size={17} /></button></div>)}
            </div>
          </section>
        </>
      ) : (
        <section className="panel screening-empty">
          <div className="empty-state compact-empty">
            <FileText size={30} />
            <h2>{candidates.length ? `${candidates.length} resume${candidates.length === 1 ? "" : "s"} ready for review` : "Start a new screening run"}</h2>
            <p>{candidates.length ? "TrueFit has not ranked these CVs yet. Confirm the job description, then click Review CVs." : "Paste or confirm a job description, upload resumes, then click Review CVs to rank candidates."}</p>
            <div className="staged-resumes">
              {candidates.map((candidate) => <span className="skill" key={candidate.name}>{candidate.name}</span>)}
            </div>
          </div>
        </section>
      )}
      {selectedMessage && <section className="panel feedback-panel"><div className="panel-head"><div><h2>{selectedMessage.title}</h2><p>{selectedCandidate?.name}{selectedMessage.subject ? ` - ${selectedMessage.subject}` : ""}</p></div><Button variant="secondary" icon={Mail} onClick={() => navigator.clipboard?.writeText(selectedMessage.body)}>Copy</Button></div><pre>{selectedMessage.body}</pre><div className="feedback-review"><label className="check-row"><input type="checkbox" checked={selectedReviewed} onChange={(event) => setSelectedReviewed(event.target.checked)} /> Human compliance check completed</label><Button icon={Mail} onClick={markFeedbackSent} disabled={!selectedReviewed || selectedSent}>{selectedSent ? "Sent" : selectedMessage.type === "invite" ? "Send invite" : "Send feedback"}</Button></div>{selectedSent && <div className="success-message">Message has been marked as sent. Email delivery backend still needs to be added for real applicant email delivery.</div>}</section>}
    </div>
  );
}

function CandidateFeedbackPage() {
  const initialCandidates = [
    { name: "Yuki Tanaka", role: "Senior Frontend Engineer", company: "Mercari", score: 68, gap: "Accessibility", status: "Reviewing", resume: "Fast-rising React and TypeScript engineer with strong product work. Needs clearer accessibility evidence." },
    { name: "Tomas Novak", role: "Senior Frontend Engineer", company: "Productboard", score: 58, gap: "TypeScript", status: "New", resume: "Solid JavaScript engineer transitioning to TypeScript. Good product instincts, still building senior depth." },
    { name: "Omar Haddad", role: "Senior Frontend Engineer", company: "Careem", score: 47, gap: "TypeScript", status: "Passed", resume: "Early-career engineer with enthusiasm and fundamentals, below the senior bar for this role." },
    { name: "Amara Okafor", role: "Lead UI Engineer", company: "Mapbox", score: 92, gap: "Full match", status: "Shortlist", resume: "Lead UI engineer with React, TypeScript, accessibility, testing, CSS architecture and measurable delivery." },
    { name: "Priya Nair", role: "Staff Engineer", company: "Razorpay", score: 88, gap: "CSS Architecture", status: "Shortlist", resume: "Staff engineer with React, TypeScript, accessibility and payments dashboard delivery." },
    { name: "Diego Ramos", role: "Senior Engineer", company: "Pleo", score: 84, gap: "Accessibility", status: "Interview", resume: "Product-minded engineer with strong TypeScript and testing discipline." },
    { name: "Lena Hoffmann", role: "Senior Engineer", company: "Personio", score: 81, gap: "Testing", status: "New", resume: "Reliable senior engineer with product experience in HR technology." },
    { name: "Grace Liu", role: "Senior Engineer", company: "Hootsuite", score: 79, gap: "Accessibility", status: "Reviewing", resume: "Pragmatic engineer with strong delivery track record across social analytics products." },
    { name: "Sofia Bergstrom", role: "Frontend Engineer", company: "Klarna", score: 76, gap: "Testing", status: "Reviewing", resume: "Design-leaning engineer with sharp craft and component architecture experience." },
    { name: "Marcus Webb", role: "Senior Engineer", company: "Notion", score: 71, gap: "Accessibility", status: "Reviewing", resume: "Versatile full-stack engineer comfortable across data layer and API design." },
  ];
  const [threshold, setThreshold] = useState(70);
  const [candidates, setCandidates] = useState(initialCandidates);
  const [selected, setSelected] = useState(initialCandidates[0]);
  const [messages, setMessages] = useState({});
  const [reviewed, setReviewed] = useState({});
  const [sent, setSent] = useState({});
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");

  const jobDescription = "Senior Frontend Engineer at Northwind Labs. Requirements: expert React, strong TypeScript, accessibility WCAG, testing with Jest or React Testing Library, CSS architecture, REST and GraphQL APIs.";
  const below = candidates.filter((candidate) => candidate.score < threshold);
  const advancing = candidates.filter((candidate) => candidate.score >= threshold);
  const selectedMessage = messages[selected.name];
  const selectedReviewed = Boolean(reviewed[selected.name]);
  const selectedSent = Boolean(sent[selected.name]);

  async function generateMessages() {
    setBusy(true);
    setError("");
    setStatus(`Generating feedback and interview invites for ${candidates.length} applicants...`);
    try {
      const nextMessages = {};
      const nextCandidates = [];

      for (const candidate of candidates) {
        const payload = {
          job_description: jobDescription,
          candidate_resume: candidate.resume,
          candidate_name: candidate.name,
        };

        if (candidate.score < threshold) {
          const result = await api.feedback(payload);
          nextMessages[candidate.name] = {
            type: "feedback",
            label: "Rejection feedback",
            subject: `An update on your application for ${candidate.role}`,
            body: result.feedback,
          };
          nextCandidates.push({ ...candidate, status: "Reject" });
        } else {
          const result = await api.invite(payload);
          nextMessages[candidate.name] = {
            type: "invite",
            label: "Interview invite",
            subject: result.subject,
            body: result.invite,
          };
          nextCandidates.push({ ...candidate, status: "Shortlist" });
        }
      }

      setCandidates(nextCandidates);
      setMessages(nextMessages);
      setSelected((current) => nextCandidates.find((candidate) => candidate.name === current.name) || nextCandidates[0]);
      setStatus(`${below.length} feedback email${below.length === 1 ? "" : "s"} and ${advancing.length} interview invite${advancing.length === 1 ? "" : "s"} generated.`);
    } catch (err) {
      setError(err.message);
      setStatus("");
    } finally {
      setBusy(false);
    }
  }

  function markSent() {
    if (!selectedReviewed) {
      setError("A human compliance check is required before sending.");
      return;
    }
    setSent((current) => ({ ...current, [selected.name]: true }));
    setError("");
    setStatus(`${selectedMessage?.type === "invite" ? "Interview invite" : "Feedback"} marked as sent to ${selected.name}.`);
  }

  return (
    <div className="page-shell">
      <section className="page-heading">
        <div>
          <span className="eyebrow">Step 5 - The differentiator</span>
          <h1>Candidate feedback</h1>
          <p>Review resumes first, then generate personalised rejection feedback below threshold and interview invites above it.</p>
        </div>
        <Button variant="secondary" icon={ArrowRight} onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}>Back to ranking</Button>
      </section>

      <section className="panel feedback-threshold">
        <div className="threshold-copy">
          <strong>Shortlist threshold</strong>
          <span>{threshold}%</span>
          <input type="range" min="40" max="95" value={threshold} onChange={(event) => setThreshold(Number(event.target.value))} />
          <p>Candidates below the line are flagged for feedback; those at or above advance.</p>
        </div>
        <div className="feedback-stats">
          <span><strong>{advancing.length}</strong> Advancing</span>
          <span><strong>{below.length}</strong> Need feedback</span>
          <span><strong>100%</strong> Feedback rate</span>
        </div>
        <Button icon={Sparkles} onClick={generateMessages} disabled={busy}>{busy ? "Generating..." : `Generate ${below.length} feedback emails`}</Button>
      </section>

      {(status || error) && <div className={error ? "form-error workspace-message" : "success-message workspace-message"}>{error || status}</div>}

      <section className="feedback-workbench">
        <aside className="panel feedback-list">
          <div className="feedback-group-title"><span className="status-dot warning-dot" /> Below threshold <small>{below.length} feedback</small></div>
          {below.map((candidate) => <FeedbackCandidateButton key={candidate.name} candidate={candidate} selected={selected.name === candidate.name} onClick={() => setSelected(candidate)} />)}
          <div className="threshold-divider">{threshold}% cut-off</div>
          <div className="feedback-group-title"><span className="status-dot" /> Advancing <small>{advancing.length} interview</small></div>
          {advancing.map((candidate) => <FeedbackCandidateButton key={candidate.name} candidate={candidate} selected={selected.name === candidate.name} onClick={() => setSelected(candidate)} />)}
        </aside>

        <article className="panel feedback-composer">
          <div className="panel-head">
            <div className="candidate-name">
              <span className="avatar">{selected.name.split(" ").map((word) => word[0]).join("").slice(0, 2)}</span>
              <span><strong>{selected.name}</strong><small>{selected.role} - {selected.score}% match</small></span>
            </div>
            <button className="text-button">Full report <ArrowRight size={15} /></button>
          </div>

          <div className="email-card">
            <div className="email-card-head">
              <span><Mail size={14} /> {selectedMessage?.label || (selected.score < threshold ? "Rejection feedback" : "Interview invite")}</span>
              <small>{selectedMessage ? "auto-drafted - editable" : "not generated yet"}</small>
            </div>
            <div className="email-meta"><span>To</span><strong>{selected.name.toLowerCase().replace(" ", ".")}@email.com</strong></div>
            <div className="email-meta"><span>Subject</span><strong>{selectedMessage?.subject || "Generate messages to draft this email"}</strong></div>
            <textarea
              className="email-body"
              value={selectedMessage?.body || `Click "Generate ${below.length} feedback emails" to create the personalised message for ${selected.name}.`}
              onChange={(event) => setMessages((current) => ({
                ...current,
                [selected.name]: {
                  type: selected.score < threshold ? "feedback" : "invite",
                  label: selected.score < threshold ? "Rejection feedback" : "Interview invite",
                  subject: selectedMessage?.subject || `An update on your application for ${selected.role}`,
                  body: event.target.value,
                },
              }))}
            />
            <label className="compliance-box">
              <input type="checkbox" checked={selectedReviewed} onChange={(event) => setReviewed((current) => ({ ...current, [selected.name]: event.target.checked }))} />
              <span><ShieldCheck size={15} /> Compliance check</span>
              <small>I confirm this is objective, role-related, and free of discriminatory content.</small>
            </label>
            <div className="composer-actions">
              <Button icon={Mail} onClick={markSent} disabled={!selectedMessage || !selectedReviewed || selectedSent}>{selectedSent ? "Sent" : selectedMessage?.type === "invite" ? "Send invite" : "Send feedback"}</Button>
              <Button variant="secondary" icon={FileText} onClick={() => selectedMessage && navigator.clipboard?.writeText(selectedMessage.body)} disabled={!selectedMessage}>Copy</Button>
              <Button variant="ghost" icon={Sparkles} onClick={generateMessages} disabled={busy}>Regenerate</Button>
              {!selectedReviewed && <span className="send-hint">Tick the compliance box to send</span>}
            </div>
          </div>

          <div className="why-row">
            {["Role-specific", "Actionable", "Empathetic", "Legally considered", "< 60s to draft"].map((item) => <span className="skill" key={item}>{item}</span>)}
          </div>
        </article>
      </section>
    </div>
  );
}

function FeedbackCandidateButton({ candidate, selected, onClick }) {
  return (
    <button className={`feedback-candidate ${selected ? "active" : ""}`} onClick={onClick}>
      <span className="avatar">{candidate.name.split(" ").map((word) => word[0]).join("").slice(0, 2)}</span>
      <span className="grow"><strong>{candidate.name}</strong><small>Gap: {candidate.gap}</small></span>
      <Score value={candidate.score} compact />
    </button>
  );
}

function CandidatesPage({ onOpenReport }) {
  const [query, setQuery] = useState("");
  const [roleFilter, setRoleFilter] = useState("All roles");
  const [statusFilter, setStatusFilter] = useState("All statuses");
  const candidates = [
    { name: "Amara Okafor", title: "Lead UI Engineer", company: "Mapbox", role: "Senior Frontend Engineer", score: 92, status: "Shortlist", exp: "8y", source: "Referral", skills: ["React", "TypeScript", "Accessibility"], resume: "Lead UI engineer with React, TypeScript, accessibility, testing, CSS architecture and measurable delivery." },
    { name: "Nina Petrova", title: "EM", company: "GitLab", role: "Engineering Manager", score: 90, status: "Shortlist", exp: "11y", source: "Referral", skills: ["Leadership", "Delivery", "Systems"], resume: "Engineering manager with strong delivery systems and people leadership." },
    { name: "Hannah Reed", title: "Senior Designer", company: "Pitch", role: "Product Designer", score: 89, status: "Shortlist", exp: "7y", source: "Referral", skills: ["Design Systems", "Research", "Product"], resume: "Senior product designer with strong design-system craft and research instincts." },
    { name: "Priya Nair", title: "Staff Engineer", company: "Razorpay", role: "Senior Frontend Engineer", score: 88, status: "Shortlist", exp: "9y", source: "Inbound", skills: ["React", "TypeScript", "Accessibility"], resume: "Staff engineer with React, TypeScript, accessibility and payments dashboard delivery." },
    { name: "Carlos Mendez", title: "Senior Engineer", company: "Stripe", role: "Backend Engineer (Go)", score: 86, status: "Interview", exp: "6y", source: "Inbound", skills: ["Go", "APIs", "Systems"], resume: "Backend engineer with Go, API platform experience and distributed systems depth." },
    { name: "Diego Ramos", title: "Senior Engineer", company: "Pleo", role: "Senior Frontend Engineer", score: 84, status: "Interview", exp: "6y", source: "LinkedIn", skills: ["React", "TypeScript", "Testing"], resume: "Product-minded engineer with strong TypeScript and testing discipline." },
    { name: "Lena Hoffmann", title: "Senior Engineer", company: "Personio", role: "Senior Frontend Engineer", score: 81, status: "New", exp: "8y", source: "Referral", skills: ["React", "TypeScript", "Accessibility"], resume: "Reliable senior engineer with product experience in HR technology." },
    { name: "Aisha Bello", title: "Analyst", company: "Monzo", role: "Data Analyst", score: 81, status: "Reviewing", exp: "5y", source: "LinkedIn", skills: ["SQL", "Python", "Dashboards"], resume: "Analyst with strong SQL and product analytics experience." },
    { name: "Grace Liu", title: "Senior Engineer", company: "Hootsuite", role: "Senior Frontend Engineer", score: 79, status: "Reviewing", exp: "6y", source: "Inbound", skills: ["React", "TypeScript", "Testing"], resume: "Pragmatic engineer with strong delivery track record across social analytics products." },
    { name: "Sofia Bergstrom", title: "Frontend Engineer", company: "Klarna", role: "Senior Frontend Engineer", score: 76, status: "Reviewing", exp: "5y", source: "LinkedIn", skills: ["React", "TypeScript", "CSS Architecture"], resume: "Design-leaning engineer with sharp craft and component architecture experience." },
    { name: "Leo Fontaine", title: "Designer", company: "Alan", role: "Product Designer", score: 72, status: "New", exp: "4y", source: "LinkedIn", skills: ["Product", "Research", "Visual Design"], resume: "Designer with product sense and thoughtful visual systems work." },
    { name: "Marcus Webb", title: "Senior Engineer", company: "Notion", role: "Senior Frontend Engineer", score: 71, status: "Reviewing", exp: "7y", source: "Inbound", skills: ["React", "TypeScript", "REST/GraphQL"], resume: "Versatile full-stack engineer comfortable across data layer and API design." },
    { name: "Yuki Tanaka", title: "Engineer", company: "Mercari", role: "Senior Frontend Engineer", score: 68, status: "New", exp: "4y", source: "LinkedIn", skills: ["React", "CSS Architecture"], resume: "Fast-rising React and TypeScript engineer with strong product work. Needs clearer accessibility evidence." },
    { name: "Wei Zhang", title: "Engineer", company: "Grab", role: "Backend Engineer (Go)", score: 64, status: "New", exp: "4y", source: "Inbound", skills: ["Go", "APIs"], resume: "Backend engineer with API experience but lighter Go systems evidence." },
    { name: "Tomas Novak", title: "Engineer", company: "Productboard", role: "Senior Frontend Engineer", score: 58, status: "New", exp: "5y", source: "LinkedIn", skills: ["React", "CSS Architecture", "REST/GraphQL"], resume: "Solid JavaScript engineer transitioning to TypeScript. Good product instincts, still building senior depth." },
    { name: "Omar Haddad", title: "Engineer", company: "Careem", role: "Senior Frontend Engineer", score: 47, status: "Reject", exp: "3y", source: "LinkedIn", skills: ["React", "CSS Architecture"], resume: "Early-career engineer with enthusiasm and fundamentals, below the senior bar for this role." },
  ];
  const roles = ["All roles", ...Array.from(new Set(candidates.map((candidate) => candidate.role)))];
  const statuses = ["All statuses", ...Array.from(new Set(candidates.map((candidate) => candidate.status)))];
  const filteredCandidates = candidates.filter((candidate) => {
    const searchTarget = `${candidate.name} ${candidate.title} ${candidate.company} ${candidate.role} ${candidate.source}`.toLowerCase();
    const matchesQuery = searchTarget.includes(query.toLowerCase());
    const matchesRole = roleFilter === "All roles" || candidate.role === roleFilter;
    const matchesStatus = statusFilter === "All statuses" || candidate.status === statusFilter;
    return matchesQuery && matchesRole && matchesStatus;
  });
  const exportPool = () => downloadCsv(
    [
      ["Candidate", "Current title", "Company", "Applied for", "Match score", "Status", "Experience", "Source"],
      ...filteredCandidates.map((candidate) => [candidate.name, candidate.title, candidate.company, candidate.role, `${candidate.score}%`, candidate.status, candidate.exp, candidate.source]),
    ],
    "truefit-talent-pool.csv",
  );

  return (
    <div className="page-shell">
      <section className="page-heading"><div><span className="eyebrow">Talent pool</span><h1>Candidates</h1><p>Everyone screened across all roles, ranked by match strength.</p></div><Button variant="secondary" icon={Upload} onClick={exportPool} disabled={!filteredCandidates.length}>Export pool</Button></section>
      <section className="panel candidates-panel">
        <div className="workspace-toolbar candidates-toolbar">
          <div className="search-box"><Search size={17} /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search name, role, company..." /></div>
          <div className="heading-actions">
            <select className="simple-select" value={roleFilter} onChange={(event) => setRoleFilter(event.target.value)}>{roles.map((role) => <option key={role}>{role}</option>)}</select>
            <select className="simple-select" value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}>{statuses.map((status) => <option key={status}>{status}</option>)}</select>
          </div>
        </div>
        <p className="table-count">{filteredCandidates.length} candidate{filteredCandidates.length === 1 ? "" : "s"} shown</p>
        <div className="candidate-table candidate-pool-table">
          <div className="candidate-row candidate-header candidate-pool-row"><span>Candidate</span><span>Applied for</span><span>Match</span><span>Status</span><span>Exp</span><span>Source</span><span /></div>
          {filteredCandidates.map((candidate) => <div className="candidate-row candidate-pool-row" key={candidate.name} onClick={() => onOpenReport(candidate)}><div className="candidate-name"><span className="avatar">{candidate.name.split(" ").map((word) => word[0]).join("").slice(0, 2)}</span><span><strong>{candidate.name}</strong><small>{candidate.title} - {candidate.company}</small></span></div><span className="table-role">{candidate.role}</span><div className="match-cell"><div className="mini-score-track"><span style={{ width: `${candidate.score}%` }} /></div><Score value={candidate.score} compact /></div><span className={`status-pill status-${candidate.status.toLowerCase()}`}>{candidate.status}</span><strong>{candidate.exp}</strong><span className="muted-cell">{candidate.source}</span><ChevronRight size={17} /></div>)}
        </div>
        {!filteredCandidates.length && <div className="empty-state compact-empty"><Search size={24} /><h2>No candidates found</h2><p>Adjust the search or filters to widen the talent pool.</p></div>}
      </section>
    </div>
  );
}

function MatchReportPage({ candidate, setPage, reportContext }) {
  const activeCandidate = candidate || { name: "Tomas Novak", role: "Senior Frontend Engineer", score: 58, status: "New", skills: ["React", "CSS Architecture", "REST/GraphQL"], resume: "Solid JavaScript engineer transitioning to TypeScript. Good product instincts, still building senior depth." };
  const [status, setStatus] = useState(activeCandidate.status || "New");
  const generatedMessage = reportContext?.message;
  const score = activeCandidate.score || 0;
  const tone = score >= 80 ? "Strong fit" : score >= 65 ? "Potential fit" : "Possible fit";
  const matched = activeCandidate.skills?.length ? activeCandidate.skills : ["React", "CSS Architecture", "REST/GraphQL"];
  const missing = score >= 80 ? ["Performance"] : score >= 65 ? ["Accessibility (WCAG)", "Testing (Jest/RTL)"] : ["TypeScript", "Accessibility (WCAG)", "Testing (Jest/RTL)"];
  const bonus = score >= 80 ? ["Design Systems", "Leadership"] : ["Node.js"];
  const feedbackType = generatedMessage?.title || (generatedMessage?.type === "invite" ? "Interview invite" : generatedMessage?.type === "feedback" ? "Rejection feedback" : score >= 70 ? "Interview invite" : "Rejection feedback");
  const fallbackFeedbackBody = score >= 70
    ? `Hi ${activeCandidate.name.split(" ")[0]},\n\nThank you for applying for the ${activeCandidate.role} role at Northwind Labs. Your CV shows strong alignment with the role, especially around ${matched.slice(0, 2).join(" and ")}.\n\nWe would like to invite you to the next interview stage so we can learn more about your recent work and the impact you have had on product teams.`
    : `Hi ${activeCandidate.name.split(" ")[0]},\n\nThank you for taking the time to apply for the ${activeCandidate.role} role at Northwind Labs. After careful review, we will not be moving forward on this occasion.\n\nYour CV showed relevant strengths in ${matched.slice(0, 2).join(" and ")}, but the main gaps for this role were ${missing.slice(0, 2).join(" and ")}. For future applications, add concrete examples, project scope, and outcomes in these areas.`;
  const feedbackBody = generatedMessage?.body || generatedMessage?.invite || generatedMessage?.feedback || fallbackFeedbackBody;
  const feedbackSubject = generatedMessage?.subject || `An update on your application for ${activeCandidate.role}`;

  function moveForward() {
    setStatus(score >= 70 ? "Interview" : "Reviewing");
  }

  return (
    <div className="page-shell match-report-page">
      <div className="breadcrumb"><button onClick={() => setPage("recruiter")}>Ranked candidates</button><span>/</span><strong>{activeCandidate.name}</strong></div>

      <section className="panel report-hero">
        <div className="candidate-name report-name">
          <span className="large-avatar">{activeCandidate.name.split(" ").map((word) => word[0]).join("").slice(0, 2)}</span>
          <span><h1>{activeCandidate.name}</h1><small>{activeCandidate.role} - via LinkedIn</small></span>
        </div>
        <div className="report-hero-actions">
          <span className="status-tag">{status}</span>
          <span className="status-tag">Rank #9</span>
          <Button variant="secondary" icon={Upload}>Export report</Button>
          <select className="status-select report-status" value={status} onChange={(event) => setStatus(event.target.value)}>
            <option>New</option>
            <option>Reviewing</option>
            <option>Shortlist</option>
            <option>Interview</option>
            <option>Reject</option>
          </select>
        </div>
      </section>

      <section className="report-layout">
        <div className="report-main">
          <article className="panel match-summary">
            <Score value={score} />
            <div>
              <span className="status-tag">{score >= 80 ? "Excellent match" : score >= 65 ? "Fair match" : "Review carefully"}</span>
              <h2>{tone} - review evidence</h2>
              <p>Matches <strong>{matched.length}/{matched.length + missing.length}</strong> required skills with <strong>{missing.length} gap{missing.length === 1 ? "" : "s"}</strong> to probe.</p>
            </div>
          </article>

          <article className="panel feedback-panel report-feedback">
            <div className="panel-head"><div><h2>Candidate feedback</h2><p>{score < 70 ? "Below the threshold - personalised constructive feedback is ready." : "At or above threshold - interview invite is ready."}</p></div><span className="status-tag">Auto-generated</span></div>
            <div className="email-card">
              <div className="email-card-head"><span><Mail size={14} /> {feedbackType}</span><small>editable</small></div>
              <div className="email-meta"><span>To</span><strong>{activeCandidate.name.toLowerCase().replace(" ", ".")}@email.com</strong></div>
              <div className="email-meta"><span>Subject</span><strong>{feedbackSubject}</strong></div>
              <textarea className="email-body" defaultValue={feedbackBody} />
              <label className="compliance-box"><input type="checkbox" /><span><ShieldCheck size={15} /> Compliance check</span><small>Human reviewed, objective, role-related, and free of discriminatory content.</small></label>
              <div className="composer-actions"><Button icon={Mail}>{score >= 70 ? "Send invite" : "Send feedback"}</Button><Button variant="secondary" icon={FileText}>Copy</Button><Button variant="ghost" icon={Sparkles}>Regenerate</Button></div>
            </div>
          </article>

          <article className="panel">
            <h2>Score breakdown</h2>
            <ScoreBar label="Required skills" value={Math.min(96, score + 8)} weight="50%" />
            <ScoreBar label="Experience and seniority" value={Math.max(52, score - 2)} weight="30%" />
            <ScoreBar label="Nice-to-have skills" value={Math.max(48, score - 6)} weight="20%" />
          </article>

          <article className="panel">
            <h2>Skill match</h2>
            <SkillSection title="Matched requirements" items={matched} tone="match" />
            <SkillSection title="Missing requirements" items={missing} tone="missing" />
            <SkillSection title="Bonus skills" items={bonus} tone="bonus" />
          </article>
        </div>

        <aside className="report-side">
          <article className="panel insight-card"><h2><Sparkles size={17} /> AI summary</h2><p>{activeCandidate.resume || "Candidate has relevant product experience. Review gaps before deciding final stage."}</p></article>
          <article className="panel"><h2>Highlights</h2><ul className="clean-list"><li>Shipped onboarding flow</li><li>Strong product instincts</li><li>Clear frontend foundation</li></ul></article>
          <article className="panel"><h2>Recommended next step</h2><ol className="number-list">{missing.slice(0, 3).map((item) => <li key={item}>Probe concrete evidence of {item}: projects, scope, and outcomes.</li>)}</ol></article>
          <article className="panel resume-preview"><div className="panel-head"><h2>Resume</h2><button className="text-button">Open</button></div><div>resume_preview.pdf</div></article>
        </aside>
      </section>

      <div className="report-bottom-actions">
        <Button variant="secondary" icon={ChevronRight} onClick={() => setPage("recruiter")}>Back to ranking</Button>
        <Button icon={Check} onClick={moveForward}>{score >= 70 ? "Move to interview" : "Keep reviewing"}</Button>
      </div>
    </div>
  );
}

function ScoreBar({ label, value, weight }) {
  return (
    <div className="score-bar">
      <div><strong>{label}</strong><span>Weighted {weight}</span></div>
      <div className="progress-track"><span style={{ width: `${value}%` }} /></div>
      <b>{value}%</b>
    </div>
  );
}

function SkillSection({ title, items, tone }) {
  return (
    <div className="skill-section">
      <strong>{title} - {items.length}</strong>
      <div className="skills">{items.map((item) => <span className={`skill skill-${tone}`} key={item}>{item}</span>)}</div>
    </div>
  );
}

function ReportsPage() {
  const currentMetrics = [
    ["Candidates screened", "64", "of 85 applied", Users],
    ["Average match", "77%", "across all roles", Target],
    ["Shortlist rate", "23%", "15 shortlisted", ShieldCheck],
    ["Avg time-to-screen", "1.4d", "down 0.6d", BarChart3],
  ];
  const recruitmentMetrics = [
    { id: "time-fill", label: "Time to fill", value: "32d", detail: "Job published to candidate hired" },
    { id: "time-hire", label: "Time to hire", value: "18d", detail: "Candidate approached to offer accepted" },
    { id: "cost-hire", label: "Cost per hire", value: "£4,250", detail: "Internal + external hiring cost per hire" },
    { id: "quality-hire", label: "Quality of hire", value: "86%", detail: "Hires meeting first-year performance expectations" },
    { id: "source-hire", label: "Source of hire", value: "Referral", detail: "Top sourcing channel for successful hires" },
    { id: "first-year-resignation", label: "First-year resignation rate", value: "4%", detail: "First-year resignations / headcount" },
    { id: "first-year-turnover", label: "First-year turnover rate", value: "7%", detail: "First-year leavers / recruits" },
    { id: "first-month-turnover", label: "First-month turnover rate", value: "1%", detail: "First-month leavers / recruits" },
    { id: "manager-satisfaction", label: "Hiring manager satisfaction", value: "88%", detail: "Hires performing well / total hires" },
    { id: "candidate-satisfaction", label: "Candidate job satisfaction", value: "84%", detail: "Satisfied new hires / total hires" },
    { id: "applicants-opening", label: "Applicants per opening", value: "17", detail: "Applicants / job openings" },
    { id: "selection-ratio", label: "Selection ratio", value: "2.4%", detail: "Hires / total candidates" },
    { id: "offer-acceptance", label: "Offer acceptance rate", value: "83%", detail: "Accepted offers / offers made" },
    { id: "vacancy-rate", label: "Vacancy rate", value: "6%", detail: "Open positions / total positions" },
    { id: "completion-rate", label: "Application completion rate", value: "79%", detail: "Completed / started applications" },
    { id: "yield-ratio", label: "Yield ratio", value: "23%", detail: "Candidates completing the current stage" },
    { id: "source-effectiveness", label: "Sourcing channel effectiveness", value: "12.8", detail: "Channel impressions per application" },
    { id: "source-cost", label: "Sourcing channel cost", value: "£310", detail: "Channel spend per successful applicant" },
    { id: "opl-cost", label: "Cost to optimum productivity", value: "£7,900", detail: "Onboarding and ramp-up cost to full productivity" },
  ];
  const [selectedMetricIds, setSelectedMetricIds] = useState(["time-fill", "time-hire", "cost-hire", "quality-hire"]);
  const selectedRecruitmentMetrics = recruitmentMetrics.filter((metric) => selectedMetricIds.includes(metric.id));
  const toggleMetric = (id) => setSelectedMetricIds((selected) => selected.includes(id) ? selected.filter((item) => item !== id) : [...selected, id]);
  const funnel = [
    ["Applied", 85, 100],
    ["Screened", 64, 75],
    ["Shortlisted", 15, 23],
    ["Interview", 6, 40],
    ["Offer", 2, 33],
  ];
  const sources = [
    ["LinkedIn", 44],
    ["Inbound", 31],
    ["Referral", 25],
  ];
  const roles = [
    ["Senior Frontend Engineer", "Engineering", 10, 74, 92],
    ["Product Designer", "Design", 18, 71, 89],
    ["Backend Engineer (Go)", "Engineering", 23, 68, 86],
    ["Data Analyst", "Data", 12, 66, 81],
    ["Engineering Manager", "Engineering", 7, 78, 90],
  ];
  const exportReport = () => downloadTextPdf([
    "TRUEFIT HIRING REPORT",
    `Generated: ${new Date().toLocaleDateString("en-GB")}`,
    "",
    "CURRENT METRICS",
    ...currentMetrics.map(([label, value, detail]) => `${label}: ${value} - ${detail}`),
    "",
    "SELECTED RECRUITMENT METRICS",
    ...(selectedRecruitmentMetrics.length ? selectedRecruitmentMetrics.map(({ label, value, detail }) => `${label}: ${value} - ${detail}`) : ["No additional recruitment metrics selected"]),
    "",
    "HIRING FUNNEL",
    ...funnel.map(([label, count]) => `${label}: ${count}`),
    "",
    "CANDIDATE SOURCES",
    ...sources.map(([label, value]) => `${label}: ${value}%`),
  ], "truefit-hiring-report.pdf");

  return (
    <div className="page-shell">
      <section className="page-heading"><div><span className="eyebrow">Insights</span><h1>Hiring reports</h1><p>Pipeline health, match quality, and sourcing performance across roles.</p></div><Button variant="secondary" icon={Upload} onClick={exportReport}>Export PDF</Button></section>
      <section className="metric-grid">
        {currentMetrics.map(([label, value, detail, Icon]) => <article className="metric-card report-metric" key={label}><Icon size={20} /><span>{label}</span><strong>{value}</strong><small>{detail}</small></article>)}
      </section>
      <section className="panel metric-selector-panel">
        <div><h2>Recruitment metrics</h2><p>Select the additional recruitment metrics to include on screen and in the PDF.</p></div>
        <details className="metric-dropdown">
          <summary><span>{selectedMetricIds.length ? `${selectedMetricIds.length} metric${selectedMetricIds.length === 1 ? "" : "s"} selected` : "Choose metrics"}</span><ChevronRight size={17} /></summary>
          <div className="metric-dropdown-menu">
            <div className="metric-selector-actions"><strong>Available metrics</strong><span><button className="text-button" type="button" onClick={() => setSelectedMetricIds(recruitmentMetrics.map(({ id }) => id))}>Select all</button><button className="text-button" type="button" onClick={() => setSelectedMetricIds([])}>Clear</button></span></div>
            <div className="metric-options">{recruitmentMetrics.map((metric) => <label className={selectedMetricIds.includes(metric.id) ? "metric-option selected" : "metric-option"} key={metric.id}><input type="checkbox" checked={selectedMetricIds.includes(metric.id)} onChange={() => toggleMetric(metric.id)} /><span><strong>{metric.label}</strong><small>{metric.detail}</small></span></label>)}</div>
          </div>
        </details>
      </section>
      {selectedRecruitmentMetrics.length > 0 && <section className="metric-grid selected-report-metrics">
        {selectedRecruitmentMetrics.map(({ id, label, value, detail }) => <article className="metric-card report-metric" key={id}><BarChart3 size={20} /><span>{label}</span><strong>{value}</strong><small>{detail}</small></article>)}
      </section>}
      <section className="report-grid">
        <article className="panel"><div className="panel-head"><div><h2>Match score distribution</h2><p>How the screened pool spreads across quality tiers.</p></div></div><div className="distribution"><span style={{ height: "72%" }}>8<small>Excellent<br />80-100</small></span><span style={{ height: "54%" }}>5<small>Good<br />65-79</small></span><span style={{ height: "32%" }}>2<small>Fair<br />50-64</small></span><span style={{ height: "20%" }}>1<small>Limited<br />0-49</small></span></div></article>
        <article className="panel"><div className="panel-head"><div><h2>Hiring funnel</h2><p>Conversion from applicant to offer.</p></div></div>{funnel.map(([label, count, width]) => <div className="funnel-row" key={label}><span>{label}</span><div><i style={{ width: `${width}%` }} /></div><strong>{count}</strong></div>)}</article>
      </section>
      <section className="report-grid lower-report-grid">
        <article className="panel"><div className="panel-head"><div><h2>Candidate sources</h2><p>Where your pool comes from.</p></div></div><div className="source-list">{sources.map(([label, value]) => <div className="source-row" key={label}><div><span className="source-dot" /><strong>{label}</strong><small>{value}%</small></div><div className="progress-track"><span style={{ width: `${value}%` }} /></div></div>)}</div></article>
        <article className="panel role-performance-panel"><div className="panel-head"><div><h2>Role performance</h2><p>Pipeline quality by active role.</p></div></div><div className="role-performance-table"><div className="role-performance-row role-performance-head"><span>Role</span><span>Pool</span><span>Avg match</span><span>Top</span></div>{roles.map(([role, team, pool, avg, top]) => <div className="role-performance-row" key={role}><div><strong>{role}</strong><small>{team}</small></div><span>{pool}</span><div className="match-cell"><div className="mini-score-track"><span style={{ width: `${avg}%` }} /></div><b>{avg}%</b></div><Score value={top} compact /></div>)}</div></article>
      </section>
    </div>
  );
}

function JobsPage({ setPage, onStartScreening }) {
  const [filter, setFilter] = useState("All Roles");
  const roles = [
    { title: "Senior Frontend Engineer", team: "Engineering", location: "Remote - US / EU", status: "Open", applicants: 10, top: 92, shortlisted: 4, screened: 10, total: 10, lead: "Jordan Reyes", posted: "Apr 28" },
    { title: "Product Designer", team: "Design", location: "Berlin, DE", status: "Open", applicants: 18, top: 89, shortlisted: 5, screened: 14, total: 18, lead: "Mia Chen", posted: "May 04" },
    { title: "Backend Engineer (Go)", team: "Engineering", location: "Remote - Global", status: "Open", applicants: 23, top: 86, shortlisted: 2, screened: 9, total: 23, lead: "Jordan Reyes", posted: "May 09" },
    { title: "Data Analyst", team: "Data", location: "London, UK", status: "Paused", applicants: 12, top: 81, shortlisted: 3, screened: 12, total: 12, lead: "Sam Patel", posted: "Apr 15" },
    { title: "Engineering Manager", team: "Engineering", location: "Remote - US", status: "Open", applicants: 7, top: 90, shortlisted: 1, screened: 4, total: 7, lead: "Mia Chen", posted: "May 12" },
    { title: "DevOps Engineer", team: "Platform", location: "Austin, US", status: "Closed", applicants: 15, top: 77, shortlisted: 0, screened: 15, total: 15, lead: "Sam Patel", posted: "Mar 30" },
  ];
  const filteredRoles = roles.filter((role) => filter === "All Roles" || role.status === filter);
  const activeRoles = roles.filter((role) => role.status === "Open").length;
  const pipeline = roles.reduce((total, role) => total + role.applicants, 0);
  const shortlisted = roles.reduce((total, role) => total + role.shortlisted, 0);

  return (
    <div className="page-shell">
      <section className="page-heading">
        <div>
          <span className="eyebrow">Hiring</span>
          <h1>Open roles</h1>
          <p>Every role you are screening for, with live pipeline health at a glance.</p>
        </div>
        <Button icon={BriefcaseBusiness} onClick={() => onStartScreening()}>New job</Button>
      </section>

      <section className="metric-grid">
        {[["Active roles", String(activeRoles), BriefcaseBusiness], ["In pipeline", String(pipeline), Users], ["Shortlisted", String(shortlisted), ShieldCheck], ["Avg time-to-screen", "1.4d", BarChart3]].map(([label, value, Icon]) => <article className="metric-card" key={label}><Icon size={20} /><span>{label}</span><strong>{value}</strong></article>)}
      </section>

      <div className="role-tabs">
        {["All Roles", "Open", "Paused", "Closed"].map((tab) => <button key={tab} className={filter === tab ? "active" : ""} onClick={() => setFilter(tab)}>{tab}</button>)}
      </div>

      <section className="jobs-grid">
        {filteredRoles.map((role, index) => (
          <article className={`panel role-card ${index === 0 ? "featured-role" : ""}`} key={role.title}>
            <div className="role-card-head">
              <div>
                <h2>{role.title}</h2>
                <p>{role.team} - {role.location}</p>
              </div>
              <span className={`status-pill status-${role.status.toLowerCase()}`}>{role.status}</span>
            </div>
            <div className="role-metrics">
              <span><strong>{role.applicants}</strong>Applicants</span>
              <span><strong>{role.top}%</strong>Top match</span>
              <span><strong>{role.shortlisted}</strong>Shortlisted</span>
            </div>
            <div className="screened-row">
              <div><strong>Screened</strong><small>{role.screened}/{role.total}</small></div>
              <div className="progress-track"><span style={{ width: `${Math.round((role.screened / role.total) * 100)}%` }} /></div>
            </div>
            <div className="role-footer">
              <div className="candidate-name">
                <span className="avatar">{role.lead.split(" ").map((word) => word[0]).join("").slice(0, 2)}</span>
                <span><strong>{role.lead}</strong><small>Posted {role.posted}</small></span>
              </div>
              <Button variant={index === 0 ? "primary" : "secondary"} icon={ArrowRight} onClick={() => onStartScreening(role)}>{index === 0 ? "Review" : "Open"}</Button>
            </div>
          </article>
        ))}
      </section>
    </div>
  );
}

function ApplicationsPage() {
  const applications = [
    { stage: "Saved", company: "Notion", role: "Frontend Engineer", location: "Remote - US", status: "Not matched", score: null, initials: "NO", age: "" },
    { stage: "Applied", company: "Klarna", role: "UI Engineer", location: "Stockholm, SE", status: "Applied", score: 74, initials: "KI", age: "3 days ago" },
    { stage: "Screening", company: "Northwind Labs", role: "Senior Frontend Engineer", location: "Remote - US / EU", status: "Screening", score: 68, initials: "NL", age: "2 days ago" },
    { stage: "Interview", company: "Mapbox", role: "Frontend Engineer", location: "Berlin, DE", status: "Interview", score: 82, initials: "MB", age: "1 week ago" },
    { stage: "Offer", company: "Pleo", role: "React Developer", location: "Remote - EU", status: "Offer", score: 90, initials: "PL", age: "2 weeks ago" },
    { stage: "Rejected", company: "Hootsuite", role: "UI Developer", location: "Vancouver, CA", status: "Rejected", score: 58, initials: "HS", age: "1 month ago" },
  ];
  const stages = ["Saved", "Applied", "Screening", "Interview", "Offer", "Rejected"];
  const inProgress = applications.filter((item) => ["Applied", "Screening", "Interview"].includes(item.stage)).length;
  const interviews = applications.filter((item) => item.stage === "Interview").length;
  const offers = applications.filter((item) => item.stage === "Offer").length;

  return (
    <div className="page-shell">
      <section className="page-heading"><div><span className="eyebrow">Stay on top of your search</span><h1>Applications</h1><p>Every role you are tracking, from saved to offer.</p></div><Button icon={BriefcaseBusiness}>Add application</Button></section>
      <section className="metric-grid">
        {[["Tracked", String(applications.length), BriefcaseBusiness], ["In progress", String(inProgress), BarChart3], ["Interviews", String(interviews), Users], ["Offers", String(offers), ShieldCheck]].map(([label, value, Icon]) => <article className="metric-card" key={label}><Icon size={20} /><span>{label}</span><strong>{value}</strong></article>)}
      </section>
      <section className="application-board">
        {stages.map((stage) => {
          const cards = applications.filter((item) => item.stage === stage);
          return (
            <div className="application-column" key={stage}>
              <div className="application-column-head"><span className={`source-dot app-dot-${stage.toLowerCase()}`} /><strong>{stage}</strong><small>{cards.length}</small></div>
              {cards.map((item) => (
                <article className="panel application-card" key={`${item.company}-${item.role}`}>
                  <div className="candidate-name">
                    <span className="avatar">{item.initials}</span>
                    <span><strong>{item.role}</strong><small>{item.company}</small></span>
                  </div>
                  <p>{item.location}</p>
                  <div className="application-card-footer">
                    {item.score ? <Score value={item.score} compact /> : <span className="status-tag">{item.status}</span>}
                    {item.age && <small>{item.age}</small>}
                  </div>
                </article>
              ))}
            </div>
          );
        })}
      </section>
    </div>
  );
}

function Profile({ user, setPage }) {
  const [bundle, setBundle] = useState({ profile: {}, experiences: [], skills: [] });
  const [profile, setProfile] = useState({});
  const [skillName, setSkillName] = useState("");
  const [experience, setExperience] = useState({ company: "", position: "", start_date: "", end_date: "", current_job: false, description: "" });
  const [showExperienceForm, setShowExperienceForm] = useState(false);
  const [busy, setBusy] = useState(true);
  const [message, setMessage] = useState("");

  const loadProfile = async () => {
    if (!user) return;
    setBusy(true);
    try {
      let data;
      try {
        data = await api.profile(user);
      } catch {
        await api.createProfile(user, user.split("@")[0]);
        data = await api.profile(user);
      }
      setBundle(data);
      setProfile(data.profile || {});
    } catch (error) {
      setMessage(error.message);
    } finally {
      setBusy(false);
    }
  };

  useEffect(() => { loadProfile(); }, [user]);

  const saveProfile = async () => {
    setBusy(true);
    try {
      const result = await api.updateProfile(user, profile);
      setProfile(result.profile);
      setMessage("Profile saved.");
    } catch (error) {
      setMessage(error.message);
    } finally {
      setBusy(false);
    }
  };

  const addSkill = async () => {
    if (!skillName.trim()) return;
    try {
      await api.addSkill(user, { skill_name: skillName.trim(), proficiency: "Intermediate" });
      setSkillName("");
      await loadProfile();
    } catch (error) { setMessage(error.message); }
  };

  const removeSkill = async (id) => {
    try { await api.deleteSkill(user, id); await loadProfile(); } catch (error) { setMessage(error.message); }
  };

  const addExperience = async () => {
    if (!experience.company.trim() || !experience.position.trim()) return;
    try {
      await api.addExperience(user, experience);
      setExperience({ company: "", position: "", start_date: "", end_date: "", current_job: false, description: "" });
      setShowExperienceForm(false);
      await loadProfile();
    } catch (error) { setMessage(error.message); }
  };

  const removeExperience = async (id) => {
    try { await api.deleteExperience(user, id); await loadProfile(); } catch (error) { setMessage(error.message); }
  };

  const completed = [profile.full_name, profile.professional_title, profile.professional_summary, bundle.skills.length, bundle.experiences.length].filter(Boolean).length;
  const strength = Math.round((completed / 5) * 100);
  const displayName = profile.full_name || user?.split("@")[0] || "Candidate";
  const initials = displayName.split(" ").map((part) => part[0]).join("").slice(0, 2).toUpperCase();
  return (
    <div className="page-shell">
      <section className="page-heading">
        <div><span className="eyebrow">Your career profile</span><h1>Profile</h1><p>Build it once. TrueFit reuses your profile to generate tailored CVs and match you to every new role.</p></div>
        <Button icon={FileText} onClick={() => setPage("optimizer")}>Generate CV</Button>
      </section>

      {message && <div className="success-message profile-message">{message}</div>}
      {busy && !profile.user_email ? <section className="panel empty-state compact-empty"><h2>Loading your profile...</h2></section> :

      <section className="profile-layout profile-full-layout">
        <aside className="profile-sidebar">
          <article className="panel profile-summary">
            <div className="large-avatar">{initials}</div>
            <h2>{displayName}</h2>
            <p>{profile.professional_title || "Add your professional title"}</p>
            <small>{profile.location || "Add your location"}</small>
          </article>
          <article className="panel profile-checklist">
            <div className="panel-head"><h2>Profile strength</h2><strong>{strength}%</strong></div>
            <div className="progress-track"><span style={{ width: `${strength}%` }} /></div>
            {["Basics", "Summary", "Skills", "Experience"].map((section, index) => <div className={index < completed ? "checklist-row" : "checklist-row muted-row"} key={section}><Check size={15} /> {section}</div>)}
          </article>
          <Button variant="secondary" icon={Target} onClick={() => setPage("optimizer")}>Match to a role</Button>
        </aside>

        <div className="profile-main">
          <article className="panel profile-form">
            <h2>Basics</h2>
            <div className="form-grid">
              <label>Full name<input value={profile.full_name || ""} onChange={(event) => setProfile({ ...profile, full_name: event.target.value })} /></label>
              <label>Professional title<input value={profile.professional_title || ""} onChange={(event) => setProfile({ ...profile, professional_title: event.target.value })} /></label>
              <label>Email<input value={profile.email || user || ""} onChange={(event) => setProfile({ ...profile, email: event.target.value })} /></label>
              <label>Phone<input value={profile.phone || ""} onChange={(event) => setProfile({ ...profile, phone: event.target.value })} /></label>
              <label>Location<input value={profile.location || ""} onChange={(event) => setProfile({ ...profile, location: event.target.value })} /></label>
              <label>Portfolio / GitHub<input value={profile.portfolio || ""} onChange={(event) => setProfile({ ...profile, portfolio: event.target.value })} /></label>
            </div>
            <div className="profile-form-actions"><Button icon={Check} onClick={saveProfile} disabled={busy}>{busy ? "Saving..." : "Save profile"}</Button></div>
          </article>

          <article className="panel profile-form">
            <h2>Professional summary</h2>
            <textarea value={profile.professional_summary || ""} onChange={(event) => setProfile({ ...profile, professional_summary: event.target.value })} />
            <p className="profile-tip">Tip: lead with years of experience and your strongest stack.</p>
            <div className="profile-form-actions"><Button icon={Check} onClick={saveProfile} disabled={busy}>Save summary</Button></div>
          </article>

          <article className="panel profile-form">
            <h2>Skills</h2>
            <div className="skills profile-skills">{bundle.skills.map((skill) => <button className="skill removable-skill" key={skill.id} onClick={() => removeSkill(skill.id)} title={`Remove ${skill.skill_name}`}>{skill.skill_name} <X size={12} /></button>)}</div>
            <div className="skill-add-row"><input value={skillName} onChange={(event) => setSkillName(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter") addSkill(); }} placeholder="Add a skill..." /><Button variant="secondary" icon={Check} onClick={addSkill}>Add</Button></div>
          </article>

          <article className="panel profile-form">
            <div className="panel-head"><h2>Experience</h2><button className="text-button" onClick={() => setShowExperienceForm((value) => !value)}>{showExperienceForm ? "Cancel" : "+ Add role"}</button></div>
            {showExperienceForm && <div className="experience-editor form-grid"><label>Position<input value={experience.position} onChange={(event) => setExperience({ ...experience, position: event.target.value })} /></label><label>Company<input value={experience.company} onChange={(event) => setExperience({ ...experience, company: event.target.value })} /></label><label>Start date<input type="date" value={experience.start_date} onChange={(event) => setExperience({ ...experience, start_date: event.target.value })} /></label><label>End date<input type="date" value={experience.end_date} disabled={experience.current_job} onChange={(event) => setExperience({ ...experience, end_date: event.target.value })} /></label><label className="check-row"><input type="checkbox" checked={experience.current_job} onChange={(event) => setExperience({ ...experience, current_job: event.target.checked, end_date: "" })} /> Current role</label><label className="full-field">Description<textarea value={experience.description} onChange={(event) => setExperience({ ...experience, description: event.target.value })} /></label><Button icon={Check} onClick={addExperience}>Save role</Button></div>}
            {bundle.experiences.map((item) => <ExperienceItem key={item.id} title={item.position} company={item.company} date={`${item.start_date || "Start"} - ${item.current_job ? "Present" : item.end_date || "End"}`} bullets={(item.description || "").split("\n").filter(Boolean)} onDelete={() => removeExperience(item.id)} />)}
            {!bundle.experiences.length && !showExperienceForm && <p className="profile-tip">Add your work history so TrueFit can tailor CVs and calculate stronger matches.</p>}
          </article>
        </div>
      </section>}
    </div>
  );
}

function ExperienceItem({ title, company, date, bullets, onDelete }) {
  return (
    <div className="experience-item">
      <div>
        <strong>{title}</strong>
        <small>{company}</small>
        <ul>{bullets.map((bullet) => <li key={bullet}>{bullet}</li>)}</ul>
      </div>
      <div className="experience-actions"><span className="status-tag">{date}</span>{onDelete && <button className="icon-button" onClick={onDelete} title="Delete experience"><X size={15} /></button>}</div>
    </div>
  );
}

export default function App() {
  const [page, setPage] = useState("landing");
  const [role, setRole] = useState("candidate");
  const [user, setUser] = useState("");
  const [apiOnline, setApiOnline] = useState(false);
  const [reportCandidate, setReportCandidate] = useState(null);
  const [reportContext, setReportContext] = useState({});
  const [jobDescription, setJobDescription] = useState(DEFAULT_SCREENING_JD);
  const [candidates, setCandidates] = useState([]);
  const [selectedCandidate, setSelectedCandidate] = useState(null);
  const [candidateMessages, setCandidateMessages] = useState({});
  const [reviewedMessages, setReviewedMessages] = useState({});
  const [sentMessages, setSentMessages] = useState({});
  const [hasReviewed, setHasReviewed] = useState(false);
  const [threshold, setThreshold] = useState(70);

  useEffect(() => {
    api.health().then(() => setApiOnline(true)).catch(() => setApiOnline(false));
  }, []);

  function authenticated(email) {
    setUser(email);
    if (role === "recruiter") {
      setReportCandidate(null);
      setReportContext({});
    }
    setPage(role === "recruiter" ? "recruiter" : "candidate");
  }

  function logout() {
    setUser("");
    setPage("landing");
  }

  function startScreening(roleToLoad = null) {
    setRole("recruiter");
    setReportCandidate(null);
    setReportContext({});
    setJobDescription(roleToLoad ? `${roleToLoad.title}\n\nTeam: ${roleToLoad.team}\nLocation: ${roleToLoad.location}\n\nPaste the full job description here before uploading resumes.` : "");
    setCandidates([]);
    setSelectedCandidate(null);
    setCandidateMessages({});
    setReviewedMessages({});
    setSentMessages({});
    setHasReviewed(false);
    setPage("recruiter");
  }

  function openMatchReport(candidate, context = {}) {
    setReportCandidate(candidate);
    setReportContext(context);
    setPage("report");
  }

  const screeningState = {
    jobDescription,
    setJobDescription,
    candidates,
    setCandidates,
    selectedCandidate,
    setSelectedCandidate,
    candidateMessages,
    setCandidateMessages,
    reviewedMessages,
    setReviewedMessages,
    sentMessages,
    setSentMessages,
    hasReviewed,
    setHasReviewed,
    threshold,
    setThreshold,
  };

  if (page === "landing") return <Landing setPage={setPage} setRole={setRole} onStartScreening={startScreening} />;
  if (page === "auth") return <Auth role={role} setRole={setRole} onAuthenticated={authenticated} />;

  return (
    <div className="app">
      <TopNav page={page} setPage={setPage} role={role} onLogout={logout} />
      {!apiOnline && <div className="offline-banner">FastAPI backend is offline. Start it on port 8000 to use live actions.</div>}
      {page === "candidate" && <CandidateDashboard setPage={setPage} user={user} />}
      {page === "optimizer" && <Optimizer />}
      {page === "profile" && <Profile user={user} setPage={setPage} />}
      {page === "applications" && <ApplicationsPage />}
      {page === "recruiter" && <RecruiterWorkspace onOpenReport={openMatchReport} screening={screeningState} />}
      {page === "feedback" && <CandidateFeedbackPage />}
      {page === "jobs" && <JobsPage setPage={setPage} onStartScreening={startScreening} />}
      {page === "candidates" && <CandidatesPage onOpenReport={openMatchReport} />}
      {page === "report" && <MatchReportPage candidate={reportCandidate} setPage={setPage} reportContext={reportContext} />}
      {page === "reports" && <ReportsPage />}
    </div>
  );
}
