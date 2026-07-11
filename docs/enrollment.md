# Face Enrollment Module Documentation

## 1. Overview

The Face Enrollment Module is responsible for securely registering a new household member into the HomeGuard facial recognition system. Unlike traditional systems that rely on a single facial image, HomeGuard captures multiple facial embeddings from different head poses to improve recognition accuracy under real-world conditions.

The enrollment process is distributed across two independent systems:

### Django Backend

Responsibilities:

- Manages users and authentication.
- Stores homes and memberships.
- Manages invitations.
- Creates enrollment sessions.
- Stores face profiles.
- Maintains the source of truth for all persistent data.

### AI Engine (FastAPI + InsightFace)

Responsibilities:

- Opens the webcam.
- Detects faces.
- Validates face quality.
- Collects multiple embeddings.
- Returns embeddings to Django.

The AI Engine **never stores permanent user information** such as users, homes, invitations, or permissions. It only processes facial data during the enrollment session.

---

# 2. Enrollment Workflow

```text
Home Owner
     │
     │ Send Invitation
     ▼
Home Invitation
     │
     │ Accept Invitation
     ▼
Enrollment Session Created
     │
     │ Open Camera
     ▼
AI Engine
     │
     │ Detect Face
     │ Validate Pose
     │ Extract Embeddings
     ▼
Embeddings Complete
     │
     ▼
Django Backend
     │
     │ Create HomeMember
     │ Create FaceProfile
     │ Accept Invitation
     │ Complete Session
     ▼
Enrollment Completed
```

---

# 3. Detailed Enrollment Process

## Step 1 — Home Owner Sends an Invitation

The owner invites another registered user to join the home.

The invitation contains:

- Home
- Invited Email
- Assigned Role
- Permission Set

Example:

```text
Home:
Green Villa

Email:
friend@gmail.com

Role:
Member

Permissions:
✓ Dashboard Access
✓ Unlock Door
✗ Manage Members
```

The invitation remains in **Pending** status until accepted.

---

## Step 2 — User Accepts Invitation

When the invited user accepts the invitation, Django **does not immediately create a HomeMember**.

Instead, it creates an **EnrollmentSession**.

```text
Invitation
        │
        ▼
EnrollmentSession
Status = Pending
```

This ensures that only users with a successfully enrolled face become members of the home.

---

## Step 3 — Browser Opens Face Enrollment

The browser redirects the user to the face scanning page.

```text
/scan-face/
```

The page receives the Django Enrollment Session ID.

Example:

```text
02f24440-c7b6-4416-b6bb-d9bdb65318e4
```

The browser sends:

```http
POST /enrollment/start
```

to the AI Engine.

---

## Step 4 — AI Engine Creates an AI Session

The AI Engine creates an in-memory enrollment session.

```text
Django Session
       │
       ▼
02f24440...
       │
       ▼
AI Session
23df63b8...
```

The AI session stores:

- Django Session ID
- FaceEnrollmentService
- Current pose
- Progress
- Collected embeddings

No permanent data is stored inside the AI Engine.

---

## Step 5 — Multi-Pose Face Capture

HomeGuard requires five head poses to improve recognition accuracy.

Required poses:

- LOOK_CENTER
- LOOK_LEFT
- LOOK_RIGHT
- LOOK_UP
- LOOK_DOWN

For each pose, multiple embeddings are collected.

Example:

```text
CENTER

Embedding 1
Embedding 2
Embedding 3
...

LEFT

Embedding 1
Embedding 2
...

RIGHT
...

UP
...

DOWN
...
```

This provides significantly better recognition performance than using only a single image.

---

## Step 6 — Face Validation

Every webcam frame is validated before an embedding is accepted.

Validation includes:

- Face detected
- Exactly one face visible
- Face confidence threshold
- Correct head pose
- Face positioned correctly
- Image quality

If validation fails, the frame is ignored.

Example:

```text
Face confidence too low.
```

Previously collected embeddings remain unaffected.

---

## Step 7 — Enrollment Progress

The AI Engine continuously reports enrollment progress.

Example:

```text
LOOK_CENTER

Frames:
1 / 10
2 / 10
...
10 / 10

↓

Pose Completed
```

Console Output:

```text
[FRAME]
Step=LOOK_LEFT
Progress=20%
Frames=5/10
```

---

## Step 8 — Embedding Generation

After all required poses are completed, the AI Engine stores facial embeddings in memory.

Example:

```json
{
  "CENTER": [...],
  "LEFT": [...],
  "RIGHT": [...],
  "UP": [...],
  "DOWN": [...]
}
```

