#!/bin/bash
# Phase 5: GitHub & Polish - Running Script
# Time Required: ~40 hours

set -e

echo "=============================================="
echo "  Phase 5: GitHub & Polish"
echo "  Estimated Time: ~40 hours"
echo "=============================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

section() {
    echo ""
    echo -e "${YELLOW}=== $1 ===${NC}"
}

section "Phase 5 Goals"
cat << 'EOF'
This phase will:
1. Build Docker containers
2. Create complete documentation
3. Run integration tests
4. Prepare GitHub repository

Expected deliverables:
✓ Docker containers working
✓ Full documentation
✓ GitHub repository ready
EOF

section "Step 1: Check Docker Installation"
echo "Verifying Docker..."
echo ""

if command -v docker &> /dev/null; then
    echo -e "${GREEN}✓${NC} Docker installed"
    docker --version
else
    echo -e "${RED}✗${NC} Docker not installed"
    echo "  Run: sudo apt install docker.io docker-compose"
    exit 1
fi

if command -v docker-compose &> /dev/null; then
    echo -e "${GREEN}✓${NC} Docker Compose installed"
    docker-compose --version
else
    echo -e "${YELLOW}!${NC} Docker Compose not found (may be included in docker.io)"
fi

section "Step 2: Verify Dockerfiles"
echo "Checking Docker configurations..."
echo ""

DOCKER_DIR="$PROJECT_ROOT/docker"
if [ -d "$DOCKER_DIR" ]; then
    echo -e "${GREEN}✓${NC} Docker directory exists"
    ls -la "$DOCKER_DIR"
else
    echo -e "${RED}✗${NC} Docker directory not found"
    echo "  Creating Docker directory..."
    mkdir -p "$DOCKER_DIR"
fi

section "Step 3: Build Docker Containers"
echo "Building Docker containers..."
echo "This may take 30-60 minutes..."
echo ""

cat << 'EOF'
# Navigate to docker directory
cd ~/martian_swarm_quantum/docker

# Build all containers
docker-compose build

# Or build individual containers:
# docker build -f Dockerfile.ros2 -t martian-swarm-ros2 .
# docker build -f Dockerfile.gazebo -t martian-swarm-gazebo .
# docker build -f Dockerfile.quantum -t martian-swarm-quantum .
EOF

section "Step 4: Test Docker Stack"
echo "Testing full Docker stack..."
echo ""

cat << 'EOF'
# Start all services
cd ~/martian_swarm_quantum/docker
docker-compose up

# Or run specific services:
# docker-compose up ros2
# docker-compose up gazebo
# docker-compose up quantum

# Run in background
# docker-compose up -d

# View logs
# docker-compose logs -f

# Stop services
# docker-compose down
EOF

section "Step 5: Run Integration Tests"
echo "Running integration tests..."
echo ""

cat << 'EOF'
# Test ROS 2
docker exec martian-swarm-ros2 ros2 topic list

# Test Gazebo
docker exec martian-swarm-gazebo gz sim --version

# Test Quantum
docker exec martian-swarm-quantum python3 -c "import cirq"

# Run full integration test
./scripts/run_integration_tests.sh
EOF

section "Step 6: Documentation Checklist"
cat << 'EOF'
Documentation to verify/create:

✓ README.md                    - Project overview (exists)
✓ SETUP_GUIDE.md              - Setup instructions (exists)
✓ PHASE_GUIDES.md             - Phase running guides (exists)
✓ TROUBLESHOOTING.md          - Common issues (create if missing)

✓ CODE_OF_CONDUCT.md          - Community guidelines
✓ CONTRIBUTING.md             - How to contribute
✓ LICENSE                    - MIT License

✓ Docker documentation        - In docker/ folder
✓ API documentation           - Auto-generated
✓ Video demonstrations        - Create if possible
EOF

section "Step 7: GitHub Preparation"
echo "Preparing GitHub repository..."
echo ""

cat << 'EOF'
# Initialize git (if not already)
cd ~/martian_swarm_quantum
git init
git add .
git commit -m "Initial commit: Martian Swarm Quantum"

# Create .gitignore
cat > .gitignore << 'GITIGNORE'
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info/
dist/
build/
*.log
results/*.json
results/*.txt
!results/.gitkeep
.ros/
install/
log/
*.swp
*.swo
.DS_Store
GITIGNORE

# Tag version
git tag v0.1.0

# Create GitHub repo (requires gh CLI or manual)
# gh repo create martian-swarm-quantum --public --source=. --push

# Or push to existing repo
# git remote add origin https://github.com/USER/repo.git
# git push -u origin main
# git push origin v0.1.0
EOF

section "Step 8: Release Checklist"
cat << 'EOF'
Pre-release checklist:

□ All tests passing
□ Documentation complete
□ Docker containers build
□ Example usage working
□ License file included
□ Screenshots/videos prepared
□ GitHub wiki populated
□ Issue templates created

Post-release:

□ Announce on social media
□ Submit to relevant communities
□ Create tutorial series
□ Respond to issues
□ Accept contributions
EOF

section "Cleanup"
echo "Cleanup commands:"
echo ""

cat << 'EOF'
# Stop Docker containers
docker-compose down

# Remove containers and images
docker-compose down --rmi all

# Clean up build artifacts
docker system prune -a

# Remove all project Docker resources
docker ps -a --filter "name=martian" -q | xargs docker rm -f
docker images --filter "reference=martian*" -q | xargs docker rmi -f
EOF

echo ""
echo -e "${GREEN}=============================================="
echo "  Phase 5 Ready!"
echo "  Follow the commands above to start"
echo "==============================================${NC}"
