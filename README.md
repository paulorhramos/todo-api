# Todo API

API REST para gerenciamento de tarefas (To-Do List) com Flask e PostgreSQL.

## 🎯 Funcionalidades

- ✅ Criar tarefas
- ✅ Listar todas as tarefas
- ✅ Atualizar tarefas
- ✅ Marcar como concluída
- ✅ Deletar tarefas
- ✅ Persistência em PostgreSQL

## 🏗️ Arquitetura

```
┌─────────────────┐
│   Frontend      │
│   (Browser)     │
└────────┬────────┘
         │
         v
┌─────────────────┐
│  Nginx Ingress  │
│ todo-api.*.nip.io│
└────────┬────────┘
         │
         v
┌─────────────────┐       ┌──────────────┐
│   Todo API      │──────>│  PostgreSQL  │
│  (Flask/Python) │       │  (StatefulSet)│
└─────────────────┘       └──────────────┘
```

## 📦 Estrutura

```
todo-api/
├── app.py                    # Aplicação Flask
├── requirements.txt          # Dependências Python
├── Dockerfile               # Build da imagem
├── k8s/                     # Manifestos Kubernetes
│   ├── deployment.yaml      # Deployment da API
│   ├── service.yaml         # Service ClusterIP
│   ├── ingress.yaml         # Nginx Ingress
│   ├── postgres.yaml        # PostgreSQL StatefulSet
│   └── postgres-secret.yaml # Credenciais do banco
└── .github/workflows/
    └── build-and-push.yaml  # CI/CD Pipeline
```

## 🚀 Endpoints da API

### Health Check
```bash
GET /health
```

### Listar Tarefas
```bash
GET /api/todos
```

### Criar Tarefa
```bash
POST /api/todos
Content-Type: application/json

{
  "title": "Minha tarefa",
  "description": "Descrição da tarefa"
}
```

### Atualizar Tarefa
```bash
PUT /api/todos/:id
Content-Type: application/json

{
  "title": "Tarefa atualizada",
  "completed": true
}
```

### Deletar Tarefa
```bash
DELETE /api/todos/:id
```

## 🔧 Desenvolvimento Local

### Requisitos
- Python 3.11+
- PostgreSQL 15+

### Setup
```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=tododb
export DB_USER=todouser
export DB_PASSWORD=todopass123

# Executar
python app.py
```

### Testar
```bash
# Health check
curl http://localhost:5000/health

# Criar tarefa
curl -X POST http://localhost:5000/api/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Test", "description": "Testing API"}'

# Listar tarefas
curl http://localhost:5000/api/todos
```

## 🐳 Docker

### Build
```bash
docker build -t prhramos/todo-api:latest .
```

### Run
```bash
docker run -p 5000:5000 \
  -e DB_HOST=postgres \
  -e DB_NAME=tododb \
  -e DB_USER=todouser \
  -e DB_PASSWORD=todopass123 \
  prhramos/todo-api:latest
```

## ☸️ Deploy Kubernetes

### Pré-requisitos
- Cluster Kubernetes
- ArgoCD instalado
- Longhorn para storage
- Secret `dockerhub-secret` configurado

### Deploy Manual
```bash
# Aplicar manifestos
kubectl apply -f k8s/

# Verificar pods
kubectl get pods -l app=todo-api
kubectl get pods -l app=postgres

# Verificar ingress
kubectl get ingress todo-api
```

### Deploy com ArgoCD
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: todo-api
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/paulorhramos/todo-api.git
    targetRevision: main
    path: k8s
  destination:
    server: https://kubernetes.default.svc
    namespace: default
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

## 🔐 Secrets

### PostgreSQL Secret
```bash
kubectl create secret generic postgres-secret \
  --from-literal=username=todouser \
  --from-literal=password=todopass123 \
  -n default
```

### Docker Hub Secret
```bash
kubectl create secret docker-registry dockerhub-secret \
  --docker-server=https://index.docker.io/v1/ \
  --docker-username=prhramos \
  --docker-password=<TOKEN> \
  -n default
```

## 📊 Monitoramento

### Logs da API
```bash
kubectl logs -f -l app=todo-api
```

### Logs do PostgreSQL
```bash
kubectl logs -f -l app=postgres
```

### Conectar ao Banco
```bash
kubectl exec -it postgres-0 -- psql -U todouser -d tododb
```

## 🛠️ Troubleshooting

### API não conecta ao banco
```bash
# Verificar se o PostgreSQL está rodando
kubectl get pods -l app=postgres

# Verificar logs do PostgreSQL
kubectl logs -l app=postgres

# Testar conexão
kubectl exec -it postgres-0 -- psql -U todouser -d tododb -c "SELECT 1"
```

### Pods em CrashLoopBackOff
```bash
# Ver logs
kubectl logs -l app=todo-api --tail=50

# Descrever pod
kubectl describe pod -l app=todo-api
```

## 🔄 GitOps Workflow

1. Fazer mudanças no código
2. Commit e push para GitHub
3. GitHub Actions builda e publica imagem
4. Atualiza deployment.yaml com nova tag
5. ArgoCD detecta mudança e faz sync
6. Aplicação atualizada automaticamente

## 📝 Variáveis de Ambiente

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| DB_HOST | Host do PostgreSQL | postgres |
| DB_PORT | Porta do PostgreSQL | 5432 |
| DB_NAME | Nome do banco | tododb |
| DB_USER | Usuário do banco | todouser |
| DB_PASSWORD | Senha do banco | (secret) |

## 🌐 Acesso

- **API**: http://todo-api.10.20.20.50.nip.io
- **Health**: http://todo-api.10.20.20.50.nip.io/health
- **Todos**: http://todo-api.10.20.20.50.nip.io/api/todos

## 📚 Stack Tecnológica

- **Backend**: Python 3.11 + Flask
- **Database**: PostgreSQL 15
- **Container**: Docker
- **Orchestration**: Kubernetes
- **GitOps**: ArgoCD
- **CI/CD**: GitHub Actions
- **Storage**: Longhorn
- **Ingress**: Nginx

---

**Repositório**: https://github.com/paulorhramos/todo-api
**Status**: 🚀 Pronto para produção
