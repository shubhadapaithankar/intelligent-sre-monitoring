# 🤖 SRE Guardian — AI-Powered Anomaly Detection for Kubernetes

> **Turn your Prometheus metrics into intelligent alerts with AI-powered root cause analysis**

**Instead of getting 100 generic CPU/memory alerts, get 3 smart alerts like:**
- *"Pod `svc-leak-777` has a memory leak - suggest rolling restart"*
- *"Pod `svc-noisy-555` is a noisy neighbor causing throttling - suggest scaling"*  
- *"Latency drift detected in `api-gateway` - SLO at risk"*

## 🚀 **30-Second Demo (No Setup Required)**

```bash
# 1. Run with synthetic data (no Kubernetes/Prometheus needed!)
docker run --rm -p 8080:8080 -e DEMO_MODE=true sre-guardian

# 2. See AI-powered anomaly detection in action
curl "http://localhost:8080/anomalies?top_k=3" | jq
```

**Example Output:**
```json
{
  "anomalies": [
    {
      "namespace": "prod",
      "pod": "svc-noisy-555", 
      "anomaly_score": 0.999,
      "rca": {
        "reasons": ["CPU throttling indicative of CPU pressure"],
        "suggested_actions": [{"action": "k8s.scale", "reason": "Increase CPU/share"}]
      }
    }
  ]
}
```

**🎭 Demo Mode Magic:** Uses realistic synthetic data to simulate memory leaks, noisy neighbors, and SLO drift - **perfect for exploration and demos!**

---

## 🚨 **Problems This Solves**

### **Before: Alert Fatigue Hell**
```
🔥 CPU > 80% on pod-1234    🔥 Memory > 90% on pod-5678
🔥 CPU > 80% on pod-2345    🔥 Memory > 90% on pod-7890  
🔥 CPU > 80% on pod-3456    🔥 Memory > 90% on pod-8901
... 47 more alerts ...
```
*Result: Team ignores alerts, misses real issues*

### **After: Smart AI Insights**  
```
🎯 3 real anomalies detected:
   • svc-leak-777: Memory leak → Restart suggested
   • svc-noisy-555: Noisy neighbor → Scale up  
   • api-gateway: SLO drift → Investigate latency
```
*Result: Team focuses on actual problems with clear solutions*

## ✨ **Key Features**
- 🧠 **AI-Powered Detection** - Learns what's "normal" for each service
- 🔍 **Root Cause Analysis** - Explains WHY something is anomalous  
- 🛠️ **Actionable Suggestions** - Recommends specific fixes
- 🎭 **Demo Mode** - Try it without any infrastructure setup
- 🛡️ **Safe by Default** - Dry-run mode prevents accidents
- 🔄 **Multi-Platform** - Kubernetes AND Podman support

---

## 🏗 Architecture

```
Prometheus --> Collector --> Featureizer --> IsolationForest scoring
                                   |                 |
                                   v                 v
                          RCA & Suggestions --> FastAPI (/anomalies, /suggest, /act)
                                     ^
                                   (CLI/UI)
```

---

## 🎮 **Try It Now - Multiple Ways**

### **Option 1: Instant Demo (Recommended for First-Time Users)**
```bash
# No setup required - runs with synthetic data
docker run --rm -p 8080:8080 -e DEMO_MODE=true sre-guardian

# Then explore the API
curl http://localhost:8080/healthz
curl "http://localhost:8080/anomalies?top_k=5" | jq
```

### **Option 2: Connect to Your Prometheus** 
```bash
docker run --rm -p 8080:8080 \
  -e PROM_URL=http://your-prometheus:9090 \
  -e NAMESPACE=your-namespace \
  sre-guardian
```

### **Option 3: Local Development**
```bash
pip install -r requirements.txt

# For demo with synthetic data (no infrastructure needed)
export DEMO_MODE=true
export K8S_IN_CLUSTER=false
python main.py

# OR for connecting to real Prometheus locally
export DEMO_MODE=false
export PROM_URL=http://localhost:9090
export K8S_IN_CLUSTER=false
python main.py
```

