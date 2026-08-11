
{
  "signature": "EosFCokBCBAYAipAeGo5c3h9vfGj1MiNDX1aRA3NZCt/g4KZBbEaLe+zxUYcypG0F49IhTYD15n7hYeXgL+FwejMq68SYK3aDroYqzIPY2xhdWRlLXNvbm5ldC01OABCCHRoaW5raW5nWiQ5ZmZjMTZmNi1lZjQ3LTQ5NWItOTNjNS1iMjAyNzQ2MTljMzkSDFRVYtrHnYFsJxcKgBoMkqqlte80kN4fExMOIjDc0Du4kr05fqoiuDv0dcvkEhEjLnTQ8kWdW7izFWqVAFKbOVAwGKe1aA+XVwX70rYqrgP6wTVuIonPCyliXjIoJRUw6+jJl33a38TWDHQcHC5gRgzEAxrQ4YhlzhYtiGr5FOfKgBBZpbADB5P6h0BgXxeTYsNPHVzLPr+lCAJnw+9Q4hAOcJcruo2GaGLhAoJD6sR+3im8jfLgHiAj9EwW0tV3UsmBHo69D7FNpHYMzZEZtw3w7vs4UcHqllHG4mQpoKRKQjjKGH8dCMYT9f1cw1+F3jvCynJdHhnzMVk0wWGJ4v0AACU8BjctGdtz1Be6d9d/2rESrH3jkYjVkpF3JVBfN39gJH9iifVEC9u+pZf+ed6fGdr3KnY38HufKGmrdSB+kTvPVK2TaVSMgovB2KvnHPQsA/5gJ0uO9wpZd2HTy6gAz+ijvCjtk2EE16HwznoLtYuB1EmBg19TAAYj1g89Xx5ims4g4v8QoxZX6J+kitw0Lz+sMSl5Gg1ZBNyMvd+BPVQKUmD7Ct4wM+c81RRBy87IshtBGdT0/EJSgW37PYor24D/S/xl+une0k4RsVhEgG/+jfhpws39HM2OOjYiCNFo3RheKnI3V59ZbWnAsE74wFqbPFIm0tiedNloGAE=",
  "type": "thinking",
  "index": 0,
  "thinking": ""
}
# SportConnect — Sprint Task Breakdown

**Priority Legend:** 🔴 P0 (Blocker) | 🟡 P1 (High) | 🟢 P2 (Normal)

---

## Phase 0: Foundations (Do First — Everything Depends On These)

- [ ] 🔴 **[Shared]** Finalize API contract doc (DTOs, error shape, SSE event names) — *blocks all other work*
- [ ] 🔴 **[Shared]** Agree on CORS origin whitelist (local dev ports + prod domain)
- [ ] 🔴 **[Backend]** Set up Spring Boot 3.x project skeleton (Java 17), Spring Data MongoDB, connect to MongoDB Atlas
- [ ] 🔴 **[Backend]** Create `User` and `Event` collections/schemas + indexes (`2dsphere`, compound sport/date, organizerId)
- [ ] 🔴 **[Frontend]** Set up React 18 + Vite + TS project skeleton, routing shell (login/register/map/detail/profile pages)

---

## Phase 1: Auth (Backend-led, blocks most Frontend work)

### Backend
- [ ] 🔴 Implement `POST /api/auth/register` (BCrypt hashing, email uniqueness validation)
- [ ] 🔴 Implement `POST /api/auth/login` (JWT HS256 issuance, expiry config)
- [ ] 🔴 Spring Security filter chain: JWT parsing/validation, anonymous fallback (no 500 on bad/expired token)
- [ ] 🟡 Role model: `GUEST`/`USER`/`ORGANIZER` (derived, not stored)
- [ ] 🟡 Bucket4j IP-based rate limiting on `/auth/*` → 429 response
- [ ] 🟡 Bean Validation on auth DTOs (email format, password rules)

### Frontend — *depends on Backend auth endpoints being live*
- [ ] 🟡 Login/Register forms + client-side validation
- [ ] 🟡 JWT storage strategy (decide memory vs localStorage) + attach `Authorization` header via HTTP client interceptor
- [ ] 🟡 401 handling → graceful redirect to guest/read-only state (no crash loop)

---

## Phase 2: Event CRUD (Backend-led, Frontend blocked until DTOs stable)

