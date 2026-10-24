import { execFileSync } from "node:child_process";
import { resolve } from "node:path";

import { describe, expect, it } from "vitest";

import { networks } from "../src/index.js";

const CONTRACT_STRKEY = /^C[A-Z2-7]{55}$/;

// deployments/<network>.json is the source of truth; never hard-code the ID.
// WATCHER_REGISTRY_CONTRACT_ID overrides it (e.g. in CI).
function expectedContractId(): string {
  const override = process.env.WATCHER_REGISTRY_CONTRACT_ID;
  if (override) return override;
  const script = resolve(__dirname, "../../../scripts/deployment_address.py");
  return execFileSync("python3", [script, "watcher-registry", "--network", "testnet"], {
    encoding: "utf8",
  }).trim();
}

describe("watcher-registry contract id", () => {
  it("is a valid contract strkey", () => {
    expect(networks.testnet.contractId).toMatch(CONTRACT_STRKEY);
  });

  it("matches the deployment manifest", () => {
    expect(networks.testnet.contractId).toBe(expectedContractId());
  });
});
