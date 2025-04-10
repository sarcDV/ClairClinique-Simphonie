import { initializeApp } from './app_initializer.js';

// Stato globale dell'applicazione
const APP_STATE = {
    isLoggedIn: false,
    currentUser: null,
  };
  
  // Gestore dell'interfaccia utente
  export const UIManager = {
    init: function () {
      this.attachEventListeners();
      this.checkLoginStatus();
    },
    attachEventListeners: function () {
      document.getElementById("welcomeLoginBtn").addEventListener("click", () => this.showScreen("login"));
      document.getElementById("welcomeRegisterBtn").addEventListener("click", () => this.showScreen("register"));
      document.getElementById("loginToRegisterBtn").addEventListener("click", () => this.showScreen("register"));
      document.getElementById("registerToLoginBtn").addEventListener("click", () => this.showScreen("login"));
      document.getElementById("logoutButton").addEventListener("click", AuthManager.logout.bind(AuthManager));
      document.getElementById("loginForm").addEventListener("submit", AuthManager.handleLogin.bind(AuthManager));
      document.getElementById("registerForm").addEventListener("submit", AuthManager.handleRegister.bind(AuthManager));
    },
    showScreen: function (screenName) {
      document.querySelectorAll("section[id$='Screen']").forEach((screen) => {
        screen.classList.add("hidden");
      });
      const screen = document.getElementById(screenName + "Screen");
      if (screen) {
        screen.classList.remove("hidden");
        // Initialize the app when the logged-in screen is shown
        if (screenName === "loggedIn") {
          initializeApp();
        }
      }
      document.getElementById("userInfo").classList.toggle("hidden", !APP_STATE.isLoggedIn);
    },
    checkLoginStatus: function () {
      const authData = localStorage.getItem("auth");
      if (authData) {
        const parsedAuthData = JSON.parse(authData);
        if (parsedAuthData.isLoggedIn && parsedAuthData.currentUser) {
          APP_STATE.isLoggedIn = true;
          APP_STATE.currentUser = parsedAuthData.currentUser;
          this.showScreen("loggedIn");
          return;
        }
      }
      this.showScreen("welcome");
    },
  };
  
  // Gestore dell'autenticazione
  const AuthManager = {
    handleLogin: function (e) {
      e.preventDefault();
      const email = document.getElementById("loginEmail").value.trim();
      const password = document.getElementById("loginPassword").value.trim();
      const users = JSON.parse(localStorage.getItem("users")) || [];
      const user = users.find((u) => u.email === email && u.password === password);
      if (!user) {
        alert("Email o password errati.");
        return;
      }
      APP_STATE.isLoggedIn = true;
      APP_STATE.currentUser = user;
      localStorage.setItem("auth", JSON.stringify({ isLoggedIn: true, currentUser: user }));
      UIManager.showScreen("loggedIn");
    },
    handleRegister: function (e) {
      e.preventDefault();
      const name = document.getElementById("registerName").value.trim();
      const email = document.getElementById("registerEmail").value.trim();
      const password = document.getElementById("registerPassword").value.trim();
      const confirmPassword = document.getElementById("confirmPassword").value.trim();
      if (!name || !email || !password || !confirmPassword) {
        alert("Completa tutti i campi.");
        return;
      }
      if (password !== confirmPassword) {
        alert("Le password non corrispondono.");
        return;
      }
      const users = JSON.parse(localStorage.getItem("users")) || [];
      const existingUser = users.find((u) => u.email === email);
      if (existingUser) {
        alert("L'email è già registrata.");
        return;
      }
      const newUser = { id: Date.now().toString(), name, email, password };
      users.push(newUser);
      localStorage.setItem("users", JSON.stringify(users));
      alert("Registrazione completata. Ora puoi accedere.");
      UIManager.showScreen("login");
    },
    logout: function () {
      APP_STATE.isLoggedIn = false;
      APP_STATE.currentUser = null;
      localStorage.removeItem("auth");
      UIManager.showScreen("welcome");
    },
  };
