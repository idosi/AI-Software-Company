
{
  "signature": "EsQCCokBCBAYAipAm7XfoF/oIRx35E81/tDxG80wswbDHr61wcGU2dWIo/8xjnLt9zzbo+XVg0zXNlFNegrZz5gltWQYvkpK74BjmjIPY2xhdWRlLXNvbm5ldC01OABCCHRoaW5raW5nWiQ5ZmZjMTZmNi1lZjQ3LTQ5NWItOTNjNS1iMjAyNzQ2MTljMzkSDE42fosXZna1qSU35RoMiWsuI4xAcaclRY+fIjCvUx/Us/tg2j3w/llZbLNs2dwlk6ihoQFQ/bpjSX6qrofoM2Z7DbCu6MREoUzilu4qaBAKS4NxmVwritSQ75vtgnJrtik0vod9sMAxVc+3XDrEWrAjZrVQAZeUu4jirJ79pZssFRwblU8sqxYzXLZwW8WSkttmxJcYMR9WFPire0wmknIyGZh4foO6FGeFzib4kDGXC+rz2BA2GAE=",
  "type": "thinking",
  "index": 0,
  "thinking": ""
}
# SportConnect — Technical Architecture Document

## 1. High-Level System Architecture

```
                                   ┌─────────────────────────┐
                                   │      Browser Client      │
                                   │  React SPA + Leaflet Map │
                                   └────────────┬─────────────┘
                                                │ HTTPS
                       ┌────────────────────────┼─────────────────────────┐
                       │                        │                         │
                REST calls (JSON)      SSE stream (text/event-stream)     │ Static assets
                       │                        │                         │
                       ▼                        ▼                         ▼
              ┌──────────────────────────────────────────┐      ┌──────────────────┐
              │           Spring Boot Backend             │      │  Nginx (static)   │
              │  ┌────────────┐  ┌──────────────────────┐ │      │  React build       │
              │  │ Security   │  │ SseEmitter Registry   │ │      └──────────────────┘
              │  │ Filter     │  │ (per-user, in-memory) │ │
              │  │ Chain(JWT) │  └──────────────────────┘ │
              │  ├────────────┤                            │
              │  │ Controllers│  Auth / Events / Notif /  │
              │  │            │  Users                     │
              │  ├────────────┤                            │
              │  │ Services   │  business logic, ownership │
              │  │            │  checks, capacity checks   │
              │  ├────────────┤                            │
              │  │ Repositories│ Spring Data MongoDB        │
              │  └────────────┘                            │
              └───────────────────────┬────────────────────┘
                                      │
                                      ▼
                          ┌───────────────────────┐
                          │   MongoDB Atlas         │
                          │   (2dsphere geo index)  │
                          └───────────────────────┘
```

**Component interaction flow (join-event example):**
1. Client sends `POST /events/{id}/join` with `Authorization: Bearer <JWT>`.
2. Security filter validates JWT → sets `Authentication` in `SecurityContext` (or falls back to anonymous — endpoint rejects if not authenticated).
3. `EventService` loads event, checks capacity, adds participant, persists via `EventRepository`.
4. `EventService` publishes a domain event → `NotificationService` pushes SSE message to affected users' `SseEmitter` (organizer + other participants) via the in-memory emitter registry.
5. Response returned to caller; other connected clients receive async SSE push independently.

**Deployment topology (MVP, single instance):**
- Docker container `backend` (Spring Boot, port 8080)
- Docker container `frontend` (Nginx serving React static build, port 80/443)
- MongoDB Atlas — external managed service, no container
- `docker-compose.yml` wires both containers + shared network + `.env` for secrets/config
- Reverse proxy (Nginx or cloud LB) terminates TLS in production, routes `/api/*` and `/notifications/*` to backend, everything else to frontend static build

---

## 2. Tech Stack & Justification

