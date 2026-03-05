import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";

const HELP_CONTENT = `
## What You Can Do

Ask me anything about weather in natural language. Here are the three core features:

---

### Current Weather
Get real-time weather conditions for any city.

**Try asking:**
- "What's the weather in New York?"
- "How hot is it in Dubai right now?"

**You'll get:** Temperature, feels-like temp, conditions, humidity, wind speed, pressure, and visibility.

---

### Multi-Day Forecast
Get a weather forecast for up to 5 days.

**Try asking:**
- "5-day forecast for London"
- "What will the weather be like in Paris this week?"

**You'll get:** Daily high/low temperatures, conditions, and average humidity.

---

### Air Quality
Check air pollution levels for any city.

**Try asking:**
- "How's the air quality in Los Angeles?"
- "Air pollution in Beijing"

**You'll get:** AQI rating (Good to Very Poor) plus pollutant levels (PM2.5, PM10, O3, NO2, CO).

| AQI | Rating | Meaning |
|-----|--------|---------|
| 1 | Good | Air quality is satisfactory |
| 2 | Fair | Acceptable for most people |
| 3 | Moderate | Sensitive groups may be affected |
| 4 | Poor | Health effects possible for everyone |
| 5 | Very Poor | Emergency conditions |

---

### Tips
- Ask about **multiple cities** in one message — e.g. "Compare weather in London and Paris"
- You can **combine features** — e.g. "Forecast and air quality for Berlin"
- City names are flexible — "NYC", "New York", and "New York City" all work
- All temperatures are in **Fahrenheit**
`;

export default function HelpPanel() {
  return (
    <div className="help-panel">
      <Markdown remarkPlugins={[remarkGfm]}>{HELP_CONTENT}</Markdown>
    </div>
  );
}
