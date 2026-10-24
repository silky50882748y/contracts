# Security Policy

## Overview

The Allergy Management smart contract handles sensitive patient health information and must maintain the highest security standards. This document outlines our security practices, threat model, and vulnerability reporting process.

## Security Features

### Authentication & Authorization

1. **Multi-level Access Control**
   - Patient-controlled access grants
   - Provider authentication via `require_auth()`
   - Admin role for system operations
   - Automatic patient self-access

2. **Permission Checks**
   - All read operations verify access permissions
   - Write operations require provider authentication
   - Access can be granted and revoked by patients
   - Admin override for emergency access

### Data Protection

1. **Input Validation**
   - Allergen type validation (med, food, env)
   - Severity level validation (mild, moderate, severe, critical)
   - Date validation (no future dates)
   - Duplicate allergy prevention

2. **Data Integrity**
   - Immutable audit trail for severity changes
   - Timestamped records
   - Resolution tracking with reasons
   - Historical data preservation

3. **Privacy Controls**
   - Explicit access grants required
   - Patient data isolation
   - No cross-patient data leakage
   - Secure storage using Soroban persistent storage

### Smart Contract Security

1. **Reentrancy Protection**
   - No external calls during state changes
   - State updates before events
   - Atomic operations

2. **Integer Overflow Protection**
   - Rust's built-in overflow checks
   - Safe arithmetic operations
   - Validated counter increments

3. **Error Handling**
   - Comprehensive error types
   - Graceful failure modes
   - No panic in production paths
   - Clear error messages

## Threat Model

### Identified Threats

1. **Unauthorized Access**
   - **Mitigation**: Multi-layer authentication and authorization
   - **Status**: Protected

2. **Data Tampering**
   - **Mitigation**: Blockchain immutability and audit trails
   - **Status**: Protected

3. **Denial of Service**
   - **Mitigation**: Gas limits and efficient algorithms
   - **Status**: Monitored

4. **Privacy Breach**
   - **Mitigation**: Access control and encryption at rest
   - **Status**: Protected

5. **Replay Attacks**
   - **Mitigation**: Stellar's built-in sequence numbers
   - **Status**: Protected

### Attack Vectors

1. **Smart Contract Vulnerabilities**
   - Regular security audits
   - Automated testing (>85% coverage)
   - Formal verification (planned)

2. **Access Control Bypass**
   - Multiple permission checks
   - Fail-secure defaults
   - Comprehensive testing

3. **Data Injection**
   - Input validation
   - Type safety
   - Sanitization

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

## Security Best Practices

### For Developers

1. **Code Review**
   - All changes require peer review
   - Security-focused review checklist
   - Automated security scanning

2. **Testing**
   - Minimum 85% code coverage
   - Security-specific test cases
   - Fuzzing for edge cases
   - Integration testing

3. **Dependencies**
   - Regular dependency updates
   - Security audit of dependencies
   - Minimal dependency footprint
   - Pinned versions in production

### For Deployers

1. **Key Management**
   - Use hardware wallets for admin keys
   - Rotate keys regularly
   - Multi-signature for critical operations
   - Secure key storage

2. **Deployment**
   - Deploy to testnet first
   - Verify contract code
   - Initialize with correct admin
   - Monitor after deployment

3. **Monitoring**
   - Set up event monitoring
   - Alert on suspicious activity
   - Regular security audits
   - Incident response plan

### For Users

1. **Access Management**
   - Grant access only to trusted providers
   - Review access grants regularly
   - Revoke unused access
   - Monitor access logs

2. **Data Verification**
   - Verify provider credentials
   - Review allergy records
   - Report discrepancies
   - Keep personal records

## Vulnerability Reporting

### Reporting Process

If you discover a security vulnerability, please follow these steps:

1. **Do Not** disclose the vulnerability publicly
2. Email security@[your-domain].com with:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)
3. Allow up to 48 hours for initial response
4. Work with us on coordinated disclosure

### What to Expect

- **Acknowledgment**: Within 48 hours
- **Initial Assessment**: Within 1 week
- **Fix Timeline**: Based on severity
  - Critical: 24-48 hours
  - High: 1 week
  - Medium: 2 weeks
  - Low: 1 month
- **Disclosure**: After fix is deployed

### Bug Bounty

We offer rewards for security vulnerabilities based on severity:

- **Critical**: $5,000 - $10,000
- **High**: $2,000 - $5,000
- **Medium**: $500 - $2,000
- **Low**: $100 - $500

Eligibility:
- First reporter of the vulnerability
- Follows responsible disclosure
- Provides clear reproduction steps
- Does not exploit the vulnerability

## Security Audits

### Completed Audits

- Internal security review: [Date]
- Automated security scanning: Continuous
- Dependency audit: Weekly

### Planned Audits

- Third-party security audit: [Planned Date]
- Formal verification: [Planned Date]
- Penetration testing: [Planned Date]

## Compliance

### Standards

- HIPAA compliance considerations
- GDPR data protection principles
- SOC 2 Type II (planned)
- ISO 27001 alignment

### Data Handling

- Minimal data collection
- Purpose limitation
- Data minimization
- Storage limitation
- Integrity and confidentiality

## Incident Response

### Response Team

- Security Lead: [Contact]
- Development Lead: [Contact]
- Operations Lead: [Contact]

### Response Process

1. **Detection**: Automated monitoring and user reports
2. **Assessment**: Severity and impact analysis
3. **Containment**: Immediate threat mitigation
4. **Eradication**: Root cause fix
5. **Recovery**: Service restoration
6. **Lessons Learned**: Post-incident review

### Communication

- Affected users notified within 24 hours
- Public disclosure after fix deployment
- Transparency in incident reports
- Regular security updates

## Security Updates

### Update Policy

- Security patches released immediately
- Regular updates every quarter
- Backward compatibility maintained
- Migration guides provided

### Notification Channels

- GitHub Security Advisories
- Email notifications
- Twitter: [@your-handle]
- Discord: [Your Server]

## Contact

For security concerns:
- Email: security@[your-domain].com
- PGP Key: [Key ID]
- Response Time: 48 hours

For general inquiries:
- Email: support@[your-domain].com
- Discord: [Your Server]

## Acknowledgments

We thank the following security researchers for their contributions:

- [Researcher Name] - [Vulnerability] - [Date]

---

Last Updated: [Date]
Version: 1.0
