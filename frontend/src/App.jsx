/* FailSafe — Premium Frontend Application Shell
   Refactored to align seamlessly with Modularized API Layer and Auth Hooks.
   Rich Aesthetics: Curated dark mode color schemes, modern Google Fonts, custom SVG Logo,
   glassmorphism styling, interactive hover micro-animations.
*/

import { useState, useEffect, useRef } from "react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell
} from "recharts";
import { useAuth } from "./hooks/useAuth";
import { dashboard, predict, interventions } from "./services/api";

// ─── Custom Logo Matching Screenshot exactly ──────────────────────────────────
function LogoIcon() {
  return (
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M4 6L12 12L20 6" stroke="var(--text-main)" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
      <path d="M4 12L12 18L20 12" stroke="var(--text-main)" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
      <path d="M4 18L12 24L20 18" stroke="var(--text-main)" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" opacity="0.4"/>
    </svg>
  );
}

// ─── Premium Custom Components ────────────────────────────────────────────────
function RiskScoreGauge({ score }) {
  const pct = Math.round(score * 100);
  const color = score >= 0.7 ? "var(--accent-red)" : score >= 0.4 ? "var(--accent-amber)" : "var(--accent-green)";
  const bg = score >= 0.7 ? "var(--accent-red-bg)" : score >= 0.4 ? "var(--accent-amber-bg)" : "var(--accent-green-bg)";

  return (
    <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
      <div style={{ flex: 1, height: "6px", background: "var(--border-light)", borderRadius: "3px", overflow: "hidden" }}>
        <div 
          style={{ 
            width: `${pct}%`, 
            height: "100%", 
            background: color, 
            borderRadius: "3px",
            boxShadow: `0 0 10px ${color}` 
          }} 
        />
      </div>
      <span 
        style={{ 
          color, 
          background: bg,
          padding: "0.15rem 0.5rem",
          borderRadius: "4px",
          border: `1px solid ${color}33`,
          fontSize: "0.75rem", 
          fontWeight: 700, 
          minWidth: "40px",
          textAlign: "center" 
        }}
      >
        {pct}%
      </span>
    </div>
  );
}

// ─── Login Screen ─────────────────────────────────────────────────────────────
function LoginScreen() {
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      await login(email, password);
    } catch (err) {
      setError(err.message || "Invalid credentials provided.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", padding: "1.5rem" }}>
      <div className="animate-fade-in" style={{ width: "100%", maxWidth: "400px" }}>
        <div style={{ textAlign: "center", marginBottom: "2.5rem" }}>
          <div style={{ display: "inline-flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.5rem" }}>
            <span className="font-stencil text-gradient" style={{ fontSize: "2.25rem", fontWeight: 700 }}>FAILSAFE</span>
            <LogoIcon />
          </div>
          <p style={{ color: "var(--text-muted)", fontSize: "0.85rem", letterSpacing: "0.02em" }}>
            Proactive early student failure detection and intervention platform
          </p>
        </div>

        <div className="glass-panel" style={{ padding: "2rem" }}>
          <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
            <div>
              <label style={{ display: "block", fontSize: "0.75rem", fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: "0.5rem" }}>
                Email Address
              </label>
              <input
                type="email"
                className="premium-input"
                placeholder="e.g. admin@failsafe.edu"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoFocus
              />
            </div>

            <div>
              <label style={{ display: "block", fontSize: "0.75rem", fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: "0.5rem" }}>
                Password
              </label>
              <input
                type="password"
                className="premium-input"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>

            {error && (
              <div className="animate-slide-in" style={{ background: "var(--accent-red-bg)", color: "var(--accent-red)", padding: "0.75rem", borderRadius: "8px", fontSize: "0.75rem", border: "1px solid rgba(234, 84, 52, 0.3)" }}>
                ⚠️ {error}
              </div>
            )}

            <button type="submit" className="premium-btn premium-btn-primary" style={{ width: "100%", justifyContent: "center", marginTop: "0.5rem" }} disabled={loading}>
              {loading ? "Signing In..." : "Sign In"}
            </button>
          </form>
        </div>

        <div style={{ marginTop: "1.5rem", textAlign: "center", color: "var(--text-dim)", fontSize: "0.75rem" }}>
          Demo Account: <span style={{ color: "var(--text-muted)" }}>admin@failsafe.edu</span> / <span style={{ color: "var(--text-muted)" }}>admin123</span>
        </div>
      </div>
    </div>
  );
}