### **Option 4: Production Kubernetes**
```bash
# Build and push to your registry
docker build -t your-registry/sre-guardian:latest .
docker push your-registry/sre-guardian:latest

# Deploy to Kubernetes cluster
kubectl apply -f deploy/k8s-manifests.yaml

# Check deployment
kubectl -n nn-slo get pods
kubectl -n nn-slo port-forward svc/nn-slo 8080:80

# Access the service
curl http://localhost:8080/healthz
```

**Note**: Update the image reference in `deploy/k8s-manifests.yaml` to point to your registry before deploying.

## 🎭 **What Happens in Demo Mode?**

Demo mode creates **4 realistic synthetic services** that simulate real SRE problems:

| Service | Behavior | AI Detection |
|---------|----------|--------------|
| `svc-a-123` | Normal, healthy service | ✅ Low anomaly score |
| `svc-b-999` | Normal, healthy service | ✅ Low anomaly score | 
| `svc-leak-777` | **Memory leak** (gradual increase) | 🚨 Medium score → "Memory leak detected" |
| `svc-noisy-555` | **Noisy neighbor** (CPU spikes, throttling) | 🔥 High score → "CPU pressure, affects others" |

**Perfect for:** Demos, testing, understanding the AI without real infrastructure!

## 🎯 **Who Is This For?**

- **🛠️ SRE Teams** - Reduce alert fatigue, catch issues proactively
- **📊 Platform Engineers** - Add intelligent monitoring to your infrastructure  
- **👩‍💻 DevOps Engineers** - Get better visibility into application health
- **🏢 Engineering Managers** - Understand SRE problems without vendor lock-in
- **🎓 Students/Learners** - See modern AI applied to operations

## 📋 **Common Use Cases**

### **Memory Leak Detection**
```bash
# AI identifies gradual memory increases before OOM kills
"Memory increasing over time (possible leak)" → Suggest restart
```

### **Noisy Neighbor Identification** 
```bash
# Find services affecting others through CPU/throttling
"CPU throttling indicative of CPU pressure" → Suggest scaling
```

### **SLO Drift Prevention**
```bash
# Catch latency degradation before SLO violations  
"p95 latency above target (SLO drift)" → Investigate performance
```

### **Container Restart Loop Detection**
```bash
# Identify crashlooping containers automatically
"Container restarted recently (possible crashloop)" → Debug pod
```

## 📊 **What You'll See**

### **Healthy Service (Low Score)**
```json
{
  "namespace": "prod",
  "pod": "svc-a-123", 
  "container": "app",
  "anomaly_score": 0.116,
  "rca": {
    "reasons": ["Generic anomaly detected"],
    "suggested_actions": [{"action": "none", "reason": "Monitor only"}]
  }
}
```

### **Memory Leak (Medium Score)**
```json
{
  "namespace": "prod", 
  "pod": "svc-leak-777",
  "container": "app", 
  "anomaly_score": 0.441,
  "rca": {
    "reasons": ["Memory increasing over time (possible leak)"],
    "suggested_actions": [{"action": "k8s.roll_restart", "reason": "Reset memory footprint"}]
  }
}
```

### **Noisy Neighbor (High Score)**
```json
{
  "namespace": "prod",
  "pod": "svc-noisy-555",
  "container": "app", 
  "anomaly_score": 0.999,
  "rca": {
    "reasons": ["Memory increasing over time (possible leak)"],
    "suggested_actions": [{"action": "k8s.roll_restart", "reason": "Reset memory footprint"}]
  }
}
```

## ❓ **Frequently Asked Questions**

### **Q: Do I need Kubernetes or Prometheus to try this?**
**A:** Nope! Use `DEMO_MODE=true` to run with realistic synthetic data. Perfect for exploration.

