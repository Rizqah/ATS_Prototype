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
    <button className="logo" onClick={onClick} aria-label="Fydara home">
      <span className="fydara-logo" aria-hidden="true" />
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
    ["recruiter-profile", "Profile", CircleUserRound],
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
        <button className="icon-button" onClick={() => setPage("security")} title="Security settings"><ShieldCheck size={18} /></button>
        <button className="icon-button" onClick={onLogout} title="Log out"><LogOut size={18} /></button>
      </div>
    </header>
  );
}

function RecruiterProfile({ user, profile, onChange, workspaceStatus }) {
  const [saved, setSaved] = useState("");
  const update = (field, value) => {
    onChange({ ...profile, [field]: value });
    setSaved("");
  };
  const confirmSave = (event) => {
    event.preventDefault();
    setSaved("Profile queued for secure workspace save.");
  };
  const initials = (profile.full_name || user || "Recruiter").split(/[\s@]+/).filter(Boolean).map((part) => part[0]).join("").slice(0, 2).toUpperCase();

  return (
    <div className="page-shell">
      <section className="page-heading"><div><span className="eyebrow">Recruiter account</span><h1>Your profile</h1><p>Keep your identity and company details current across hiring communications and workspaces.</p></div><span className="workspace-save-status">{workspaceStatus}</span></section>
      {saved && <div className="success-message profile-message">{saved}</div>}
      <section className="profile-layout recruiter-profile-layout">
        <aside className="panel profile-summary">
          <span className="large-avatar">{initials}</span>
          <div><h2>{profile.full_name || "Recruiter name"}</h2><p>{profile.job_title || "Recruiter"}</p></div>
          <span className="status-tag">{profile.company || "Company not added"}</span>
          <small>{user}</small>
        </aside>
        <form className="panel profile-form" onSubmit={confirmSave}>
          <div className="panel-head"><div><h2>Personal and company details</h2><p>These details are saved with your recruiter account.</p></div><CircleUserRound size={22} /></div>
          <div className="form-grid">
            <label>Full name<input value={profile.full_name || ""} onChange={(event) => update("full_name", event.target.value)} placeholder="Your full name" /></label>
            <label>Job title<input value={profile.job_title || ""} onChange={(event) => update("job_title", event.target.value)} placeholder="e.g. Talent Acquisition Lead" /></label>
            <label>Company<input value={profile.company || ""} onChange={(event) => update("company", event.target.value)} placeholder="Company name" /></label>
            <label>Company website<input type="url" value={profile.company_website || ""} onChange={(event) => update("company_website", event.target.value)} placeholder="https://company.com" /></label>
            <label>Location<input value={profile.location || ""} onChange={(event) => update("location", event.target.value)} placeholder="City or remote" /></label>
            <label>Hiring team size<input value={profile.team_size || ""} onChange={(event) => update("team_size", event.target.value)} placeholder="e.g. 5" /></label>
            <label className="full">About you<textarea value={profile.bio || ""} onChange={(event) => update("bio", event.target.value)} placeholder="Describe your role and the teams you hire for." /></label>
          </div>
          <div className="profile-form-actions"><Button type="submit" icon={Check}>Save profile</Button></div>
        </form>
      </section>
    </div>
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
          <p>Fydara ranks resumes against the real requirements of a role and turns every score into clear, useful next steps.</p>
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

function Auth({ role, setRole, onAuthenticated, setPage }) {
  const [mode, setMode] = useState("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [otpCode, setOtpCode] = useState("");
  const [otpRequired, setOtpRequired] = useState(false);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(event) {
    event.preventDefault();
    setError("");
    setBusy(true);
    try {
      const result = mode === "login" ? await api.login(email, password, otpRequired ? otpCode : null) : await api.signup(email, password);
      if (result.requires_2fa) { setOtpRequired(true); return; }
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
        <div><span className="eyebrow">{otpRequired ? "Two-factor authentication" : mode === "login" ? "Welcome back" : "Create account"}</span><h2>{otpRequired ? "Verify your sign-in" : mode === "login" ? "Sign in to Fydara" : "Start using Fydara"}</h2></div>
        <label>Email<input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" required /></label>
        {!otpRequired && <label>Password<input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="At least 8 characters" required /></label>}
        {otpRequired && <label>Authenticator or backup code<input value={otpCode} onChange={(event) => setOtpCode(event.target.value.replace(/\s/g, "").slice(0, 12))} autoComplete="one-time-code" required /></label>}
        {error && <div className="form-error">{error}</div>}
        <Button type="submit" disabled={busy}>{busy ? "Working..." : otpRequired ? "Verify code" : mode === "login" ? "Sign in" : "Create account"}</Button>
        {otpRequired && <button className="text-button" type="button" onClick={() => { setOtpRequired(false); setOtpCode(""); }}>Use another account</button>}
        {!otpRequired && <button className="text-button" type="button" onClick={() => setMode(mode === "login" ? "signup" : "login")}>
          {mode === "login" ? "Need an account? Sign up" : "Already have an account? Sign in"}
        </button>}
        {mode === "login" && !otpRequired && <button className="text-button" type="button" onClick={() => setPage("password-reset")}>Forgot password?</button>}
      </form>
    </main>
  );
}

function PasswordResetPage({ setPage }) {
  const [email, setEmail] = useState("");
  const [token, setToken] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [requested, setRequested] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const requestReset = async (event) => {
    event.preventDefault(); setBusy(true); setError("");
    try {
      const response = await api.requestPasswordReset(email);
      setRequested(true);
      setMessage(response.development_token ? `${response.message} Development code: ${response.development_token}` : response.message);
    } catch (requestError) { setError(requestError.message); }
    finally { setBusy(false); }
  };
  const confirmReset = async (event) => {
    event.preventDefault(); setError("");
    if (password !== confirmPassword) { setError("Passwords do not match"); return; }
    setBusy(true);
    try { const response = await api.confirmPasswordReset(email, token, password); setMessage(response.message); setTimeout(() => setPage("auth"), 1200); }
    catch (requestError) { setError(requestError.message); }
    finally { setBusy(false); }
  };
  return <main className="auth-page"><div className="auth-message"><Logo onClick={() => setPage("landing")} /><span className="eyebrow">Account recovery</span><h1>Reset your password securely.</h1><p>Reset codes expire after one hour and can only be used once.</p></div><form className="auth-form" onSubmit={requested ? confirmReset : requestReset}><div><span className="eyebrow">Password reset</span><h2>{requested ? "Enter your reset code" : "Request a reset code"}</h2></div><label>Email<input type="email" value={email} onChange={(event) => setEmail(event.target.value)} disabled={requested} required /></label>{requested && <><label>Six-digit code<input value={token} onChange={(event) => setToken(event.target.value.replace(/\D/g, "").slice(0, 6))} inputMode="numeric" required /></label><label>New password<input type="password" value={password} onChange={(event) => setPassword(event.target.value)} required /></label><label>Confirm password<input type="password" value={confirmPassword} onChange={(event) => setConfirmPassword(event.target.value)} required /></label></>}{message && <div className="success-message">{message}</div>}{error && <div className="form-error">{error}</div>}<Button type="submit" disabled={busy}>{busy ? "Working..." : requested ? "Reset password" : "Request code"}</Button>{requested && <button className="text-button" type="button" onClick={() => { setRequested(false); setMessage(""); }}>Request another code</button>}<button className="text-button" type="button" onClick={() => setPage("auth")}>Back to sign in</button></form></main>;
}

function SecurityPage({ user, setPage, onLogout }) {
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [twoFactorEnabled, setTwoFactorEnabled] = useState(false);
  const [setupData, setSetupData] = useState(null);
  const [twoFactorCode, setTwoFactorCode] = useState("");
  const [disablePassword, setDisablePassword] = useState("");
  const [backupCodes, setBackupCodes] = useState([]);
  const [deletePassword, setDeletePassword] = useState("");
  const [deleteConfirmation, setDeleteConfirmation] = useState("");
  useEffect(() => { api.twoFactorStatus(user).then((result) => setTwoFactorEnabled(result.enabled)).catch(() => {}); }, [user]);
  const submit = async (event) => {
    event.preventDefault(); setError(""); setMessage("");
    if (newPassword !== confirmPassword) { setError("Passwords do not match"); return; }
    setBusy(true);
    try { const response = await api.changePassword(user, currentPassword, newPassword); setMessage(response.message); setCurrentPassword(""); setNewPassword(""); setConfirmPassword(""); }
    catch (requestError) { setError(requestError.message); }
    finally { setBusy(false); }
  };
  const beginTwoFactor = async () => { setError(""); try { setSetupData(await api.setupTwoFactor(user)); } catch (requestError) { setError(requestError.message); } };
  const confirmTwoFactor = async () => { setError(""); try { const response = await api.confirmTwoFactor(user, twoFactorCode); setTwoFactorEnabled(true); setSetupData(null); setTwoFactorCode(""); setBackupCodes(response.backup_codes || []); setMessage(response.message); } catch (requestError) { setError(requestError.message); } };
  const turnOffTwoFactor = async () => { setError(""); try { const response = await api.disableTwoFactor(user, disablePassword, twoFactorCode); setTwoFactorEnabled(false); setDisablePassword(""); setTwoFactorCode(""); setBackupCodes([]); setMessage(response.message); } catch (requestError) { setError(requestError.message); } };
  const downloadMyData = async () => { setError(""); try { const response = await api.exportPersonalData(user); downloadFile(JSON.stringify(response, null, 2), `fydara-data-${new Date().toISOString().slice(0, 10)}.json`, "application/json"); setMessage("Your personal data export has downloaded."); } catch (requestError) { setError(requestError.message); } };
  const removeMyAccount = async () => { if (!window.confirm("This permanently deletes your TrueFit account and associated data. Continue?")) return; setError(""); try { await api.deleteAccount(user, deletePassword, deleteConfirmation); onLogout(); } catch (requestError) { setError(requestError.message); } };
  return <div className="page-shell"><section className="page-heading"><div><span className="eyebrow">Account protection</span><h1>Security settings</h1><p>Manage your password and protect access to your TrueFit account.</p></div><Button variant="secondary" icon={ChevronRight} onClick={() => setPage("candidate")}>Back to dashboard</Button></section>{message && <div className="success-message security-message">{message}</div>}{error && <div className="form-error security-message">{error}</div>}<section className="security-layout"><form className="panel profile-form" onSubmit={submit}><div className="panel-head"><div><h2>Change password</h2><p>Use at least eight characters with uppercase, lowercase and a number.</p></div><ShieldCheck size={22} /></div><label>Current password<input type="password" value={currentPassword} onChange={(event) => setCurrentPassword(event.target.value)} required /></label><label>New password<input type="password" value={newPassword} onChange={(event) => setNewPassword(event.target.value)} required /></label><label>Confirm new password<input type="password" value={confirmPassword} onChange={(event) => setConfirmPassword(event.target.value)} required /></label><Button type="submit" disabled={busy}>{busy ? "Updating..." : "Update password"}</Button></form><article className="panel profile-form"><div className="panel-head"><div><h2>Two-factor authentication</h2><p>{twoFactorEnabled ? "Your account requires an authenticator or backup code at sign-in." : "Add an authenticator app as a second sign-in step."}</p></div><span className={twoFactorEnabled ? "status-pill status-offer" : "status-pill"}>{twoFactorEnabled ? "Enabled" : "Off"}</span></div>{!twoFactorEnabled && !setupData && <Button icon={ShieldCheck} onClick={beginTwoFactor}>Set up authenticator</Button>}{setupData && <div className="two-factor-setup"><p>Add this secret to Google Authenticator, Microsoft Authenticator, Authy, or another TOTP app:</p><code>{setupData.secret}</code><small>{setupData.otpauth_uri}</small><label>Six-digit authenticator code<input value={twoFactorCode} onChange={(event) => setTwoFactorCode(event.target.value.replace(/\D/g, "").slice(0, 6))} inputMode="numeric" /></label><Button onClick={confirmTwoFactor} disabled={twoFactorCode.length !== 6}>Verify and enable</Button></div>}{twoFactorEnabled && <div className="two-factor-disable"><label>Password<input type="password" value={disablePassword} onChange={(event) => setDisablePassword(event.target.value)} /></label><label>Authenticator or backup code<input value={twoFactorCode} onChange={(event) => setTwoFactorCode(event.target.value.replace(/\s/g, "").slice(0, 12))} /></label><Button variant="secondary" onClick={turnOffTwoFactor} disabled={!disablePassword || twoFactorCode.length < 6}>Disable 2FA</Button></div>}{backupCodes.length > 0 && <div className="backup-codes"><strong>Save these one-time backup codes now</strong><code>{backupCodes.join("\n")}</code><small>Each code can be used once if you lose access to your authenticator.</small></div>}</article></section><section className="panel privacy-panel"><div className="panel-head"><div><h2>Privacy and personal data</h2><p>Download a portable copy of your account data or permanently delete your account.</p></div><Button variant="secondary" icon={Upload} onClick={downloadMyData}>Download my data</Button></div><div className="danger-zone"><div><strong>Delete account</strong><p>This removes your account, profile, skills, experience, achievements, generated CVs and usage records.</p></div><label>Password<input type="password" value={deletePassword} onChange={(event) => setDeletePassword(event.target.value)} /></label><label>Type your email to confirm<input value={deleteConfirmation} onChange={(event) => setDeleteConfirmation(event.target.value)} placeholder={user} /></label><Button variant="secondary" onClick={removeMyAccount} disabled={!deletePassword || deleteConfirmation !== user}>Delete permanently</Button></div></section></div>;
}

function CandidateDashboard({ setPage, user }) {
  const [dashboard, setDashboard] = useState({ profile: {}, experiences: [], skills: [], cvs: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  useEffect(() => {
    if (!user) return;
    setLoading(true);
    api.profile(user)
      .catch(async () => { await api.createProfile(user, user.split("@")[0]); return api.profile(user); })
      .then((data) => { setDashboard(data); setError(""); })
      .catch((requestError) => setError(requestError.message))
      .finally(() => setLoading(false));
  }, [user]);
  const profile = dashboard.profile || {};
  const displayName = profile.full_name || (user ? user.split("@")[0] : "Candidate");
  const cvs = dashboard.cvs || [];
  const activeApplications = cvs.filter((cv) => !["Draft", "Rejected"].includes(cv.application_status)).length;
  const offers = cvs.filter((cv) => cv.application_status === "Offer").length;
  const recentApplications = cvs.slice(0, 4).map((cv) => {
    const score = Number(cv.match_score || 0);
    const normalizedScore = Math.round(score <= 1 ? score * 100 : score);
    const created = cv.created_at ? new Date(cv.created_at) : null;
    return { id: cv.id, company: "Tailored CV", role: cv.job_title || "Untitled role", status: cv.application_status || "Draft", score: normalizedScore, initials: (cv.job_title || "CV").split(" ").map((part) => part[0]).join("").slice(0, 2).toUpperCase(), age: created && !Number.isNaN(created.valueOf()) ? created.toLocaleDateString("en-GB", { day: "numeric", month: "short" }) : "" };
  });
  const profileChecks = [profile.full_name, profile.professional_summary, profile.location, dashboard.skills?.length, dashboard.experiences?.length];
  const profileStrength = Math.round((profileChecks.filter(Boolean).length / profileChecks.length) * 100);
  const strongestCv = [...cvs].sort((a, b) => Number(b.match_score || 0) - Number(a.match_score || 0))[0];
  const strongestScoreValue = Number(strongestCv?.match_score || 0);
  const strongestScore = Math.round(strongestScoreValue <= 1 ? strongestScoreValue * 100 : strongestScoreValue);
  const actions = [
    [Target, "Optimise for a role", "Paste a JD, see your match, and tailor your CV.", "optimizer"],
    [CircleUserRound, "Build your profile", "Keep your career profile sharp for instant CVs.", "profile"],
    [BriefcaseBusiness, "Track applications", "Follow every role from saved to offer.", "applications"],
  ];

  return (
    <div className="page-shell">
      <section className="page-heading">
        <div><span className="eyebrow">Your job search</span><h1>Welcome back, {displayName}</h1><p>{loading ? "Loading your latest activity..." : `${cvs.length} tailored CV${cvs.length === 1 ? "" : "s"} - ${activeApplications} active application${activeApplications === 1 ? "" : "s"}${offers ? ` - ${offers} offer${offers === 1 ? "" : "s"}` : ""}.`}</p></div>
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
          <div className="panel-head"><div><h2>Recent tailored CVs</h2></div><button className="text-button" onClick={() => setPage("applications")}>View all <ArrowRight size={15} /></button></div>
          <div className="application-list candidate-application-list">
            {recentApplications.map((item) => <button className="application-row candidate-app-row" key={item.id} onClick={() => setPage("applications")}><div className="company-mark">{item.initials}</div><div className="grow"><strong>{item.role}</strong><span>{item.company} - {item.age}</span></div><span className={`status-pill status-${item.status.toLowerCase()}`}>{item.status}</span><Score value={item.score} compact /></button>)}
            {!loading && !recentApplications.length && <div className="empty-state compact-empty"><FileText size={24} /><h2>No tailored CVs yet</h2><p>Match your first role to start building your application history.</p><Button icon={Target} onClick={() => setPage("optimizer")}>Match a role</Button></div>}
            {error && <div className="error-message">{error}</div>}
          </div>
        </article>

        <div className="candidate-side-stack">
          <article className="panel profile-strength-card">
            <Score value={profileStrength} />
            <div><h2>Profile strength</h2><p>{profileStrength === 100 ? "Your profile has the core information needed for tailored CVs." : "Add your summary, skills and experience to improve your matches."}</p><Button variant="secondary" icon={CircleUserRound} onClick={() => setPage("profile")}>{profileStrength === 100 ? "Review profile" : "Complete profile"}</Button></div>
          </article>
          <article className="panel next-move-card">
            <Sparkles size={19} />
            <div><h2>Next best move</h2><p>{strongestCv ? <>Your <strong>{strongestCv.job_title}</strong> CV scored {strongestScore}%. Tailor it against the latest job description to strengthen the match.</> : <>Create your first tailored CV and get an evidence-based match score.</>}</p><Button icon={Target} onClick={() => setPage("optimizer")}>{strongestCv ? "Optimise it now" : "Start matching"}</Button></div>
          </article>
        </div>
      </section>
    </div>
  );
}

function Optimizer({ user, setPage }) {
  const [jd, setJd] = useState("Senior Frontend Engineer - Northwind Labs\n\nWe're building the data-visualization layer for a real-time analytics platform. You'll own complex, accessible UI and partner closely with design and backend.\n\nRequirements:\n- Expert-level React and modern JavaScript\n- Strong TypeScript across a large typed codebase\n- Deep CSS architecture skills and design-token systems\n- Accessibility - you build to WCAG AA standards by default\n- Solid testing discipline with Jest and React Testing Library\n- Comfortable consuming REST and GraphQL APIs");
  const [jobTitle, setJobTitle] = useState("Senior Frontend Engineer");
  const [result, setResult] = useState(null);
  const [profileBundle, setProfileBundle] = useState({ profile: {}, experiences: [], achievements_by_experience: {}, skills: [] });
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [analysis, setAnalysis] = useState({ requirements: [], matched_requirements: [], missing_requirements: [], suggestions: [], evidence_score: 0 });
  const jdFileRef = useRef(null);
  useEffect(() => {
    if (!user) return;
    api.profile(user).then(setProfileBundle).catch((error) => setMessage(error.message));
  }, [user]);
  useEffect(() => {
    if (!jd.trim()) { setAnalysis({ requirements: [], matched_requirements: [], missing_requirements: [], suggestions: [], evidence_score: 0 }); return undefined; }
    const candidateText = JSON.stringify(profileBundle);
    const timeout = setTimeout(() => {
      api.analyseMatch({ job_description: jd, candidate_resume: candidateText })
        .then(setAnalysis)
        .catch((error) => setMessage(error.message));
    }, 350);
    return () => clearTimeout(timeout);
  }, [jd, profileBundle]);
  const matched = analysis.matched_requirements || [];
  const missing = analysis.missing_requirements || [];
  const matchScore = analysis.evidence_score || 0;

  async function renderPreview() {
    setBusy(true);
    setMessage("");
    try {
      const response = await api.renderCv({ profile: profileBundle.profile || {}, work_experiences: profileBundle.experiences || [], achievements_by_experience: profileBundle.achievements_by_experience || {}, skills: profileBundle.skills || [], job_description: jd });
      setResult(response.text);
      setMessage("Tailored CV generated. Download it or save it to Applications.");
    } catch (error) {
      setMessage(error.message);
    } finally {
      setBusy(false);
    }
  }

  const cvPayload = { profile: profileBundle.profile || {}, work_experiences: profileBundle.experiences || [], achievements_by_experience: profileBundle.achievements_by_experience || {}, skills: profileBundle.skills || [], job_description: jd };
  const safeFilename = `${(profileBundle.profile?.full_name || "Fydara_CV").replace(/[^a-z0-9]+/gi, "_")}_${(jobTitle || "Role").replace(/[^a-z0-9]+/gi, "_")}`;
  const downloadGeneratedCv = async (format) => {
    setBusy(true);
    try {
      const response = format === "pdf" ? await api.downloadCvPdf(cvPayload) : await api.downloadCvDocx(cvPayload);
      downloadFile(response.blob, `${safeFilename}.${format}`, format === "pdf" ? "application/pdf" : "application/vnd.openxmlformats-officedocument.wordprocessingml.document");
      setMessage(`${format.toUpperCase()} downloaded successfully.`);
    } catch (error) { setMessage(error.message); }
    finally { setBusy(false); }
  };
  const saveGeneratedCv = async () => {
    if (!result) return;
    setBusy(true);
    try {
      await api.saveCv(user, { job_title: jobTitle.trim(), match_score: matchScore / 100, cv_content: result, job_description: jd });
      setMessage("CV saved to Applications.");
    } catch (error) { setMessage(error.message); }
    finally { setBusy(false); }
  };
  const uploadJobDescription = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    setBusy(true);
    try { const response = await api.extractResume(file); setJd(response.text || ""); setMessage("Job description uploaded."); }
    catch (error) { setMessage(error.message); }
    finally { setBusy(false); event.target.value = ""; }
  };

  return (
    <div className="page-shell">
      <section className="page-heading"><div><span className="eyebrow">Per-role tailoring</span><h1>CV Optimizer</h1><p>Paste any job description. Fydara matches it against your profile, scores the fit, and generates an application-ready CV.</p></div><Button variant="secondary" icon={CircleUserRound} onClick={() => setPage("profile")}>Edit profile</Button></section>
      {message && <div className={message.toLowerCase().includes("failed") || message.toLowerCase().includes("error") ? "error-message optimizer-message" : "success-message optimizer-message"}>{message}</div>}
      <section className="optimizer-grid">
        <article className="panel optimizer-input-panel">
          <label>Job title<input value={jobTitle} onChange={(event) => setJobTitle(event.target.value)} placeholder="e.g. HR Advisor" /></label>
          <div className="panel-head optimizer-jd-head"><div><h2><FileText size={17} /> Job description</h2></div><div className="heading-actions"><input ref={jdFileRef} className="hidden-input" type="file" accept="application/pdf" onChange={uploadJobDescription} /><Button variant="ghost" icon={Upload} onClick={() => jdFileRef.current?.click()}>Upload PDF</Button><button className="icon-button" onClick={() => setJd("")} title="Clear"><X size={17} /></button></div></div>
          <textarea value={jd} onChange={(e) => setJd(e.target.value)} />
          <div className="optimizer-input-footer"><Button icon={Target} onClick={renderPreview} disabled={busy || !jd.trim() || !jobTitle.trim()}>{busy ? "Generating..." : "Generate tailored CV"}</Button><span>{matched.length + missing.length} relevant requirements detected</span></div>
          <div className="parsed-requirements"><strong>Parsed requirements</strong><div className="skills">{[...matched, ...missing].map((skill) => <span className="skill" key={skill}>{skill}</span>)}</div></div>
        </article>

        <div className="optimizer-results">
          <article className="panel optimizer-score-card">
            <Score value={matchScore} />
            <div><h2>Your match</h2><p>You match <strong>{matched.length}/{matched.length + missing.length || 0}</strong> detected requirements. Review the gaps before generating your tailored CV.</p><Button icon={Sparkles} onClick={renderPreview} disabled={busy || !jd.trim() || !jobTitle.trim()}>{busy ? "Applying..." : "Apply profile to role"}</Button></div>
          </article>

          <article className="panel">
            <SkillSection title="You match" items={matched} tone="match" />
            <SkillSection title="Missing" items={missing} tone="missing" />
          </article>

          <article className="panel optimisation-panel">
            <div className="panel-head"><div><h2>Optimisation suggestions</h2><p>Add each to your CV to raise your match score.</p></div></div>
            <div className="suggestion-list">{(analysis.suggestions || []).map(({ requirement, advice }) => <div className="suggestion-row" key={requirement}><Sparkles size={16} /><div><strong>{requirement}</strong><p>{advice}</p></div></div>)}</div>
          </article>
        </div>
      </section>
      {result && <section className="panel result-panel cv-preview-panel"><div className="panel-head"><div><h2>Tailored CV preview</h2><p>Generated from your persisted Fydara profile.</p></div><Score value={matchScore} /></div><pre>{result}</pre><div className="cv-download-actions"><Button icon={FileText} onClick={() => downloadGeneratedCv("pdf")} disabled={busy}>Download PDF</Button><Button variant="secondary" icon={FileText} onClick={() => downloadGeneratedCv("docx")} disabled={busy}>Download DOCX</Button><Button variant="secondary" icon={BriefcaseBusiness} onClick={saveGeneratedCv} disabled={busy || !jobTitle.trim()}>Save to Applications</Button></div></section>}
    </div>
  );
}

function RecruiterWorkspace({ onOpenReport, screening, recruiterEmail }) {
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
    workspaceStatus,
    communicationHistory,
    setCommunicationHistory,
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
    setCommunicationHistory([]);
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
          email: inferCandidateEmail(result.text),
        });
      }

      const nextCandidates = extracted.map((candidate) => ({
        name: candidate.name,
        role: "Uploaded resume",
        score: null,
        status: "Pending Review",
        skills: inferSkills(candidate.resume),
        resume: candidate.resume,
        email: candidate.email,
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
        skills: candidate.matched_requirements || [],
        matched_requirements: candidate.matched_requirements || [],
        missing_requirements: candidate.missing_requirements || [],
        bonus_skills: candidate.bonus_skills || [],
        suggestions: candidate.suggestions || [],
        resume: candidate.resume || candidates[index]?.resume,
        email: candidates[index]?.email || inferCandidateEmail(candidate.resume || candidates[index]?.resume),
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

  async function markFeedbackSent() {
    if (!selectedCandidate) return;
    if (!selectedReviewed) {
      setError("A human compliance check is required before this message can be sent.");
      return;
    }
    if (!selectedCandidate.email) { setError("Add the candidate's email address before sending."); return; }
    setBusy(true);
    try {
      const subject = selectedMessage?.subject || `Update on your application for ${selectedCandidate.role || jobTitle}`;
      const delivery = await api.sendEmail({ recruiter_email: recruiterEmail, to_email: selectedCandidate.email, subject, body: selectedMessage?.body || "" });
      setSentMessages((current) => ({ ...current, [selectedCandidate.name]: true }));
      setCommunicationHistory((current) => [...current, { candidate_name: selectedCandidate.name, to_email: selectedCandidate.email, subject, type: selectedMessage?.type || "feedback", sent_at: new Date().toISOString(), provider_status: delivery.provider_status, message_id: delivery.message_id || "" }]);
      setError("");
      setStatus(`${selectedMessage?.type === "invite" ? "Interview invite" : "Feedback"} sent to ${selectedCandidate.email}.`);
    } catch (sendError) { setError(sendError.message); }
    finally { setBusy(false); }
  }

  function setSelectedReviewed(checked) {
    if (!selectedCandidate) return;
    setReviewedMessages((current) => ({ ...current, [selectedCandidate.name]: checked }));
  }

  function inferSkills(resumeText = "") {
    const text = resumeText.toLowerCase();
    return ["React", "TypeScript", "Accessibility", "Testing", "GraphQL", "Python", "SQL", "CSS"].filter((skill) => text.includes(skill.toLowerCase())).slice(0, 5);
  }
  function inferCandidateEmail(resumeText = "") { return resumeText.match(/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/i)?.[0] || ""; }
  function updateCandidateEmail(email) { if (!selectedCandidate) return; setCandidates((current) => current.map((candidate) => candidate.name === selectedCandidate.name ? { ...candidate, email } : candidate)); setSelectedCandidate((current) => current ? { ...current, email } : current); }

  return (
    <div className="page-shell">
      <section className="page-heading"><div><span className="eyebrow">Recruiter workspace</span><h1>{jobTitle}</h1><p>Start with a job description, upload resumes, then review CVs when you are ready to rank them.</p>{workspaceStatus && <small className="workspace-save-status">{workspaceStatus}</small>}</div><div className="heading-actions"><input ref={fileInputRef} className="hidden-input" type="file" accept="application/pdf" multiple onChange={processUploadedFiles} /><Button variant="secondary" icon={Sparkles} onClick={startNewScreening} disabled={busy}>Start screening</Button><Button variant="secondary" icon={Upload} onClick={() => fileInputRef.current?.click()} disabled={busy || !jobDescription.trim()}>Upload resumes</Button><Button icon={Sparkles} onClick={reviewCVs} disabled={busy || !candidates.length || !jobDescription.trim()}>Review CVs</Button></div></section>
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
            <p>{candidates.length ? "Fydara has not ranked these CVs yet. Confirm the job description, then click Review CVs." : "Paste or confirm a job description, upload resumes, then click Review CVs to rank candidates."}</p>
            <div className="staged-resumes">
              {candidates.map((candidate) => <span className="skill" key={candidate.name}>{candidate.name}</span>)}
            </div>
          </div>
        </section>
      )}
      {selectedMessage && <section className="panel feedback-panel"><div className="panel-head"><div><h2>{selectedMessage.title}</h2><p>{selectedCandidate?.name}{selectedMessage.subject ? ` - ${selectedMessage.subject}` : ""}</p></div><Button variant="secondary" icon={Mail} onClick={() => navigator.clipboard?.writeText(selectedMessage.body)}>Copy</Button></div><label>Candidate email<input type="email" value={selectedCandidate?.email || ""} onChange={(event) => updateCandidateEmail(event.target.value)} placeholder="candidate@example.com" /></label><pre>{selectedMessage.body}</pre><div className="feedback-review"><label className="check-row"><input type="checkbox" checked={selectedReviewed} onChange={(event) => setSelectedReviewed(event.target.checked)} /> Human compliance check completed</label><Button icon={Mail} onClick={markFeedbackSent} disabled={!selectedReviewed || selectedSent || busy}>{busy ? "Sending..." : selectedSent ? "Sent" : selectedMessage.type === "invite" ? "Send invite" : "Send feedback"}</Button></div>{selectedSent && <div className="success-message">Accepted by the configured email provider and recorded in communication history.</div>}</section>}
      {communicationHistory.length > 0 && <section className="panel communication-history"><div className="panel-head"><div><h2>Communication history</h2><p>Provider-confirmed sends for this workspace.</p></div><span className="status-tag">{communicationHistory.length} sent</span></div>{communicationHistory.slice().reverse().map((item) => <div className="communication-history-row" key={`${item.sent_at}-${item.to_email}`}><div><strong>{item.candidate_name}</strong><small>{item.to_email} - {item.subject}</small></div><span>{new Date(item.sent_at).toLocaleString("en-GB")}</span></div>)}</section>}
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

export function CandidatesPage({ onOpenReport, workspace }) {
  const [query, setQuery] = useState("");
  const [roleFilter, setRoleFilter] = useState("All roles");
  const [statusFilter, setStatusFilter] = useState("All statuses");
  const sampleCandidatesPool = [
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
  const candidates = (workspace?.candidates || []).map((candidate) => ({ ...candidate, title: candidate.title || "Uploaded candidate", company: candidate.company || "Not provided", role: candidate.role || workspace?.job_title || "Current role", exp: candidate.exp || "-", source: candidate.source || "Uploaded CV" }));
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
    "fydara-talent-pool.csv",
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
  const matched = activeCandidate.matched_requirements || activeCandidate.skills || [];
  const missing = activeCandidate.missing_requirements || [];
  const bonus = activeCandidate.bonus_skills || [];
  const feedbackType = generatedMessage?.title || (generatedMessage?.type === "invite" ? "Interview invite" : generatedMessage?.type === "feedback" ? "Rejection feedback" : score >= 70 ? "Interview invite" : "Rejection feedback");
  const fallbackFeedbackBody = score >= 70
    ? `Hi ${activeCandidate.name.split(" ")[0]},\n\nThank you for applying for the ${activeCandidate.role} role at Northwind Labs. Your CV shows strong alignment with the role, especially around ${matched.slice(0, 2).join(" and ")}.\n\nWe would like to invite you to the next interview stage so we can learn more about your recent work and the impact you have had on product teams.`
    : `Hi ${activeCandidate.name.split(" ")[0]},\n\nThank you for taking the time to apply for the ${activeCandidate.role} role at Northwind Labs. After careful review, we will not be moving forward on this occasion.\n\nYour CV showed relevant strengths in ${matched.slice(0, 2).join(" and ")}, but the main gaps for this role were ${missing.slice(0, 2).join(" and ")}. For future applications, add concrete examples, project scope, and outcomes in these areas.`;
  const feedbackBody = generatedMessage?.body || generatedMessage?.invite || generatedMessage?.feedback || fallbackFeedbackBody;
  const feedbackSubject = generatedMessage?.subject || `An update on your application for ${activeCandidate.role}`;

  function moveForward() {
    setStatus(score >= 70 ? "Interview" : "Reviewing");
  }
  const exportCandidateReport = () => downloadTextPdf(["TRUEFIT CANDIDATE MATCH REPORT", `Generated: ${new Date().toLocaleDateString("en-GB")}`, "", `Candidate: ${activeCandidate.name}`, `Email: ${activeCandidate.email || "Not provided"}`, `Role: ${activeCandidate.role}`, `Match score: ${score}%`, `Status: ${status}`, "", `Matched requirements: ${matched.join(", ") || "None detected"}`, `Missing requirements: ${missing.join(", ") || "None detected"}`, `Bonus skills: ${bonus.join(", ") || "None detected"}`, "", "CANDIDATE FEEDBACK", `Subject: ${feedbackSubject}`, "", ...feedbackBody.split("\n"), "", "RESUME EVIDENCE", ...(activeCandidate.resume || "No resume text available").split("\n")], `truefit-${activeCandidate.name.replace(/[^a-z0-9]+/gi, "-").toLowerCase()}-report.pdf`);

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
          <Button variant="secondary" icon={Upload} onClick={exportCandidateReport}>Export report</Button>
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

export function ReportsPage({ workspace }) {
  const candidates = workspace?.candidates || [];
  const screened = candidates.filter((candidate) => typeof candidate.score === "number");
  const shortlistedCandidates = candidates.filter((candidate) => ["Shortlist", "Interview", "Offer"].includes(candidate.status));
  const averageMatch = screened.length ? Math.round(screened.reduce((total, candidate) => total + Number(candidate.score || 0), 0) / screened.length) : 0;
  const shortlistRate = screened.length ? Math.round((shortlistedCandidates.length / screened.length) * 100) : 0;
  const currentMetrics = [
    ["Candidates screened", String(screened.length), `of ${candidates.length} uploaded`, Users],
    ["Average match", `${averageMatch}%`, "current workspace", Target],
    ["Shortlist rate", `${shortlistRate}%`, `${shortlistedCandidates.length} shortlisted`, ShieldCheck],
    ["Avg time-to-screen", "Not tracked", "Add screening timestamps to calculate", BarChart3],
  ];
  const recruitmentMetrics = [
    { id: "time-fill", label: "Time to fill", value: "Not tracked", detail: "Job published to candidate hired" },
    { id: "time-hire", label: "Time to hire", value: "Not tracked", detail: "Candidate approached to offer accepted" },
    { id: "cost-hire", label: "Cost per hire", value: "Not tracked", detail: "Internal + external hiring cost per hire" },
    { id: "quality-hire", label: "Quality of hire", value: "Not tracked", detail: "Hires meeting first-year performance expectations" },
    { id: "source-hire", label: "Source of hire", value: "Not tracked", detail: "Top sourcing channel for successful hires" },
    { id: "first-year-resignation", label: "First-year resignation rate", value: "Not tracked", detail: "First-year resignations / headcount" },
    { id: "first-year-turnover", label: "First-year turnover rate", value: "Not tracked", detail: "First-year leavers / recruits" },
    { id: "first-month-turnover", label: "First-month turnover rate", value: "Not tracked", detail: "First-month leavers / recruits" },
    { id: "manager-satisfaction", label: "Hiring manager satisfaction", value: "Not tracked", detail: "Hires performing well / total hires" },
    { id: "candidate-satisfaction", label: "Candidate job satisfaction", value: "Not tracked", detail: "Satisfied new hires / total hires" },
    { id: "applicants-opening", label: "Applicants per opening", value: String(candidates.length), detail: "Applicants / job openings" },
    { id: "selection-ratio", label: "Selection ratio", value: `${shortlistRate}%`, detail: "Selected candidates / total candidates" },
    { id: "offer-acceptance", label: "Offer acceptance rate", value: "Not tracked", detail: "Accepted offers / offers made" },
    { id: "vacancy-rate", label: "Vacancy rate", value: "Not tracked", detail: "Open positions / total positions" },
    { id: "completion-rate", label: "Application completion rate", value: "Not tracked", detail: "Completed / started applications" },
    { id: "yield-ratio", label: "Yield ratio", value: `${shortlistRate}%`, detail: "Candidates completing the current stage" },
    { id: "source-effectiveness", label: "Sourcing channel effectiveness", value: "Not tracked", detail: "Channel impressions per application" },
    { id: "source-cost", label: "Sourcing channel cost", value: "Not tracked", detail: "Channel spend per successful applicant" },
    { id: "opl-cost", label: "Cost to optimum productivity", value: "Not tracked", detail: "Onboarding and ramp-up cost to full productivity" },
  ];
  const [selectedMetricIds, setSelectedMetricIds] = useState(["time-fill", "time-hire", "cost-hire", "quality-hire"]);
  const selectedRecruitmentMetrics = recruitmentMetrics.filter((metric) => selectedMetricIds.includes(metric.id));
  const toggleMetric = (id) => setSelectedMetricIds((selected) => selected.includes(id) ? selected.filter((item) => item !== id) : [...selected, id]);
  const funnel = [
    ["Uploaded", candidates.length, 100],
    ["Screened", screened.length, candidates.length ? Math.round((screened.length / candidates.length) * 100) : 0],
    ["Shortlisted", shortlistedCandidates.length, screened.length ? shortlistRate : 0],
    ["Interview", candidates.filter((candidate) => candidate.status === "Interview").length, candidates.length ? Math.round((candidates.filter((candidate) => candidate.status === "Interview").length / candidates.length) * 100) : 0],
    ["Offer", candidates.filter((candidate) => candidate.status === "Offer").length, candidates.length ? Math.round((candidates.filter((candidate) => candidate.status === "Offer").length / candidates.length) * 100) : 0],
  ];
  const sources = [
    ["Uploaded CV", candidates.length ? 100 : 0],
  ];
  const roles = workspace?.job_description ? [[workspace.job_title || getJobTitle(workspace.job_description), "Current workspace", candidates.length, averageMatch, screened.length ? Math.max(...screened.map((candidate) => Number(candidate.score || 0))) : 0]] : [];
  const distribution = [["Excellent", "80-100", screened.filter((candidate) => candidate.score >= 80).length], ["Good", "65-79", screened.filter((candidate) => candidate.score >= 65 && candidate.score < 80).length], ["Fair", "50-64", screened.filter((candidate) => candidate.score >= 50 && candidate.score < 65).length], ["Limited", "0-49", screened.filter((candidate) => candidate.score < 50).length]];
  const distributionMax = Math.max(1, ...distribution.map((item) => item[2]));
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
  ], "fydara-hiring-report.pdf");

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
        <article className="panel"><div className="panel-head"><div><h2>Match score distribution</h2><p>How the screened pool spreads across quality tiers.</p></div></div><div className="distribution">{distribution.map(([label, range, count]) => <span key={label} style={{ height: `${Math.max(12, Math.round((count / distributionMax) * 80))}%` }}>{count}<small>{label}<br />{range}</small></span>)}</div></article>
        <article className="panel"><div className="panel-head"><div><h2>Hiring funnel</h2><p>Conversion from applicant to offer.</p></div></div>{funnel.map(([label, count, width]) => <div className="funnel-row" key={label}><span>{label}</span><div><i style={{ width: `${width}%` }} /></div><strong>{count}</strong></div>)}</article>
      </section>
      <section className="report-grid lower-report-grid">
        <article className="panel"><div className="panel-head"><div><h2>Candidate sources</h2><p>Where your pool comes from.</p></div></div><div className="source-list">{sources.map(([label, value]) => <div className="source-row" key={label}><div><span className="source-dot" /><strong>{label}</strong><small>{value}%</small></div><div className="progress-track"><span style={{ width: `${value}%` }} /></div></div>)}</div></article>
        <article className="panel role-performance-panel"><div className="panel-head"><div><h2>Role performance</h2><p>Pipeline quality by active role.</p></div></div><div className="role-performance-table"><div className="role-performance-row role-performance-head"><span>Role</span><span>Pool</span><span>Avg match</span><span>Top</span></div>{roles.map(([role, team, pool, avg, top]) => <div className="role-performance-row" key={role}><div><strong>{role}</strong><small>{team}</small></div><span>{pool}</span><div className="match-cell"><div className="mini-score-track"><span style={{ width: `${avg}%` }} /></div><b>{avg}%</b></div><Score value={top} compact /></div>)}</div></article>
      </section>
    </div>
  );
}

function JobsPage({ setPage, onStartScreening, workspace }) {
  const [filter, setFilter] = useState("All Roles");
  const sampleRoles = [
    { title: "Senior Frontend Engineer", team: "Engineering", location: "Remote - US / EU", status: "Open", applicants: 10, top: 92, shortlisted: 4, screened: 10, total: 10, lead: "Jordan Reyes", posted: "Apr 28" },
    { title: "Product Designer", team: "Design", location: "Berlin, DE", status: "Open", applicants: 18, top: 89, shortlisted: 5, screened: 14, total: 18, lead: "Mia Chen", posted: "May 04" },
    { title: "Backend Engineer (Go)", team: "Engineering", location: "Remote - Global", status: "Open", applicants: 23, top: 86, shortlisted: 2, screened: 9, total: 23, lead: "Jordan Reyes", posted: "May 09" },
    { title: "Data Analyst", team: "Data", location: "London, UK", status: "Paused", applicants: 12, top: 81, shortlisted: 3, screened: 12, total: 12, lead: "Sam Patel", posted: "Apr 15" },
    { title: "Engineering Manager", team: "Engineering", location: "Remote - US", status: "Open", applicants: 7, top: 90, shortlisted: 1, screened: 4, total: 7, lead: "Mia Chen", posted: "May 12" },
    { title: "DevOps Engineer", team: "Platform", location: "Austin, US", status: "Closed", applicants: 15, top: 77, shortlisted: 0, screened: 15, total: 15, lead: "Sam Patel", posted: "Mar 30" },
  ];
  const liveCandidates = workspace?.candidates || [];
  const roles = workspace?.job_description ? [{ title: workspace.job_title || getJobTitle(workspace.job_description), team: "Current workspace", location: "Not specified", status: "Open", applicants: liveCandidates.length, top: liveCandidates.length ? Math.max(...liveCandidates.map((candidate) => Number(candidate.score || 0))) : 0, shortlisted: liveCandidates.filter((candidate) => ["Shortlist", "Interview", "Offer"].includes(candidate.status)).length, screened: liveCandidates.filter((candidate) => typeof candidate.score === "number").length, total: liveCandidates.length, lead: workspace.recruiter_email || "Recruiter", posted: workspace.updated_at ? new Date(workspace.updated_at).toLocaleDateString("en-GB", { day: "numeric", month: "short" }) : "Recently" }] : [];
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
        {[["Active roles", String(activeRoles), BriefcaseBusiness], ["In pipeline", String(pipeline), Users], ["Shortlisted", String(shortlisted), ShieldCheck], ["Avg time-to-screen", "Not tracked", BarChart3]].map(([label, value, Icon]) => <article className="metric-card" key={label}><Icon size={20} /><span>{label}</span><strong>{value}</strong></article>)}
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
              <Button variant="primary" icon={ArrowRight} onClick={() => setPage("recruiter")}>Review workspace</Button>
            </div>
          </article>
        ))}
      </section>
      {!roles.length && <section className="panel empty-state"><BriefcaseBusiness size={28} /><h2>No persisted role yet</h2><p>Start a screening workspace to create your first live role.</p><Button icon={BriefcaseBusiness} onClick={() => onStartScreening()}>Start screening</Button></section>}
    </div>
  );
}

