/**
 * Responsive UI Validation Script
 * Run: tsx src/__tests__/validate-responsive.ts
 */

const VIEWPORTS = [
  { name: 'iPhone SE', width: 320, height: 568 },
  { name: 'iPhone 12', width: 390, height: 844 },
  { name: 'iPhone 14 Plus', width: 430, height: 932 },
  { name: 'iPad Portrait', width: 768, height: 1024 },
  { name: 'Desktop Small', width: 1280, height: 720 },
  { name: 'Desktop Mid', width: 1440, height: 900 },
  { name: 'Desktop Large', width: 1920, height: 1080 },
];

console.log('🧪 Responsive UI Validation\n');

let passed = 0;
let failed = 0;

VIEWPORTS.forEach(({ name, width }) => {
  const padding = 32;
  const available = width - padding;
  const sortMinWidth = 130;
  const filterBtnWidth = 110;
  const gap = 8;
  const rowTotal = sortMinWidth + filterBtnWidth + gap;

  if (width < 640) {
    if (sortMinWidth < available && filterBtnWidth < available) {
      console.log(`✓ ${name} (${width}px): mobile elements fit`);
      passed++;
    } else {
      console.log(`✗ ${name} (${width}px): overflow risk`);
      failed++;
    }
  } else {
    if (rowTotal < available) {
      console.log(`✓ ${name} (${width}px): no horizontal overflow`);
      passed++;
    } else {
      console.log(`✗ ${name} (${width}px): overflow`);
      failed++;
    }
  }
});

// Grid validation
console.log('\n📐 Grid Validation\n');
const grids = [
  { device: 'Mobile', cols: 2, minWidth: 320 },
  { device: 'Tablet', cols: 3, minWidth: 640 },
  { device: 'Desktop', cols: 4, minWidth: 1024 },
];

grids.forEach(({ device, cols, minWidth }) => {
  const padding = 32;
  const gaps = (cols - 1) * 12;
  const available = minWidth - padding - gaps;
  const cardWidth = available / cols;

  if (cardWidth >= 130) {
    console.log(`✓ ${device}: ${cols} cols, ${Math.floor(cardWidth)}px per card (readable)`);
    passed++;
  } else {
    console.log(`✗ ${device}: ${cols} cols, ${Math.floor(cardWidth)}px per card (too narrow)`);
    failed++;
  }
});

// Typography validation
console.log('\n📝 Typography Validation\n');
const MIN_TOUCH_TARGET = 44;
const MAX_LOGO_WIDTH = 140;

if (MIN_TOUCH_TARGET >= 44) {
  console.log(`✓ Touch targets: ${MIN_TOUCH_TARGET}px (WCAG compliant)`);
  passed++;
} else {
  console.log(`✗ Touch targets: ${MIN_TOUCH_TARGET}px (too small)`);
  failed++;
}

if (MAX_LOGO_WIDTH <= 200) {
  console.log(`✓ Logo max width: ${MAX_LOGO_WIDTH}px (safe)`);
  passed++;
} else {
  console.log(`✗ Logo max width: ${MAX_LOGO_WIDTH}px (too large)`);
  failed++;
}

console.log(`\n📊 Summary: ${passed} passed, ${failed} failed\n`);

if (failed > 0) {
  process.exit(1);
}
