#!/usr/bin/env python3
"""
Process CSV files containing Solana version and build configuration data.
"""

import csv
import sys
from pathlib import Path
from typing import List, Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SolanaVersionProcessor:
    """Process CSV files containing Solana version data."""
    
    def __init__(self, csv_file_path: str):
        self.csv_file_path = Path(csv_file_path)
        self.versions = []
    
    def read_csv(self) -> List[Dict[str, Any]]:
        """Read CSV file and return list of version configurations."""
        if not self.csv_file_path.exists():
            raise FileNotFoundError(f"CSV file not found: {self.csv_file_path}")
        
        with open(self.csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            self.versions = [row for row in reader]
        
        logger.info(f"Loaded {len(self.versions)} versions from CSV")
        return self.versions
    
    def validate_versions(self) -> bool:
        """Validate version format and required fields."""
        required_fields = ['version', 'dockerfile_path']
        
        for i, version_data in enumerate(self.versions):
            for field in required_fields:
                if field not in version_data or not version_data[field]:
                    logger.error(f"Row {i+1}: Missing required field '{field}'")
                    return False
            
            # Validate version format (e.g., "1.14.23")
            version = version_data['version']
            if not self._is_valid_version_format(version):
                logger.error(f"Row {i+1}: Invalid version format '{version}'")
                return False
        
        return True
    
    def _is_valid_version_format(self, version: str) -> bool:
        """Check if version follows semantic versioning pattern."""
        parts = version.split('.')
        if len(parts) != 3:
            return False
        
        try:
            for part in parts:
                int(part)
            return True
        except ValueError:
            return False
    
    def generate_dockerfiles(self) -> Dict[str, str]:
        """Generate Dockerfile content for each version."""
        dockerfiles = {}
        
        for version_data in self.versions:
            version = version_data['version']
            dockerfile_content = self._generate_dockerfile_content(version_data)
            dockerfile_path = f"docker/v{version}.Dockerfile"
            dockerfiles[dockerfile_path] = dockerfile_content
        
        return dockerfiles
    
    def _generate_dockerfile_content(self, version_data: Dict[str, Any]) -> str:
        """Generate Dockerfile content for a specific version."""
        version = version_data['version']
        base_image = version_data.get('base_image', 'ubuntu:20.04')
        additional_deps = version_data.get('additional_deps', '')
        
        dockerfile_content = f"""FROM {base_image}

# Install Solana CLI version {version}
RUN apt-get update && apt-get install -y \\
    curl \\
    build-essential \\
    pkg-config \\
    libudev-dev \\
    && rm -rf /var/lib/apt/lists/*

# Install Rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${{PATH}}"

# Install Solana CLI
RUN sh -c "$(curl -sSfL https://release.solana.com/v{version}/install)"
ENV PATH="/root/.local/share/solana/install/active_release/bin:${{PATH}}"

# Install additional dependencies if specified
{additional_deps}

WORKDIR /workspace
"""
        return dockerfile_content
    
    def write_dockerfiles(self, output_dir: str = "docker") -> None:
        """Write generated Dockerfiles to the output directory."""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        dockerfiles = self.generate_dockerfiles()
        
        for dockerfile_path, content in dockerfiles.items():
            full_path = Path(dockerfile_path)
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Generated Dockerfile: {dockerfile_path}")

def main():
    """Main entry point for CSV processing."""
    if len(sys.argv) != 2:
        print("Usage: python process_csv.py <csv_file_path>")
        sys.exit(1)
    
    csv_file_path = sys.argv[1]
    
    try:
        processor = SolanaVersionProcessor(csv_file_path)
        processor.read_csv()
        
        if not processor.validate_versions():
            logger.error("CSV validation failed")
            sys.exit(1)
        
        processor.write_dockerfiles()
        logger.info("CSV processing completed successfully")
        
    except Exception as e:
        logger.error(f"Error processing CSV: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
