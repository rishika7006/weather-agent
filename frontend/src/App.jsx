import ChatInterface from "./components/ChatInterface";
import "./App.css";

function App() {
  return (
    <div className="app">
      <header className="header">
        <span className="header-icon">{"\u26C5"}</span>
        <div>
          <h1>Weather Agent</h1>
          <p>Powered by LangChain + OpenWeatherMap</p>
        </div>
      </header>
      <ChatInterface />
    </div>
  );
}

export default App;