| Layer | Choice | Justification |
|---|---|---|
| **Backend** | Spring Boot 3.x (Java 17+) | Mature Spring Security for JWT + role-based auth, first-class SseEmitter support for SSE without extra libs, Spring Data MongoDB for geo-queries, strong DTO validation via Bean Validation. |
| **Frontend** | React 18 + Vite + TypeScript | Fast dev/build (Vite < 2s target load), TS for DTO contract safety with backend, component model fits map/filter/list UI. |
| **Map** | Leaflet + react-leaflet + marker clustering plugin (`react-leaflet-cluster`) | Free/open-source, no API-key billing risk (vs Google Maps), lightweight, good clustering ecosystem, sufficient for pin+popup MVP needs. |
| **State/Data fetching** | React Query (TanStack Query) | Built-in caching, refetch-on-window-focus works well combined with SSE-triggered cache invalidation, reduces boilerplate vs raw fetch/hooks. |
| **Realtime** | Server-Sent Events (native `EventSource`) | Simpler than WebSockets for unidirectional server→client push; native browser reconnection primitive; fits "no native app" + notification-only use case; avoids Socket.io/WS infra complexity for MVP. |
| **Database** | MongoDB Atlas | Document model fits Event entity (nested participant list) naturally; native `2dsphere` geo-index supports `$near`/`$geoWithin` radius & bounding-box queries required by spec; managed Atlas removes ops burden. |
| **Auth** | JWT (HS256), Spring Security filter chain | Stateless → horizontally scalable REST tier; no server-side session store needed. |
| **Password hashing** | BCrypt (Spring Security `BCryptPasswordEncoder`, strength 10) | Explicit PRD requirement, industry standard. |
| **Infra** | Docker + docker-compose | Explicit PRD requirement; separate backend/frontend containers, env-based config via `.env`/Spring profiles. |
| **Rate limiting** | Bucket4j (in-memory, IP-keyed) on `/auth/*` | Lightweight, no external dependency (Redis) needed for single-instance MVP. |

**Explicitly deferred (per PRD Out-of-Scope):** Redis pub/sub for SSE fan-out, refresh token rotation, OAuth/social login, WebSocket clustering — documented as post-MVP scaling path, not built now.

---

## 3. Data Model / Key Entities

### `User`
```json
{
  "_id": "ObjectId",
  "email": "string (unique, indexed)",
  "passwordHash": "string",
  "displayName": "string",
  "roles": ["USER"],               // GUEST implicit for unauthenticated, ORGANIZER derived not stored
  "preferredSports": ["FOOTBALL", "TENNIS"],
  "homeLocation": { "type": "Point", "coordinates": [lng, lat] },
  "createdAt": "ISODate",
  "updatedAt": "ISODate"
}
```

### `Event`
```json
{
  "_id": "ObjectId",
  "sportType": "FOOTBALL | BASKETBALL | TENNIS | ...",
  "title": "string",
  "description": "string",
  "location": {
    "type": "Point",
    "coordinates": [lng, lat]        // 2dsphere indexed
  },
  "addressLabel": "string",
  "startTime": "ISODate",
  "durationMinutes": "int",
  "maxParticipants": "int",
  "participantIds": ["ObjectId", "..."],
  "organizerId": "ObjectId",
  "status": "OPEN | FULL | CANCELLED | COMPLETED",
  "createdAt": "ISODate",
  "updatedAt": "ISODate"
}
```
Index: `{ location: "2dsphere" }`, `{ sportType: 1, startTime: 1 }`, `{ organizerId: 1 }`.

### `NotificationMessage` (transient, not persisted in MVP — pushed live only; optionally logged for debugging)
```json
{
  "type": "NEW_GAME_MATCH | ROSTER_CHANGE | EVENT_CANCELLED | EVENT_EDITED | EVENT_REMINDER",
  "eventId": "ObjectId",
  "payload": { "...": "type-specific fields" },
  "timestamp": "ISODate"
}
```

**Relationships:** `Event.organizerId` → `User._id` (1:N). `Event.participantIds` → `User._id` (N:N, embedded array — acceptable given MVP scale ≤500 concurrent users, avoids join complexity).

---

## 4. API Contract

Base path: `/api`. All authenticated endpoints require `Authorization: Bearer <JWT>`.

### Auth
```
POST /api/auth/register
Request:  { "email": "string", "password": "string", "displayName": "string" }
Response: 201 { "id": "string", "email": "string", "displayName": "string" }

POST /api/auth/login
Request:  { "email": "string", "password": "string" }
Response: 200 { "accessToken": "string", "expiresIn": 3600, "user": { "id", "email", "displayName" } }
Errors:   401 invalid credentials, 429 rate-limited
```

### Events
```
POST /api/events                          [USER+]
Request:
{
  "sportType": "FOOTBALL",
  "title": "5-a-side at Riverside Park",
  "description": "string",
  "location": { "lat": 48.8566, "lng": 2.3522 },
  "addressLabel": "Riverside Park, Paris",
  "startTime": "2025-06-01T18:00:00Z",
  "durationMinutes": 90,
  "maxParticipants": 10
}
Response: 201 { EventDTO }

GET /api/events?sportType=FOOTBALL&startAfter=...&startBefore=...&lat=...&lng=...&radiusKm=5
Response: 200 { "items": [EventDTO], "total": 42 }
  [GUEST readable]

GET /api/events/{id}
Response: 200 { EventDTO } | 404
  [GUEST readable]

PUT /api/events/{id}                      [ORGANIZER only, ownership enforced server-side]
Request: full EventUpdateDTO (same shape as create)
Response: 200 { EventDTO } | 403 (not owner) | 404

DELETE /api/events/{id}                   [ORGANIZER only]
Response: 204 | 403 | 404
(sets status = CANCELLED, notifies participants via SSE)

POST /api/events/{id}/join                [USER+]
Response: 200 { EventDTO } | 409 (full/already joined) | 404

POST /api/events/{id}/leave                [USER+]
Response: 200 { EventDTO } | 400 (not a participant) | 404
```

