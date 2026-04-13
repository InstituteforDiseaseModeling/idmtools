# Platforms

idmtools supports multiple compute platforms for running simulations.

## Available Platforms

### Production Platforms

- **[COMPS](comps.md)** - Computational Modeling Platform Service
  IDM's cloud-based HPC platform

- **[Slurm](slurm.md)** - HPC Cluster Platform
  Run on Slurm-managed clusters

- **[Container](container.md)** - Docker Platform
  Local execution in Docker containers

## Choosing a Platform

| Platform | Best For | Scale |
|----------|----------|-------|
| **COMPS** | IDM users, cloud compute | Large (1000s of sims) |
| **Slurm** | HPC cluster access | Large (1000s of sims) |
| **Container** | Local testing, reproducibility | Medium (10s-100s of sims) |

## Platform Comparison

### COMPS
- ✅ Cloud-based, no local resources needed
- ✅ Massive scalability
- ✅ IDM support
- ❌ Requires IDM access

### Slurm
- ✅ Use existing HPC infrastructure
- ✅ High performance
- ✅ Resource management
- ❌ Requires cluster access

### Container
- ✅ Reproducible environments
- ✅ Local execution
- ✅ No cluster needed
- ❌ Limited by local resources

## Getting Started

1. [Configure your platform](../getting-started/configuration.md)
2. Follow platform-specific guides
3. See [tutorials](../tutorials/index.md) for examples