### **Q: Will this break my cluster?** 
**A:** No! Dry-run mode is enabled by default. All actions are simulated unless you explicitly disable it.

### **Q: How is this different from regular Prometheus alerts?**
**A:** Traditional alerts use static thresholds (CPU > 80%). This uses AI to learn what's normal for each service and only alerts on genuine anomalies.

### **Q: What if I don't have SRE/DevOps experience?**
**A:** The demo mode is perfect for learning! It shows realistic problems and explains them in plain English.

### **Q: Can I use this with my existing monitoring?**
**A:** Yes! It reads from your Prometheus and provides an additional intelligence layer. It doesn't replace your existing tools.

---

## 🐳 Docker Guide

### Building the Image
```bash
# Build with default settings
docker build -t sre-guardian .

# Build with specific tag
docker build -t sre-guardian:v1.0 .

# Build for different architecture (if needed)
docker build --platform linux/amd64 -t sre-guardian .
```

### Running Modes

#### 🎭 Demo Mode (No Prometheus Required)
Perfect for testing and development:
```bash
docker run --rm -p 8080:8080 \
  -e DEMO_MODE=true \
  sre-guardian
```

#### 🏭 Production Mode
Connect to your Prometheus instance:
```bash
docker run --rm -p 8080:8080 \
  -e PROM_URL=http://your-prometheus:9090 \
  -e NAMESPACE=production \
  -e K8S_DRY_RUN=false \
  sre-guardian
```

#### 🔧 Development Mode
With custom configuration:
```bash
docker run --rm -p 8080:8080 \
  -e DEMO_MODE=true \
  -e HISTORY_HOURS=12 \
  -e ISOFOREST_CONTAM=0.1 \
  -e SLO_P95_TARGET_MS=500 \
  sre-guardian
```

### Environment Variables
| Variable | Default | Description |
|----------|---------|-------------|
| `DEMO_MODE` | `false` | Generate synthetic data for testing |
| `PROM_URL` | `http://prometheus.monitoring:9090` | Prometheus endpoint |
| `NAMESPACE` | `""` | Filter to specific K8s namespace |
| `HISTORY_HOURS` | `24` | Metrics lookback window |
| `ISOFOREST_CONTAM` | `0.07` | Anomaly detection sensitivity |
| `K8S_DRY_RUN` | `true` | Safe mode for K8s actions |
| `PODMAN_DRY_RUN` | `true` | Safe mode for Podman actions |
| `SLO_P95_TARGET_MS` | `300` | Latency SLO threshold |

### Volume Mounts
```bash
# Persist model cache
docker run --rm -p 8080:8080 \
  -v sre-guardian-models:/tmp \
  -e DEMO_MODE=true \
  sre-guardian

# Custom config file (if you add one)
docker run --rm -p 8080:8080 \
  -v ./config.yaml:/app/config.yaml \
  -e CONFIG_FILE=/app/config.yaml \
  sre-guardian
```

### Network Configuration
```bash
# Connect to existing network
docker run --rm -p 8080:8080 \
  --network prometheus-net \
  -e PROM_URL=http://prometheus:9090 \
  sre-guardian

# Access host services (Prometheus on host)
docker run --rm -p 8080:8080 \
  --add-host=host.docker.internal:host-gateway \
  -e PROM_URL=http://host.docker.internal:9090 \
  sre-guardian
```

### Health Checks
```bash
# Check if container is healthy
docker ps --format "table {{.Names}}\t{{.Status}}"

# Manual health check
curl http://localhost:8080/healthz

# View container logs
docker logs <container-name>
```

### Docker Compose Example
Create `docker-compose.yml`:
```yaml
version: '3.8'
services:
  sre-guardian:
    build: .
    ports:
      - "8080:8080"
    environment:
      - DEMO_MODE=true
      - HISTORY_HOURS=12
      - ISOFOREST_CONTAM=0.05
    volumes:
      - sre-models:/tmp
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8080/healthz')"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  sre-models:
```

