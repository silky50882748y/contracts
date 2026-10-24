# Telemedicine Contract — Security Notes

## Cross-State Prescription Enforcement (#563)

### Threat

A provider licensed in State A conducting a virtual visit with a patient located in State B could
issue a prescription that violates State B's telemedicine prescribing laws (e.g., the Ryan Haight
Act for controlled substances).

### Enforcement logic in `prescribe_during_visit`

1. **Session-active check** — `prescribe_during_visit` rejects any prescription if
   `visit.status != VisitStatus::InProgress`. Prescribing after `end_virtual_session` returns
   `Error::SessionNotActive`.

2. **License check** — The provider must hold an active, non-expired license stored under
   `DataKey::LicenseRegistry(provider_id, patient_location)`. If no such license exists,
   `Error::ProviderNotLicensedInPatientState` is returned. This check uses `patient_location`,
   which is set at session-start time in `start_virtual_session`.

3. **Controlled-substance policy** — When `PrescriptionRequest.is_controlled_substance` is
   `true`, the jurisdiction policy stored under
   `DataKey::ControlledSubstancePolicy(patient_location)` is read. If `requires_inperson` is
   set to `true` for that jurisdiction, `Error::ControlledSubstanceRequiresInPerson` is
   returned, blocking the telehealth prescription for schedule I–V substances.

### Configuring policies

Controlled-substance policies are set per jurisdiction by an authorized admin:

```rust
contract.set_controlled_substance_policy(admin, jurisdiction, requires_inperson);
```

Provider licenses are self-registered by the provider:

```rust
contract.register_provider_license(provider_id, jurisdiction, license_number, valid_until);
```

### Limitations

- License validity is time-based (`valid_until`). Clock manipulation on the ledger is not
  possible, but long-lived (non-expiring, `valid_until = 0`) licenses are allowed.
- Compact interstate licensing is enforced only at session-start (`start_virtual_session` via
  `verify_telemedicine_eligibility`). For prescriptions, only a **direct** state license is
  accepted; compact membership does not satisfy the prescription license check.
- The `is_controlled_substance` flag is caller-supplied and not verified against a formulary.
  A future integration with a drug formulary contract can provide this verification.

## Pending State

Pending state is a change that has been proposed or approved but not yet executed. It stays
stored after the reason for it has gone, so it can take effect later than the operator expects.

This contract has no pending-admin, timelock, or proposer-removal flow of its own. The pending
state that governs it sits in the governance contracts:

| Pending state | Contract | Lifetime | Stale-state risk |
|---|---|---|---|
| Admin nomination (`PendingAdmin`) | `governance-voting` | 24 hours (`ADMIN_ROTATION_WINDOW`) | Nominee accepts after the admin's intent has changed and nobody cancels it |
| Multisig action (`Proposal` per `action_id`) | `multisig-governance` | Proposal TTL | Approved action executes after the signer set has changed |
| Upgrade proposal | `upgrade-governance` | 7-day voting window (`VOTING_WINDOW`), then 24-hour timelock (`TIMELOCK_DELAY`) | Reaches threshold and executes after the timelock |

### Known Gaps

- **Approved upgrades cannot be cancelled.** `ProposalStatus::Cancelled` is never assigned and
  there is no cancel entry point. Once an upgrade is approved, the timelock is the only delay.
- **Admin rotations emit no events.** `propose_admin_rotation`, `accept_admin_rotation`, and
  `cancel_admin_rotation` publish nothing, and `PendingAdmin` has no getter. A nomination is
  visible only through the transaction that created it.
- **Signer changes do not reach open proposals.** `eligible_signers` is captured when a multisig
  proposal is created. Do not assume a later signer removal applies to it.

### Operator Checks

1. After every admin or signer change, call `get_proposal` on each open multisig action and
   confirm its approvers still match intent.
2. Record each `propose_admin_rotation` with its ledger timestamp. The nomination stays live
   until that timestamp plus 86,400 seconds, unless it is cancelled first.
3. For each approved upgrade, record `approved_at + TIMELOCK_DELAY` and confirm the upgrade is
   intended before that time.
4. Before closing a rotation, confirm `cancel_admin_rotation` has run or the nomination has expired.
