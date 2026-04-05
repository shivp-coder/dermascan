// Main SPA controller
const App = {
    state: {
        user: null,
        conversations: [],
        activeConvId: null,
        pendingImage: null,
    },

    async init() {
        // Load user session
        try {
            const { user } = await API.me();
            this.state.user = user;
        } catch { this.state.user = null; }

        this.bindNav();
        this.renderAuthNav();
        window.addEventListener("popstate", () => this.route());
        this.route();
    },

    bindNav() {
        document.body.addEventListener("click", (e) => {
            const a = e.target.closest("a[data-link]");
            if (a) {
                e.preventDefault();
                this.navigate(a.getAttribute("href"));
            }
        });
        document.getElementById("navToggle").addEventListener("click", () => {
            document.getElementById("navLinks").classList.toggle("open");
        });
    },

    navigate(path) {
        history.pushState(null, "", path);
        document.getElementById("navLinks").classList.remove("open");
        this.route();
    },

    renderAuthNav() {
        const el = document.getElementById("navAuth");
        if (this.state.user) {
            el.innerHTML = `
              <a href="/dashboard" data-link>Dashboard</a>
              <a href="/experts" data-link>Experts</a>
              <button class="btn btn-ghost btn-sm" id="logoutBtn">Sign out</button>
            `;
            document.getElementById("logoutBtn").onclick = async () => {
                await API.logout();
                this.state.user = null;
                this.renderAuthNav();
                this.navigate("/");
            };
        } else {
            el.innerHTML = `
              <a href="/login" data-link>Sign in</a>
              <a href="/signup" data-link class="btn btn-primary btn-sm">Get started</a>
            `;
        }
    },

    async route() {
        const path = location.pathname;
        const app = document.getElementById("app");
        app.className = "app";

        // Mark active nav
        document.querySelectorAll(".nav-links a").forEach(a => {
            a.classList.toggle("active", a.getAttribute("href") === path);
        });

        if (path === "/" || path === "") {
            app.innerHTML = Views.landing();
            return;
        }
        if (path === "/login") {
            if (this.state.user) return this.navigate("/dashboard");
            app.className = "app narrow";
            app.innerHTML = Views.login();
            this.bindLogin();
            return;
        }
        if (path === "/signup") {
            if (this.state.user) return this.navigate("/dashboard");
            app.className = "app narrow";
            app.innerHTML = Views.signup();
            this.bindSignup();
            return;
        }
        if (path === "/dashboard") {
            if (!this.state.user) return this.navigate("/login");
            await this.renderDashboard();
            return;
        }
        if (path === "/conditions") {
            await this.renderConditions();
            return;
        }
        if (path.startsWith("/conditions/")) {
            await this.renderConditionDetail(path.split("/")[2]);
            return;
        }
        if (path === "/pricing") {
            await this.renderPricing();
            return;
        }
        if (path === "/experts") {
            if (!this.state.user) return this.navigate("/login");
            await this.renderExperts();
            return;
        }
        app.innerHTML = `<div class="text-center" style="padding: 4rem;"><h1>404</h1><p>Page not found</p></div>`;
    },

    // AUTH
    bindLogin() {
        document.getElementById("loginForm").onsubmit = async (e) => {
            e.preventDefault();
            const fd = new FormData(e.target);
            try {
                const { user } = await API.login(fd.get("email"), fd.get("password"));
                this.state.user = user;
                this.renderAuthNav();
                this.navigate("/dashboard");
            } catch (err) {
                document.getElementById("loginErr").textContent = err.message;
            }
        };
    },

    bindSignup() {
        document.getElementById("signupForm").onsubmit = async (e) => {
            e.preventDefault();
            const fd = new FormData(e.target);
            try {
                const { user } = await API.signup(fd.get("name"), fd.get("email"), fd.get("password"));
                this.state.user = user;
                this.renderAuthNav();
                this.navigate("/dashboard");
            } catch (err) {
                document.getElementById("signupErr").textContent = err.message;
            }
        };
    },

    // DASHBOARD
    async renderDashboard() {
        const app = document.getElementById("app");
        app.className = "app wide";
        try {
            const { conversations } = await API.listConversations();
            this.state.conversations = conversations;
        } catch { this.state.conversations = []; }
        app.innerHTML = Views.dashboardShell(this.state.user, this.state.conversations);
        this.bindDashboard();
    },

    bindDashboard() {
        document.getElementById("newAnalysisBtn").onclick = () => this.openNewAnalysisModal();
        const emptyBtn = document.getElementById("emptyNewBtn");
        if (emptyBtn) emptyBtn.onclick = () => this.openNewAnalysisModal();
        document.querySelectorAll(".conv-item[data-conv-id]").forEach(el => {
            el.onclick = () => this.openConversation(parseInt(el.dataset.convId));
        });
    },

    async openConversation(convId) {
        this.state.activeConvId = convId;
        document.querySelectorAll(".conv-item").forEach(el => {
            el.classList.toggle("active", parseInt(el.dataset.convId) === convId);
        });
        const main = document.getElementById("dashMain");
        main.innerHTML = `<div class="spinner"></div>`;
        try {
            const { conversation, messages } = await API.getConversation(convId);
            main.innerHTML = Views.conversationView(conversation);
            const body = document.getElementById("chatBody");
            body.innerHTML = messages.map(m => {
                if (m.role === "user") {
                    return Views.messageBubble("user", { content: m.content, image_data: m.image_data });
                }
                try {
                    const parsed = JSON.parse(m.content);
                    return Views.assistantBubble(parsed);
                } catch {
                    return Views.messageBubble("assistant", { message: m.content, analysis: {} });
                }
            }).join("");
            body.scrollTop = body.scrollHeight;
            this.bindChat();
        } catch (err) {
            toast(err.message, "error");
        }
    },

    bindChat() {
        const input = document.getElementById("chatText");
        const sendBtn = document.getElementById("chatSendBtn");
        const uploadBtn = document.getElementById("chatUploadBtn");
        const fileInput = document.getElementById("chatFileInput");

        uploadBtn.onclick = () => fileInput.click();
        fileInput.onchange = () => {
            if (fileInput.files[0]) {
                this.state.pendingImage = fileInput.files[0];
                const wrap = document.getElementById("chatPreviewWrap");
                const reader = new FileReader();
                reader.onload = e => {
                    wrap.innerHTML = `
                      <div class="chat-preview">
                        <img src="${e.target.result}" alt="">
                        <span>${fileInput.files[0].name}</span>
                        <button class="btn btn-ghost btn-sm" id="clearPreview">✕</button>
                      </div>
                    `;
                    document.getElementById("clearPreview").onclick = () => {
                        this.state.pendingImage = null;
                        wrap.innerHTML = "";
                        fileInput.value = "";
                    };
                };
                reader.readAsDataURL(fileInput.files[0]);
            }
        };

        input.addEventListener("keydown", (e) => {
            if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                sendBtn.click();
            }
        });

        sendBtn.onclick = () => this.sendFollowUp();

        // Follow-up chips
        document.querySelectorAll(".followup-chip").forEach(chip => {
            chip.onclick = () => {
                input.value = chip.dataset.q;
                input.focus();
            };
        });

        // Escalate to expert
        const escalateBtn = document.getElementById("escalateBtn");
        if (escalateBtn) {
            escalateBtn.onclick = () => {
                if (!this.state.user.expert_chat_enabled) {
                    toast("Expert chat requires the Expert+ plan", "error");
                    setTimeout(() => this.navigate("/pricing"), 800);
                    return;
                }
                this.navigate("/experts");
            };
        }
    },

    async sendFollowUp() {
        const input = document.getElementById("chatText");
        const text = input.value.trim();
        if (!text && !this.state.pendingImage) return;

        const body = document.getElementById("chatBody");
        // Optimistic user bubble
        let userImgData = null;
        if (this.state.pendingImage) {
            userImgData = await this.fileToDataUrl(this.state.pendingImage);
        }
        body.insertAdjacentHTML("beforeend",
            Views.messageBubble("user", { content: text, image_data: userImgData }));
        body.insertAdjacentHTML("beforeend",
            `<div class="msg assistant"><div class="msg-avatar">AI</div><div class="msg-content typing"><span></span><span></span><span></span></div></div>`);
        body.scrollTop = body.scrollHeight;
        input.value = "";

        try {
            let result;
            if (this.state.pendingImage) {
                const fd = new FormData();
                fd.append("text", text);
                fd.append("image", this.state.pendingImage);
                const resp = await API.sendFollowUp(this.state.activeConvId, fd);
                result = resp.result;
            } else {
                const resp = await API.sendFollowUpText(this.state.activeConvId, text);
                result = resp.result;
            }
            // Replace typing indicator
            const typing = body.querySelector(".msg.assistant:last-child");
            typing.outerHTML = Views.assistantBubble(result);
            body.scrollTop = body.scrollHeight;
            // Re-bind chips
            document.querySelectorAll(".followup-chip").forEach(chip => {
                chip.onclick = () => { input.value = chip.dataset.q; input.focus(); };
            });
        } catch (err) {
            const typing = body.querySelector(".msg.assistant:last-child");
            if (typing) typing.remove();
            toast(err.message, "error");
        }

        // Clear pending image
        this.state.pendingImage = null;
        const wrap = document.getElementById("chatPreviewWrap");
        if (wrap) wrap.innerHTML = "";
    },

    fileToDataUrl(file) {
        return new Promise(resolve => {
            const r = new FileReader();
            r.onload = e => resolve(e.target.result);
            r.readAsDataURL(file);
        });
    },

    // NEW ANALYSIS MODAL
    openNewAnalysisModal() {
        document.body.insertAdjacentHTML("beforeend", Views.newAnalysisModal());
        const overlay = document.getElementById("modalOverlay");
        const drop = document.getElementById("uploadDrop");
        const fileInput = document.getElementById("modalFile");
        const preview = document.getElementById("modalPreview");
        const submit = document.getElementById("modalSubmit");
        let selectedFile = null;

        const close = () => overlay.remove();
        document.getElementById("modalCancel").onclick = close;
        overlay.onclick = e => { if (e.target === overlay) close(); };

        drop.onclick = () => fileInput.click();
        ["dragover", "dragenter"].forEach(ev => {
            drop.addEventListener(ev, e => { e.preventDefault(); drop.classList.add("drag"); });
        });
        ["dragleave", "drop"].forEach(ev => {
            drop.addEventListener(ev, e => { e.preventDefault(); drop.classList.remove("drag"); });
        });
        drop.addEventListener("drop", e => {
            const file = e.dataTransfer.files[0];
            if (file) handleFile(file);
        });
        fileInput.onchange = () => { if (fileInput.files[0]) handleFile(fileInput.files[0]); };

        const handleFile = (file) => {
            selectedFile = file;
            const r = new FileReader();
            r.onload = e => {
                preview.innerHTML = `<img src="${e.target.result}" style="max-width: 100%; max-height: 280px; border-radius: var(--radius-sm);">`;
                preview.hidden = false;
            };
            r.readAsDataURL(file);
            submit.disabled = false;
        };

        submit.onclick = async () => {
            if (!selectedFile) return;
            submit.disabled = true;
            submit.textContent = "Analyzing...";
            const fd = new FormData();
            fd.append("image", selectedFile);
            fd.append("text", document.getElementById("modalText").value);
            try {
                const { conversation_id } = await API.startAnalysis(fd);
                close();
                // Refresh user (scan count) and list
                const { user } = await API.me();
                this.state.user = user;
                await this.renderDashboard();
                await this.openConversation(conversation_id);
            } catch (err) {
                toast(err.message, "error");
                submit.disabled = false;
                submit.textContent = "Analyze";
            }
        };
    },

    // CONDITIONS LIBRARY
    async renderConditions() {
        const app = document.getElementById("app");
        app.innerHTML = `<div class="spinner"></div>`;
        try {
            const { conditions } = await API.listConditions();
            app.innerHTML = Views.conditionsLibrary(conditions);
            document.querySelectorAll(".cond-card").forEach(el => {
                el.onclick = () => this.navigate("/conditions/" + el.dataset.cond);
            });
        } catch (err) {
            toast(err.message, "error");
        }
    },

    async renderConditionDetail(key) {
        const app = document.getElementById("app");
        app.innerHTML = `<div class="spinner"></div>`;
        try {
            const { condition } = await API.getCondition(key);
            app.innerHTML = Views.conditionDetail(condition);
        } catch (err) {
            toast(err.message, "error");
            this.navigate("/conditions");
        }
    },

    // PRICING
    async renderPricing() {
        const app = document.getElementById("app");
        app.innerHTML = `<div class="spinner"></div>`;
        try {
            const { plans } = await API.plans();
            const currentPlan = this.state.user ? this.state.user.plan : null;
            app.innerHTML = Views.pricing(plans, currentPlan);
            document.querySelectorAll("button[data-plan]").forEach(btn => {
                btn.onclick = async () => {
                    if (!this.state.user) return this.navigate("/signup");
                    try {
                        const { user } = await API.changePlan(btn.dataset.plan);
                        this.state.user = user;
                        toast(`Switched to ${user.plan_name}`, "success");
                        this.renderAuthNav();
                        this.renderPricing();
                    } catch (err) { toast(err.message, "error"); }
                };
            });
        } catch (err) { toast(err.message, "error"); }
    },

    // EXPERTS
    async renderExperts() {
        const app = document.getElementById("app");
        app.className = "app wide";
        let chats = [];
        if (this.state.user && this.state.user.expert_chat_enabled) {
            try { chats = (await API.listExpertChats()).chats; } catch { chats = []; }
        }
        app.innerHTML = Views.expertsView(this.state.user, chats);
        this.bindExperts();
    },

    bindExperts() {
        const btn = document.getElementById("newExpertChat");
        if (btn) btn.onclick = () => this.openNewExpertChatModal();
        document.querySelectorAll(".conv-item[data-chat-id]").forEach(el => {
            el.onclick = () => this.openExpertChat(parseInt(el.dataset.chatId));
        });
    },

    async openNewExpertChatModal() {
        let conversations = [];
        try { conversations = (await API.listConversations()).conversations; } catch {}
        document.body.insertAdjacentHTML("beforeend", Views.newExpertChatModal(conversations));
        const overlay = document.getElementById("modalOverlay");
        const close = () => overlay.remove();
        document.getElementById("modalCancel").onclick = close;
        overlay.onclick = e => { if (e.target === overlay) close(); };
        document.getElementById("expCreate").onclick = async () => {
            const subject = document.getElementById("expSubject").value.trim();
            const urgency = document.getElementById("expUrgency").value;
            const conv_id = document.getElementById("expConv").value;
            if (!subject) return toast("Subject required", "error");
            try {
                const { chat_id } = await API.createExpertChat({
                    subject, urgency,
                    conversation_id: conv_id ? parseInt(conv_id) : null,
                });
                close();
                await this.renderExperts();
                await this.openExpertChat(chat_id);
            } catch (err) { toast(err.message, "error"); }
        };
    },

    async openExpertChat(chatId) {
        const main = document.getElementById("expertMain");
        main.innerHTML = `<div class="spinner"></div>`;
        try {
            const { chat, messages } = await API.getExpertChat(chatId);
            main.innerHTML = Views.expertChat(chat, messages);
            this.bindExpertChatInput(chatId);
            const body = document.getElementById("expertBody");
            body.scrollTop = body.scrollHeight;
        } catch (err) { toast(err.message, "error"); }
    },

    bindExpertChatInput(chatId) {
        const input = document.getElementById("expertText");
        const btn = document.getElementById("expertSendBtn");
        const send = async () => {
            const text = input.value.trim();
            if (!text) return;
            const body = document.getElementById("expertBody");
            body.insertAdjacentHTML("beforeend", `<div class="expert-msg user">${escapeHtml(text)}</div>`);
            input.value = "";
            body.scrollTop = body.scrollHeight;
            try {
                await API.sendExpertMessage(chatId, text);
                const { messages } = await API.getExpertChat(chatId);
                const last = messages[messages.length - 1];
                if (last.sender !== "user") {
                    body.insertAdjacentHTML("beforeend",
                        `<div class="expert-msg ${last.sender}">${escapeHtml(last.content)}</div>`);
                    body.scrollTop = body.scrollHeight;
                }
            } catch (err) { toast(err.message, "error"); }
        };
        btn.onclick = send;
        input.addEventListener("keydown", e => {
            if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); }
        });
    },
};

document.addEventListener("DOMContentLoaded", () => App.init());
