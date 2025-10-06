# Solana Verifiable Build - AI Agent Guide

This guide helps AI agents understand and work effectively with the Solana Verifiable Build project.

## Project Overview

This project provides tooling to implement verified builds for Solana programs, ensuring deployed programs match their public source code. The system consists of:

- Rust-based CLI tool (`solana-verify`) for building and verifying Solana programs
- Docker-based build environment for reproducible builds
- Python scripts for managing Docker image generation

## Key Components

### 1. Build Environment (Docker)

- Docker images defined in `docker/*.Dockerfile` provide consistent build environments for each Solana version
- Image naming convention: `solana.v{VERSION}` (e.g., `solana.v1.14.23`)
- Generated using `build-all-images.sh` which automates building all version-specific images

### 2. CLI Tool (Rust)

- Main implementation in Rust using Solana SDK v2.3.1
- Key dependencies: `borsh` for serialization, `solana-sdk` for core functionality
- Command structure follows: `solana-verify [build|verify-from-repo|remote]`

## Development Workflows

### Adding Support for New Solana Versions

1. Create new Dockerfile in `docker/` directory:
   ```
   v{VERSION}.Dockerfile
   ```

2. Run build script to generate new image:
   ```bash
   ./build-all-images.sh
   ```

### Building and Testing

```bash
# Build CLI tool
cargo build

# Build a Solana program with verification
solana-verify build

# Verify deployment
solana-verify verify-from-repo -u $NETWORK_URL --program-id $PROGRAM_ID $REPO_URL
```

## Project Conventions

1. Docker Image Structure:
   - All images based on specific Solana versions
   - Located in `docker/` directory
   - Named following strict `v{MAJOR}.{MINOR}.{PATCH}.Dockerfile` pattern

2. Version Management:
   - Python scripts (`generate_dockerfiles.py`, `update_image_whitelist.py`) manage Docker image generation
   - Version dependencies locked in `Cargo.toml` for stability

3. Security Practices:
   - All build processes are containerized for reproducibility
   - Programs must be built in clean environments
   - Build verification happens on-chain

## Integration Points

1. Solana Program Interface:
   - Uses `solana-sdk` and `solana-loader-v3-interface` for program deployment
   - Interacts with Solana clusters via RPC (`solana-rpc-client`)

2. Remote Verification:
   - Build data uploaded on-chain
   - Remote jobs triggered for verification using program ID

Remember: Focus on maintaining reproducible builds and version-specific environments when making changes.