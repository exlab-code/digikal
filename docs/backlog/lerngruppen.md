# Lerngruppen (Learning Sprints)

## Idea

Curated peer learning groups for nonprofit professionals. DigiKal already aggregates the events — the missing piece is connecting people who want to learn the same topic and giving them structure to do it together.

## Core concept

- **Time-boxed**: 3 months per sprint
- **Rolling**: no fixed start dates — a new group forms whenever enough people have signed up for a topic. Groups launch throughout the year
- **Small groups**: 5-8 people
- **Topic-based**: e.g. "KI fuer Nonprofits", "Datenschutz"
- **Self-organized**: no facilitator from DigiKal, groups run themselves
- **Goal-oriented**: each participant has a personal project (e.g. "implement one KI tool in my org"). Graduation/showcase at the end

Events are fuel, not curriculum. The real learning happens in the group conversations and personal projects between events.

**Multiplier effect**: 8 people, 5 events per month. Each person attends 1-2 and reports back to the group. You get the essence of all events without attending everything yourself. Like a reading circle — not everyone reads every book, but at the end everyone knows the key ideas.

## How it works

1. **Signup** on digikal.org with:
   - Name + email
   - Topic
   - "Was moechtest du erreichen?" (one sentence — the personal project)
   - Experience level: haven't started / experimenting / already using it
   - Organization type (Verein, Stiftung, Wohlfahrtsverband, etc.)
   - Organization size (under 10 / 10-50 / 50+ Mitarbeitende)
   - 3 preferred weekly time slots (e.g. "Dienstag 10-11", "Donnerstag 14-15") — used to find a biweekly slot that works for the whole group
2. **Group formation** — agent forms diverse groups based on signup data. Participants don't choose their group. Mix experience levels, org types/sizes. Aligned in ambition.
3. **Kickoff email** with:
   - Miro board link (duplicated from template)
   - Calendar invite series (biweekly, 1h, with video link)
   - One-page playbook with prompts for each session
4. **During the sprint**:
   - Biweekly video calls where participants share progress
   - Attend relevant events individually, discuss in the group
   - Document progress on Miro board
5. **Graduation**: final meeting where each participant presents what they achieved

## Infrastructure (keep it simple)

