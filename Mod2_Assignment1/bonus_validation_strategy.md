# Validation Strategy Design Document
## Enterprise QA Lab — Network Performance & Validation Tooling

### Purpose
This document outlines where TRex, IXChariot, and VeriWave would each be used
within an enterprise QA lab's network validation strategy, and how they
complement each other rather than overlap.

---

### 1. TRex — Infrastructure & Device-Level Load Testing
**Where it fits:** Early-stage validation of network hardware and core
infrastructure — routers, switches, firewalls, load balancers.

**Use case:** Before a new router or firewall is approved for production,
TRex would be used to push it to its rated throughput (e.g. verifying a
10 Gbps interface actually sustains 10 Gbps under realistic mixed traffic,
not just synthetic single-flow tests). It's ideal for capacity testing,
stress testing, and regression testing after firmware/config changes,
since it's scriptable and integrates well into automated CI/CD pipelines.

**Why here:** Open-source, high raw throughput, low cost to scale across
many test rigs — well suited for frequent, repeatable automated tests.

---

### 2. IXChariot — Application-Level Experience Validation
**Where it fits:** Mid-to-late stage validation, once infrastructure is
confirmed stable, to test how actual applications perform across it.

**Use case:** Validating that a VoIP rollout, video conferencing platform,
or file-sync application performs acceptably across the company's WAN —
measuring real jitter, latency, and throughput as experienced by
endpoint-to-endpoint application traffic, across branch offices or
data centers, not just raw link capacity.

**Why here:** IXChariot tests from the application's point of view using
real endpoints, which raw packet generators like TRex don't capture —
this is what tells you whether users will actually have a good experience,
not just whether the pipe is big enough.

---

### 3. VeriWave — Wireless/WLAN-Specific Validation
**Where it fits:** Any stage where wireless access is part of the
deployment — office Wi-Fi rollouts, wireless guest networks, IoT device
onboarding.

**Use case:** Before deploying new access points across an office floor,
VeriWave would validate how many simultaneous wireless clients a single AP
can support without service degradation, how well clients roam between
APs, and how the network holds up under RF interference or congestion —
none of which wired-only tools like TRex or IXChariot are built to test.

**Why here:** Wireless has failure modes (roaming handoff delay,
co-channel interference, client density limits) that simply don't exist
on wired links, so it needs purpose-built tooling.

---

### Summary Table

| Tool       | Layer Tested          | Best Used For                          | Stage in Pipeline        |
|------------|------------------------|------------------------------------------|---------------------------|
| TRex       | Network / Device       | Router, switch, firewall throughput & stress testing | Early (infra validation) |
| IXChariot  | Application            | Real app performance (VoIP, video, file transfer) across the network | Mid-to-late (experience validation) |
| VeriWave   | Wireless / RF          | AP capacity, roaming, wireless client density | Any stage involving Wi-Fi |

### Overall Strategy
A mature QA lab would layer these tools rather than pick one: TRex confirms
the underlying infrastructure can handle the required load, VeriWave
confirms the wireless layer (if applicable) can support the expected
client density, and IXChariot confirms that real applications running over
that validated infrastructure deliver an acceptable end-user experience.
Together they cover device capacity, application experience, and
wireless-specific behavior — three failure points that a single tool
cannot adequately test alone.
