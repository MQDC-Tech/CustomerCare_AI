"""
Distributed Multi-Agent Deployment Configuration
Deploy agents as separate remote services with automatic discovery
"""

import os
from typing import Dict, List, Any
import yaml


def create_distributed_deployment_configs():
    """
    Create deployment configurations for running agents as separate remote services.
    Each agent tier can be deployed independently and will discover others via A2A protocol.
    """
    
    # Configuration for distributed agent deployment
    deployment_configs = {
        "core_agents": {
            "deployment_type": "remote_service",
            "agents": ["coordinator", "llm_agent", "memory_agent", "notifications"],
            "discovery_mode": "automatic",
            "communication_protocol": "A2A",
            "scaling": {
                "min_instances": 1,
                "max_instances": 5,
                "auto_scale": True
            },
            "endpoints": {
                "coordinator": "https://core-coordinator-service.run.app",
                "llm_agent": "https://core-llm-service.run.app", 
                "memory_agent": "https://core-memory-service.run.app",
                "notifications": "https://core-notifications-service.run.app"
            }
        },
        
        "context_agent": {
            "deployment_type": "remote_service",
            "agents": ["context_agent"],
            "discovery_mode": "automatic",
            "communication_protocol": "A2A",
            "scaling": {
                "min_instances": 1,
                "max_instances": 3,
                "auto_scale": True
            },
            "endpoints": {
                "context_agent": "https://context-service.run.app"
            }
        },
        
        "domain_agents": {
            "deployment_type": "remote_service", 
            "agents": ["domain_realestate"],
            "discovery_mode": "automatic",
            "communication_protocol": "A2A",
            "scaling": {
                "min_instances": 2,
                "max_instances": 10,
                "auto_scale": True
            },
            "endpoints": {
                "domain_realestate": "https://domain-realestate-service.run.app"
            }
        }
    }
    
    return deployment_configs


def create_agent_discovery_config():
    """
    Create agent discovery configuration for automatic service discovery.
    """
    
    discovery_config = {
        "discovery": {
            "mode": "automatic",
            "protocol": "A2A",
            "registry": {
                "type": "google_cloud_service_directory",
                "project_id": "${GOOGLE_CLOUD_PROJECT}",
                "region": "us-central1"
            },
            "health_check": {
                "enabled": True,
                "interval_seconds": 30,
                "timeout_seconds": 10
            },
            "load_balancing": {
                "strategy": "round_robin",
                "failover": True,
                "circuit_breaker": True
            }
        },
        
        "agent_registry": {
            "core_agents": {
                "service_name": "core-agents-service",
                "namespace": "customer-care",
                "agents": ["coordinator", "llm_agent", "memory_agent", "notifications"]
            },
            "context_agent": {
                "service_name": "context-agent-service", 
                "namespace": "customer-care",
                "agents": ["context_agent"]
            },
            "domain_agents": {
                "service_name": "domain-agents-service",
                "namespace": "customer-care", 
                "agents": ["domain_realestate"]
            }
        },
        
        "communication": {
            "a2a_protocol": {
                "enabled": True,
                "encryption": True,
                "authentication": "service_account",
                "timeout_seconds": 30,
                "retry_attempts": 3
            },
            "service_mesh": {
                "enabled": True,
                "istio_integration": True,
                "traffic_management": True
            }
        }
    }
    
    return discovery_config


