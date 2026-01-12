# AI Appointment Assistant MVP Blueprint

## Product summary
A smart scheduling and client management assistant for solo service businesses (barbers, nail techs, trainers, tutors, therapists, consultants, and similar operators). It reduces missed appointments, prevents double-bookings, automates reminders, and keeps client records organized.

## Part 1 — Foundation

### User flow (MVP)
1. **Service owner onboarding**
   - Create account → connect calendar → set business hours → define services.
2. **Client booking**
   - Client opens booking link → selects service/time → submits contact info → confirmation sent.
3. **Calendar management**
   - Booking writes to connected calendar → buffer rules avoid overlaps.
4. **Reminder automation**
   - System sends reminders (24h + 2h prior) → optional confirmation.
5. **Day-of service**
   - Appointment occurs → owner adds client notes → follow-up triggered.

### Core screens
1. **Owner onboarding**
   - Calendar connection
   - Business hours
   - Services + pricing
2. **Booking form (client-facing)**
   - Service selection
   - Date/time picker
   - Contact fields
   - Notes field
3. **Dashboard**
   - Today’s schedule
   - Upcoming bookings
   - Quick actions (reschedule/cancel)
4. **Client profile**
   - Appointment history
   - Notes
   - Contact info
5. **Settings**
   - Reminder rules
   - Calendar connection status
   - Message templates

### Core use case
A client books a haircut through a shared link. The system checks availability in the owner’s calendar, creates a booking, and sends reminders. After the appointment, the owner adds notes, and the assistant sends a follow-up message requesting feedback.

## Part 2 — Build MVP features

### Booking form
- **Frontend:** service list, calendar picker, contact fields, consent checkbox.
- **Validation:** required fields, double-booking prevention, time buffers.
- **Output:** create booking record + calendar event.

### Calendar connection
- **Provider:** Google Calendar (MVP) via OAuth.
- **Logic:** free/busy check + create event with reminders.
- **Storage:** token + calendar ID tied to owner.

### Reminder automation
- **Channels:** SMS (Twilio) + email (SendGrid).
- **Rules:** default 24h + 2h prior; adjustable per owner.
- **Templates:** confirmation + reminder + cancellation.

## Part 3 — AI assistant capabilities

### Rescheduling
- Detect conflict or request → suggest top 3 alternative slots.

### Follow-ups
- Auto-send “how was your visit?” + feedback link.

### Client summaries
- Generate quick summary of past notes and preferences before appointment.

## Final part — Validation

1. Test with 2 real users from target audience.
2. Capture friction (booking completion rate, reminder effectiveness).
3. Iterate on UI flow and messages.
4. Prepare demo walkthrough with real booking flow.

## Deliverables checklist
- [ ] Booking intake form (responsive)
- [ ] Calendar sync (Google)
- [ ] Reminder automation (SMS/email)
- [ ] Simple dashboard (today + upcoming)
- [ ] Client notes + profiles
- [ ] AI helper actions (reschedule, follow-up, summaries)
