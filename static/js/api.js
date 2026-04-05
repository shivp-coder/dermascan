// Lightweight fetch wrapper for DermScan API
const API = {
    async request(path, opts = {}) {
        const res = await fetch(path, {
            credentials: "same-origin",
            ...opts,
            headers: {
                ...(opts.body instanceof FormData ? {} : { "Content-Type": "application/json" }),
                ...(opts.headers || {}),
            },
        });
        let data;
        try { data = await res.json(); } catch { data = {}; }
        if (!res.ok) {
            const err = new Error(data.error || `Request failed (${res.status})`);
            err.status = res.status;
            err.code = data.code;
            throw err;
        }
        return data;
    },
    get(p)         { return this.request(p); },
    post(p, body)  { return this.request(p, { method: "POST", body: JSON.stringify(body) }); },
    postForm(p, fd){ return this.request(p, { method: "POST", body: fd }); },

    // Auth
    me()                     { return this.get("/api/auth/me"); },
    login(email, password)   { return this.post("/api/auth/login", { email, password }); },
    signup(name, email, password) { return this.post("/api/auth/signup", { name, email, password }); },
    logout()                 { return this.post("/api/auth/logout", {}); },
    changePlan(plan)         { return this.post("/api/auth/plan", { plan }); },

    // Plans
    plans()                  { return this.get("/api/plans"); },

    // Analysis
    listConversations()      { return this.get("/api/analysis/conversations"); },
    getConversation(id)      { return this.get(`/api/analysis/conversations/${id}`); },
    startAnalysis(fd)        { return this.postForm("/api/analysis/start", fd); },
    sendFollowUp(id, fd)     { return this.postForm(`/api/analysis/conversations/${id}/message`, fd); },
    sendFollowUpText(id, text) {
        return this.post(`/api/analysis/conversations/${id}/message`, { text });
    },

    // Conditions library
    listConditions()         { return this.get("/api/conditions"); },
    getCondition(key)        { return this.get(`/api/conditions/${key}`); },

    // Expert chat
    listExpertChats()        { return this.get("/api/expert/chats"); },
    createExpertChat(body)   { return this.post("/api/expert/chats", body); },
    getExpertChat(id)        { return this.get(`/api/expert/chats/${id}`); },
    sendExpertMessage(id, content) {
        return this.post(`/api/expert/chats/${id}/message`, { content });
    },
};

function toast(msg, kind = "") {
    const el = document.getElementById("toast");
    el.textContent = msg;
    el.className = "toast " + kind;
    el.hidden = false;
    clearTimeout(toast._t);
    toast._t = setTimeout(() => { el.hidden = true; }, 3600);
}

function escapeHtml(t) {
    if (t == null) return "";
    const d = document.createElement("div");
    d.textContent = String(t);
    return d.innerHTML;
}
