# GitOps with Argo & Kubernetes: One-Month Study Plan

## Week 1: ArgoCD Foundations & GitOps Principles
- **Days 1-2: GitOps Fundamentals**
  - Review GitOps principles and benefits
    - [GitOps Principles](https://opengitops.dev/) - CNCF GitOps Working Group
    - [What is GitOps?](https://about.gitlab.com/topics/gitops/) by GitLab
    - [Understanding GitOps](https://www.redhat.com/en/topics/devops/what-is-gitops) - RedHat's guide
  - Understand declarative vs. imperative approaches
    - [Declarative vs Imperative in Kubernetes](https://kubernetes.io/docs/concepts/overview/working-with-objects/object-management/)
    - [Infrastructure as Code: Imperative vs Declarative](https://blog.container-solutions.com/infrastructure-as-code-imperative-vs-declarative)
  - Study Git workflows for infrastructure management
    - [GitOps Workflows with ArgoCD](https://argo-cd.readthedocs.io/en/stable/user-guide/ci_automation/)
    - [Trunk-Based Development](https://trunkbaseddevelopment.com/)
    - [Environment Promotion in GitOps](https://codefresh.io/learn/gitops/environment-promotion-in-gitops/)
  - Practical guides to get started
    - [Hands-on introduction to GitOps](https://www.redhat.com/architect/gitops-introduction) by RedHat
    - [ArgoCD Tutorial for Beginners](https://redhat-scholars.github.io/argocd-tutorial/argocd-tutorial/index.html)
  
- **Days 3-5: ArgoCD Deep Dive**
  - Revisit ArgoCD architecture components
  - Set up a personal ArgoCD instance
  - Practice application deployment with ArgoCD
  - Explore sync policies and automated sync
  - Study Application CRDs in depth

- **Weekend Project:** Deploy a multi-component application using ArgoCD
  
  **TaskHub: A Multi-Component Task Management Application**
  
  Components:
  - React frontend with Tailwind CSS
  - Python FastAPI backend
  - PostgreSQL database
  - Redis for caching
  
  Repository Structure:
  ```
  taskhub/
  ├── frontend/
  │   ├── deployment.yaml
  │   ├── service.yaml
  │   └── ingress.yaml
  ├── backend/
  │   ├── deployment.yaml
  │   ├── service.yaml
  │   └── configmap.yaml
  ├── database/
  │   ├── statefulset.yaml
  │   ├── service.yaml
  │   └── pvc.yaml
  ├── redis/
  │   ├── deployment.yaml
  │   └── service.yaml
  └── application.yaml (ArgoCD Application manifest)
  ```
  
  ### Implementation Steps:
  
  1. **Create a new repository for this project**
     - Create a new GitHub/GitLab repository called `taskhub-gitops`
     - Clone it to your local machine
  
  2. **Set up the directory structure**
     ```bash
     mkdir -p taskhub/{frontend,backend,database,redis}
     ```
  
  3. **Create Kubernetes manifests for each component**
  
     **Frontend (React with Tailwind)**
     ```yaml
     # taskhub/frontend/deployment.yaml
     apiVersion: apps/v1
     kind: Deployment
     metadata:
       name: taskhub-frontend
     spec:
       replicas: 1
       selector:
         matchLabels:
           app: taskhub-frontend
       template:
         metadata:
           labels:
             app: taskhub-frontend
         spec:
           containers:
           - name: frontend
             # Replace with your own image after building
             image: your-registry/taskhub-frontend:latest
             ports:
             - containerPort: 80
             env:
             - name: REACT_APP_API_URL
               value: "http://taskhub-backend:8000"
     
     # taskhub/frontend/service.yaml
     apiVersion: v1
     kind: Service
     metadata:
       name: taskhub-frontend
     spec:
       selector:
         app: taskhub-frontend
       ports:
       - port: 80
         targetPort: 80
     
     # taskhub/frontend/ingress.yaml
     apiVersion: networking.k8s.io/v1
     kind: Ingress
     metadata:
       name: taskhub-frontend
       annotations:
         kubernetes.io/ingress.class: "public-iks-k8s-nginx"
     spec:
       tls:
       - hosts:
         - taskhub.CLUSTER-ID.us-south.containers.appdomain.cloud
         secretName: taskhub-tls-secret
       rules:
       - host: taskhub.CLUSTER-ID.us-south.containers.appdomain.cloud
         http:
           paths:
           - path: /
             pathType: Prefix
             backend:
               service:
                 name: taskhub-frontend
                 port:
                   number: 80
     ```
  
     **Backend (Python FastAPI)**
     ```yaml
     # taskhub/backend/deployment.yaml
     apiVersion: apps/v1
     kind: Deployment
     metadata:
       name: taskhub-backend
     spec:
       replicas: 1
       selector:
         matchLabels:
           app: taskhub-backend
       template:
         metadata:
           labels:
             app: taskhub-backend
         spec:
           containers:
           - name: backend
             # Replace with your own image after building
             image: your-registry/taskhub-backend:latest
             ports:
             - containerPort: 8000
             env:
             - name: DATABASE_URL
               value: "postgresql://postgres:postgres@taskhub-database:5432/taskhub"
             - name: REDIS_URL
               value: "redis://taskhub-redis:6379/0"
     
     # taskhub/backend/service.yaml
     apiVersion: v1
     kind: Service
     metadata:
       name: taskhub-backend
     spec:
       selector:
         app: taskhub-backend
       ports:
       - port: 8000
         targetPort: 8000
     
     # taskhub/backend/configmap.yaml
     apiVersion: v1
     kind: ConfigMap
     metadata:
       name: taskhub-backend-config
     data:
       API_LOG_LEVEL: "info"
       ALLOW_ORIGINS: "http://taskhub-frontend"
     ```
  
     **Database (PostgreSQL)**
     ```yaml
     # taskhub/database/statefulset.yaml
     apiVersion: apps/v1
     kind: StatefulSet
     metadata:
       name: taskhub-database
     spec:
       serviceName: taskhub-database
       replicas: 1
       selector:
         matchLabels:
           app: taskhub-database
       template:
         metadata:
           labels:
             app: taskhub-database
         spec:
           containers:
           - name: postgres
             image: postgres:14
             ports:
             - containerPort: 5432
             env:
             - name: POSTGRES_USER
               value: postgres
             - name: POSTGRES_PASSWORD
               value: postgres
             - name: POSTGRES_DB
               value: taskhub
             volumeMounts:
             - name: postgres-data
               mountPath: /var/lib/postgresql/data
       volumeClaimTemplates:
       - metadata:
           name: postgres-data
         spec:
           accessModes: ["ReadWriteOnce"]
           resources:
             requests:
               storage: 1Gi
     
     # taskhub/database/service.yaml
     apiVersion: v1
     kind: Service
     metadata:
       name: taskhub-database
     spec:
       selector:
         app: taskhub-database
       ports:
       - port: 5432
         targetPort: 5432
     ```
  
     **Redis (Caching)**
     ```yaml
     # taskhub/redis/deployment.yaml
     apiVersion: apps/v1
     kind: Deployment
     metadata:
       name: taskhub-redis
     spec:
       replicas: 1
       selector:
         matchLabels:
           app: taskhub-redis
       template:
         metadata:
           labels:
             app: taskhub-redis
         spec:
           containers:
           - name: redis
             image: redis:6
             ports:
             - containerPort: 6379
     
     # taskhub/redis/service.yaml
     apiVersion: v1
     kind: Service
     metadata:
       name: taskhub-redis
     spec:
       selector:
         app: taskhub-redis
       ports:
       - port: 6379
         targetPort: 6379
     ```
  
  4. **Create the ArgoCD Application manifest**
     ```yaml
     # application.yaml (in repository root)
     apiVersion: argoproj.io/v1alpha1
     kind: Application
     metadata:
       name: taskhub
       namespace: argocd
     spec:
       project: default
       source:
         repoURL: https://github.com/yourusername/taskhub-gitops.git
         targetRevision: HEAD
         path: taskhub
       destination:
         server: https://kubernetes.default.svc
         namespace: taskhub
       syncPolicy:
         automated:
           prune: true
           selfHeal: true
         syncOptions:
         - CreateNamespace=true
     ```
  
  5. **Commit and push to your repository**
     ```bash
     git add .
     git commit -m "Initial TaskHub application manifests"
     git push
     ```
  
  6. **Deploy to your cluster using ArgoCD**
     ```bash
     # Option 1: Using the UI
     # Navigate to ArgoCD UI -> New App -> Fill in details using your repository
     
     # Option 2: Using CLI
     argocd app create taskhub \
       --repo https://github.com/yourusername/taskhub-gitops.git \
       --path taskhub \
       --dest-server https://kubernetes.default.svc \
       --dest-namespace taskhub \
       --sync-policy automated
     ```
  
  7. **Verify the application is syncing and healthy**
     - Check the ArgoCD UI to see all components being deployed
     - Use `kubectl get all -n taskhub` to verify resources
  
  ### Bonus Challenges:
  
  - **Add a Helm Chart**: Convert the raw manifests to a Helm chart for cleaner parameter management
  - **Implement Sync Waves**: Use annotations to control the order of resource creation
  - **Add Health Checks**: Implement readiness/liveness probes for all components
  - **Set up Progressive Delivery**: Add Argo Rollouts for canary deployments of the frontend
  
  ### Resources for Building Images:
  
  - **Sample Frontend Dockerfile**:
    ```Dockerfile
    FROM node:16 as build
    WORKDIR /app
    COPY package*.json ./
    RUN npm install
    COPY . .
    RUN npm run build
    
    FROM nginx:alpine
    COPY --from=build /app/build /usr/share/nginx/html
    EXPOSE 80
    CMD ["nginx", "-g", "daemon off;"]
    ```
  
  - **Sample Backend Dockerfile**:
    ```Dockerfile
    FROM python:3.9
    WORKDIR /app
    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt
    COPY . .
    EXPOSE 8000
    CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
    ```
  
  This project demonstrates:
  - Multi-component application deployment using ArgoCD
  - GitOps principles with a declarative application state
  - Service dependencies and networking
  - Stateful vs. stateless components
  - Configuration management

## Week 2: Advanced ArgoCD & Argo Rollouts
- **Days 1-2: Advanced ArgoCD Features**
  - Implement webhook notifications
  - Configure SSO and RBAC
  - Set up ArgoCD ApplicationSets
  - Explore Helm and Kustomize integration

- **Days 3-5: Argo Rollouts**
  - Set up Argo Rollouts controller
  - Implement canary deployments
  - Configure blue/green deployments
  - Integrate with metrics providers
  - Set up progressive delivery pipelines

- **Weekend Project:** Implement a canary deployment with automated analysis

## Week 3: Argo Workflows & CI/CD Integration
- **Days 1-3: Argo Workflows**
  - Set up Argo Workflows controller
  - Design and run basic workflows
  - Implement artifacts and parameters
  - Create workflow templates
  - Study workflow scheduling and dependencies

- **Days 4-5: CI/CD Integration**
  - Connect CI tools (GitHub Actions/Jenkins) with Argo tools
  - Implement GitOps-based CI/CD pipeline
  - Automate testing and deployment processes

- **Weekend Project:** Build an end-to-end CI/CD pipeline with Argo Workflows and ArgoCD

## Week 4: Argo Events & Production-Ready GitOps
- **Days 1-3: Argo Events**
  - Set up Argo Events controller
  - Configure event sources and sensors
  - Implement event-driven workflows
  - Create complex event dependencies
  - Integrate with Argo Workflows

- **Days 4-5: Production-Ready GitOps**
  - Implement multi-cluster management
  - Study disaster recovery strategies
  - Configure secrets management
  - Implement monitoring and observability
  - Set up GitOps for environment promotion

- **Final Project:** Design and implement a complete GitOps platform with all Argo components

## Key Resources
- Official Documentation:
  - [Argo CD](https://argo-cd.readthedocs.io/)
  - [Argo Workflows](https://argoproj.github.io/argo-workflows/)
  - [Argo Rollouts](https://argoproj.github.io/argo-rollouts/)
  - [Argo Events](https://argoproj.github.io/argo-events/)

- Recommended Courses:
  - "GitOps Fundamentals" by Codefresh
  - "Argo CD: Applying GitOps Principles" on Pluralsight
  - "Kubernetes and GitOps" on Linux Foundation

- GitHub Repositories:
  - [Argo CD Examples](https://github.com/argoproj/argocd-example-apps)
  - [Argo Workflows Examples](https://github.com/argoproj/argo-workflows/tree/master/examples)
  - [Argo Rollouts Examples](https://github.com/argoproj/argo-rollouts/tree/master/examples)

## Daily Learning Structure (Recommended)
1. 30-60 minutes: Read documentation/tutorials 
2. 60-90 minutes: Hands-on practice
3. 30 minutes: Reflect & document learnings

## Progress Tracking
- [ ] Week 1 Completed
- [ ] ArgoCD instance set up
- [ ] Multi-component app deployed
- [ ] Week 2 Completed  
- [ ] Canary deployment implemented
- [ ] Week 3 Completed
- [ ] CI/CD pipeline created
- [ ] Week 4 Completed
- [ ] Final project delivered
