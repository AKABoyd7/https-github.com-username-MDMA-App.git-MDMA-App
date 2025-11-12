# Project Jareth v1 - Architecture Design Document

## Project Overview
**Project Jareth v1** - Advanced Conversational AI System with Memory Management
**Codename**: MDMA App (Memory-Driven Multi-Agent Application)

## Version History

### Version 1 (Legacy)
- **Architecture**: CLI-based Langgraph agent
- **Model**: ChatOllama (Llama 3)
- **Features**:
  - Conversational AI with memory
  - State management using Langgraph
  - Single-user CLI interface
  - Memory persistence with MemorySaver

### Version 2 (Current - Hybrid Architecture) ✅
- **Architecture**: FastAPI + Langgraph Integration
- **Model**: Meta Llama 3.3 70B Instruct
- **Decision**: **Option C - Combined Features**

## Architecture Decision Record (ADR)

### Decision: Hybrid Architecture (FastAPI + Langgraph)

**Date**: 2025-11-12

**Status**: ✅ Accepted

**Context**:
- Version 1 had excellent memory management but lacked API access
- Version 2 had REST API but no conversation memory
- Need production-ready solution supporting multiple users

**Decision**:
We chose to combine both architectures into a unified system.

**Rationale**:

#### 1. Production-Ready Architecture
```
┌─────────────────────────────────────┐
│      FastAPI REST Server            │
├─────────────────────────────────────┤
│  ┌──────────────────────────────┐  │
│  │   Langgraph State Manager    │  │
│  │   - Conversation Memory      │  │
│  │   - Multi-thread Support     │  │
│  │   - Context Awareness        │  │
│  └──────────────────────────────┘  │
├─────────────────────────────────────┤
│  Ollama Backend (Llama 3.3 70B)    │
└─────────────────────────────────────┘
```

#### 2. Feature Matrix Comparison

| Feature | V1 Only | V2 Only | Combined ✅ |
|---------|---------|---------|-------------|
| Memory Management | ✅ | ❌ | ✅ |
| REST API | ❌ | ✅ | ✅ |
| Multi-user Support | ❌ | ✅ | ✅ |
| Health Monitoring | ❌ | ✅ | ✅ |
| Network Repair | ❌ | ✅ | ✅ |
| Conversation Context | ✅ | ❌ | ✅ |
| Production Ready | ❌ | ⚠️ | ✅✅ |

#### 3. Benefits

**Technical Benefits**:
- ✅ Stateful conversations across API calls
- ✅ Multi-user conversation isolation
- ✅ RESTful API for integration
- ✅ Scalable architecture
- ✅ Built-in monitoring and health checks

**Business Benefits**:
- ✅ Web application backend ready
- ✅ Mobile app integration support
- ✅ Third-party service integration (Discord, Telegram, etc.)
- ✅ Future-proof for microservices
- ✅ Single codebase = easier maintenance

#### 4. Trade-offs

**Pros**:
- Best of both worlds
- Production-ready from day 1
- Scalable to multiple users
- Industry-standard tech stack

**Cons**:
- Slightly more complex than separate versions
- Requires understanding both FastAPI and Langgraph
- Higher memory usage for maintaining conversation states

**Verdict**: Pros far outweigh cons for production use.

## System Architecture

### Core Components

#### 1. FastAPI Server
- **Port**: 8500
- **Host**: 0.0.0.0 (all interfaces)
- **Purpose**: REST API interface for all operations

#### 2. Langgraph State Manager
- **Purpose**: Conversation memory and state management
- **Storage**: MemorySaver (in-memory with optional persistence)
- **Thread Management**: UUID-based conversation threads

#### 3. Ollama Backend
- **Model**: meta-llama-3.3-70b-instruct
- **Endpoint**: http://localhost:11434
- **GPU**: NVIDIA RTX 3090 Ti (CUDA backend)

