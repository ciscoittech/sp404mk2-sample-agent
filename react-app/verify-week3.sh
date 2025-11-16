#!/bin/bash
# Week 3 Component Verification Script

echo "================================================"
echo "Week 3 Component Verification"
echo "================================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check files exist
echo "1. Verifying Component Files..."
echo "-------------------------------"

files=(
  "src/components/kits/Pad.tsx"
  "src/components/kits/PadGrid.tsx"
  "src/components/kits/index.ts"
  "src/components/kits/__tests__/PadGrid.test.tsx"
  "src/components/samples/MatchingVisualization.tsx"
  "src/pages/KitsPage.tsx"
)

all_exist=true
for file in "${files[@]}"; do
  if [ -f "$file" ]; then
    echo -e "${GREEN}✓${NC} $file"
  else
    echo -e "${RED}✗${NC} $file - MISSING"
    all_exist=false
  fi
done

echo ""

# Check recharts installation
echo "2. Verifying Dependencies..."
echo "----------------------------"
if npm list recharts &> /dev/null; then
  version=$(npm list recharts 2>/dev/null | grep recharts | awk '{print $2}')
  echo -e "${GREEN}✓${NC} recharts installed: $version"
else
  echo -e "${RED}✗${NC} recharts not installed"
  all_exist=false
fi

echo ""

# TypeScript compilation
echo "3. Running TypeScript Compilation..."
echo "------------------------------------"
if npm run build > /dev/null 2>&1; then
  echo -e "${GREEN}✓${NC} TypeScript compilation successful"
else
  echo -e "${RED}✗${NC} TypeScript compilation failed"
  all_exist=false
fi

echo ""

# Count components
echo "4. Component Summary..."
echo "-----------------------"
pad_lines=$(wc -l < src/components/kits/Pad.tsx)
grid_lines=$(wc -l < src/components/kits/PadGrid.tsx)
viz_lines=$(wc -l < src/components/samples/MatchingVisualization.tsx)
page_lines=$(wc -l < src/pages/KitsPage.tsx)

echo "Pad Component: $pad_lines lines"
echo "PadGrid Component: $grid_lines lines"
echo "MatchingVisualization: $viz_lines lines"
echo "KitsPage: $page_lines lines"
total_lines=$((pad_lines + grid_lines + viz_lines + page_lines))
echo -e "${YELLOW}Total new code:${NC} $total_lines lines"

echo ""

# Final status
echo "5. Final Status..."
echo "------------------"
if [ "$all_exist" = true ]; then
  echo -e "${GREEN}✓ ALL WEEK 3 COMPONENTS VERIFIED${NC}"
  echo ""
  echo "Components ready for:"
  echo "  • Kit creation and management"
  echo "  • 48-pad SP-404MK2 grid"
  echo "  • Sample assignment/removal"
  echo "  • Sample matching visualization"
  echo ""
  echo "Run 'npm run dev' to see components in action!"
  exit 0
else
  echo -e "${RED}✗ VERIFICATION FAILED${NC}"
  echo "Please check missing components or dependencies"
  exit 1
fi
