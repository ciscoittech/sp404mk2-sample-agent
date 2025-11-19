# Feature Split: Open-Source vs Commercial

**Purpose:** Define clear boundaries between open-source functionality and commercial SaaS features
**Principle:** Open-source provides core value; commercial adds business features

---

## Open-Source Features (Public Repository)

### Core Features (Always Free)
- Audio processing and analysis (librosa-based)
- AI vibe analysis (users bring their own OpenRouter API keys)
- Sample management (single user, no auth)
- SP-404MK2 project builder
- CLI tools and batch processing
- React UI components (base)

**Why Open-Source:**
- Core intellectual value (attracts users)
- Community can improve algorithms
- Educational value
- No competitive advantage keeping private

---

## Commercial Features (Private Repository)

### Exclusive to SaaS
- User authentication and authorization
- Multi-user team management
- Subscription and billing (Stripe integration)
- API quota enforcement
- Admin dashboard and analytics
- Rate limiting and DDoS protection
- Commercial SaaS hosting (zero setup)

**Why Commercial:**
- Multi-user infrastructure costs money
- Stripe integration requires business entity
- Payment processing has legal requirements
- Support and reliability are paid services

---

## Git Submodule Strategy

```bash
# Production always pins to stable tags
open-source/ → v1.2.3 (tagged release)

# Development can track latest
open-source/ → main branch (with caution)
```

**Contributing Back to Open-Source:**
- Bug fixes → Submit PR upstream (MIT license)
- Commercial features → Keep in private repo only
- Improvements → Share with community where possible

---

## Summary Table

| Feature | Open-Source | Commercial | Reason |
|---------|-------------|------------|--------|
| Audio Analysis | ✅ Full | ✅ Proxied | Core value |
| AI Vibe Analysis | ✅ BYOK | ✅ Pooled keys | Open enables power users |
| Sample CRUD | ✅ Single user | ✅ Multi-tenant | Public works solo, SaaS isolates users |
| Project Builder | ✅ Full | ✅ Same | Hardware integration benefits everyone |
| CLI Tools | ✅ Full | ❌ N/A | Power users want CLI |
| React UI | ✅ Base | ✅ SaaS UI | Components public, business logic private |
| Authentication | ❌ None | ✅ Required | Multi-user needs auth |
| Subscriptions | ❌ None | ✅ Stripe | Payment processing is business core |
| Quotas | ❌ None | ✅ Enforced | Prevents abuse, enables pricing tiers |
| Teams | ❌ None | ✅ Full | Enterprise feature |
| Admin Dashboard | ❌ None | ✅ Full | Business metrics are proprietary |
| Rate Limiting | ❌ None | ✅ Edge (Cloudflare) | DDoS protection requires infrastructure |
| Analytics | ❌ None | ✅ Full | Usage tracking for billing |

---

## Philosophy

**Open-source should be fully functional for self-hosters.** Commercial should add convenience and enterprise features that justify subscription, not cripple the free version.