#### 4. Auto-Monitoring System
- **CPU/RAM Monitoring**: Every 60 seconds
- **Auto-healing**: Triggers cleanup at 90% threshold
- **Background Thread**: Daemon process

### API Endpoints

#### Health & Monitoring
```
GET /health
Response: {
  "mode": "local",
  "model": "Meta Llama-3.3-70B-Instruct",
  "gpu": "NVIDIA RTX 3090 Ti",
  "cpu": 15.2,
  "ram": 45.3,
  "platform": "Linux"
}
```

#### Network Operations
```
POST /repair_network
Response: {
  "repair_log": [...]
}
```

#### Chat Operations (New!)
```
POST /chat
Body: {
  "message": "Hello, who are you?",
  "thread_id": "user-123" (optional)
}
Response: {
  "response": "I am Jareth AiNV...",
  "thread_id": "user-123"
}
```

```
GET /conversations
Response: {
  "conversations": [...]
}
```

```
GET /conversation/{thread_id}
Response: {
  "thread_id": "user-123",
  "messages": [...]
}
```

```
DELETE /conversation/{thread_id}
Response: {
  "status": "deleted"
}
```

## Configuration

### config_local.yml
```yaml
mode: local
model: meta-llama-3.3-70b-instruct
gpu_backend: cuda
device: "NVIDIA RTX 3090 Ti"
nvapi_token: "nvapi-***" (secured)
auto_heal: true
debug_tools: true
```

## Dependencies

### Production Dependencies
```
fastapi          - Web framework
uvicorn          - ASGI server
psutil           - System monitoring
torch            - GPU detection
requests         - HTTP client
langchain        - LLM framework
langgraph        - State management
langchain-community - Ollama integration
pyyaml           - Config parsing
```

## Deployment

### Local Development
```bash
# PowerShell
./run.ps1
```

### Production Deployment
```bash
# Linux/Unix
python main.py
```

### Docker (Future)
```dockerfile
# TODO: Create Dockerfile
# - Multi-stage build
# - GPU support
# - Volume for config
```

## Security Considerations

1. **API Token**: nvapi_token should be in environment variables
2. **Network Repair**: Requires admin privileges on Windows
3. **Rate Limiting**: TODO - Add rate limiting middleware
4. **Authentication**: TODO - Add API key authentication

## Performance

### Expected Metrics
- **Response Time**: < 2s for simple queries
- **Throughput**: ~10 concurrent conversations
- **Memory**: ~4GB base + ~500MB per active conversation
- **GPU**: 100% utilization during inference

### Optimization Opportunities
1. Response streaming for real-time UX
2. Conversation pruning for old threads
3. Response caching for common queries
4. Load balancing for multiple GPU instances

## Future Enhancements

### Phase 1 (Immediate)
- [ ] Streaming responses
- [ ] API authentication
- [ ] Rate limiting
- [ ] Error handling improvements

### Phase 2 (Near-term)
- [ ] Web UI dashboard
- [ ] Conversation export (JSON/CSV)
- [ ] Analytics and usage statistics
- [ ] Multiple AI personalities

### Phase 3 (Long-term)
- [ ] Multi-model support (GPT-4, Claude, etc.)
- [ ] Distributed deployment
- [ ] Real-time collaboration
- [ ] Plugin system

## Conclusion

The hybrid architecture (Option C) provides the best foundation for a production-ready AI application. By combining FastAPI's robust API framework with Langgraph's sophisticated memory management, we achieve:

✅ **Scalability** - Ready for multiple users
✅ **Maintainability** - Single, unified codebase
✅ **Extensibility** - Easy to add new features
✅ **Production-Ready** - Industry-standard architecture

This design positions Project Jareth v1 as a professional-grade conversational AI system suitable for real-world deployments.

---

**Last Updated**: 2025-11-12
**Version**: 2.0
**Author**: Claude AI
**Status**: ✅ Active Development
