# Kubernetes

## Overview

The k8s directory contains all manifests to run the todo application on a Kubernetes cluster.

```
k8s/
  namespace.yaml
  secret.yaml
  configmap.yaml
  postgres/
    pvc.yaml
    deployment.yaml
    service.yaml
  redis/
    deployment.yaml
    service.yaml
  django/
    deployment.yaml
    service.yaml
    hpa.yaml
  ingress/
    ingress.yaml
  kustomization.yaml
```

---

## Prerequisites

- A running Kubernetes cluster (local: minikube or kind, cloud: EKS/GKE/AKS)
- kubectl installed and configured against your cluster
- Docker image of the backend built and pushed to a registry
- nginx ingress controller installed on the cluster

---

## Step 1 - Build and push the Docker image

The Django deployment references `your-dockerhub-username/todo-backend:latest`.
Replace this with your actual image before applying.

```bash
cd app/backend
docker build -t your-dockerhub-username/todo-backend:latest .
docker push your-dockerhub-username/todo-backend:latest
```

Then update `k8s/django/deployment.yaml`:

```yaml
image: your-dockerhub-username/todo-backend:latest
```

---

## Step 2 - Update the Secret

`k8s/secret.yaml` uses `stringData` so values are plain text (Kubernetes encodes them).
Before applying to a real cluster, change the values:

```yaml
stringData:
  SECRET_KEY: "a-long-random-string"
  DB_PASSWORD: "a-strong-password"
```

Never commit real secrets to git. Use a secrets manager or sealed-secrets in production.

---

## Step 3 - Install nginx ingress controller (if not already installed)

For minikube:

```bash
minikube addons enable ingress
```

For a bare cluster:

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.10.1/deploy/static/provider/cloud/deploy.yaml
```

---

## Step 4 - Apply all manifests

From the project root:

```bash
kubectl apply -k k8s/
```

This applies every resource listed in `kustomization.yaml` in the correct order.

---

## Step 5 - Verify everything is running

```bash
kubectl get all -n todo-k8s-project
```

Expected output shows pods for postgres, redis, and django all in Running state.

Check pod logs if something is not ready:

```bash
kubectl logs -n todo-k8s-project deployment/django
kubectl logs -n todo-k8s-project deployment/postgres
```

---

## Step 6 - Access the application

Add the ingress host to your local hosts file.

On Linux/macOS:

```bash
echo "$(minikube ip) todo.local" | sudo tee -a /etc/hosts
```

On Windows (run as Administrator):

```
notepad C:\Windows\System32\drivers\etc\hosts
```

Add this line:

```
127.0.0.1 todo.local
```

For minikube use the minikube IP instead of 127.0.0.1:

```bash
minikube ip
```

Then open:

```
http://todo.local/api/docs/
```

---

## Manifest Reference

### namespace.yaml

Creates the `todo-k8s-project` namespace. All other resources live inside it.

### secret.yaml

Holds all sensitive values: SECRET_KEY, DB credentials, Redis URLs.
Uses `stringData` so you write plain text and Kubernetes stores it base64 encoded.
The Django deployment loads all keys from this secret via `envFrom.secretRef`.

### configmap.yaml

Holds non-sensitive config: DEBUG=False, ALLOWED_HOSTS.
Loaded into Django via `envFrom.configMapRef`.

### postgres/pvc.yaml

Requests 1Gi of persistent storage for the postgres data directory.
Uses `ReadWriteOnce` which means one node can mount it at a time - correct for a single postgres pod.

### postgres/deployment.yaml

Runs `postgres:16-alpine`. Credentials come from the secret.
Has a readiness probe using `pg_isready` so Django pods only start after postgres is accepting connections.

### postgres/service.yaml

ClusterIP service named `postgres-service`. Django connects to this hostname on port 5432.
This matches `DB_HOST=postgres-service` in the secret.

### redis/deployment.yaml

Runs `redis:7-alpine`. No persistence - Redis is used only as a Celery broker and result backend.
Has a TCP readiness probe on port 6379.

### redis/service.yaml

ClusterIP service named `redis-service`. Celery connects to `redis://redis-service:6379/0`.
This matches the CELERY_BROKER_URL and CELERY_RESULT_BACKEND in the secret.

### django/deployment.yaml

Runs 2 replicas of the backend image. Loads all env from the secret and configmap.
Has readiness and liveness probes hitting `/api/schema/` which is a lightweight endpoint.
Resource limits are set to prevent one pod from consuming all node resources.

### django/service.yaml

ClusterIP service named `django-service` on port 80 routing to pod port 8000.
The ingress routes to this service.

### django/hpa.yaml

HorizontalPodAutoscaler that keeps Django between 2 and 5 replicas.
Scales up when average CPU across pods exceeds 70%.
Requires metrics-server to be installed on the cluster.

For minikube:

```bash
minikube addons enable metrics-server
```

### ingress/ingress.yaml

Routes `http://todo.local/` to `django-service:80`.
Requires the nginx ingress controller.
Change the `host` value to your actual domain when deploying to a real cluster.

---

## Teardown

To delete everything:

```bash
kubectl delete -k k8s/
```

To delete only the namespace (removes everything inside it):

```bash
kubectl delete namespace todo-k8s-project
```