Run with:
```bash
docker-compose up -d
docker-compose logs -f
```

### Troubleshooting Docker Issues

#### Container Won't Start
```bash
# Check logs
docker logs <container-name>

# Run with shell access
docker run --rm -it --entrypoint /bin/bash sre-guardian

# Test inside container
docker exec -it <container-name> python -c "from sre_guardian.api import app; print('OK')"
```

#### Port Already in Use
```bash
# Find what's using the port
lsof -i :8080

# Use different port
docker run --rm -p 8081:8080 sre-guardian
```

#### Memory/Performance Issues
```bash
# Run with memory limits
docker run --rm -p 8080:8080 \
  --memory="512m" \
  --cpus="1.0" \
  sre-guardian

# Monitor resource usage
docker stats <container-name>
```

#### Prometheus Connection Issues
```bash
# Test connection from inside container
docker exec -it <container-name> curl http://prometheus:9090/api/v1/status/config

# Check network connectivity
docker exec -it <container-name> nslookup prometheus
```

---

## 🧪 Testing

### 1) API health
```bash
curl http://localhost:8080/healthz
curl "http://localhost:8080/anomalies?namespace=default&top_k=5"
```

### 2) Synthetic AI demo (no Prometheus needed)
```bash
python tests/simulate_metrics_demo.py
```
This script generates fake workloads (normal, memory leak, noisy neighbor) and shows how the AI flags them as anomalous.

---

## ⚙️ Configuration (env vars)
- `PROM_URL` — Prometheus URL
- `HISTORY_HOURS` — training lookback (default: 24h)
- `ISOFOREST_CONTAM` — anomaly contamination ratio (default: 0.07)
- `K8S_DRY_RUN`, `PODMAN_DRY_RUN` — safe defaults
- `SLO_P95_TARGET_MS` — latency budget for drift detection

---

## 🌐 Endpoints
- `GET /healthz` → service check  
- `GET /anomalies?namespace=&top_k=` → ranked anomalies + RCA  
- `POST /suggest` → automation-friendly anomalies  
- `POST /act` → run guarded actions (K8s/Podman)

---

## 🤖 AI Model Details

- **Model type**: Isolation Forest (unsupervised anomaly detection)  
- **Library**: scikit-learn  
- **Where in code**: `src/sre_guardian/models.py`  
- **Training**: automatic on `/anomalies` call  
- **Model file**: cached at `/tmp/nn_slo_iforest.joblib`  

### Features
- CPU/memory: mean, std, p95, max, min, slope  
- Throttling: mean, p95, max  
- Restarts: mean, max  
- Latency: mean, p95, max  

### Why AI?
Unlike static thresholds, the service **learns what’s normal** and flags deviations, even if they don’t trip simple CPU/Memory alerts. This helps catch subtle SRE issues (memory leaks, noisy neighbors, SLO drift).

### No Pre-training Needed
You don’t need to install or download any model — it trains automatically from your Prometheus data.

### Optional Extensions
- Swap to advanced detectors (PyOD, AutoEncoders)
- Add time-series prediction for SLO forecasting
- Use LLMs for natural language RCA reports

---

## 🔧 Troubleshooting
- **Empty results**: verify PromQL metric names in `collectors.py`
- **RBAC issues**: check Kubernetes role bindings
- **Noise**: tune `ISOFOREST_CONTAM`, lookback windows, or metric step
- **Security**: put behind ingress/gateway with auth

### Demo mode (no Prometheus needed)
Set `DEMO_MODE=true` to synthesize realistic metrics so `/anomalies` returns results even without Prometheus:

```bash
export DEMO_MODE=true
export K8S_IN_CLUSTER=false
python main.py
curl "http://localhost:8080/anomalies?top_k=5" | jq
```