// ─── Dashboard Screen ─────────────────────────────────────────────────────────
function DashboardScreen({ onSelectStudent }) {
  const [stats, setStats] = useState(null);
  const [students, setStudents] = useState([]);
  const [filter, setFilter] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    Promise.all([
      dashboard.stats().catch(() => null),
      dashboard.students().catch(() => [])
    ]).then(([sData, stData]) => {
      if (!mounted) return;
      if (sData) setStats(sData);
      if (stData) setStudents(stData);
      setLoading(false);
    });

    return () => { mounted = false; };
  }, []);

  const filteredStudents = students.filter(s => !filter || s.risk_level === filter);

  const chartData = stats ? [
    { name: "High Risk", value: stats.at_risk_high, color: "var(--accent-red)" },
    { name: "Medium Risk", value: stats.at_risk_medium, color: "var(--accent-amber)" },
    { name: "Low Risk", value: stats.at_risk_low, color: "var(--accent-green)" },
  ] : [];

  return (
    <div className="animate-fade-in" style={{ display: "flex", flexDirection: "column", gap: "2rem" }}>
      {/* Dynamic Summary Cards */}
      {stats && (
        <div className="dashboard-grid">
          {[
            { label: "Total Students", value: stats.total_students, color: "var(--text-main)" },
            { label: "High Risk Students", value: stats.at_risk_high, color: "var(--accent-red)", glow: true },
            { label: "Pending Interventions", value: stats.interventions_pending, color: "var(--accent-amber)" },
            { label: "Completed Interventions", value: stats.interventions_completed, color: "var(--accent-green)" },
          ].map((item, idx) => (
            <div key={idx} className="glass-panel" style={{ padding: "1.25rem", animationDelay: `${idx * 0.05}s` }}>
              <div style={{ fontSize: "0.7rem", fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: "0.5rem" }}>
                {item.label}
              </div>
              <div className="font-display" style={{ fontSize: "2.25rem", fontWeight: 700, color: item.color, textShadow: item.glow ? "0 0 15px rgba(234,84,52,0.4)" : "none" }}>
                {item.value}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Visual analytics block */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "1.5rem" }}>
        <div className="glass-panel" style={{ padding: "1.5rem" }}>
          <div style={{ fontSize: "0.75rem", fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: "1rem" }}>
            Risk Distribution
          </div>
          <ResponsiveContainer width="100%" height={180}>
            <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border-subtle)" vertical={false} />
              <XAxis dataKey="name" tick={{ fill: "var(--text-muted)", fontSize: 10 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: "var(--text-muted)", fontSize: 10 }} axisLine={false} tickLine={false} />
              <Tooltip
                contentStyle={{ background: "var(--bg-surface)", border: "1px solid var(--border-light)", borderRadius: "8px", fontSize: "0.75rem" }}
                labelStyle={{ color: "var(--text-main)", fontWeight: 600 }}
                itemStyle={{ color: "var(--text-muted)" }}
                formatter={(val) => [val, "Students"]}
              />
              <Bar dataKey="value" radius={[6, 6, 0, 0]} barSize={40}>
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="glass-panel" style={{ padding: "1.5rem", display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
          <div>
            <div style={{ fontSize: "0.75rem", fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: "1rem" }}>
              Intervention Status
            </div>
            {stats ? (
              <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
                {[
                  { label: "Pending Review", value: stats.interventions_pending, color: "var(--text-muted)" },
                  { label: "In Progress", value: stats.interventions_in_progress, color: "var(--accent-amber)" },
                  { label: "Completed", value: stats.interventions_completed, color: "var(--accent-green)" },
                ].map((row, i) => (
                  <div key={i} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", paddingBottom: "0.5rem", borderBottom: "1px solid var(--border-subtle)" }}>
                    <span style={{ fontSize: "0.85rem", color: "var(--text-main)" }}>{row.label}</span>
                    <span className="font-display" style={{ fontSize: "1.1rem", fontWeight: 700, color: row.color }}>{row.value}</span>
                  </div>
                ))}
              </div>
            ) : (
              <div style={{ color: "var(--text-dim)", fontSize: "0.85rem" }}>No metrics loaded</div>
            )}
          </div>
          <div style={{ fontSize: "0.7rem", color: "var(--text-dim)", marginTop: "1rem" }}>
            💡 Select any student row below to view their detailed risk profile and intervention plan.
          </div>
        </div>
      </div>

      {/* Main interactive directory */}
      <div className="glass-panel" style={{ overflow: "hidden" }}>
        <div style={{ padding: "1.25rem 1.5rem", borderBottom: "1px solid var(--border-light)", display: "flex", flexWrap: "wrap", justifyContent: "space-between", alignItems: "center", gap: "1rem" }}>
          <div style={{ fontSize: "0.85rem", fontWeight: 700, color: "var(--text-main)", textTransform: "uppercase", letterSpacing: "0.06em" }}>
            Student Roster
          </div>
          <div style={{ display: "flex", gap: "0.5rem" }}>
            {["", "High", "Medium", "Low"].map((level) => (
              <button
                key={level}
                onClick={() => setFilter(level)}
                className={`premium-btn ${filter === level ? "premium-btn-secondary" : "premium-btn-ghost"}`}
                style={{ padding: "0.35rem 0.75rem", fontSize: "0.75rem" }}
              >
                {level || "All"}
              </button>
            ))}
          </div>
        </div>

        {loading ? (
          <div style={{ padding: "4rem", textAlign: "center", color: "var(--text-muted)" }}>
            <div style={{ fontSize: "1.5rem", marginBottom: "0.5rem" }}>⏳</div>
            Loading student data...
          </div>
        ) : (
          <div style={{ overflowX: "auto" }}>
            <table className="table-custom">
              <thead>
                <tr>
                  <th>Student Name</th>
                  <th>System Identifier</th>
                  <th>Risk Score</th>
                  <th>Risk Level</th>
                  <th>Status</th>
                  <th>Last Updated</th>
                </tr>
              </thead>
              <tbody>
                {filteredStudents.map((st) => (
                  <tr key={st.id} className="table-row" onClick={() => onSelectStudent(st)}>
                    <td style={{ fontWeight: 600, color: "#ffffff" }}>{st.name}</td>
                    <td className="font-mono" style={{ color: "var(--text-muted)", fontSize: "0.75rem" }}>{st.student_id}</td>
                    <td style={{ minWidth: "150px" }}>
                      <RiskScoreGauge score={st.risk_score} />
                    </td>
                    <td>
                      <span className={`badge badge-${st.risk_level.toLowerCase()}`}>
                        {st.risk_level}
                      </span>
                    </td>
                    <td>
                      <span className={`status-tag status-${st.intervention_status || "pending"}`}>
                        {(st.intervention_status || "Pending").replace("_", " ")}
                      </span>
                    </td>
                    <td style={{ color: "var(--text-muted)", fontSize: "0.75rem" }}>
                      {new Date(st.predicted_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
                {filteredStudents.length === 0 && (
                  <tr>
                    <td colSpan="6" style={{ textAlign: "center", padding: "3rem", color: "var(--text-dim)" }}>
                      No students match the current filters.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

// ─── Student Detail View (SHAP Explainer) ─────────────────────────────────────
function StudentDetailScreen({ student, onBack }) {
  const [detail, setDetail] = useState(null);
  const [loading, setLoading] = useState(true);
  const [notes, setNotes] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    let mounted = true;
    dashboard.studentDetail(student.id)
      .then((data) => {
        if (!mounted) return;
        setDetail(data);
        const activePlan = data.predictions?.[0]?.intervention;
        if (activePlan?.faculty_notes) setNotes(activePlan.faculty_notes);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Detail query failed", err);
        if (mounted) setLoading(false);
      });
    return () => { mounted = false; };
  }, [student.id]);

  const currentPred = detail?.predictions?.[0];
  const activeIntervention = currentPred?.intervention;

  const handleStatusChange = async (newStatus) => {
    if (!activeIntervention) return;
    try {
      await interventions.update(activeIntervention.id, { status: newStatus });
      setDetail(prev => ({
        ...prev,
        predictions: prev.predictions.map((p, idx) => 
          idx === 0 ? { ...p, intervention: { ...p.intervention, status: newStatus } } : p
        )
      }));
    } catch (e) {
      alert("Failed to update status.");
    }
  };

  const handleNotesSave = async () => {
    if (!activeIntervention) return;
    setSaving(true);
    try {
      await interventions.update(activeIntervention.id, { faculty_notes: notes });
      alert("Notes saved successfully.");
    } catch (e) {
      alert("Failed to save notes.");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div style={{ padding: "4rem", textAlign: "center", color: "var(--text-muted)" }}>
        Loading student details...
      </div>
    );
  }

  const shapContributions = currentPred?.shap_values?.slice(0, 8).map(item => ({
    name: item.description || item.feature,
    value: item.shap_value,
    actualValue: item.feature_value
  })) || [];

  return (
    <div className="animate-fade-in" style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
      <button onClick={onBack} className="premium-btn premium-btn-ghost" style={{ alignSelf: "flex-start", paddingLeft: 0 }}>
        ← Back to Dashboard
      </button>

      {/* Header Panel */}
      <div className="glass-panel" style={{ padding: "1.5rem", display: "flex", flexWrap: "wrap", justifyContent: "space-between", alignItems: "center", gap: "1rem" }}>
        <div>
          <div style={{ fontSize: "1.5rem", fontWeight: 700, color: "#ffffff", marginBottom: "0.25rem" }}>
            {student.name}
          </div>
          <div className="font-mono" style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
            UUID: {student.student_id}
          </div>
        </div>

        {currentPred && (
          <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
            <div style={{ textAlign: "right" }}>
              <span className={`badge badge-${currentPred.risk_level.toLowerCase()}`} style={{ fontSize: "0.85rem", padding: "0.35rem 0.85rem" }}>
                {currentPred.risk_level} Risk
              </span>
            </div>
            <div className="glass-panel-elevated" style={{ padding: "0.65rem 1.25rem", textAlign: "center", border: `1px solid ${currentPred.risk_level === "High" ? "var(--accent-red)" : "var(--border-light)"}` }}>
              <div className="font-display" style={{ fontSize: "1.75rem", fontWeight: 700, color: currentPred.risk_level === "High" ? "var(--accent-red)" : "var(--accent-amber)", lineHeight: 1 }}>
                {Math.round(currentPred.risk_score * 100)}%
              </div>
              <div style={{ fontSize: "0.65rem", color: "var(--text-muted)", letterSpacing: "0.08em", marginTop: "0.25rem" }}>
                RISK SCORE
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Analytics Layout */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(340px, 1fr))", gap: "1.5rem" }}>
        {/* SHAP Impact Waterfall */}
        <div className="glass-panel" style={{ padding: "1.5rem" }}>
          <div style={{ fontSize: "0.75rem", fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: "0.5rem" }}>
            Key Risk Factors
          </div>
          <p style={{ fontSize: "0.75rem", color: "var(--text-dim)", marginBottom: "1.25rem" }}>
            The top factors contributing to this student's risk score.
          </p>

          {shapContributions.length > 0 ? (
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={shapContributions} layout="vertical" margin={{ left: 10, right: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border-subtle)" horizontal={false} />
                <XAxis type="number" tick={{ fill: "var(--text-muted)", fontSize: 10 }} axisLine={false} tickLine={false} />
                <YAxis dataKey="name" type="category" width={140} tick={{ fill: "var(--text-main)", fontSize: 11 }} axisLine={false} tickLine={false} />
                <Tooltip
                  contentStyle={{ background: "var(--bg-surface)", border: "1px solid var(--border-light)", borderRadius: "8px", fontSize: "0.75rem" }}
                  formatter={(val, name, props) => [
                    `${val > 0 ? "+" : ""}${val.toFixed(3)} (Value: ${props.payload.actualValue})`, 
                    "Impact"
                  ]}
                />
                <Bar dataKey="value" radius={[0, 4, 4, 0]} barSize={14}>
                  {shapContributions.map((item, idx) => (
                    <Cell key={idx} fill={item.value > 0 ? "var(--accent-red)" : "var(--accent-green)"} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div style={{ padding: "3rem", textAlign: "center", color: "var(--text-dim)" }}>
              No detailed risk factors available for this student.
            </div>
          )}

          <div style={{ display: "flex", gap: "1.25rem", justifyContent: "center", fontSize: "0.75rem", color: "var(--text-muted)", marginTop: "1rem", paddingTop: "0.75rem", borderTop: "1px solid var(--border-subtle)" }}>
            <span style={{ display: "inline-flex", alignItems: "center", gap: "0.35rem" }}>
              <span style={{ width: "8px", height: "8px", borderRadius: "50%", background: "var(--accent-red)" }} />
              Increases Risk
            </span>
            <span style={{ display: "inline-flex", alignItems: "center", gap: "0.35rem" }}>
              <span style={{ width: "8px", height: "8px", borderRadius: "50%", background: "var(--accent-green)" }} />
              Decreases Risk
            </span>
          </div>
        </div>

        {/* Narrative & Timeline Stream */}
        <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
          <div className="glass-panel" style={{ padding: "1.5rem", flex: 1 }}>
            <div style={{ fontSize: "0.75rem", fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: "0.75rem" }}>
              AI Summary
            </div>
            <div style={{
              background: "var(--bg-surface-elevated)",
              padding: "1.25rem",
              borderRadius: "8px",
              border: "1px solid var(--border-subtle)",
              fontSize: "0.85rem",
              lineHeight: 1.6,
              color: "var(--text-main)",
              whiteSpace: "pre-line"
            }}>
              {currentPred?.explanation_text || "No summary available."}
            </div>
          </div>

          {detail?.predictions?.length > 1 && (
            <div className="glass-panel" style={{ padding: "1.25rem 1.5rem" }}>
              <div style={{ fontSize: "0.75rem", fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: "0.5rem" }}>
                Risk Trend
              </div>
              <ResponsiveContainer width="100%" height={70}>
                <BarChart data={detail.predictions.slice().reverse().map((p, i) => ({
                  label: `T-${detail.predictions.length - i}`,
                  index: Math.round(p.risk_score * 100)
                }))}>
                  <Bar dataKey="index" fill="var(--accent-blue)" radius={[4, 4, 0, 0]} barSize={24} />
                  <Tooltip contentStyle={{ background: "var(--bg-surface)", border: "1px solid var(--border-light)", borderRadius: "8px", fontSize: "0.75rem" }} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      </div>

      {/* Auto-generated Intervention Module */}
      {activeIntervention && (
        <div className="glass-panel" style={{ padding: "1.5rem" }}>
          <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "space-between", alignItems: "center", gap: "1rem", marginBottom: "1.25rem", paddingBottom: "1rem", borderBottom: "1px solid var(--border-light)" }}>
            <div>
              <div style={{ fontSize: "0.85rem", fontWeight: 700, color: "#ffffff", textTransform: "uppercase", letterSpacing: "0.06em" }}>
                Recommended Intervention Plan
              </div>
              <p style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
                Actionable steps to support the student.
              </p>
            </div>

            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <span style={{ fontSize: "0.75rem", color: "var(--text-dim)" }}>Status:</span>
              {["pending", "in_progress", "completed"].map((stage) => (
                <button
                  key={stage}
                  onClick={() => handleStatusChange(stage)}
                  className={`premium-btn ${activeIntervention.status === stage ? "premium-btn-secondary" : "premium-btn-ghost"}`}
                  style={{ 
                    padding: "0.25rem 0.65rem", 
                    fontSize: "0.7rem",
                    borderColor: activeIntervention.status === stage ? "var(--border-focus)" : "transparent",
                    color: activeIntervention.status === stage ? "#ffffff" : "var(--text-muted)"
                  }}
                >
                  {stage.replace("_", " ").toUpperCase()}
                </button>
              ))}
            </div>
          </div>

          <div style={{
            background: "var(--bg-surface-elevated)",
            borderLeft: `4px solid ${activeIntervention.risk_level === "High" ? "var(--accent-red)" : "var(--accent-amber)"}`,
            padding: "1rem 1.25rem",
            borderRadius: "0 8px 8px 0",
            fontSize: "0.85rem",
            color: "var(--text-main)",
            marginBottom: "1.5rem"
          }}>
            <strong>Summary:</strong> {activeIntervention.summary}
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "1rem", marginBottom: "1.5rem" }}>
            {(activeIntervention.actions || []).map((act, i) => (
              <div key={i} style={{
                background: "var(--bg-base)",
                border: "1px solid var(--border-subtle)",
                borderRadius: "8px",
                padding: "1.25rem",
                display: "flex",
                flexDirection: "column",
                justifyContent: "space-between"
              }}>
                <div>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.75rem" }}>
                    <span style={{ fontSize: "0.75rem", fontWeight: 700, color: "var(--accent-blue)" }}>{act.category}</span>
                    <span className={`badge badge-${act.priority.toLowerCase()}`} style={{ fontSize: "0.65rem" }}>{act.priority}</span>
                  </div>
                  <p style={{ fontSize: "0.85rem", color: "var(--text-main)", marginBottom: "0.75rem", lineHeight: 1.5 }}>
                    {act.action}
                  </p>
                </div>
                <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", borderTop: "1px solid var(--border-subtle)", paddingTop: "0.5rem", marginTop: "0.5rem" }}>
                  <strong>Follow-up:</strong> {act.followup}
                </div>
              </div>
            ))}
          </div>

          {/* Persistent Logs Block */}
          <div>
            <label style={{ display: "block", fontSize: "0.75rem", fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: "0.5rem" }}>
              Faculty Notes
            </label>
            <textarea
              className="premium-input"
              style={{ height: "100px", resize: "vertical", marginBottom: "0.75rem" }}
              placeholder="Add notes from meetings, phone calls, or emails..."
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
            />
            <button 
              onClick={handleNotesSave} 
              className="premium-btn premium-btn-secondary" 
              style={{ borderColor: "var(--border-light)" }}
              disabled={saving}
            >
              {saving ? "Saving..." : "Save Notes"}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

// ─── CSV Batch Upload Stream ──────────────────────────────────────────────────
function UploadScreen({ onUploaded }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);
  const fileInputRef = useRef();

  const handleDrop = (e) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile?.name.endsWith(".csv")) {
      setFile(droppedFile);
      setError("");
    } else {
      setError("Error: Only CSV files are accepted.");
    }
  };

  const executeUploadStream = async () => {
    if (!file) return;
    setLoading(true);
    setError("");
    try {
      const responsePayload = await predict.uploadCSV(file);
      setResult(responsePayload);
    } catch (err) {
      setError(err.message || "Error processing file.");
    } finally {
      setLoading(false);
    }
  };

  if (result) {
    return (
      <div className="animate-fade-in" style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
        <div className="glass-panel" style={{ padding: "1.5rem", borderLeft: "4px solid var(--accent-green)" }}>
          <div style={{ fontSize: "1.25rem", fontWeight: 700, color: "#ffffff", marginBottom: "0.5rem" }}>
            Upload Successful
          </div>
          <p style={{ fontSize: "0.85rem", color: "var(--text-muted)" }}>
            Student data has been processed and analyzed successfully.
          </p>
        </div>

        <div className="dashboard-grid">
          <div className="glass-panel" style={{ padding: "1.25rem" }}>
            <div style={{ fontSize: "0.7rem", color: "var(--text-muted)", textTransform: "uppercase" }}>Total Records</div>
            <div className="font-display" style={{ fontSize: "2rem", fontWeight: 700, color: "var(--accent-blue)" }}>{result.total}</div>
          </div>
          <div className="glass-panel" style={{ padding: "1.25rem" }}>
            <div style={{ fontSize: "0.7rem", color: "var(--text-muted)", textTransform: "uppercase" }}>At Risk Students</div>
            <div className="font-display" style={{ fontSize: "2rem", fontWeight: 700, color: "var(--accent-red)" }}>{result.at_risk_count}</div>
          </div>
          <div className="glass-panel" style={{ padding: "1.25rem" }}>
            <div style={{ fontSize: "0.7rem", color: "var(--text-muted)", textTransform: "uppercase" }}>On Track Students</div>
            <div className="font-display" style={{ fontSize: "2rem", fontWeight: 700, color: "var(--accent-green)" }}>{result.total - result.at_risk_count}</div>
          </div>
        </div>

        <div className="glass-panel" style={{ overflow: "hidden" }}>
          <div style={{ padding: "1rem 1.5rem", borderBottom: "1px solid var(--border-light)", fontSize: "0.85rem", fontWeight: 700 }}>
            Sample Results
          </div>
          <table className="table-custom">
            <thead>
              <tr>
                <th>Student Name</th>
                <th>Risk Score</th>
                <th>Risk Level</th>
              </tr>
            </thead>
            <tbody>
              {result.results?.slice(0, 8).map((row, i) => (
                <tr key={i} className="table-row">
                  <td style={{ fontWeight: 600 }}>{row.name}</td>
                  <td><RiskScoreGauge score={row.risk_score} /></td>
                  <td><span className={`badge badge-${row.risk_level.toLowerCase()}`}>{row.risk_level}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div style={{ display: "flex", gap: "1rem" }}>
          <button onClick={onUploaded} className="premium-btn premium-btn-primary">
            Go to Dashboard
          </button>
          <button onClick={() => { setResult(null); setFile(null); }} className="premium-btn premium-btn-ghost">
            Upload Another File
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="animate-fade-in" style={{ maxWidth: "700px", margin: "0 auto", width: "100%" }}>
      <div className="glass-panel" style={{ padding: "2.5rem", textAlign: "center" }}>
        <div style={{ fontSize: "1.25rem", fontWeight: 700, color: "#ffffff", marginBottom: "0.5rem" }}>
          Data Upload
        </div>
        <p style={{ color: "var(--text-muted)", fontSize: "0.85rem", marginBottom: "2rem" }}>
          Upload student data (CSV) to analyze risk levels and generate intervention plans.
        </p>

        <div
          onDragOver={(e) => e.preventDefault()}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          style={{
            border: "2px dashed var(--border-light)",
            borderRadius: "12px",
            padding: "3.5rem 2rem",
            background: "var(--bg-base)",
            cursor: "pointer",
            transition: "all 0.2s ease",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: "1rem"
          }}
        >
          <input 
            ref={fileInputRef} 
            type="file" 
            accept=".csv" 
            style={{ display: "none" }} 
            onChange={(e) => {
              if (e.target.files[0]) setFile(e.target.files[0]);
            }} 
          />
          <div style={{ fontSize: "2.5rem" }}>📁</div>
          <div>
            <div style={{ fontWeight: 600, color: "var(--text-main)", marginBottom: "0.25rem", fontSize: "0.95rem" }}>
              {file ? file.name : "Drag & drop your CSV file here"}
            </div>
            <div style={{ fontSize: "0.75rem", color: "var(--text-dim)" }}>
              {file ? `${(file.size / 1024).toFixed(1)} KB` : "or click to browse"}
            </div>
          </div>
        </div>

        {error && (
          <div style={{ color: "var(--accent-red)", fontSize: "0.75rem", marginTop: "1rem", padding: "0.5rem", background: "var(--accent-red-bg)", borderRadius: "6px" }}>
            {error}
          </div>
        )}

        <div style={{ marginTop: "2rem", display: "flex", justifyContent: "center", gap: "1rem" }}>
          <button
            onClick={executeUploadStream}
            className="premium-btn premium-btn-primary"
            disabled={!file || loading}
          >
            {loading ? "Analyzing Data..." : "Analyze Data"}
          </button>
          {file && (
            <button onClick={() => setFile(null)} className="premium-btn premium-btn-ghost">
              Clear
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

// ─── Global Interventions Roster View ─────────────────────────────────────────
function InterventionsScreen() {
  const [list, setList] = useState([]);
  const [filter, setFilter] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    interventions.list(filter)
      .then((data) => {
        if (!mounted) return;
        setList(data || []);
        setLoading(false);
      })
      .catch(() => {
        if (mounted) setLoading(false);
      });
    return () => { mounted = false; };
  }, [filter]);

  const updateItemStatus = async (id, stage) => {
    try {
      await interventions.update(id, { status: stage });
      setList(prev => prev.map(item => item.id === id ? { ...item, status: stage } : item));
    } catch (e) {
      alert("Status dispatch update rejected.");
    }
  };

  return (
    <div className="animate-fade-in" style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
      <div className="glass-panel" style={{ padding: "1.25rem 1.5rem", display: "flex", flexWrap: "wrap", justifyContent: "space-between", alignItems: "center", gap: "1rem" }}>
        <div style={{ fontSize: "1rem", fontWeight: 700, color: "#ffffff", textTransform: "uppercase", letterSpacing: "0.06em" }}>
          Interventions List
        </div>
        <div style={{ display: "flex", gap: "0.5rem" }}>
          {["", "pending", "in_progress", "completed"].map((st) => (
            <button
              key={st}
              onClick={() => setFilter(st)}
              className={`premium-btn ${filter === st ? "premium-btn-secondary" : "premium-btn-ghost"}`}
              style={{ padding: "0.35rem 0.75rem", fontSize: "0.75rem" }}
            >
              {st ? st.replace("_", " ").toUpperCase() : "All Statuses"}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div style={{ padding: "4rem", textAlign: "center", color: "var(--text-muted)" }}>
          Loading interventions...
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
          {list.map((item) => (
            <div key={item.id} className="glass-panel" style={{ padding: "1.5rem", display: "flex", flexDirection: "column", gap: "1rem" }}>
              <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "space-between", alignItems: "flex-start", gap: "1rem" }}>
                <div>
                  <div style={{ fontSize: "1.1rem", fontWeight: 700, color: "#ffffff", marginBottom: "0.25rem" }}>
                    {item.student_name}
                  </div>
                  <p style={{ fontSize: "0.85rem", color: "var(--text-muted)", maxWidth: "800px" }}>
                    {item.summary}
                  </p>
                </div>

                <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
                  <span className={`badge badge-${item.risk_level.toLowerCase()}`}>{item.risk_level}</span>
                  <span className={`status-tag status-${item.status}`}>
                    {item.status.replace("_", " ").toUpperCase()}
                  </span>
                </div>
              </div>

              {item.actions && item.actions.length > 0 && (
                <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
                  {item.actions.map((act, i) => (
                    <span key={i} style={{ background: "var(--bg-base)", border: "1px solid var(--border-subtle)", padding: "0.2rem 0.6rem", borderRadius: "4px", fontSize: "0.75rem", color: "var(--text-dim)" }}>
                      {act.category}
                    </span>
                  ))}
                </div>
              )}

              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderTop: "1px solid var(--border-subtle)", paddingTop: "1rem", marginTop: "0.25rem" }}>
                <span style={{ fontSize: "0.75rem", color: "var(--text-dim)" }}>
                  Trigger Date: {new Date(item.created_at).toLocaleDateString()}
                </span>
                <div style={{ display: "flex", gap: "0.5rem" }}>
                  {["pending", "in_progress", "completed"].map((st) => (
                    <button
                      key={st}
                      onClick={() => updateItemStatus(item.id, st)}
                      className={`premium-btn ${item.status === st ? "premium-btn-secondary" : "premium-btn-ghost"}`}
                      style={{ padding: "0.25rem 0.65rem", fontSize: "0.7rem" }}
                    >
                      Set {st.replace("_", " ")}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ))}
          {list.length === 0 && (
            <div style={{ padding: "4rem", textAlign: "center", color: "var(--text-dim)" }}>
              No interventions found.
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ─── Main Portal Context & Router ─────────────────────────────────────────────
export default function App() {
  const { user, logout } = useAuth();
  const [currentTab, setCurrentTab] = useState("dashboard");
  const [selectedStudent, setSelectedStudent] = useState(null);

  if (!user) {
    return <LoginScreen />;
  }

  const navigateToTab = (tabId) => {
    setCurrentTab(tabId);
    setSelectedStudent(null);
  };

  const handleStudentSelect = (studentObj) => {
    setSelectedStudent(studentObj);
    setCurrentTab("student_detail");
  };

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
      {/* Universal Sticky Top Header */}
      <header 
        style={{ 
          height: "64px", 
          background: "var(--bg-surface)", 
          borderBottom: "1px solid var(--border-light)", 
          display: "flex", 
          alignItems: "center", 
          justifyContent: "space-between", 
          padding: "0 2rem",
          position: "sticky",
          top: 0,
          zIndex: 100,
          boxShadow: "0 4px 20px rgba(0,0,0,0.5)"
        }}
      >
        <div 
          onClick={() => navigateToTab("dashboard")} 
          style={{ display: "flex", alignItems: "center", gap: "0.65rem", cursor: "pointer" }}
        >
          <span className="font-stencil text-gradient" style={{ fontSize: "1.5rem", fontWeight: 700 }}>FAILSAFE</span>
          <div style={{ transform: "scale(0.85)", transformOrigin: "left center" }}>
            <LogoIcon />
          </div>
        </div>

        <nav style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          {[
            { id: "dashboard", label: "Dashboard" },
            { id: "upload", label: "Upload Data" },
            { id: "interventions", label: "Interventions" },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => navigateToTab(tab.id)}
              className={`premium-btn ${currentTab === tab.id && !selectedStudent ? "premium-btn-secondary" : "premium-btn-ghost"}`}
              style={{ padding: "0.45rem 1rem", fontSize: "0.8rem", borderRadius: "6px" }}
            >
              {tab.label}
            </button>
          ))}
        </nav>

        <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
          <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end" }}>
            <span style={{ fontSize: "0.8rem", fontWeight: 600, color: "var(--text-main)", lineHeight: 1.2 }}>
              {user.full_name}
            </span>
            <span style={{ fontSize: "0.65rem", color: "var(--accent-purple)", fontWeight: 700, letterSpacing: "0.06em", textTransform: "uppercase" }}>
              Tier: {user.role}
            </span>
          </div>
          
          <div style={{ width: "1px", height: "24px", background: "var(--border-light)" }} />

          <button
            onClick={logout}
            className="premium-btn premium-btn-ghost"
            style={{ padding: "0.4rem 0.75rem", fontSize: "0.75rem" }}
            title="Sign Out"
          >
            Sign Out
          </button>
        </div>
      </header>

      {/* Main Responsive Routing Canvas */}
      <main style={{ flex: 1, padding: "2.5rem 2rem", maxWidth: "1400px", margin: "0 auto", width: "100%" }}>
        {currentTab === "dashboard" && !selectedStudent && (
          <DashboardScreen onSelectStudent={handleStudentSelect} />
        )}
        {currentTab === "student_detail" && selectedStudent && (
          <StudentDetailScreen 
            student={selectedStudent} 
            onBack={() => navigateToTab("dashboard")} 
          />
        )}
        {currentTab === "upload" && (
          <UploadScreen onUploaded={() => navigateToTab("dashboard")} />
        )}
        {currentTab === "interventions" && (
          <InterventionsScreen />
        )}
      </main>
    </div>
  );
}