### Backend
- [ ] 🔴 `POST /api/events` — create, Bean Validation on lat/lng/required fields
- [ ] 🔴 `GET /api/events` — list w/ filters (sportType, date range, geo radius via `$geoWithin`/`$near`)
- [ ] 🔴 `GET /api/events/{id}` — detail, guest-readable
- [ ] 🟡 `PUT /api/events/{id}` — ownership enforcement (403 if not organizer)
- [ ] 🟡 `DELETE /api/events/{id}` — soft-cancel (`status = CANCELLED`), triggers notification
- [ ] 🟡 `POST /api/events/{id}/join` — capacity check, 409 if full/already joined
- [ ] 🟡 `POST /api/events/{id}/leave` — 400 if not participant
- [ ] 🟢 Status transition logic (`OPEN`→`FULL`→`CANCELLED`/`COMPLETED`)
- [ ] 🟢 `GET /api/users/me/organized-events`, `GET /api/users/me/joined-events`
- [ ] 🟢 `GET/PUT /api/users/me` profile endpoints

### Frontend — *depends on Event API being stable*
- [ ] 🔴 Leaflet map integration: base map, geolocation w/ manual address fallback
- [ ] 🟡 Pin rendering + marker clustering (`react-leaflet-cluster`)
- [ ] 🟡 Popup with event summary + Join/View CTA
- [ ] 🟡 Filter panel (sport, date range, radius) wired via React Query to `GET /events`
- [ ] 🟡 Event detail page (join/leave actions, organizer edit/delete controls conditional on `isOwnedByCurrentUser`)
- [ ] 🟡 Create/Edit event form (mirrors backend validation, non-authoritative)
- [ ] 🟢 "My Events"/"My Games" profile views

---

## Phase 3: Realtime Notifications (Backend must ship stream endpoint before Frontend integrates)

### Backend
- [ ] 🟡 `SseEmitter` registry (per-user, in-memory map)
- [ ] 🟡 `GET /api/notifications/stream` — authenticated-only SSE endpoint
- [ ] 🟡 Heartbeat scheduler (~30s ping) to keep connections alive
- [ ] 🟡 Emit events on: create (`new-game`), join/leave (`roster-change`), cancel (`event-cancelled`)
- [ ] 🟢 Scheduled reminder job for "starting soon" notifications
- [ ] 🟢 Document single-instance SSE limitation (no Redis fan-out) in README/ADR

### Frontend — *depends on SSE endpoint live + Auth complete*
- [ ] 🟡 `EventSource` client, parse typed frames (`new-game`/`roster-change`/`event-cancelled`/`heartbeat`)
- [ ] 🟡 Wire SSE events → React Query cache invalidation / toast notifications
- [ ] 🟡 Visibility-based connection mgmt: close on tab hidden, reconnect w/ exponential backoff (max 5 attempts) on visible/network-drop

---

## Phase 4: Infra & Deployment (Parallel track, can start early)

- [ ] 🟡 **[Backend]** Dockerfile for backend service, Spring profiles (`dev`/`prod`) for env config
- [ ] 🟡 **[Frontend]** Dockerfile + Nginx config for static build serving
- [ ] 🟢 **[Shared]** `docker-compose.yml` wiring both containers + shared network + `.env`
- [ ] 🟢 **[Shared]** Reverse proxy / TLS termination config, route `/api/*` + `/notifications/*` to backend

---

## Phase 5: Polish & Hardening (Last, non-blocking)

- [ ] 🟢 **[Backend]** Standard error response shape across all endpoints
- [ ] 🟢 **[Frontend]** Error banner/toast mapping from standard error shape
- [ ] 🟢 **[Frontend]** Code-splitting, lazy-load map bundle (<2s load target on 4G)
- [ ] 🟢 **[Shared]** Consider generating TS types from OpenAPI spec for DTO alignment

---

## Dependency Summary

```
Phase 0 (Foundations)
   └─▶ Phase 1 (Auth: BE first, then FE)
          └─▶ Phase 2 (Event CRUD: BE first, then FE map/list/detail)
                 └─▶ Phase 3 (SSE: BE first, then FE realtime UI)

Phase 4 (Infra) — parallel, independent
Phase 5 (Polish) — after respective feature phases land
```

**Key blocking risks to flag in standup:**
- Frontend map/filter work cannot start meaningfully until Event DTO shape is locked (Phase 0/2 backend).
- Frontend SSE integration blocked until backend `SseEmitter` registry + stream endpoint deployed.
- Auth must be stable before either Event or Notification frontend work can be tested end-to-end.