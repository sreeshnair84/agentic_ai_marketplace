output.tf

output "agent_service_url" {
  value = "http://${aws_api_gateway.example.invoke_url}/api/v1/agents"
}

output "tool_service_url" {
  value = "http://${aws_api_gateway.example.invoke_url}/api/tools"
}

output "rag_service_url" {
  value = "http://${aws_api_gateway.example.invoke_url}/api/rag"
}

output "sql_tool_service_url" {
  value = "http://${aws_api_gateway.example.invoke_url}/api/sql"
}

output "observability_service_url" {
  value = "http://${aws_api_gateway.example.invoke_url}/api/observability"
}

output "workflow_service_url" {
  value = "http://${aws_api_gateway.example.invoke_url}/api/workflows"
}