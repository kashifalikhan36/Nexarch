"""
Azure OpenAI Integration with LangChain
Handles all AI-powered architecture generation
"""
from langchain_openai import AzureChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain.schema import SystemMessage, HumanMessage
from core.config import settings
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import logging
import json

logger = logging.getLogger(__name__)


class AIArchitectureRecommendation(BaseModel):
    """AI-generated architecture recommendation"""
    architecture_type: str = Field(description="Type of architecture (microservices, monolith, serverless, etc.)")
    recommended_patterns: List[str] = Field(description="Recommended design patterns")
    scalability_recommendations: List[str] = Field(description="How to improve scalability")
    performance_optimizations: List[str] = Field(description="Performance improvement suggestions")
    cost_optimizations: List[str] = Field(description="Cost reduction strategies")
    security_recommendations: List[str] = Field(description="Security improvements")
    technology_stack: Dict[str, str] = Field(description="Recommended technologies")
    migration_strategy: str = Field(description="Step-by-step migration approach")
    estimated_effort: str = Field(description="Estimated implementation effort")
    risk_assessment: str = Field(description="Risk analysis")


class AIWorkflowGeneration(BaseModel):
    """AI-generated workflow"""
    workflow_name: str
    workflow_type: str
    description: str
    steps: List[Dict[str, str]]
    dependencies: List[str]
    estimated_duration: str
    complexity_score: int
    risk_score: int
    benefits: List[str]
    challenges: List[str]
    prerequisites: List[str]