- **Miro** — pre-made template board per topic, duplicated manually for each group (API board copy requires Business plan, we're on Starter). Sections: Vorstellungsrunde, Meine Ziele, Fortschritte, besuchte Veranstaltungen, Ressourcen
- **Calendar** — hosted .ics file per group with the biweekly meeting series + Jitsi link (jitsi.fem.tu-ilmenau.de with random room name per group, e.g. `/digikal-ki-a3f8b2`)
- **Scheduling** — Nuudel or Rallly poll to find the biweekly slot before kickoff
- **Email** — welcome email, weekly event recommendations, nudges
- No Slack, no Teams, no new accounts. Just Miro + calendar + email

## Where an agent adds value

The mechanical parts (duplicate board, send email, generate .ics) are regular automation (Directus flow or Python script on cron).

An agent is valuable for the judgment calls:

### Group formation (highest value)
Not just counting to 8. Smart matching:
- Mix experience levels (beginner + someone who's started)
- Mix org types (small Verein + larger Wohlfahrtsverband = different perspectives)
- Geographic diversity or proximity depending on preference
- Timing — group people who signed up around the same time so momentum is fresh

### Nudging / keeping groups alive
Most self-organized groups die after 3-4 weeks. Well-timed interventions:
- "Your next meeting is Thursday — here's a prompt to think about beforehand"
- "It's been 3 weeks since the last group activity — here's something to get you going again"
- Personalized based on group context and progress

### Event recommendations (nice-to-have)
Read event descriptions and match to what the group is actually working on, not just topic tags. But participants can also filter events themselves — this is lower priority than group formation and nudging.

## Technical approach

Python script (like the existing event pipeline), runs on cron:
- Reads signup/group data from Directus
- Calls Claude API for judgment tasks (group matching, nudge drafting)
- Calls Miro API, email API, .ics generation for mechanical tasks
- Writes results back to Directus

Directus collections needed:
- `lerngruppen` — group name, topic, start/end date, status, miro link, calendar link
- `lerngruppen_signups` — name, email, topic, motivation text, experience level, org type, org size, 3 preferred time slots, signup date
- `lerngruppen_members` — links signup to group

## Signup form implementation

1. Create `lerngruppen_signups` collection in Directus with fields matching the signup form
2. In Directus: Settings → Access Policies → Public → give **create-only** permission on `lerngruppen_signups` (no read/update/delete)
3. Build a form page on digikal.org (e.g. `/lernsprint`) that POSTs to `https://calapi.buerofalk.de/items/lerngruppen_signups`
4. No authentication needed — public create permission allows anonymous form submissions

## First topics

- **KI fuer Nonprofits** — high demand, lots of events
- **Datenschutz** — everyone needs it, steady event supply

## Example sprint: KI fuer Nonprofits (April–Juni 2026)

Based on actual events in DigiKal. ~30 KI-related events in 3 months, almost all free and online.

**Ziel**: Jede/r setzt ein konkretes KI-Tool in der eigenen Organisation ein.

### Monat 1: Orientieren (April)
*"Was gibt's, was passt zu mir?"*

Empfohlene Events:
- 14.04 — Datenschutzkonform mit KI arbeiten (Haus des Stiftens)
- 21.04 — Der neue Vereinsassistent: KI-Einstieg (Aktion Zivilcourage)
- 21.04 — Praesentationen mit KI erstellen (Haus des Stiftens)
- 23.04 — MCP: Wie der neue Standard KI mit Daten verbindet (Civic Data Community)
- 29.04 — Austauschtreffen KI fuers Gemeinwohl (Civic Data Community)

Gruppenmeetings:
1. Vorstellung, Ziele, wo steht ihr? Jede/r formuliert ein konkretes Vorhaben
2. Welche Events habt ihr besucht? Was habt ihr mitgenommen? Erstes Tool ausprobiert?

### Monat 2: Ausprobieren (Mai)
*"Ich mach das jetzt einfach mal"*

Empfohlene Events:
- 05.05 — Texte mit KI zu Posts/Podcasts/Erklaervideos (Haus des Stiftens)
- 05.05 — Foerderantraege mit KI meistern (Aktion Zivilcourage)
- 21.05 — Externe Kommunikation & Freiwilligengewinnung mit KI (Haus des Stiftens)
- 21.05 — Datenschutz und Generative KI (Civic Data Community)
- 27.05 — Austauschtreffen KI fuers Gemeinwohl (Civic Data Community)
- 28.05 — Digital Ordnung schaffen, KI sinnvoll nutzen (Open Transfer, Hamburg)

Gruppenmeetings:
3. Fortschritt am eigenen Projekt. Wo hakt's? Gruppe hilft Gruppe
4. Was funktioniert, was nicht? Erfahrungen teilen

### Monat 3: Vertiefen & Abschliessen (Juni)
*"Wie mache ich das nachhaltig?"*

Empfohlene Events:
- 09.06 — KI und Macht: Wer steckt dahinter? (Haus des Stiftens)
- 11.06 — KI-Richtlinie entwickeln (Haus des Stiftens)
- 11.06 — EU AI Act Einfuehrung (CorrelAid)
- 11.06 — Civic Data Camp Erfurt (Barcamp — wer kann, faehrt hin!)
- 18.06 — Copilot KI-Assistenten (Haus des Stiftens)
- 18.06 — Rechtssichere KI-Integration (Haus des Stiftens)
- 23.06 — KI-Werkzeuge zur Bild- und Videoerstellung (Haus des Stiftens)

Gruppenmeetings:
5. Generalprobe — jede/r stellt vor, was sie/er gemacht hat
6. Graduation/Showcase: Was habt ihr erreicht? Was wuerdet ihr eurem vergangenen Ich raten?

### Meeting-Struktur (je 60 Min)
- 5 Min: Check-in
- 30 Min: Event-Berichte (jede/r 3 Min: welches Event besucht, Top-Takeaways). Notizen auf Miro-Board in Spalte pro Event
- 15 Min: Projektupdate — wo stehe ich, wo brauche ich Hilfe?
- 10 Min: Naechste Schritte, wer besucht welches Event?

## Open questions

- Rolling vs. fixed start dates: pure rolling (group forms when 8 people are ready) is flexible but lacks urgency. Fixed batches ("next KI group starts May 1") create commitment through deadlines. Could do both: signup is always open, but announce upcoming start dates to create urgency
- How to handle dropouts mid-sprint? Minimum viable group size?
- Should there be a light application/screening to ensure commitment?
- How to handle the graduation — public showcase or group-internal?
- Pricing: free? Symbolic fee to increase commitment?
- ~~Who generates the Jitsi/video links~~ — solved: static Jitsi room per group on jitsi.fem.tu-ilmenau.de
- Documentation/wiki for groups: Miro alone is weak for structured text. Shared Google Doc / HedgeDoc is pragmatic but uninspiring. No great option found yet