def create_cloud_run_deployment_yamls():
    """
    Create Cloud Run deployment configurations for each agent tier.
    """
    
    # Core Agents Cloud Run Service
    core_agents_yaml = {
        "apiVersion": "serving.knative.dev/v1",
        "kind": "Service",
        "metadata": {
            "name": "core-agents-service",
            "namespace": "customer-care",
            "annotations": {
                "run.googleapis.com/ingress": "internal-and-cloud-load-balancing",
                "run.googleapis.com/execution-environment": "gen2"
            }
        },
        "spec": {
            "template": {
                "metadata": {
                    "annotations": {
                        "autoscaling.knative.dev/minScale": "1",
                        "autoscaling.knative.dev/maxScale": "5",
                        "run.googleapis.com/cpu-throttling": "false"
                    }
                },
                "spec": {
                    "containerConcurrency": 100,
                    "containers": [{
                        "image": "gcr.io/${PROJECT_ID}/core-agents:latest",
                        "ports": [{"containerPort": 8080}],
                        "env": [
                            {"name": "ADK_AGENT_MANIFEST", "value": "manifests/core_agent.manifest.yaml"},
                            {"name": "A2A_DISCOVERY_ENABLED", "value": "true"},
                            {"name": "GOOGLE_CLOUD_PROJECT", "valueFrom": {"secretKeyRef": {"name": "project-config", "key": "project_id"}}}
                        ],
                        "resources": {
                            "limits": {"cpu": "2", "memory": "4Gi"},
                            "requests": {"cpu": "1", "memory": "2Gi"}
                        }
                    }]
                }
            }
        }
    }
    
    # Context Agent Cloud Run Service  
    context_agent_yaml = {
        "apiVersion": "serving.knative.dev/v1",
        "kind": "Service", 
        "metadata": {
            "name": "context-agent-service",
            "namespace": "customer-care"
        },
        "spec": {
            "template": {
                "metadata": {
                    "annotations": {
                        "autoscaling.knative.dev/minScale": "1",
                        "autoscaling.knative.dev/maxScale": "3"
                    }
                },
                "spec": {
                    "containers": [{
                        "image": "gcr.io/${PROJECT_ID}/context-agent:latest",
                        "ports": [{"containerPort": 8080}],
                        "env": [
                            {"name": "ADK_AGENT_MANIFEST", "value": "manifests/context_agent.manifest.yaml"},
                            {"name": "A2A_DISCOVERY_ENABLED", "value": "true"}
                        ]
                    }]
                }
            }
        }
    }
    
    # Domain Agent Cloud Run Service
    domain_agent_yaml = {
        "apiVersion": "serving.knative.dev/v1", 
        "kind": "Service",
        "metadata": {
            "name": "domain-realestate-service",
            "namespace": "customer-care"
        },
        "spec": {
            "template": {
                "metadata": {
                    "annotations": {
                        "autoscaling.knative.dev/minScale": "2",
                        "autoscaling.knative.dev/maxScale": "10"
                    }
                },
                "spec": {
                    "containers": [{
                        "image": "gcr.io/${PROJECT_ID}/domain-realestate:latest",
                        "ports": [{"containerPort": 8080}],
                        "env": [
                            {"name": "ADK_AGENT_MANIFEST", "value": "manifests/domain_realestate.manifest.yaml"},
                            {"name": "A2A_DISCOVERY_ENABLED", "value": "true"},
                            {"name": "A2A_REMOTE_AGENTS", "value": "context_agent,llm_agent,memory_agent,notifications"}
                        ]
                    }]
                }
            }
        }
    }
    
    return {
        "core_agents": core_agents_yaml,
        "context_agent": context_agent_yaml, 
        "domain_agent": domain_agent_yaml
    }


def create_dockerfile_for_distributed_deployment():
    """
    Create Dockerfiles for containerizing each agent tier.
    """
    
    # Base Dockerfile for all agents
    base_dockerfile = """
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy agent code
COPY agents/ ./agents/
COPY manifests/ ./manifests/
COPY utils/ ./utils/
COPY framework/ ./framework/

# Set environment variables
ENV PYTHONPATH=/app
ENV ADK_DISCOVERY_MODE=automatic
ENV A2A_PROTOCOL_ENABLED=true

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8080/health || exit 1

# Start agent service
CMD ["adk", "serve", "--manifest", "${ADK_AGENT_MANIFEST}", "--port", "8080", "--host", "0.0.0.0"]
"""
    
    return base_dockerfile


def create_deployment_scripts():
    """
    Create deployment scripts for distributed agent setup.
    """
    
    # Deploy script
    deploy_script = """#!/bin/bash
set -e

echo "🚀 Deploying Distributed Multi-Agent System"

# Set project variables
export PROJECT_ID=${GOOGLE_CLOUD_PROJECT}
export REGION=us-central1

# Build and push container images
echo "📦 Building container images..."
docker build -t gcr.io/${PROJECT_ID}/core-agents:latest -f deployment/Dockerfile.core .
docker build -t gcr.io/${PROJECT_ID}/context-agent:latest -f deployment/Dockerfile.context .
docker build -t gcr.io/${PROJECT_ID}/domain-realestate:latest -f deployment/Dockerfile.domain .

docker push gcr.io/${PROJECT_ID}/core-agents:latest
docker push gcr.io/${PROJECT_ID}/context-agent:latest  
docker push gcr.io/${PROJECT_ID}/domain-realestate:latest

# Deploy to Cloud Run
echo "☁️  Deploying to Cloud Run..."
gcloud run deploy core-agents-service \\
    --image gcr.io/${PROJECT_ID}/core-agents:latest \\
    --region ${REGION} \\
    --platform managed \\
    --allow-unauthenticated \\
    --set-env-vars="A2A_DISCOVERY_ENABLED=true"

gcloud run deploy context-agent-service \\
    --image gcr.io/${PROJECT_ID}/context-agent:latest \\
    --region ${REGION} \\
    --platform managed \\
    --allow-unauthenticated \\
    --set-env-vars="A2A_DISCOVERY_ENABLED=true"

gcloud run deploy domain-realestate-service \\
    --image gcr.io/${PROJECT_ID}/domain-realestate:latest \\
    --region ${REGION} \\
    --platform managed \\
    --allow-unauthenticated \\
    --set-env-vars="A2A_DISCOVERY_ENABLED=true,A2A_REMOTE_AGENTS=context_agent,llm_agent,memory_agent,notifications"

echo "✅ Distributed deployment complete!"
echo "🔗 Agents will automatically discover each other via A2A protocol"
"""
    
    return deploy_script