class AzureOpenAIClient:
    """Azure OpenAI client with LangChain integration"""
    
    def __init__(self):
        self.llm = None
        if settings.ENABLE_AI_GENERATION and settings.AZURE_OPENAI_API_KEY:
            self.llm = AzureChatOpenAI(
                azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
                api_key=settings.AZURE_OPENAI_API_KEY,
                api_version=settings.AZURE_OPENAI_API_VERSION,
                deployment_name=settings.AZURE_OPENAI_DEPLOYMENT,
                temperature=settings.AZURE_OPENAI_TEMPERATURE,
                max_tokens=settings.AZURE_OPENAI_MAX_TOKENS
            )
            logger.info("Azure OpenAI client initialized successfully")
        else:
            logger.warning("Azure OpenAI not configured - AI features will be disabled")
    
    async def generate_architecture_recommendation(
        self,
        architecture: Dict[str, Any],
        issues: List[Dict[str, Any]],
        constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive architecture recommendations using AI"""
        
        if not self.llm:
            logger.warning("Azure OpenAI not configured, returning fallback recommendations")
            return {
                "patterns": [
                    "Consider implementing Circuit Breaker pattern for resilience",
                    "Add API Gateway for centralized routing",
                    "Implement distributed caching with Redis",
                    "Use message queue for async processing"
                ],
                "recommendations": [
                    "Optimize database queries to reduce latency",
                    "Implement horizontal scaling for bottleneck services",
                    "Add health check endpoints",
                    "Enable distributed tracing"
                ]
            }
        
        # Build context from current architecture
        context = self._build_architecture_context(architecture, issues)
        
        # Create prompt
        prompt = f"""You are an expert software architect. Analyze this production architecture and provide recommendations.

**Current Architecture:**
{json.dumps(context['architecture'], indent=2)}

**Detected Issues:**
{json.dumps(context['issues'], indent=2)}

**Constraints:**
{json.dumps(constraints or {}, indent=2)}

Provide:
1. Top 5 design patterns to implement
2. Top 5 actionable recommendations
3. Critical improvements

Return as JSON with keys: patterns (list), recommendations (list), critical_improvements (list)
"""
        
        # Generate recommendation
        try:
            response = await self.llm.ainvoke(prompt)
            
            # Try to parse JSON
            try:
                result = json.loads(response.content)
            except json.JSONDecodeError:
                # Fallback parsing
                logger.warning("Failed to parse AI response as JSON, using fallback")
                result = {
                    "patterns": ["Circuit Breaker", "API Gateway", "Event Sourcing"],
                    "recommendations": ["Optimize performance", "Add caching", "Scale horizontally"],
                    "critical_improvements": ["Fix high latency", "Reduce error rate"]
                }
            
            logger.info("Successfully generated AI architecture recommendation")
            return result
        
        except Exception as e:
            logger.error(f"AI generation failed: {e}")
            return {
                "patterns": ["Error generating patterns"],
                "recommendations": ["Error generating recommendations"],
                "error": str(e)
            }
    
    async def generate_workflow_alternatives(
        self,
        architecture: Dict[str, Any],
        issues: List[Dict[str, Any]],
        goal: str = "balanced"
    ) -> Dict[str, Any]:
        """Generate multiple workflow alternatives using AI"""
        
        if not self.llm:
            logger.warning("Azure OpenAI not configured, returning empty workflows")
            return {"workflows": []}
        
        prompt = f"""Generate 3 workflow alternatives for this architecture:

Architecture: {json.dumps(architecture, indent=2)[:1000]}
Issues: {json.dumps(issues, indent=2)[:1000]}
Goal: {goal}

Generate workflows for:
1. Minimal change (low risk, quick)
2. Performance optimized (speed focus)
3. Cost efficient (reduce costs)

For each workflow provide JSON with:
- name (string)
- description (string)
- steps (array of dicts with "action" and "details")
- impact_score (float 0-1)

Return as JSON: {{"workflows": [...]}}
"""
        
        try:
            response = await self.llm.ainvoke(prompt)
            
            # Try to parse JSON
            try:
                result = json.loads(response.content)
                if "workflows" in result:
                    logger.info(f"Generated {len(result['workflows'])} AI workflow alternatives")
                    return result
            except json.JSONDecodeError:
                logger.warning("Failed to parse AI workflow response as JSON")
                pass
            
            # Fallback
            logger.warning("Failed to parse AI workflows, returning empty")
            return {"workflows": []}
        
        except Exception as e:
            logger.error(f"Workflow generation failed: {e}")
            return {"workflows": []}
    
    async def explain_decision(
        self,
        workflow: Dict[str, Any],
        architecture: Dict[str, Any]
    ) -> str:
        """Generate natural language explanation for a workflow decision"""
        
        if not self.llm:
            return "AI explanation not available - Azure OpenAI not configured"
        
        prompt = f"""
        Explain why this workflow was recommended for this architecture.
        Be specific about technical decisions and tradeoffs.
        
        Workflow: {json.dumps(workflow, indent=2)}
        Architecture: {json.dumps(architecture, indent=2)}
        
        Provide a clear, detailed explanation that a CTO or senior engineer would appreciate.
        """
        
        try:
            response = await self.llm.ainvoke(prompt)
            return response.content
        
        except Exception as e:
            logger.error(f"Explanation generation failed: {e}")
            return f"Error generating explanation: {str(e)}"
    
    async def generate_dashboard_insights(
        self,
        metrics: Dict[str, Any],
        trends: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate AI-powered dashboard insights and anomalies"""
        
        if not self.llm:
            return {"insights": [], "anomalies": [], "recommendations": []}
        
        prompt = f"""
        Analyze these metrics and trends to generate actionable insights:
        
        Metrics: {json.dumps(metrics, indent=2)}
        Trends: {json.dumps(trends, indent=2)}
        
        Identify:
        1. Critical anomalies that need immediate attention
        2. Positive trends worth noting
        3. Areas for improvement
        4. Proactive recommendations
        
        Return as JSON with keys: insights, anomalies, recommendations
        """
        
        try:
            response = await self.llm.ainvoke(prompt)
            insights = json.loads(response.content)
            return insights
        
        except Exception as e:
            logger.error(f"Insights generation failed: {e}")
            return {"insights": [], "anomalies": [], "recommendations": []}
    
    def _build_architecture_context(
        self,
        architecture: Dict[str, Any],
        issues: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Build context for AI prompt"""
        return {
            "architecture": {
                "services": len(architecture.get("nodes", [])),
                "dependencies": len(architecture.get("edges", [])),
                "complexity": architecture.get("metrics_summary", {}).get("avg_degree", 0),
                "error_rate": architecture.get("metrics_summary", {}).get("error_rate", 0),
                "avg_latency": architecture.get("metrics_summary", {}).get("avg_latency_ms", 0)
            },
            "issues": [
                {
                    "type": issue.get("type"),
                    "severity": issue.get("severity"),
                    "description": issue.get("description"),
                    "affected_nodes": issue.get("affected_nodes", [])
                }
                for issue in issues
            ]
        }
    
    def _parse_recommendation(self, content: str) -> AIArchitectureRecommendation:
        """Parse AI response into structured recommendation"""
        try:
            data = json.loads(content)
            return AIArchitectureRecommendation(**data)
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Failed to parse AI recommendation: {e}, using fallback")
            # Fallback to default
            return AIArchitectureRecommendation(
                architecture_type="microservices",
                recommended_patterns=["Circuit Breaker", "API Gateway", "Service Mesh"],
                scalability_recommendations=["Implement horizontal scaling", "Add caching layer"],
                performance_optimizations=["Database optimization", "CDN integration"],
                cost_optimizations=["Right-size instances", "Use spot instances"],
                security_recommendations=["Enable encryption", "Implement rate limiting"],
                technology_stack={"cache": "Redis", "queue": "RabbitMQ"},
                migration_strategy="Incremental migration with feature flags",
                estimated_effort="3-6 months",
                risk_assessment="Medium risk with proper testing"
            )
    
    def _parse_workflows(self, content: str) -> List[AIWorkflowGeneration]:
        """Parse AI response into workflows"""
        try:
            data = json.loads(content)
            return [AIWorkflowGeneration(**w) for w in data]
        except (json.JSONDecodeError, ValueError, TypeError) as e:
            logger.warning(f"Failed to parse AI workflows: {e}")
            return []


# Singleton instance
_ai_client = None

def get_ai_client() -> AzureOpenAIClient:
    """Get or create AI client singleton"""
    global _ai_client
    if _ai_client is None:
        _ai_client = AzureOpenAIClient()
    return _ai_client
