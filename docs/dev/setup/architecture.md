# Architecture Overview

## System Components

```mermaid
graph TB
    subgraph "API Gateway Layer"
        CF[CloudFront CDN]
        AG[API Gateway/Lambda URL]
    end
    
    subgraph "Application Layer"
        LF[Lambda Function]
        FA[FastAPI Application]
        RT[Route Handlers]
    end
    
    subgraph "Service Layer"
        SL[Service Logic]
        TS[Type Safety]
        VL[Validation]
    end
    
    CF --> AG
    AG --> LF
    LF --> FA
    FA --> RT
    RT --> SL
    SL --> TS
    SL --> VL


## Request Flow

 - **CloudFront** - Caches and distributes content globally
 - **Lambda Function URL** - Provides HTTPS endpoint
 - **Mangum Adapter** - Converts AWS Lambda events to ASGI
 - **FastAPI** - Handles routing and request processing
 - **Service Layer** - Business logic with type safety