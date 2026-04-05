// View renderers — each returns HTML strings for a given route.

const Views = {

    landing() {
        return `
          <section class="hero">
            <div class="hero-badge">◈ Powered by Claude Opus 4.6 Vision</div>
            <h1>
              Smarter skin triage,<br>
              <span class="gradient">in seconds</span>
            </h1>
            <p class="hero-sub">
              Upload a photo, chat with our AI, and get structured insights grounded
              in dermatological frameworks. When it matters, escalate to a real
              dermatologist through our expert network.
            </p>
            <div class="hero-cta">
              <a class="btn btn-primary btn-lg" href="/signup" data-link>Start free</a>
              <a class="btn btn-secondary btn-lg" href="/conditions" data-link>Browse library</a>
            </div>
            <p class="hero-disclaimer">
              DermScan AI is for informational triage only. Not a medical device. Always consult a qualified healthcare professional.
            </p>
          </section>

          <section class="features">
            <div class="section-title">
              <h2>Everything skin-smart, in one place</h2>
              <p>Vision-based AI, a rich condition library, and direct expert access for serious cases.</p>
            </div>
            <div class="grid grid-3">
              <div class="feature">
                <div class="feature-icon">📸</div>
                <h3>Vision analysis</h3>
                <p>Upload a photo. Claude's vision model analyzes morphology, color, border, and texture — then explains what it sees.</p>
              </div>
              <div class="feature">
                <div class="feature-icon">💬</div>
                <h3>Multi-turn triage</h3>
                <p>The AI asks follow-up questions and builds on your answers. Not sure? It offers 2–3 possibilities with confidence scores.</p>
              </div>
              <div class="feature">
                <div class="feature-icon">📚</div>
                <h3>Condition library</h3>
                <p>Plain-language info on 12+ common skin conditions — appearance, causes, self-care, and when to see a doctor.</p>
              </div>
              <div class="feature">
                <div class="feature-icon">⚕️</div>
                <h3>Expert chat</h3>
                <p>For serious cases, connect directly with verified dermatologists. Urgent escalation available on Expert+.</p>
              </div>
              <div class="feature">
                <div class="feature-icon">🔒</div>
                <h3>Private & secure</h3>
                <p>Your images and conversations are encrypted at rest. You own your data.</p>
              </div>
              <div class="feature">
                <div class="feature-icon">🎯</div>
                <h3>ABCDE framework</h3>
                <p>For pigmented lesions we apply the clinical ABCDE rule — Asymmetry, Border, Color, Diameter, Evolution.</p>
              </div>
            </div>
          </section>

          <section class="features">
            <div class="section-title">
              <h2>How it works</h2>
            </div>
            <div class="grid grid-4">
              <div class="feature"><div class="feature-icon">1</div><h3>Snap a photo</h3><p>Take a clear, well-lit picture of the area you're concerned about.</p></div>
              <div class="feature"><div class="feature-icon">2</div><h3>Upload & describe</h3><p>Add context: how long it's been there, any symptoms, recent changes.</p></div>
              <div class="feature"><div class="feature-icon">3</div><h3>Get triaged</h3><p>Receive up to 3 possible conditions, severity, and next-step guidance.</p></div>
              <div class="feature"><div class="feature-icon">4</div><h3>Escalate if needed</h3><p>For significant findings, chat directly with a verified dermatologist.</p></div>
            </div>
          </section>
        `;
    },

    login() {
        return `
          <div class="auth-wrap">
            <h1>Welcome back</h1>
            <p class="sub">Sign in to continue your skin triage.</p>
            <form id="loginForm" class="stack">
              <div class="form-group">
                <label>Email</label>
                <input type="email" name="email" required autofocus>
              </div>
              <div class="form-group">
                <label>Password</label>
                <input type="password" name="password" required minlength="8">
              </div>
              <button class="btn btn-primary btn-block btn-lg" type="submit">Sign in</button>
              <div class="form-error" id="loginErr"></div>
            </form>
            <p class="auth-foot">No account? <a href="/signup" data-link>Create one</a></p>
          </div>
        `;
    },

    signup() {
        return `
          <div class="auth-wrap">
            <h1>Create your account</h1>
            <p class="sub">Start with 5 free AI scans per month.</p>
            <form id="signupForm" class="stack">
              <div class="form-group">
                <label>Full name</label>
                <input type="text" name="name" required autofocus>
              </div>
              <div class="form-group">
                <label>Email</label>
                <input type="email" name="email" required>
              </div>
              <div class="form-group">
                <label>Password</label>
                <input type="password" name="password" required minlength="8">
              </div>
              <button class="btn btn-primary btn-block btn-lg" type="submit">Create account</button>
              <div class="form-error" id="signupErr"></div>
            </form>
            <p class="auth-foot">Already have one? <a href="/login" data-link>Sign in</a></p>
          </div>
        `;
    },

    dashboardShell(user, conversations) {
        const usage = user.scans_limit === -1
            ? `${user.scans_used} scans used`
            : `${user.scans_used}/${user.scans_limit} scans used`;
        const convItems = conversations.length === 0
            ? `<p style="color: var(--text-dim); font-size: 0.88rem;">No scans yet. Click "New analysis" to start.</p>`
            : conversations.map(c => `
                <div class="conv-item" data-conv-id="${c.id}">
                  <div class="conv-title">${escapeHtml(c.title)}</div>
                  <div class="conv-meta">
                    <span class="sev-pill sev-${c.severity_score || 1}">Sev ${c.severity_score || 1}</span>
                    <span>${new Date(c.updated_at + 'Z').toLocaleDateString()}</span>
                  </div>
                </div>
              `).join("");

        return `
          <div class="dash">
            <aside class="dash-sidebar">
              <button class="btn btn-primary btn-block" id="newAnalysisBtn">+ New analysis</button>
              <div class="mt-3">
                <h3>Your plan</h3>
                <div class="card" style="padding: 0.85rem; background: var(--bg-elev);">
                  <div style="font-weight: 600;">${escapeHtml(user.plan_name)}</div>
                  <div style="font-size: 0.82rem; color: var(--text-dim);">${usage}</div>
                  ${user.plan !== 'expert' ? `<a href="/pricing" data-link class="btn btn-ghost btn-sm" style="padding: 0; margin-top: 0.4rem;">Upgrade →</a>` : ''}
                </div>
              </div>
              <div class="mt-3">
                <h3>Recent scans</h3>
                <div id="convList">${convItems}</div>
              </div>
            </aside>
            <section class="dash-main" id="dashMain">
              ${this.dashboardEmpty()}
            </section>
          </div>
        `;
    },

    dashboardEmpty() {
        return `
          <div class="dash-empty">
            <div style="font-size: 3.5rem; margin-bottom: 1rem;">◈</div>
            <h3>Welcome to DermScan AI</h3>
            <p>Start a new analysis to get AI-powered triage in seconds. You can continue the conversation to clarify, add photos, and refine results.</p>
            <button class="btn btn-primary btn-lg" id="emptyNewBtn">+ Start new analysis</button>
          </div>
        `;
    },

    conversationView(conv) {
        return `
          <div class="dash-header">
            <div>
              <h2>${escapeHtml(conv.title)}</h2>
              <span class="sev-pill sev-${conv.severity_score || 1}">Severity ${conv.severity_score || 1}</span>
            </div>
            <button class="btn btn-ghost btn-sm" id="escalateBtn">⚕️ Escalate to expert</button>
          </div>
          <div class="chat-body" id="chatBody"></div>
          <div class="chat-input">
            <div id="chatPreviewWrap"></div>
            <div class="chat-input-row">
              <button class="icon-btn" id="chatUploadBtn" title="Add photo">📎</button>
              <input type="file" id="chatFileInput" accept="image/*" hidden>
              <textarea id="chatText" rows="1" placeholder="Reply or share more details..."></textarea>
              <button class="btn btn-primary" id="chatSendBtn">Send</button>
            </div>
          </div>
        `;
    },

    messageBubble(role, data) {
        if (role === "user") {
            const img = data.image_data ? `<img src="${data.image_data}" class="msg-img" alt="">` : "";
            return `
              <div class="msg user">
                <div class="msg-avatar">You</div>
                <div class="msg-content">${img}${escapeHtml(data.content)}</div>
              </div>
            `;
        }
        // assistant — data is parsed result
        return this.assistantBubble(data);
    },

    assistantBubble(r) {
        const a = r.analysis || {};
        const conds = (a.top_conditions || []).map(c => `
          <div class="cond-row">
            <div>
              <div class="cond-name">${escapeHtml(c.name)}</div>
              ${c.why ? `<div class="cond-why">${escapeHtml(c.why)}</div>` : ''}
            </div>
            <div class="cond-conf">${Math.round(c.confidence_percent || 0)}%</div>
          </div>
        `).join("");

        const followups = (r.follow_up_questions || []).map(q =>
            `<span class="followup-chip" data-q="${escapeHtml(q)}">${escapeHtml(q)}</span>`
        ).join("");

        const urgent = a.needs_urgent_care || r.escalate_to_expert
            ? `<div class="urgent-banner"><strong>⚠ Recommend prompt care:</strong> ${escapeHtml(a.doctor_recommendation || 'This may warrant urgent evaluation.')}</div>`
            : "";

        const analysisBlock = conds ? `
          <div class="analysis-block">
            <h4>Possible matches <span class="sev-pill sev-${a.severity_score || 1}" style="margin-left: 0.4rem;">Sev ${a.severity_score || 1}</span></h4>
            ${conds}
          </div>
        ` : "";

        const nextSteps = (a.next_steps && a.next_steps.length) ? `
          <div class="analysis-block">
            <h4>Next steps</h4>
            <ul style="padding-left: 1.25rem; color: var(--text-dim); font-size: 0.9rem;">
              ${a.next_steps.map(s => `<li>${escapeHtml(s)}</li>`).join("")}
            </ul>
          </div>
        ` : "";

        const fuBlock = followups ? `
          <div class="followups">
            <h4 style="font-size: 0.78rem; text-transform: uppercase; color: var(--text-muted); margin-bottom: 0.5rem;">A few questions</h4>
            ${followups}
          </div>
        ` : "";

        return `
          <div class="msg assistant">
            <div class="msg-avatar">AI</div>
            <div class="msg-content">
              <div>${escapeHtml(r.message || '')}</div>
              ${analysisBlock}
              ${nextSteps}
              ${urgent}
              ${fuBlock}
            </div>
          </div>
        `;
    },

    newAnalysisModal() {
        return `
          <div class="modal-overlay" id="modalOverlay">
            <div class="modal">
              <h2>New skin analysis</h2>
              <p class="sub">Upload a clear, well-lit photo of the area.</p>
              <div class="upload-drop" id="uploadDrop">
                <div class="upload-icon">📸</div>
                <p><strong>Drag & drop</strong> or click to upload</p>
                <p style="color: var(--text-muted); font-size: 0.82rem; margin-top: 0.3rem;">PNG, JPG, WEBP — max 10MB</p>
                <input type="file" id="modalFile" accept="image/*" hidden>
              </div>
              <div id="modalPreview" hidden style="margin-top: 1rem;"></div>
              <div class="form-group mt-2">
                <label>Describe what you're noticing (optional)</label>
                <textarea name="text" rows="3" id="modalText" placeholder="E.g. new spot on my arm, noticed ~2 weeks ago, mildly itchy..."></textarea>
              </div>
              <div class="modal-actions">
                <button class="btn btn-ghost" id="modalCancel">Cancel</button>
                <button class="btn btn-primary" id="modalSubmit" disabled>Analyze</button>
              </div>
            </div>
          </div>
        `;
    },

    conditionsLibrary(conditions) {
        const cards = conditions.map(c => `
          <div class="cond-card" data-cond="${escapeHtml(c.key)}">
            <span class="cond-cat cat-${escapeHtml(c.category)}">${escapeHtml(c.category)}</span>
            <h3>${escapeHtml(c.name)}</h3>
            <p>${escapeHtml(c.short_description)}</p>
          </div>
        `).join("");
        return `
          <div class="section-title" style="margin-bottom: 1rem;">
            <h2>Condition library</h2>
            <p>Plain-language info on common skin conditions. Not a substitute for medical advice.</p>
          </div>
          <div class="library-grid">${cards}</div>
        `;
    },

    conditionDetail(c) {
        const list = (items) => items && items.length
            ? `<ul>${items.map(i => `<li>${escapeHtml(i)}</li>`).join("")}</ul>`
            : `<p>—</p>`;
        return `
          <a href="/conditions" data-link class="btn btn-ghost btn-sm" style="margin-bottom: 1rem;">← Back to library</a>
          <div class="cond-detail">
            <span class="cond-cat cat-${escapeHtml(c.category)}">${escapeHtml(c.category)}</span>
            <h1>${escapeHtml(c.name)}</h1>
            <p style="color: var(--text-dim); margin-bottom: 1rem;">${escapeHtml(c.short_description)}</p>
            ${c.prevalence ? `<span class="badge">${escapeHtml(c.prevalence)}</span>` : ''}
            <section class="mt-3"><h2>Overview</h2><p>${escapeHtml(c.overview)}</p></section>
            <section><h2>Typical appearance</h2><p>${escapeHtml(c.appearance)}</p></section>
            <section><h2>Common causes</h2>${list(c.causes)}</section>
            <section><h2>Symptoms</h2>${list(c.symptoms)}</section>
            <section><h2>Self-care</h2>${list(c.self_care)}</section>
            <section><h2>When to see a doctor</h2><p>${escapeHtml(c.when_to_see_doctor)}</p></section>
            <div class="urgent-banner"><strong>Reminder:</strong> This information is educational only and not a substitute for professional medical advice.</div>
          </div>
        `;
    },

    pricing(plans, currentPlan) {
        const order = ["free", "pro", "expert"];
        const cards = order.map(key => {
            const p = plans[key];
            const isCurrent = currentPlan === key;
            const featured = key === "pro";
            return `
              <div class="plan ${featured ? 'featured' : ''}">
                ${featured ? '<div class="plan-tag">Most popular</div>' : ''}
                <h3>${escapeHtml(p.name)}</h3>
                <div class="plan-price">$${p.price}<small>/month</small></div>
                <p style="color: var(--text-dim); font-size: 0.9rem;">
                  ${p.monthly_scans === -1 ? 'Unlimited scans' : `${p.monthly_scans} scans/month`}
                </p>
                <ul>${p.features.map(f => `<li>${escapeHtml(f)}</li>`).join("")}</ul>
                ${isCurrent
                    ? `<button class="btn btn-secondary btn-block" disabled>Current plan</button>`
                    : `<button class="btn btn-primary btn-block" data-plan="${key}">${currentPlan ? 'Switch plan' : 'Choose ' + p.name}</button>`
                }
              </div>
            `;
        }).join("");
        return `
          <div class="section-title">
            <h2>Simple, transparent pricing</h2>
            <p>Start free. Upgrade when you need more scans or expert access.</p>
          </div>
          <div class="pricing-grid">${cards}</div>
          <p class="text-center" style="color: var(--text-muted); font-size: 0.85rem;">
            Prices shown in USD. Cancel anytime. DermScan AI is not a medical device.
          </p>
        `;
    },

    expertsView(user, chats) {
        if (!user) {
            return `<div class="text-center"><h2>Sign in required</h2><p style="color:var(--text-dim)">Please sign in to access expert chat.</p><a class="btn btn-primary mt-2" href="/login" data-link>Sign in</a></div>`;
        }
        if (!user.expert_chat_enabled) {
            return `
              <div class="card text-center" style="max-width: 560px; margin: 3rem auto;">
                <div style="font-size: 3rem;">⚕️</div>
                <h2 style="margin: 1rem 0 0.5rem;">Expert chat is on Expert+</h2>
                <p style="color: var(--text-dim);">Chat directly with verified dermatologists for serious cases, including urgent escalations.</p>
                <a href="/pricing" data-link class="btn btn-primary mt-3">Upgrade to Expert+</a>
              </div>
            `;
        }
        const chatItems = chats.length === 0
            ? `<p style="color:var(--text-dim); font-size:0.88rem;">No chats yet. Start one below.</p>`
            : chats.map(c => `
                <div class="conv-item" data-chat-id="${c.id}">
                  <div class="conv-title">${escapeHtml(c.subject)}</div>
                  <div class="conv-meta">
                    <span class="sev-pill sev-${c.urgency === 'urgent' ? 5 : c.urgency === 'priority' ? 4 : 2}">${escapeHtml(c.urgency)}</span>
                    <span>${escapeHtml(c.assigned_expert || '').split(',')[0]}</span>
                  </div>
                </div>
              `).join("");
        return `
          <div class="expert-layout">
            <aside class="dash-sidebar">
              <button class="btn btn-primary btn-block" id="newExpertChat">+ New consultation</button>
              <div class="mt-3">
                <h3>Your consults</h3>
                <div id="expertList">${chatItems}</div>
              </div>
            </aside>
            <section class="dash-main" id="expertMain">
              <div class="dash-empty">
                <div style="font-size: 3rem;">⚕️</div>
                <h3>Expert consultations</h3>
                <p>Start a new chat with a verified dermatologist, or open an existing one from the left.</p>
              </div>
            </section>
          </div>
        `;
    },

    expertChat(chat, messages) {
        const bubbles = messages.map(m => {
            if (m.sender === "user") return `<div class="expert-msg user">${escapeHtml(m.content)}</div>`;
            if (m.sender === "expert") return `<div class="expert-msg expert">${escapeHtml(m.content)}</div>`;
            return `<div class="expert-msg system">${escapeHtml(m.content)}</div>`;
        }).join("");
        return `
          <div class="dash-header">
            <div>
              <h2>${escapeHtml(chat.subject)}</h2>
              <span class="badge">${escapeHtml(chat.assigned_expert || 'Dermatologist')}</span>
              <span class="sev-pill sev-${chat.urgency === 'urgent' ? 5 : chat.urgency === 'priority' ? 4 : 2}" style="margin-left:0.4rem;">${escapeHtml(chat.urgency)}</span>
            </div>
          </div>
          <div class="expert-chat-body" id="expertBody">${bubbles}</div>
          <div class="chat-input">
            <div class="chat-input-row">
              <textarea id="expertText" rows="1" placeholder="Type your message..."></textarea>
              <button class="btn btn-primary" id="expertSendBtn">Send</button>
            </div>
          </div>
        `;
    },

    newExpertChatModal(conversations) {
        const opts = (conversations || []).map(c => `<option value="${c.id}">${escapeHtml(c.title)}</option>`).join("");
        return `
          <div class="modal-overlay" id="modalOverlay">
            <div class="modal">
              <h2>Start an expert consultation</h2>
              <p class="sub">A verified dermatologist will review your case.</p>
              <div class="form-group">
                <label>Subject</label>
                <input type="text" id="expSubject" placeholder="e.g. Changing mole on my back">
              </div>
              <div class="form-group">
                <label>Urgency</label>
                <select id="expUrgency">
                  <option value="routine">Routine — within 24 hours</option>
                  <option value="priority">Priority — within a few hours</option>
                  <option value="urgent">Urgent — ASAP</option>
                </select>
              </div>
              <div class="form-group">
                <label>Link a previous AI scan (optional)</label>
                <select id="expConv"><option value="">— none —</option>${opts}</select>
              </div>
              <div class="modal-actions">
                <button class="btn btn-ghost" id="modalCancel">Cancel</button>
                <button class="btn btn-primary" id="expCreate">Start consultation</button>
              </div>
            </div>
          </div>
        `;
    },
};