function ApplicationsPage({ user, setPage }) {
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const stages = ["Saved", "Applied", "Screening", "Interview", "Offer", "Rejected"];
  const loadApplications = async () => {
    if (!user) return;
    setLoading(true);
    try {
      const result = await api.cvHistory(user);
      setApplications((result.cvs || []).map((cv) => {
        const rawScore = Number(cv.match_score || 0);
        const created = cv.created_at ? new Date(cv.created_at) : null;
        return { ...cv, stage: cv.application_status === "Draft" ? "Saved" : cv.application_status || "Saved", score: Math.round(rawScore <= 1 ? rawScore * 100 : rawScore), initials: (cv.job_title || "CV").split(" ").map((part) => part[0]).join("").slice(0, 2).toUpperCase(), age: created && !Number.isNaN(created.valueOf()) ? created.toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" }) : "" };
      }));
      setError("");
    } catch (requestError) { setError(requestError.message); }
    finally { setLoading(false); }
  };
  useEffect(() => { loadApplications(); }, [user]);

  const changeStage = async (item, stage) => {
    try {
      await api.updateCvStatus(user, item.id, stage === "Saved" ? "Draft" : stage);
      setApplications((current) => current.map((application) => application.id === item.id ? { ...application, stage } : application));
    } catch (requestError) { setError(requestError.message); }
  };

  const removeApplication = async (item) => {
    if (!window.confirm(`Delete the saved CV for ${item.job_title || "this role"}?`)) return;
    try {
      await api.deleteCv(user, item.id);
      setApplications((current) => current.filter((application) => application.id !== item.id));
    } catch (requestError) { setError(requestError.message); }
  };
  const inProgress = applications.filter((item) => ["Applied", "Screening", "Interview"].includes(item.stage)).length;
  const interviews = applications.filter((item) => item.stage === "Interview").length;
  const offers = applications.filter((item) => item.stage === "Offer").length;

  return (
    <div className="page-shell">
      <section className="page-heading"><div><span className="eyebrow">Stay on top of your search</span><h1>Applications</h1><p>Every tailored CV you are tracking, from saved to offer.</p></div><Button icon={BriefcaseBusiness} onClick={() => setPage("optimizer")}>Add application</Button></section>
      {error && <div className="error-message application-message">{error}</div>}
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
                <article className="panel application-card" key={item.id}>
                  <div className="candidate-name">
                    <span className="avatar">{item.initials}</span>
                    <span><strong>{item.job_title || "Untitled role"}</strong><small>Tailored CV</small></span>
                  </div>
                  <p>Created {item.age || "recently"}</p>
                  <select className="status-select application-status-select" value={item.stage} onChange={(event) => changeStage(item, event.target.value)} aria-label={`Status for ${item.job_title}`}>{stages.map((option) => <option key={option}>{option}</option>)}</select>
                  <div className="application-card-footer">
                    <Score value={item.score} compact />
                    <button className="text-button danger-text" onClick={() => removeApplication(item)}>Delete</button>
                  </div>
                </article>
              ))}
            </div>
          );
        })}
      </section>
      {!loading && !applications.length && <section className="panel empty-state"><BriefcaseBusiness size={28} /><h2>No applications tracked yet</h2><p>Create a tailored CV to add your first role to the board.</p><Button icon={Target} onClick={() => setPage("optimizer")}>Match a role</Button></section>}
      {loading && <section className="panel empty-state compact-empty"><h2>Loading applications...</h2></section>}
    </div>
  );
}

