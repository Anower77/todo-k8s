# ArgoCD

## Overview

ArgoCD is a GitOps continuous delivery tool for Kubernetes.
It watches a Git repository and automatically syncs the cluster state to match what is in the repo.
Any change pushed to the `k8s/` directory is automatically applied to the cluster.

```
argocd/
  application.yaml
```

---

## How it works

1. You push a change to the Git repo (e.g. update the Django image tag)
2. ArgoCD detects the change within 3 minutes (default poll interval)
3. ArgoCD applies the change to the cluster automatically
4. If the cluster drifts from the repo state, ArgoCD self-heals it

---

## Prerequisites

- ArgoCD installed in the cluster (done)
- The project pushed to a public or private GitHub repository
- kubectl configured against the cluster

---

## Step 1 - Push the project to GitHub

Initialize a git repo and push:

```bash
git init
git add .
git commit -m "initial commit"
git remote add origin https://github.com/your-username/todo-k8s-project.git
git push -u origin main
```

---

## Step 2 - Update application.yaml

Open `argocd/application.yaml` and replace the repoURL with your actual GitHub repo:

```yaml
source:
  repoURL: https://github.com/your-username/todo-k8s-project.git
```

---

## Step 3 - Apply the Application

```bash
kubectl apply -f argocd/application.yaml
```

ArgoCD will immediately start syncing the `k8s/` directory to the cluster.

---

## Step 4 - Access the ArgoCD UI

Port-forward the ArgoCD server:

```bash
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

Open in browser:

```
https://localhost:8080
```

Login credentials:
- Username: `admin`
- Password: retrieve with this command:

```bash
kubectl get secret argocd-initial-admin-secret -n argocd -o jsonpath="{.data.password}" | base64 -d
```

On Windows (PowerShell):

```powershell
[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String((kubectl get secret argocd-initial-admin-secret -n argocd -o jsonpath="{.data.password}")))
```

---

## Step 5 - Verify sync status

In the UI you will see the `todo-app` application. It should show `Synced` and `Healthy`.

From the CLI:

```bash
kubectl get application -n argocd
```

Expected output:

```
NAME       SYNC STATUS   HEALTH STATUS
todo-app   Synced        Healthy
```

---

## Sync Policy explained

The application.yaml has these sync options set:

- `automated.prune: true` - if you delete a manifest from the repo, ArgoCD deletes the resource from the cluster
- `automated.selfHeal: true` - if someone manually changes a resource in the cluster, ArgoCD reverts it back to match the repo
- `CreateNamespace=true` - ArgoCD creates the namespace if it does not exist

---

## Triggering a deployment

To deploy a new image:

1. Build and push the new image:

```bash
cd app/backend
docker build -t anower77/todo-backend:v2 .
docker push anower77/todo-backend:v2
```

2. Update the image tag in `k8s/django/deployment.yaml`:

```yaml
image: anower77/todo-backend:v2
```

3. Commit and push:

```bash
git add k8s/django/deployment.yaml
git commit -m "deploy v2"
git push
```

ArgoCD detects the change and rolls out the new deployment automatically.

---

## Teardown

To remove the ArgoCD application (does not delete the todo app resources):

```bash
kubectl delete -f argocd/application.yaml
```

To remove ArgoCD entirely:

```bash
kubectl delete namespace argocd
```