`EventDTO` shape:
```json
{
  "id": "string",
  "sportType": "string",
  "title": "string",
  "description": "string",
  "location": { "lat": 0, "lng": 0 },
  "addressLabel": "string",
  "startTime": "ISO8601",
  "durationMinutes": 90,
  "maxParticipants": 10,
  "currentParticipants": 6,
  "participantIds": ["..."],
  "organizerId": "string",
  "status": "OPEN",
  "isOwnedByCurrentUser": true,
  "isJoinedByCurrentUser": false
}
```

### Notifications (SSE)
```
GET /api/notifications/stream             [USER+, authenticated only]
Response: text/event-stream, one connection per authenticated user.

Event frame examples:
event: new-game
data: {"eventId": "...", "sportType": "FOOTBALL", "distanceKm": 1.2}

event: roster-change
data: {"eventId": "...", "currentParticipants": 7, "maxParticipants": 10}

event: event-cancelled
data: {"eventId": "..."}

event: heartbeat
data: {"ts": "ISO8601"}     // every 30s to keep connection alive
```

### Users
```
GET /api/users/me                         [USER+]
Response: 200 { "id", "email", "displayName", "preferredSports", "homeLocation" }

PUT /api/users/me                         [USER+]
Request: { "displayName", "preferredSports", "homeLocation": { "lat", "lng" } }
Response: 200 { UserDTO }

GET /api/users/me/organized-events        [USER+]
Response: 200 { "items": [EventDTO] }

GET /api/users/me/joined-events           [USER+]
Response: 200 { "items": [EventDTO] }
```

**Standard error shape:**
```json
{ "timestamp": "ISO8601", "status": 400, "error": "Bad Request", "message": "field 'lat' out of range", "path": "/api/events" }
```

---

## 5. Split of Responsibilities

### Backend Developer
- Spring Security filter chain: JWT parsing/validation, graceful fallback to anonymous context (no 500s on expired/invalid token), role model (`GUEST`/`USER`/`ORGANIZER` derived), CORS config with env-driven whitelist.
- Auth module: register/login, BCrypt hashing, JWT issuance (HS256, short expiry), IP-based rate limiting (Bucket4j) on `/auth/*`.
- Event CRUD + business rules: ownership enforcement on `PUT`/`DELETE`, capacity check on join, status transitions (`OPEN`→`FULL`→`CANCELLED`/`COMPLETED`).
- MongoDB schema/indexes: `2dsphere` on `Event.location`, compound indexes for filter queries; geo bounding-box/radius query implementation (`$geoWithin`/`$near`).
- Bean Validation on all DTOs (reject malformed lat/lng, missing required fields).
- SSE: `SseEmitter` registry (per-user, in-memory map), heartbeat scheduler (~30s ping), emit on event create/edit/cancel/join/leave, reminder job (scheduled task) for "starting soon" notifications.
- User profile endpoints (`/users/me/*`).
- Dockerfile for backend, Spring profiles (`dev`/`prod`) for env-based config (Mongo URI, JWT secret, CORS origins).
- Document known SSE single-instance limitation in README/ADR.

### Frontend Developer
- React app shell, routing (event list/map view, event detail, profile, login/register).
- Leaflet map integration: pin rendering, marker clustering, popup with event summary + Join/View CTA, browser geolocation with manual address fallback.
- Filter panel UI (sport type, date range, radius) wired to `GET /events` query params via React Query.
- Auth flows: login/register forms, JWT storage (memory/localStorage per chosen strategy), attach `Authorization` header to requests, handle 401 → redirect to guest/read-only state (no crash loop).
- `EventSource` client for `/notifications/stream`: parse typed event frames, update React Query cache / toast notifications on `new-game`/`roster-change`/`event-cancelled`.
- **Visibility-based connection management:** listen to `document.visibilitychange`, close `EventSource` on hidden tab, reconnect with exponential backoff (max 5 attempts) on visible/network-drop.
- "My Events"/"My Games" profile views consuming respective endpoints.
- Client-side form validation mirroring backend constraints (fail fast, but never relied upon as security boundary).
- Performance: code-splitting, lazy-load map bundle, target <2s initial load on 4G.
- Dockerfile/Nginx config for static build serving.

### Shared/Joint
- API contract review and DTO/type alignment (consider generating TS types from OpenAPI spec if time allows).
- CORS origin list agreement (local dev ports vs prod domain).
- Error response format consumption (toast/banner mapping from standard error shape).