def create_agent_discovery_test():
    """
    Create test script to verify agent discovery and communication.
    """
    
    test_script = """
import asyncio
import aiohttp
import json
from typing import Dict, Any


async def test_agent_discovery():
    \"\"\"Test that distributed agents can discover and communicate with each other.\"\"\"
    
    # Agent service endpoints (will be auto-discovered in production)
    agent_endpoints = {
        "domain_realestate": "https://domain-realestate-service.run.app",
        "context_agent": "https://context-agent-service.run.app", 
        "core_agents": "https://core-agents-service.run.app"
    }
    
    print("🔍 Testing Agent Discovery and A2A Communication")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        
        # Test 1: Check agent health and discovery
        for agent_name, endpoint in agent_endpoints.items():
            try:
                async with session.get(f"{endpoint}/health") as response:
                    if response.status == 200:
                        print(f"✅ {agent_name}: Online and discoverable")
                    else:
                        print(f"❌ {agent_name}: Health check failed")
            except Exception as e:
                print(f"❌ {agent_name}: Connection failed - {e}")
        
        # Test 2: Test A2A communication flow
        print("\\n🔗 Testing A2A Communication Flow")
        
        # Send request to domain agent, which should trigger A2A calls
        test_request = {
            "user_id": "test_user_123",
            "inquiry": "I'm looking for a 3-bedroom house",
            "test_a2a": True
        }
        
        try:
            async with session.post(
                f"{agent_endpoints['domain_realestate']}/process_inquiry",
                json=test_request
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ A2A Communication Flow: Success")
                    print(f"   - A2A Calls Made: {result.get('a2a_calls', 0)}")
                    print(f"   - Agents Contacted: {result.get('agents_contacted', [])}")
                else:
                    print(f"❌ A2A Communication Flow: Failed ({response.status})")
                    
        except Exception as e:
            print(f"❌ A2A Communication Test Failed: {e}")
        
        # Test 3: Test agent registry and discovery
        print("\\n📋 Testing Agent Registry")
        
        try:
            async with session.get(f"{agent_endpoints['core_agents']}/agents/registry") as response:
                if response.status == 200:
                    registry = await response.json()
                    print(f"✅ Agent Registry: {len(registry.get('agents', []))} agents registered")
                    for agent in registry.get('agents', []):
                        print(f"   - {agent['name']}: {agent['status']}")
                else:
                    print(f"❌ Agent Registry: Failed to retrieve")
        except Exception as e:
            print(f"❌ Agent Registry Test Failed: {e}")
    
    print("\\n🎯 Distributed Agent Testing Complete!")


if __name__ == "__main__":
    asyncio.run(test_agent_discovery())
"""
    
    return test_script


if __name__ == "__main__":
    print("🏗️  Creating Distributed Multi-Agent Deployment Configuration")
    
    # Create deployment configs
    configs = create_distributed_deployment_configs()
    discovery_config = create_agent_discovery_config()
    cloud_run_yamls = create_cloud_run_deployment_yamls()
    dockerfile = create_dockerfile_for_distributed_deployment()
    deploy_script = create_deployment_scripts()
    test_script = create_agent_discovery_test()
    
    print(f"✅ Distributed deployment configuration created!")
    print(f"📊 Agent Tiers: {len(configs)}")
    print(f"🔗 A2A Protocol: Enabled with automatic discovery")
    print(f"☁️  Cloud Run Services: {len(cloud_run_yamls)}")
    print(f"🧪 Discovery Tests: Ready")
    
    print(f"\\n🚀 Ready for distributed deployment:")
    print(f"   1. Each agent tier runs as separate Cloud Run service")
    print(f"   2. Automatic service discovery via A2A protocol")
    print(f"   3. Load balancing and auto-scaling enabled")
    print(f"   4. Fault-tolerant inter-agent communication")
