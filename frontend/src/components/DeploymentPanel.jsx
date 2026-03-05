import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";

const DEPLOYMENT_CONTENT = `
## Deployment Discussion

This application has three independent services — the React frontend, the Agent backend, and the MCP Server. Here's how each deployment strategy would work and when to pick it.

---

### Option 1: Docker + Docker Compose

The simplest path from local development to a hosted environment.

**How it would work:**
- Each service gets its own \`Dockerfile\` (Node for frontend, Python for backend and MCP Server)
- A single \`docker-compose.yml\` orchestrates all three containers
- Environment variables (\`ANTHROPIC_API_KEY\`, \`OPENWEATHER_API_KEY\`) are injected via \`.env\` or secrets
- The frontend container serves a production build via Nginx
- Internal networking lets the backend reach the MCP Server by container name

**Example structure:**
\`\`\`
docker-compose.yml
├── frontend/Dockerfile      # Node build → Nginx serve
├── backend/Dockerfile       # Python + uvicorn
└── mcp-server/Dockerfile    # Python + uvicorn
\`\`\`

| Pros | Cons |
|------|------|
| One command to start everything (\`docker compose up\`) | Limited to a single host — no auto-scaling |
| Mirrors local dev closely | Manual restart on failure (unless using restart policies) |
| Easy to share and reproduce | Not suitable for high-traffic production |
| Works on any machine with Docker | |

**Best for:** Development, demos, small team deployments, single-server hosting.

---

### Option 2: Kubernetes

For production-grade deployments with high availability and scaling needs.

**How it would work:**
- Each service is a **Deployment** with its own **Pod** spec and container image
- The MCP Server and Agent Backend are **ClusterIP Services** (internal only)
- The frontend is exposed via an **Ingress** controller with TLS termination
- API keys are stored in **Kubernetes Secrets**
- **Horizontal Pod Autoscalers (HPA)** scale the MCP Server and backend based on CPU/request load

**Kubernetes resources per service:**

| Resource | Frontend | Agent Backend | MCP Server |
|----------|----------|---------------|------------|
| Deployment | 1 | 1 | 1 |
| Service | Ingress (public) | ClusterIP (internal) | ClusterIP (internal) |
| HPA | Optional | Yes | Yes |
| ConfigMap | Nginx config | Env vars | Env vars |
| Secret | — | Anthropic API key | OpenWeather API key |

**Scaling considerations:**
- The **MCP Server** is stateless and lightweight — scales easily to handle many concurrent weather API calls
- The **Agent Backend** is the bottleneck since each request involves an LLM call; scaling helps with concurrent users but costs increase with Anthropic API usage
- The **Frontend** is static files — a CDN or a single replica with caching is usually sufficient

| Pros | Cons |
|------|------|
| Auto-scaling and self-healing | Significant operational complexity |
| Rolling deployments with zero downtime | Requires Kubernetes expertise |
| Service discovery built in | Overkill for small-scale use |
| Works across cloud providers (EKS, GKE, AKS) | Cluster costs even at low traffic |

**Best for:** Production workloads, teams with Kubernetes experience, multi-region deployments.

---

### Option 3: Serverless

Minimize infrastructure management by running each service as a function.

**How it would work:**
- **Frontend** → Static build deployed to **S3 + CloudFront** (or Vercel/Netlify)
- **Agent Backend** → **AWS Lambda** behind **API Gateway**, triggered per chat request
- **MCP Server** → **AWS Lambda** behind **API Gateway**, triggered per weather API call
- API keys stored in **AWS Secrets Manager** or environment variables on the Lambda

**Architecture on AWS:**
\`\`\`
CloudFront (CDN)
  └── S3 (React build)

API Gateway
  ├── POST /api/chat     → Lambda (Agent Backend)
  └── GET  /api/weather/* → Lambda (MCP Server)
\`\`\`

**Cold start considerations:**
- Python Lambdas with LangChain dependencies can have **3-8 second cold starts**
- The Agent Backend is especially heavy due to LangChain + Anthropic SDK imports
- Mitigations: **Provisioned Concurrency**, or keeping the agent backend as a long-running container (ECS/Fargate) instead

| Pros | Cons |
|------|------|
| Zero cost at zero traffic (pay per request) | Cold starts hurt latency for the agent |
| No servers to manage or patch | Large dependency bundles for Python Lambdas |
| Auto-scales to any load | Harder to debug locally |
| Built-in monitoring via CloudWatch | 15-minute max execution time per request |

**Best for:** Variable/unpredictable traffic, cost-sensitive deployments, teams already on AWS.

---

### Option 4: Hybrid Approach (Recommended)

Combine strategies based on each service's characteristics.

| Service | Strategy | Reason |
|---------|----------|--------|
| Frontend | **S3 + CDN** (CloudFront, Vercel, or Netlify) | Static files, globally distributed, near-zero cost |
| Agent Backend | **Container** (ECS Fargate or Cloud Run) | Avoids cold starts, scales on demand, handles LLM latency well |
| MCP Server | **Serverless** (Lambda or Cloud Function) | Lightweight, stateless, fast cold starts, cheap at scale |

This gives you the best of each world — fast frontend delivery, reliable agent responses, and cost-efficient weather API calls.

---

### Environment & Secrets Management

Regardless of deployment strategy, API keys should never be in code or images:

| Strategy | Where to store secrets |
|----------|----------------------|
| Docker Compose | \`.env\` file (not committed) or Docker secrets |
| Kubernetes | \`kubectl create secret\` / sealed-secrets / external-secrets |
| Serverless | AWS Secrets Manager, SSM Parameter Store, or Lambda env vars (encrypted) |
| Hybrid | Match each service to its platform's secret management |
`;

export default function DeploymentPanel() {
  return (
    <div className="help-panel">
      <Markdown remarkPlugins={[remarkGfm]}>{DEPLOYMENT_CONTENT}</Markdown>
    </div>
  );
}
