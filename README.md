# INFO404-Alzheimer-MCP-Project
LLM + MCP system for analyzing Alzheimer’s gene expression and identifying drug targets

# AI-Assisted Identification of Alzheimer's Candidate Drug Targets

## Overview
This project uses an LLM connected to a biological database through MCP to analyze Alzheimer’s gene expression data and identify candidate drug targets.

## Tools Used
- LM Studio
- Qwen LLM
- MCP server
- Python
- PostgreSQL / SQLite
- Oracle APEX
- GEO dataset

## System Workflow
1. Load Alzheimer’s gene expression data
2. Query data using MCP tools
3. Identify genes with large AD vs Control expression differences
4. Compare candidate genes with known Alzheimer’s drug targets
5. Save results in database tables
6. Visualize results in Oracle APEX

## Main Database Tables
- brain_samples
- gene_expression
- drug_targets
- candidate_targets

## Agentic AI Component
The LLM acts as an agent by selecting MCP tools, querying the database, generating plots, and returning biological insights.

## Drug Discovery Connection
The system connects Alzheimer’s gene expression differences to known drug targets, supporting early-stage target discovery.

## Screenshots
Screenshots of plots and dashboard pages are included in the screenshots folder.
