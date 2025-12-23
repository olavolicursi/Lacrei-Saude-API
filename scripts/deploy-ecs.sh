#!/bin/bash
# Deploy script for AWS ECS
# Uso: ./deploy-ecs.sh <staging|production> [image-tag]

set -e

ENVIRONMENT=$1
IMAGE_TAG=${2:-latest}

if [ -z "$ENVIRONMENT" ]; then
    echo "❌ Usage: $0 <staging|production> [image-tag]"
    exit 1
fi

echo "🚀 Deploying to $ENVIRONMENT environment..."
echo "Image tag: $IMAGE_TAG"

# Configurações por ambiente
if [ "$ENVIRONMENT" == "staging" ]; then
    CLUSTER="lacrei-staging-cluster"
    SERVICE="lacrei-staging-service"
    TASK_FAMILY="lacrei-staging-task"
    DOCKER_IMAGE="${DOCKER_USERNAME}/lacrei-api:develop-${IMAGE_TAG}"
elif [ "$ENVIRONMENT" == "production" ]; then
    CLUSTER="lacrei-production-cluster"
    SERVICE="lacrei-production-service"
    TASK_FAMILY="lacrei-production-task"
    DOCKER_IMAGE="${DOCKER_USERNAME}/lacrei-api:${IMAGE_TAG}"
else
    echo "❌ Invalid environment: $ENVIRONMENT"
    echo "Valid options: staging, production"
    exit 1
fi

echo "Cluster: $CLUSTER"
echo "Service: $SERVICE"
echo "Task: $TASK_FAMILY"
echo "Image: $DOCKER_IMAGE"
echo ""

# Verificar se AWS CLI está instalado
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Please install it first."
    exit 1
fi

# Obter task definition atual
echo "📥 Fetching current task definition..."
TASK_DEFINITION=$(aws ecs describe-task-definition \
    --task-definition $TASK_FAMILY \
    --query 'taskDefinition' \
    --output json)

# Atualizar imagem na task definition
echo "🔄 Updating task definition with new image..."
NEW_TASK_DEF=$(echo $TASK_DEFINITION | jq --arg IMAGE "$DOCKER_IMAGE" \
    '.containerDefinitions[0].image=$IMAGE | 
     del(.taskDefinitionArn, .revision, .status, .requiresAttributes, .compatibilities, .registeredAt, .registeredBy)')

# Registrar nova task definition
echo "📝 Registering new task definition..."
NEW_TASK_INFO=$(aws ecs register-task-definition \
    --cli-input-json "$NEW_TASK_DEF")

NEW_REVISION=$(echo $NEW_TASK_INFO | jq -r '.taskDefinition.revision')
echo "✅ New task definition registered: $TASK_FAMILY:$NEW_REVISION"

# Atualizar service
echo "🔄 Updating ECS service..."
aws ecs update-service \
    --cluster $CLUSTER \
    --service $SERVICE \
    --task-definition $TASK_FAMILY:$NEW_REVISION \
    --force-new-deployment \
    --output json > /dev/null

echo "⏳ Waiting for service to stabilize..."
aws ecs wait services-stable \
    --cluster $CLUSTER \
    --services $SERVICE

echo ""
echo "✅ Deployment completed successfully!"
echo "Environment: $ENVIRONMENT"
echo "Task Definition: $TASK_FAMILY:$NEW_REVISION"
echo "Image: $DOCKER_IMAGE"
echo ""
echo "🔍 To check service status:"
echo "aws ecs describe-services --cluster $CLUSTER --services $SERVICE"
