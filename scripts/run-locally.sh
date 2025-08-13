#!/bin/bash
export LOCALSTACK_ENABLED=True
uvicorn mgraph_ai_service_llms.fast_api.lambda_handler:app --reload --host 0.0.0.0 --port 10011