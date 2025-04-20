This document provides instructions for deploying the dashboard in various environments.

## Table of Contents

- [Local Development](#local-development)
- [AWS Deployment](#aws-deployment)
  - [Using ECS Fargate](#using-ecs-fargate)
  - [Using EKS](#using-eks)
- [Kubernetes (Generic)](#kubernetes-generic)
- [Security Considerations](#security-considerations)
- [Scaling Considerations](#scaling-considerations)

## Local Development

Local development is managed through Docker Compose:

```bash
# Clone the repository
git clone https://github.com/avrtt/superset-supremacy.git
cd superset-supremacy

# Create and configure the .env file
cp .env.example .env
# Edit .env with your custom values

# Start the services
docker-compose up -d

# Access Superset at http://localhost:8088
# Default credentials: admin/admin
```

## AWS Deployment

### Using ECS Fargate

The project includes AWS ECS task definitions and a GitHub Actions workflow for automated deployments.

#### Prerequisites

1. An AWS account with appropriate permissions
2. An ECS cluster named `superset-marketing-cluster`
3. A service named `superset-marketing-service`
4. AWS Secrets Manager secrets for sensitive values

#### Deployment Steps

1. Set up the required AWS resources:
   ```bash
   # Create the ECS cluster
   aws ecs create-cluster --cluster-name superset-marketing-cluster

   # Create secrets in AWS Secrets Manager
   aws secretsmanager create-secret --name superset/db/password --secret-string "your-db-password"
   aws secretsmanager create-secret --name superset/secret_key --secret-string "your-secret-key"
   aws secretsmanager create-secret --name superset/oauth/client_id --secret-string "your-oauth-client-id"
   aws secretsmanager create-secret --name superset/oauth/client_secret --secret-string "your-oauth-client-secret"
   ```

2. Configure GitHub repository secrets:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `SLACK_WEBHOOK_URL` (optional, for notifications)

3. Update the task definition in `.aws/task-definition.json`:
   - Update the AWS account ID (`123456789012`)
   - Update the image repository URL
   - Modify CPU and memory allocations if needed

4. Push changes to the main branch to trigger the deployment pipeline.

### Using EKS

The project also supports deployment to Amazon EKS (Kubernetes).

#### Prerequisites

1. An EKS cluster named `superset-marketing-cluster`
2. `kubectl` configured to communicate with the cluster
3. Kubernetes secrets for sensitive values

#### Deployment Steps

1. Create the namespace and secrets:
   ```bash
   # Create namespace
   kubectl apply -f kubernetes/namespace.yaml

   # Create secrets
   kubectl create secret generic superset-secrets \
     --namespace=superset \
     --from-literal=db_password=your-db-password \
     --from-literal=secret_key=your-secret-key \
     --from-literal=oauth_client_id=your-oauth-client-id \
     --from-literal=oauth_client_secret=your-oauth-client-secret
   ```

2. Deploy the Kubernetes resources:
   ```bash
   kubectl apply -f kubernetes/configmap.yaml
   kubectl apply -f kubernetes/deployment.yaml
   kubectl apply -f kubernetes/service.yaml
   kubectl apply -f kubernetes/ingress.yaml
   ```

3. Alternatively, enable the EKS deployment in the GitHub Actions workflow by setting the condition to `true` for the EKS deployment steps in `.github/workflows/ci.yml`.

## Kubernetes (Generic)

For deployment to other Kubernetes environments:

1. Create the Kubernetes manifests in a `kubernetes` directory:
   - `namespace.yaml`
   - `configmap.yaml` (for superset_config.py)
   - `secrets.yaml` (for sensitive values)
   - `deployment.yaml`
   - `service.yaml`
   - `ingress.yaml` (if needed)

2. Deploy using `kubectl apply -f kubernetes/`.

## Security Considerations

1. **Secrets Management**: Use a secure secrets management solution like AWS Secrets Manager, HashiCorp Vault, or Kubernetes Secrets.

2. **Network Security**: 
   - Use private subnets for the Superset instances
   - Implement a Web Application Firewall (WAF) for public-facing deployments
   - Use TLS for all connections

3. **Access Control**:
   - Implement OAuth or OIDC for authentication
   - Configure Superset RBAC for authorization
   - Periodically audit access logs

4. **Database Security**:
   - Use minimal-privilege database users
   - Encrypt data at rest and in transit
   - Implement network security groups to restrict database access

## Scaling Considerations

1. **Horizontal Scaling**:
   - Configure auto-scaling for the Superset service based on CPU/memory utilization
   - For AWS ECS, update the desired count of tasks
   - For Kubernetes, use Horizontal Pod Autoscaler (HPA)

2. **Resource Optimization**:
   - Tune Redis caching for optimal performance
   - Configure appropriate CPU and memory limits
   - Use materialized views for heavy queries

3. **Database Scaling**:
   - Consider using read replicas for read-heavy workloads
   - Implement connection pooling
   - Use a managed database service like Amazon RDS

4. **Monitoring**:
   - Set up CloudWatch (AWS) or Prometheus/Grafana monitoring
   - Configure alerts for resource utilization and response times
   - Monitor database performance metrics 