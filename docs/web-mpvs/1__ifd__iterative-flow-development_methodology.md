# Iterative Flow Development (IFD) Methodology

## Philosophy & Principles

### Core Philosophy
IFD is a development methodology that prioritizes maintaining developer flow state while building production-ready web applications through iterative enhancement. It leverages LLM capabilities as an intelligent coding partner while maintaining full developer control over architecture and UX decisions.

### Fundamental Principles

1. **Flow State Preservation**
   - Minimize context switching between tools
   - Maintain focus on UX and business logic
   - Let the LLM handle boilerplate and pattern implementation
   - Never let technical implementation block creative thinking

2. **Version Independence**
   - Each version is a complete, working system
   - No shared dependencies between versions
   - Clean migration paths when consolidating
   - Freedom to experiment without breaking existing work

3. **Real Data First**
   - No mocked data or stubs
   - Production API from day one
   - Immediate feedback with real systems
   - Cache-aware development

4. **Progressive Enhancement**
   - Start with core MVP (v0.1)
   - Add features incrementally
   - Consolidate only proven features
   - Maintain backward compatibility

5. **Zero External Dependencies**
   - Use native web platform features
   - Leverage modern browser capabilities
   - Reduce build complexity
   - Improve long-term maintainability

## The "Flow State" Approach

### Entering Flow
- Clear project vision before starting
- FastAPI backend ready with basic endpoints
- LLM primed with project context
- Development environment configured

### Maintaining Flow
- Describe features in natural language
- Let LLM generate initial implementations
- Focus on testing and UX refinement
- Iterate rapidly without overthinking

### Flow Patterns
```
Developer Intent → LLM Generation → Manual Integration → Test → Refine
         ↑                                                      ↓
         ←──────────────── Feedback Loop ──────────────────────↓
```

## Version Evolution Strategy

### Version Numbering
- **v0.1**: Core MVP with essential features
- **v0.2-v0.9**: Feature additions and refinements
- **v1.0**: Production consolidation of proven features

### Evolution Rules
1. Each version builds on concepts, not code
2. Features prove themselves before consolidation
3. Breaking changes are acceptable between versions
4. v1.0 represents the "best of" all experiments

## LLM Collaboration Patterns

### Effective Prompting
- Provide complete context in each session
- Reference existing patterns explicitly
- Specify technical constraints upfront
- Request self-contained components

### Air Gap Advantages
- Forces clear thinking about requirements
- Prevents over-reliance on LLM
- Maintains developer ownership
- Encourages batch processing of changes

### Integration Workflow
1. Design feature in your mind
2. Describe to LLM with context
3. Copy generated code to IDE
4. Test with real API
5. Refine and iterate

## Production Readiness Criteria

### Code Quality
- ✓ All components self-contained
- ✓ Consistent error handling
- ✓ Proper event cleanup
- ✓ Memory leak prevention
- ✓ Accessibility basics

### Architecture
- ✓ Clear separation of concerns
- ✓ Event-driven communication
- ✓ Stateless components where possible
- ✓ Predictable data flow

### Performance
- ✓ Lazy loading where appropriate
- ✓ Efficient DOM manipulation
- ✓ Debounced API calls
- ✓ Proper cache utilization

### Maintainability
- ✓ Clear file organization
- ✓ Consistent naming conventions
- ✓ Documented component interfaces
- ✓ Obvious extension points

## Success Metrics

### Productivity Indicators
- Lines of working code per hour
- Features completed per session
- Time from idea to implementation
- Bugs per feature ratio

### Quality Indicators
- Code reusability across versions
- Time to consolidate to v1.0
- API efficiency (cache hit rate)
- User-facing errors per session

### Developer Experience
- Flow state duration
- Context switch frequency
- Debugging time ratio
- Confidence in changes

## Common Pitfalls & Solutions

### Pitfall: Over-engineering early versions
**Solution**: Keep v0.1 deliberately simple

### Pitfall: Version dependency creep
**Solution**: Enforce strict isolation between versions

### Pitfall: LLM hallucinations in API calls
**Solution**: Test immediately with real backend

### Pitfall: Lost context between sessions
**Solution**: Maintain clear version documentation

### Pitfall: Premature consolidation
**Solution**: Wait for feature stability before v1.0