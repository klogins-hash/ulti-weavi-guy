# Northflank Deployment Guide

## Overview

This guide covers deploying the Ulti Weavi Guy MVP to Northflank, a full-stack cloud platform optimized for containerized applications. The deployment includes:

- **Backend API**: FastAPI service with LangChain integrations
- **Frontend**: Next.js application with TypeScript
- **Weaviate**: Vector database service
- **Redis**: Job queue and caching
- **PostgreSQL**: Metadata storage (optional)

## Prerequisites

1. **Northflank Account**: Sign up at [northflank.com](https://northflank.com)
2. **Git Repository**: Push your code to GitHub, GitLab, or Bitbucket
3. **API Keys**: Obtain required API keys (see Secret Groups section)

## Deployment Architecture

```
Internet → Northflank Load Balancer
    ↓
Frontend (Next.js) ← → Backend API (FastAPI)
    ↓                      ↓
Weaviate Vector DB    Redis Queue
    ↓
PostgreSQL (optional)
```

## Step-by-Step Deployment

### 1. Create Project and Secret Group

1. **Create New Project**:
   - Go to Northflank dashboard
   - Click "Create New" → "Project"
   - Name: `ulti-weavi-guy`
   - Description: `Ultimate Weaviate Frontend Tool`

2. **Create Secret Group**:
   ```bash
   # Upload the secret group configuration
   nf secrets create --file .northflank/secret-groups.yaml
   ```
   
   Or manually create in dashboard:
   - Go to "Secret Groups" → "Create New"
   - Name: `ulti-weavi-secrets`
   - Add the following secrets:

   **Required Secrets:**
   ```
   FIRECRAWL_API_KEY=your_firecrawl_key
   APIFY_API_KEY=your_apify_key
   UNSTRUCTURED_API_KEY=your_unstructured_key
   COHERE_API_KEY=your_cohere_key
   ANTHROPIC_API_KEY=your_anthropic_key
   ```

   **Optional Secrets:**
   ```
   WEAVIATE_API_KEY=your_weaviate_key (if auth enabled)
   DEBUG=false
   LOG_LEVEL=INFO
   SECRET_KEY=auto-generated-32-char-string
   JWT_SECRET=auto-generated-64-char-string
   ```

### 2. Deploy Database Addons

#### Redis Addon
1. Go to "Addons" → "Create New"
2. Select "Redis"
3. Configuration:
   - Name: `ulti-weavi-redis`
   - Version: `7.0`
   - Plan: `nf-compute-10` (or higher for production)
   - Storage: `1GB`
   - Persistence: Enabled
   - TLS: Disabled (internal communication)
   - Public Access: Disabled

#### PostgreSQL Addon (Optional)
1. Go to "Addons" → "Create New"
2. Select "PostgreSQL"
3. Configuration:
   - Name: `ulti-weavi-postgres`
   - Version: `15`
   - Plan: `nf-compute-10`
   - Storage: `10GB`
   - Persistence: Enabled
   - TLS: Disabled
   - Public Access: Disabled

### 3. Deploy Weaviate Service

1. **Create Deployment Service**:
   - Go to "Services" → "Create New" → "Deployment Service"
   - Name: `ulti-weavi-weaviate`

2. **Configuration**:
   - **Image**: `semitechnologies/weaviate:1.22.4`
   - **Port**: `8080` (HTTP, Public)
   - **Resources**: 
     - CPU: `0.5 vCPU`
     - Memory: `2GB`
     - Storage: `10GB`

3. **Environment Variables**:
   ```
   QUERY_DEFAULTS_LIMIT=25
   AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true
   PERSISTENCE_DATA_PATH=/var/lib/weaviate
   DEFAULT_VECTORIZER_MODULE=none
   ENABLE_MODULES=text2vec-cohere,text2vec-openai,generative-openai,generative-cohere
   CLUSTER_HOSTNAME=node1
   ```

4. **Volumes**:
   - Mount Path: `/var/lib/weaviate`
   - Size: `10GB`

### 4. Deploy Backend API

1. **Create Combined Service**:
   - Go to "Services" → "Create New" → "Combined Service"
   - Name: `ulti-weavi-backend`

2. **Repository Configuration**:
   - Connect your Git repository
   - Branch: `main` (or your deployment branch)
   - Build Context: `/backend`

3. **Build Configuration**:
   - Build Type: `Dockerfile`
   - Dockerfile Path: `/backend/Dockerfile`

4. **Port Configuration**:
   - Internal Port: `8000`
   - Protocol: `HTTP`
   - Public: `Yes`

5. **Resources**:
   - CPU: `1 vCPU`
   - Memory: `2GB`
   - Replicas: `1`

6. **Environment Variables**:
   ```
   PORT=8000
   PYTHONPATH=/app
   WEAVIATE_URL=${LINK.ulti-weavi-weaviate.HOST}:${LINK.ulti-weavi-weaviate.PORT}
   REDIS_URL=redis://${ADDON.ulti-weavi-redis.HOST}:${ADDON.ulti-weavi-redis.PORT}
   DATABASE_URL=postgresql://${ADDON.ulti-weavi-postgres.USERNAME}:${ADDON.ulti-weavi-postgres.PASSWORD}@${ADDON.ulti-weavi-postgres.HOST}:${ADDON.ulti-weavi-postgres.PORT}/${ADDON.ulti-weavi-postgres.DATABASE}
   ```

7. **Secret Groups**:
   - Link: `ulti-weavi-secrets`

8. **Health Checks**:
   - Path: `/health`
   - Initial Delay: `30s`
   - Period: `30s`

### 5. Deploy Frontend

1. **Create Combined Service**:
   - Go to "Services" → "Create New" → "Combined Service"
   - Name: `ulti-weavi-frontend`

2. **Repository Configuration**:
   - Same repository as backend
   - Branch: `main`
   - Build Context: `/frontend`

3. **Build Configuration**:
   - Build Type: `Dockerfile`
   - Dockerfile Path: `/frontend/Dockerfile`

4. **Port Configuration**:
   - Internal Port: `3000`
   - Protocol: `HTTP`
   - Public: `Yes`

5. **Resources**:
   - CPU: `0.5 vCPU`
   - Memory: `1GB`
   - Replicas: `1`

6. **Environment Variables**:
   ```
   NODE_ENV=production
   NEXT_PUBLIC_API_URL=${LINK.ulti-weavi-backend.HOST}
   ```

7. **Build Arguments**:
   ```
   NODE_VERSION=18
   NEXT_PUBLIC_API_URL=${LINK.ulti-weavi-backend.HOST}
   ```

### 6. Configure Custom Domains (Optional)

1. **Add Domain**:
   - Go to project settings → "Domains"
   - Add your custom domain
   - Configure DNS records as instructed

2. **SSL/TLS**:
   - Northflank automatically provisions SSL certificates
   - Certificates auto-renew

## Environment-Specific Configurations

### Development Environment
- Use smaller resource allocations
- Enable debug logging
- Use development API keys

### Staging Environment
- Mirror production configuration
- Use staging API keys
- Enable additional logging

### Production Environment
- Increase resource allocations
- Enable monitoring and alerts
- Use production API keys
- Configure backup schedules

## Monitoring and Observability

### Built-in Monitoring
- **Metrics**: CPU, Memory, Network, Storage
- **Logs**: Centralized logging with search
- **Health Checks**: Automated endpoint monitoring
- **Alerts**: Email/Slack notifications

### Custom Monitoring
```python
# Add to backend for custom metrics
from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter('requests_total', 'Total requests')
REQUEST_DURATION = Histogram('request_duration_seconds', 'Request duration')
```

## Scaling and Performance

### Horizontal Scaling
```yaml
# Increase replicas for high traffic
replicas: 3
resources:
  cpu: "2 vCPU"
  memory: "4GB"
```

### Vertical Scaling
- Monitor resource usage in dashboard
- Adjust CPU/Memory allocations as needed
- Use auto-scaling policies

### Database Scaling
- Upgrade addon plans for more resources
- Enable read replicas for PostgreSQL
- Configure Redis clustering for high availability

## Security Best Practices

### Network Security
- All internal communication uses private networking
- Public endpoints only where necessary
- TLS encryption for external traffic

### Secret Management
- All API keys stored in secret groups
- Secrets encrypted at rest and in transit
- Regular secret rotation

### Access Control
- Use Northflank teams and roles
- Principle of least privilege
- Regular access reviews

## Backup and Disaster Recovery

### Database Backups
- Automated daily backups for addons
- Point-in-time recovery available
- Cross-region backup replication

### Application Backups
- Git repository serves as source backup
- Container images stored in registry
- Configuration stored in Northflank

### Recovery Procedures
1. Restore from addon backup
2. Redeploy services from Git
3. Verify functionality
4. Update DNS if needed

## Cost Optimization

### Resource Right-Sizing
- Monitor actual usage vs allocated resources
- Use appropriate addon plans
- Scale down non-production environments

### Development Workflow
- Use feature branches for testing
- Implement CI/CD for efficient deployments
- Use staging environments sparingly

## Troubleshooting

### Common Issues

**Service Won't Start**:
- Check logs in Northflank dashboard
- Verify environment variables
- Ensure dependencies are available

**Database Connection Issues**:
- Verify addon is running
- Check connection strings
- Review network policies

**Build Failures**:
- Check Dockerfile syntax
- Verify build context
- Review build logs

### Debug Commands
```bash
# View logs
nf logs service ulti-weavi-backend

# Check service status
nf get services

# Restart service
nf restart service ulti-weavi-backend
```

## CLI Deployment (Alternative)

```bash
# Install Northflank CLI
npm install -g @northflank/cli

# Login
nf login

# Deploy using configuration file
nf deploy --file northflank.json
```

## Next Steps

1. **Monitoring Setup**: Configure alerts and dashboards
2. **CI/CD Pipeline**: Automate deployments with GitHub Actions
3. **Performance Testing**: Load test your deployment
4. **Security Audit**: Review security configurations
5. **Documentation**: Update team documentation

## Support

- **Northflank Docs**: [docs.northflank.com](https://docs.northflank.com)
- **Community**: [community.northflank.com](https://community.northflank.com)
- **Support**: support@northflank.com

---

**Your Ulti Weavi Guy MVP is now ready for production deployment on Northflank!** 🚀