Only numerical embeddings are stored.

No facial images are permanently saved.

---

## Step 9 — Upload Embeddings to Django

The AI Engine sends the collected embeddings back to Django.

```http
POST /api/faces/save/
```

Payload:

```json
{
    "session_id": "02f24440...",
    "embeddings": {
        "CENTER": [...],
        "LEFT": [...],
        "RIGHT": [...],
        "UP": [...],
        "DOWN": [...]
    }
}
```

---

## Step 10 — Django Completes Enrollment

The FaceSaveView forwards the request to the Application Layer.

```text
FaceSaveView
      │
      ▼
EnrollmentService
      │
      ▼
Repositories
      │
      ▼
Database
```

This follows the principles of Clean Architecture by keeping business logic inside the service layer.

---

## Step 11 — HomeMember Creation

The Enrollment Service creates a new HomeMember using information from the invitation.

Copied information includes:

- Home
- User
- Role
- Dashboard permission
- Device control permission
- Door unlock permission
- Alert settings

Example:

```text
HomeMember

Home:
Green Villa

Role:
Member

Permissions:
✓ Dashboard
✓ Unlock Door
✓ Alerts
```

---

## Step 12 — FaceProfile Creation

After the HomeMember is created, a FaceProfile is generated.

```text
FaceProfile
      │
      ▼
HomeMember
      │
      ▼
Embeddings
      │
      ▼
Verified = True
```

The label name is automatically generated from:

```python
user.full_name
```

---

## Step 13 — Invitation Completion

After successful enrollment:

Invitation:

```text
Pending
```

becomes

```text
Accepted
```

Enrollment Session:

```text
Pending
```

becomes

```text
Completed
```

Any duplicate pending invitations for the same user and home are removed.

---

## Step 14 — AI Session Removal

Once Django confirms successful enrollment, the AI session is deleted.

```text
AI Session
      │
      ▼
Removed
```

Only Django retains permanent records.

---

# 4. Overall Architecture

```text
                 Browser
                    │
                    ▼
             Django Backend
                    │
         Enrollment Session ID
                    │
                    ▼
        AI Engine (FastAPI)
                    │
        Face Detection
        Pose Validation
        Embedding Extraction
                    │
                    ▼
             Facial Embeddings
                    │
                    ▼
        Django Application Layer
                    │
                    ▼
              Repositories
                    │
                    ▼
               PostgreSQL
```

---

# 5. Database Objects Created

After successful enrollment, the database contains:

```text
HomeInvitation
Status = Accepted

        │
        ▼

EnrollmentSession
Status = Completed

        │
        ▼

HomeMember

        │
        ▼

FaceProfile
```

---

# 6. Why HomeMember Is Created After Face Enrollment

HomeGuard intentionally delays creating the `HomeMember` record until face enrollment succeeds.

This approach ensures:

- Only verified users become members.
- Users cannot access home resources before biometric verification.
- Permission assignments are activated only after successful enrollment.
- Failed enrollments do not leave orphaned member records.
- Database consistency is maintained.

This design also simplifies recovery because a failed enrollment only affects the EnrollmentSession rather than partially created records.

---

# 7. Advantages of the Design

- Clean separation between AI processing and business logic.
- Django remains the single source of truth.
- AI Engine performs temporary processing only.
- Multi-pose enrollment significantly improves recognition accuracy.
- Service and Repository layers encapsulate business logic.
- Automatic permission assignment from invitations.
- Transactional enrollment ensures that all related database operations either succeed together or fail together.
- Scalable architecture allows multiple AI Engines to communicate with the same Django backend in the future.

---

# 8. Technologies Used

| Component | Technology |
|-----------|------------|
| Backend | Django REST Framework |
| AI Engine | FastAPI |
| Face Detection | InsightFace |
| Computer Vision | OpenCV |
| Communication | REST API |
| Database | PostgreSQL / SQLite (Development) |
| Architecture | Clean Architecture |
| Pattern | Service-Repository Pattern |

---

# 9. Summary

The Face Enrollment Module is designed to securely register household members using AI-based facial recognition. The Django backend manages business logic, invitations, permissions, and persistent storage, while the FastAPI AI Engine performs temporary computer vision tasks such as face detection, pose validation, and embedding extraction. By separating these responsibilities and using multi-pose facial enrollment, HomeGuard achieves improved recognition accuracy, maintains database consistency, and follows a scalable Clean Architecture suitable for production deployment.