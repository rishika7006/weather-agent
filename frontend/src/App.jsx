import { useState } from "react";
import ChatInterface from "./components/ChatInterface";
import HelpPanel from "./components/HelpPanel";
import ArchitecturePanel from "./components/ArchitecturePanel";
import AgentPanel from "./components/AgentPanel";
import ExperiencePanel from "./components/ExperiencePanel";
import ImprovementsPanel from "./components/ImprovementsPanel";
import DeploymentPanel from "./components/DeploymentPanel";
import "./App.css";

function App() {
  const [activeTab, setActiveTab] = useState("chat");

  return (
    <div className="app">
      <header className="header">
        <div className="header-top">
          <span className="header-icon">{"\u26C5"}</span>
          <div className="header-text">
            <h1>Weather Agent</h1>
            <p>Powered by LangChain + OpenWeatherMap</p>
          </div>
        </div>
        <nav className="header-tabs">
          <button
            className={`tab-btn ${activeTab === "chat" ? "active" : ""}`}
            onClick={() => setActiveTab("chat")}
          >
            Chat
          </button>
          <button
            className={`tab-btn ${activeTab === "help" ? "active" : ""}`}
            onClick={() => setActiveTab("help")}
          >
            Help
          </button>
          <button
            className={`tab-btn ${activeTab === "architecture" ? "active" : ""}`}
            onClick={() => setActiveTab("architecture")}
          >
            Architecture
          </button>
          <button
            className={`tab-btn ${activeTab === "agent" ? "active" : ""}`}
            onClick={() => setActiveTab("agent")}
          >
            Agent
          </button>
          <button
            className={`tab-btn ${activeTab === "experience" ? "active" : ""}`}
            onClick={() => setActiveTab("experience")}
          >
            Experience
          </button>
          <button
            className={`tab-btn ${activeTab === "improvements" ? "active" : ""}`}
            onClick={() => setActiveTab("improvements")}
          >
            Improvements
          </button>
          <button
            className={`tab-btn ${activeTab === "deployment" ? "active" : ""}`}
            onClick={() => setActiveTab("deployment")}
          >
            Deployment
          </button>
        </nav>
      </header>
      {activeTab === "chat" && <ChatInterface />}
      {activeTab === "help" && <HelpPanel />}
      {activeTab === "architecture" && <ArchitecturePanel />}
      {activeTab === "agent" && <AgentPanel />}
      {activeTab === "experience" && <ExperiencePanel />}
      {activeTab === "improvements" && <ImprovementsPanel />}
      {activeTab === "deployment" && <DeploymentPanel />}
    </div>
  );
}

export default App;