function Profile({ user, setPage }) {
  const [bundle, setBundle] = useState({ profile: {}, experiences: [], skills: [] });
  const [profile, setProfile] = useState({});
  const [skillName, setSkillName] = useState("");
  const [skillProficiency, setSkillProficiency] = useState("Intermediate");
  const [experience, setExperience] = useState({ company: "", position: "", start_date: "", end_date: "", current_job: false, description: "" });
  const [editingExperienceId, setEditingExperienceId] = useState(null);
  const [education, setEducation] = useState({ qualification: "", institution: "", start_year: "", end_year: "" });
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
    if (bundle.skills.some((skill) => skill.skill_name.toLowerCase() === skillName.trim().toLowerCase())) { setMessage("That skill is already on your profile."); return; }
    try {
      await api.addSkill(user, { skill_name: skillName.trim(), proficiency: skillProficiency });
      setSkillName("");
      await loadProfile();
    } catch (error) { setMessage(error.message); }
  };

  const updateSkillProficiency = async (id, proficiency) => {
    try { await api.updateSkill(user, id, { proficiency }); setBundle((current) => ({ ...current, skills: current.skills.map((skill) => skill.id === id ? { ...skill, proficiency } : skill) })); } catch (error) { setMessage(error.message); }
  };

  const removeSkill = async (id) => {
    try { await api.deleteSkill(user, id); await loadProfile(); } catch (error) { setMessage(error.message); }
  };

  const saveExperience = async () => {
    if (!experience.company.trim() || !experience.position.trim()) return;
    try {
      if (editingExperienceId) await api.updateExperience(user, editingExperienceId, experience);
      else await api.addExperience(user, experience);
      setExperience({ company: "", position: "", start_date: "", end_date: "", current_job: false, description: "" });
      setEditingExperienceId(null);
      setShowExperienceForm(false);
      await loadProfile();
    } catch (error) { setMessage(error.message); }
  };

  const editExperience = (item) => { setExperience({ company: item.company || "", position: item.position || "", start_date: item.start_date || "", end_date: item.end_date || "", current_job: Boolean(item.current_job), description: item.description || "" }); setEditingExperienceId(item.id); setShowExperienceForm(true); };

  const removeExperience = async (id) => {
    try { await api.deleteExperience(user, id); await loadProfile(); } catch (error) { setMessage(error.message); }
  };

  const addAchievement = async (experienceId, data) => { try { await api.addAchievement(user, experienceId, data); await loadProfile(); } catch (error) { setMessage(error.message); } };
  const removeAchievement = async (experienceId, achievementId) => { try { await api.deleteAchievement(user, experienceId, achievementId); await loadProfile(); } catch (error) { setMessage(error.message); } };
  const saveEducation = async () => {
    if (!education.qualification.trim() || !education.institution.trim()) return;
    const nextEducation = [...(profile.education || []), { ...education, id: `edu_${Date.now()}` }];
    try { const result = await api.updateProfile(user, { ...profile, education: nextEducation }); setProfile(result.profile); setEducation({ qualification: "", institution: "", start_year: "", end_year: "" }); setMessage("Education saved."); } catch (error) { setMessage(error.message); }
  };
  const removeEducation = async (id) => { const nextEducation = (profile.education || []).filter((item) => item.id !== id); try { const result = await api.updateProfile(user, { ...profile, education: nextEducation }); setProfile(result.profile); } catch (error) { setMessage(error.message); } };

  const completed = [profile.full_name, profile.professional_title, profile.professional_summary, bundle.skills.length, bundle.experiences.length, profile.education?.length].filter(Boolean).length;
  const strength = Math.round((completed / 6) * 100);
  const displayName = profile.full_name || user?.split("@")[0] || "Candidate";
  const initials = displayName.split(" ").map((part) => part[0]).join("").slice(0, 2).toUpperCase();
  return (
    <div className="page-shell">
      <section className="page-heading">
        <div><span className="eyebrow">Your career profile</span><h1>Profile</h1><p>Build it once. Fydara reuses your profile to generate tailored CVs and match you to every new role.</p></div>
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
            {["Basics", "Title", "Summary", "Skills", "Experience", "Education"].map((section, index) => <div className={index < completed ? "checklist-row" : "checklist-row muted-row"} key={section}><Check size={15} /> {section}</div>)}
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
            <div className="profile-skill-list">{bundle.skills.map((skill) => <div className="skill-editor-row" key={skill.id}><strong>{skill.skill_name}</strong><select className="simple-select" value={skill.proficiency || "Intermediate"} onChange={(event) => updateSkillProficiency(skill.id, event.target.value)}>{["Beginner", "Intermediate", "Advanced", "Expert"].map((level) => <option key={level}>{level}</option>)}</select><button className="icon-button" onClick={() => removeSkill(skill.id)} title={`Remove ${skill.skill_name}`}><X size={14} /></button></div>)}</div>
            <div className="skill-add-row"><input value={skillName} onChange={(event) => setSkillName(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter") addSkill(); }} placeholder="Add a skill..." /><select className="simple-select" value={skillProficiency} onChange={(event) => setSkillProficiency(event.target.value)}>{["Beginner", "Intermediate", "Advanced", "Expert"].map((level) => <option key={level}>{level}</option>)}</select><Button variant="secondary" icon={Check} onClick={addSkill}>Add</Button></div>
          </article>

          <article className="panel profile-form">
            <div className="panel-head"><h2>Experience</h2><button className="text-button" onClick={() => { setShowExperienceForm((value) => !value); setEditingExperienceId(null); setExperience({ company: "", position: "", start_date: "", end_date: "", current_job: false, description: "" }); }}>{showExperienceForm ? "Cancel" : "+ Add role"}</button></div>
            {showExperienceForm && <div className="experience-editor form-grid"><label>Position<input value={experience.position} onChange={(event) => setExperience({ ...experience, position: event.target.value })} /></label><label>Company<input value={experience.company} onChange={(event) => setExperience({ ...experience, company: event.target.value })} /></label><label>Start date<input type="date" value={experience.start_date} onChange={(event) => setExperience({ ...experience, start_date: event.target.value })} /></label><label>End date<input type="date" value={experience.end_date} disabled={experience.current_job} onChange={(event) => setExperience({ ...experience, end_date: event.target.value })} /></label><label className="check-row"><input type="checkbox" checked={experience.current_job} onChange={(event) => setExperience({ ...experience, current_job: event.target.checked, end_date: "" })} /> Current role</label><label className="full-field">Description<textarea value={experience.description} onChange={(event) => setExperience({ ...experience, description: event.target.value })} /></label><Button icon={Check} onClick={saveExperience}>{editingExperienceId ? "Update role" : "Save role"}</Button></div>}
            {bundle.experiences.map((item) => <ExperienceItem key={item.id} title={item.position} company={item.company} date={`${item.start_date || "Start"} - ${item.current_job ? "Present" : item.end_date || "End"}`} bullets={(item.description || "").split("\n").filter(Boolean)} achievements={bundle.achievements_by_experience?.[item.id] || []} onEdit={() => editExperience(item)} onDelete={() => removeExperience(item.id)} onAddAchievement={(data) => addAchievement(item.id, data)} onDeleteAchievement={(achievementId) => removeAchievement(item.id, achievementId)} />)}
            {!bundle.experiences.length && !showExperienceForm && <p className="profile-tip">Add your work history so TrueFit can tailor CVs and calculate stronger matches.</p>}
          </article>
          <article className="panel profile-form"><h2>Education</h2><div className="form-grid"><label>Qualification<input value={education.qualification} onChange={(event) => setEducation({ ...education, qualification: event.target.value })} placeholder="e.g. BSc Computer Science" /></label><label>Institution<input value={education.institution} onChange={(event) => setEducation({ ...education, institution: event.target.value })} /></label><label>Start year<input value={education.start_year} onChange={(event) => setEducation({ ...education, start_year: event.target.value })} /></label><label>End year<input value={education.end_year} onChange={(event) => setEducation({ ...education, end_year: event.target.value })} /></label></div><div className="profile-form-actions"><Button variant="secondary" icon={Check} onClick={saveEducation}>Add education</Button></div>{(profile.education || []).map((item) => <div className="experience-item" key={item.id}><div><strong>{item.qualification}</strong><small>{item.institution}</small></div><div className="experience-actions"><span className="status-tag">{item.start_year} - {item.end_year || "Present"}</span><button className="icon-button" onClick={() => removeEducation(item.id)}><X size={14} /></button></div></div>)}</article>
        </div>
      </section>}
    </div>
  );
}

