# Contributing

Thanks for contributing to this Soroban contracts workspace.

## Development environment

### Dev container (recommended)

The repo includes a dev container that installs everything needed to build and test the contracts:

- Rust (stable) with the `wasm32-unknown-unknown` target
- Stellar CLI 28.0.0
- Node.js 20

To use it, open the repo in GitHub Codespaces or in VS Code with the Dev Containers extension ("Dev Containers: Reopen in Container"). The Stellar CLI is installed once when the container is created, so the first start takes several minutes.

### Manual setup

If you are not using the dev container, install the following:

```bash
# Install Rust (https://rustup.rs), then the wasm target
rustup target add wasm32-unknown-unknown

# Install Stellar CLI (pinned to 28.0.0 to match the dev container)
cargo install --locked stellar-cli --version 28.0.0
```

See the [Prerequisites](README.md#prerequisites) section of the README for details.

## Building and testing

```bash
cargo build --locked   # build the workspace
make test              # build contracts, then run cargo test
make fmt               # format the workspace
```

Keep `Cargo.lock` committed so builds use the same dependency versions.
