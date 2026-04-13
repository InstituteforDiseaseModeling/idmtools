"""
Build Singularity Images on COMPS

This script automates building one or more Singularity images from definition files.

Usage:
    # Build all images
    python build_images.py --all

    # Build specific image(s)
    python build_images.py --images python_minimal python_scientific

    # Build with specific platform
    python build_images.py --images python_minimal --platform SlurmStage
"""
import argparse
from pathlib import Path
from idmtools.core.platform_factory import Platform
from idmtools_platform_comps.utils.singularity_build import SingularityBuildWorkItem

# Available definition files and their metadata
AVAILABLE_IMAGES = {
    "python_minimal": {
        "def_file": "python_minimal.def",
        "description": "Minimal Python (NumPy + Matplotlib)",
        "estimated_time": "2-3 min"
    },
    "python_scientific": {
        "def_file": "python_scientific.def",
        "description": "Full Python scientific stack",
        "estimated_time": "10-15 min"
    },
    "python_ml": {
        "def_file": "python_ml.def",
        "description": "Python ML (TensorFlow, PyTorch, etc.)",
        "estimated_time": "15-20 min"
    },
    "epi_modeling": {
        "def_file": "epi_modeling.def",
        "description": "Epidemiological modeling environment",
        "estimated_time": "10-12 min"
    },
    "bioinformatics": {
        "def_file": "bioinformatics.def",
        "description": "Bioinformatics tools",
        "estimated_time": "12-15 min"
    },
    "r_analysis": {
        "def_file": "r_analysis.def",
        "description": "R statistical analysis",
        "estimated_time": "15-20 min"
    },
    "julia_analysis": {
        "def_file": "julia_analysis.def",
        "description": "Julia scientific computing",
        "estimated_time": "20-25 min"
    },
    "multi_language": {
        "def_file": "multi_language.def",
        "description": "Python + R + Julia",
        "estimated_time": "25-30 min"
    },
    "shell_tools": {
        "def_file": "shell_tools.def",
        "description": "Shell utilities (jq, yq, etc.)",
        "estimated_time": "3-5 min"
    }
}


def build_image(image_name, platform, wait=True):
    """
    Build a single Singularity image.

    Args:
        image_name: Name of the image (key from AVAILABLE_IMAGES)
        platform: Platform object
        wait: Whether to wait for build to complete

    Returns:
        Tuple of (success, asset_collection, work_item)
    """
    if image_name not in AVAILABLE_IMAGES:
        print(f"ERROR: Unknown image '{image_name}'")
        print(f"Available: {', '.join(AVAILABLE_IMAGES.keys())}")
        return False, None, None

    image_info = AVAILABLE_IMAGES[image_name]
    def_file = image_info["def_file"]
    sif_name = f"{image_name}.sif"

    print("=" * 70)
    print(f"Building: {image_name}")
    print("=" * 70)
    print(f"Description: {image_info['description']}")
    print(f"Definition file: {def_file}")
    print(f"Estimated time: {image_info['estimated_time']}")
    print(f"Output: {sif_name}")
    print()

    # Check if definition file exists
    if not Path(def_file).exists():
        print(f"ERROR: Definition file not found: {def_file}")
        return False, None, None

    # Create Singularity build work item
    sbi = SingularityBuildWorkItem(
        name=f"{image_info['description']} - Singularity Build",
        definition_file=def_file,
        image_name=sif_name
    )

    # Add tags for tracking
    sbi.tags = {
        "environment": image_name,
        "description": image_info["description"],
        "created_by": "build_images.py"
    }

    print(f"Submitting build to {platform.__class__.__name__}...")

    try:
        ac = sbi.run(wait_until_done=wait, platform=platform)

        if wait:
            if sbi.succeeded:
                print(f"\n✓ SUCCESS: {image_name} built successfully!")

                # Save asset collection ID
                id_file = f"{image_name}.sif.id"
                ac.to_id_file(id_file)
                print(f"✓ Asset Collection ID saved to: {id_file}")
                print(f"  Asset Collection ID: {ac.uid}")
                print(f"  Work Item ID: {sbi.uid}")
                return True, ac, sbi
            else:
                print(f"\n✗ FAILED: {image_name} build failed")
                print(f"  Work Item ID: {sbi.uid}")
                print(f"  Check COMPS for error details")
                return False, None, sbi
        else:
            print(f"\n→ Build submitted (not waiting)")
            print(f"  Work Item ID: {sbi.uid}")
            return None, ac, sbi

    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        return False, None, None


def main():
    parser = argparse.ArgumentParser(
        description="Build Singularity images on COMPS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Build minimal Python image
  python build_images.py --images python_minimal

  # Build multiple images
  python build_images.py --images python_minimal python_scientific

  # Build all images (will take 1-2 hours total)
  python build_images.py --all

  # Submit builds without waiting
  python build_images.py --images python_minimal --no-wait
        """
    )

    parser.add_argument(
        "--images",
        nargs="+",
        choices=list(AVAILABLE_IMAGES.keys()),
        help="Specific image(s) to build"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Build all available images"
    )
    parser.add_argument(
        "--platform",
        default="SlurmStage",
        help="Platform to use (default: SlurmStage)"
    )
    parser.add_argument(
        "--no-wait",
        action="store_true",
        help="Don't wait for builds to complete"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available images and exit"
    )

    args = parser.parse_args()

    # List images if requested
    if args.list:
        print("Available Singularity Images:")
        print("=" * 70)
        for name, info in AVAILABLE_IMAGES.items():
            print(f"\n{name}")
            print(f"  Description: {info['description']}")
            print(f"  Build time: {info['estimated_time']}")
            print(f"  Definition: {info['def_file']}")
        print("\n" + "=" * 70)
        return

    # Determine which images to build
    if args.all:
        images_to_build = list(AVAILABLE_IMAGES.keys())
        print(f"Building ALL {len(images_to_build)} images")
        print("This will take approximately 1-2 hours total")
        response = input("Continue? (yes/no): ")
        if response.lower() not in ["yes", "y"]:
            print("Cancelled")
            return
    elif args.images:
        images_to_build = args.images
    else:
        parser.print_help()
        return

    # Create platform
    print(f"\nConnecting to platform: {args.platform}")
    platform = Platform(args.platform)

    # Build images
    results = {}
    for image_name in images_to_build:
        success, ac, sbi = build_image(
            image_name,
            platform,
            wait=not args.no_wait
        )
        results[image_name] = {
            "success": success,
            "asset_collection": ac,
            "work_item": sbi
        }
        print()

    # Summary
    print("\n" + "=" * 70)
    print("BUILD SUMMARY")
    print("=" * 70)

    if args.no_wait:
        print("\nBuilds submitted (not waiting for completion)")
        for image_name, result in results.items():
            if result["work_item"]:
                print(f"  {image_name}: Work Item {result['work_item'].uid}")
    else:
        succeeded = [name for name, r in results.items() if r["success"]]
        failed = [name for name, r in results.items() if r["success"] is False]

        print(f"\nSucceeded: {len(succeeded)}/{len(results)}")
        for name in succeeded:
            print(f"  ✓ {name}")

        if failed:
            print(f"\nFailed: {len(failed)}/{len(results)}")
            for name in failed:
                print(f"  ✗ {name}")

        print("\nGenerated .sif.id files:")
        for name in succeeded:
            print(f"  {name}.sif.id")

    print("=" * 70)


if __name__ == "__main__":
    main()