function ExperienceItem({ title, company, date, bullets, achievements = [], onEdit, onDelete, onAddAchievement, onDeleteAchievement }) {
  const [achievement, setAchievement] = useState("");
  const [metric, setMetric] = useState("");
  const add = async () => { if (!achievement.trim()) return; await onAddAchievement({ achievement: achievement.trim(), metric: metric.trim() }); setAchievement(""); setMetric(""); };
  return (
    <div className="experience-item">
      <div>
        <strong>{title}</strong>
        <small>{company}</small>
        <ul>{bullets.map((bullet) => <li key={bullet}>{bullet}</li>)}</ul>
        {achievements.length > 0 && <div className="achievement-list"><strong>Achievements</strong>{achievements.map((item) => <div key={item.id}><span>{item.achievement}{item.metric ? ` - ${item.metric}` : ""}</span><button className="icon-button" onClick={() => onDeleteAchievement(item.id)}><X size={12} /></button></div>)}</div>}
        {onAddAchievement && <div className="achievement-add-row"><input value={achievement} onChange={(event) => setAchievement(event.target.value)} placeholder="Add a measurable achievement" /><input value={metric} onChange={(event) => setMetric(event.target.value)} placeholder="Metric (optional)" /><Button variant="secondary" icon={Check} onClick={add}>Add</Button></div>}
      </div>
      <div className="experience-actions"><span className="status-tag">{date}</span>{onEdit && <button className="text-button" onClick={onEdit}>Edit</button>}{onDelete && <button className="icon-button" onClick={onDelete} title="Delete experience"><X size={15} /></button>}</div>
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
  const [communicationHistory, setCommunicationHistory] = useState([]);
  const [hasReviewed, setHasReviewed] = useState(false);
  const [threshold, setThreshold] = useState(70);
  const [workspaceLoaded, setWorkspaceLoaded] = useState(false);
  const [workspaceStatus, setWorkspaceStatus] = useState("");
  const [recruiterProfile, setRecruiterProfile] = useState({});

  useEffect(() => {
    api.health().then(() => setApiOnline(true)).catch(() => setApiOnline(false));
  }, []);

  useEffect(() => {
    if (!user || role !== "recruiter") { setWorkspaceLoaded(false); return; }
    setWorkspaceStatus("Restoring saved workspace...");
    api.recruiterWorkspace(user).then((result) => {
      const workspace = result.workspace;
      if (workspace) {
        setJobDescription(workspace.job_description || "");
        setCandidates(workspace.candidates || []);
        setSelectedCandidate(workspace.selected_candidate || null);
        setCandidateMessages(workspace.candidate_messages || {});
        setReviewedMessages(workspace.reviewed_messages || {});
        setSentMessages(workspace.sent_messages || {});
        setCommunicationHistory(workspace.communication_history || []);
        setHasReviewed(Boolean(workspace.has_reviewed));
        setThreshold(Number(workspace.threshold || 70));
        setRecruiterProfile(workspace.recruiter_profile || {});
        setWorkspaceStatus("Saved workspace restored");
      } else setWorkspaceStatus("New workspace - changes save automatically");
    }).catch(() => setWorkspaceStatus("Workspace could not be restored")).finally(() => setWorkspaceLoaded(true));
  }, [user, role]);

  useEffect(() => {
    if (!workspaceLoaded || !user || role !== "recruiter") return undefined;
    setWorkspaceStatus("Saving...");
    const timeout = setTimeout(() => {
      api.saveRecruiterWorkspace(user, { job_description: jobDescription, job_title: getJobTitle(jobDescription), candidates, selected_candidate: selectedCandidate, candidate_messages: candidateMessages, reviewed_messages: reviewedMessages, sent_messages: sentMessages, communication_history: communicationHistory, has_reviewed: hasReviewed, threshold, recruiter_profile: recruiterProfile })
        .then(() => setWorkspaceStatus("All changes saved"))
        .catch(() => setWorkspaceStatus("Save failed - retrying after the next change"));
    }, 600);
    return () => clearTimeout(timeout);
  }, [workspaceLoaded, user, role, jobDescription, candidates, selectedCandidate, candidateMessages, reviewedMessages, sentMessages, communicationHistory, hasReviewed, threshold, recruiterProfile]);

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
    setCommunicationHistory([]);
    setHasReviewed(false);
    setPage(user ? "recruiter" : "auth");
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
    workspaceStatus,
    communicationHistory,
    setCommunicationHistory,
  };
  const recruiterWorkspaceView = { recruiter_email: user, job_description: jobDescription, job_title: getJobTitle(jobDescription), candidates, candidate_messages: candidateMessages, threshold, has_reviewed: hasReviewed };

  if (page === "landing") return <Landing setPage={setPage} setRole={setRole} onStartScreening={startScreening} />;
  if (page === "auth") return <Auth role={role} setRole={setRole} onAuthenticated={authenticated} setPage={setPage} />;
  if (page === "password-reset") return <PasswordResetPage setPage={setPage} />;

  return (
    <div className="app">
      <TopNav page={page} setPage={setPage} role={role} onLogout={logout} />
      {!apiOnline && <div className="offline-banner">FastAPI backend is offline. Start it on port 8000 to use live actions.</div>}
      {page === "candidate" && <CandidateDashboard setPage={setPage} user={user} />}
      {page === "optimizer" && <Optimizer user={user} setPage={setPage} />}
      {page === "profile" && <Profile user={user} setPage={setPage} />}
      {page === "applications" && <ApplicationsPage user={user} setPage={setPage} />}
      {page === "recruiter" && <RecruiterWorkspace onOpenReport={openMatchReport} screening={screeningState} recruiterEmail={user} />}
      {page === "recruiter-profile" && <RecruiterProfile user={user} profile={recruiterProfile} onChange={setRecruiterProfile} workspaceStatus={workspaceStatus} />}
      {page === "feedback" && <CandidateFeedbackPage />}
      {page === "jobs" && <JobsPage setPage={setPage} onStartScreening={startScreening} workspace={recruiterWorkspaceView} />}
      {page === "candidates" && <CandidatesPage onOpenReport={openMatchReport} workspace={recruiterWorkspaceView} />}
      {page === "report" && <MatchReportPage candidate={reportCandidate} setPage={setPage} reportContext={reportContext} />}
      {page === "reports" && <ReportsPage workspace={recruiterWorkspaceView} />}
      {page === "security" && <SecurityPage user={user} setPage={setPage} onLogout={logout} />}
    </div>
  );
}
