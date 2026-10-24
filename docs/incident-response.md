# Incident Response

## Containment

### Stale Pending State

Use these steps when a pending admin nomination, multisig action, or upgrade proposal is open
and was not intended. The full risk model and operator checks are in the threat models:
[allergy-management](../contracts/allergy-management/SECURITY.md#pending-state) and
[telemedicine](../contracts/telemedicine/SECURITY.md#pending-state).

1. **Admin nomination:** the current admin calls `cancel_admin_rotation` in `governance-voting`
   before the nomination expires. Nothing else clears `PendingAdmin` before its expiry.
2. **Multisig action:** do not approve or execute it. Let it reach its TTL, then call
   `finalize_expired` to mark it failed.
3. **Upgrade proposal:** there is no on-chain cancel. Keep approvals below threshold until the
   voting window lapses. Once the threshold is reached, the 24-hour timelock is the only delay,
   so escalate to the signers immediately.
4. Run the operator checks in the threat models above and record each open item.
