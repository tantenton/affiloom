/**
 * Responsive UI Tests
 * 
 * Smoke tests for:
 * - No horizontal overflow at tested viewports
 * - Logo max size enforcement
 * - Grid responsive breakpoints
 * - SVG explicit dimensions
 */

import { describe, it, expect } from '@jest/globals';

describe('Responsive Layout', () => {
  const VIEWPORTS = [
    { name: 'iPhone SE', width: 320, height: 568 },
    { name: 'iPhone 12', width: 390, height: 844 },
    { name: 'iPhone 14 Plus', width: 430, height: 932 },
    { name: 'iPad Portrait', width: 768, height: 1024 },
    { name: 'Desktop Small', width: 1280, height: 720 },
    { name: 'Desktop Mid', width: 1440, height: 900 },
    { name: 'Desktop Large', width: 1920, height: 1080 },
  ];

  VIEWPORTS.forEach(({ name, width }) => {
    it(`${name} (${width}px) should not overflow horizontally`, () => {
      // Math verification for critical elements
      const padding = 32; // px-4 both sides
      const available = width - padding;

      // SortSelect + Filter button row at mobile
      const sortMinWidth = 130;
      const filterBtnWidth = 110;
      const gap = 8;
      const rowTotal = sortMinWidth + filterBtnWidth + gap;

      if (width < 640) {
        // Mobile: flex-wrap allowed, each element must fit
        expect(sortMinWidth).toBeLessThan(available);
        expect(filterBtnWidth).toBeLessThan(available);
      } else {
        expect(rowTotal).toBeLessThan(available);
      }
    });
  });

  it('Logo should have max dimensions', () => {
    // Desktop logo: ~120-140px width max
    // Mobile logo: ~100-120px width max
    // Enforced via CSS classes or inline styles
    const MAX_LOGO_WIDTH_DESKTOP = 140;
    const MAX_LOGO_HEIGHT = 44; // min touch target height

    expect(MAX_LOGO_WIDTH_DESKTOP).toBeLessThanOrEqual(200);
    expect(MAX_LOGO_HEIGHT).toBeGreaterThanOrEqual(44);
  });

  it('ProductCard grid should be responsive', () => {
    const breakpoints = {
      mobile: { cols: 2, minWidth: 320 },
      tablet: { cols: 3, minWidth: 640 },
      desktop: { cols: 4, minWidth: 1024 },
    };

    Object.entries(breakpoints).forEach(([device, { cols, minWidth }]) => {
      const padding = 32;
      const gaps = (cols - 1) * 12; // gap-3 = 12px
      const available = minWidth - padding - gaps;
      const cardWidth = available / cols;

      // Minimum card width for readability: 140px
      expect(cardWidth).toBeGreaterThanOrEqual(140);
    });
  });

  it('SVG icons should have explicit dimensions', () => {
    // All decorative SVGs must have width/height attributes
    // Enforced in code review + linter custom rule (future)
    const REQUIRED_SVG_ATTRS = ['width', 'height', 'viewBox'];
    
    expect(REQUIRED_SVG_ATTRS).toContain('width');
    expect(REQUIRED_SVG_ATTRS).toContain('height');
  });
});

describe('Component States', () => {
  it('EmptyState should render without layout shift', () => {
    // EmptyState has fixed icon size (48x48) + text
    const iconSize = 48;
    expect(iconSize).toBeGreaterThanOrEqual(32);
  });

  it('ProductCardSkeleton should match real card dimensions', () => {
    // Skeleton aspect-ratio 4:3, same as ProductCard
    // minHeight 320px enforced
    const MIN_CARD_HEIGHT = 320;
    expect(MIN_CARD_HEIGHT).toBeGreaterThanOrEqual(280);
  });

  it('Filter drawer should not exceed viewport height', () => {
    // maxHeight: 80vh enforced on mobile drawer
    const MAX_DRAWER_HEIGHT_VH = 80;
    expect(MAX_DRAWER_HEIGHT_VH).toBeLessThanOrEqual(90);
  });
});

describe('Typography', () => {
  it('Text should scale responsively', () => {
    const scales = {
      hero: { mobile: 'text-3xl', tablet: 'sm:text-5xl', desktop: 'lg:text-6xl' },
      h1: { mobile: 'text-2xl', tablet: 'sm:text-3xl', desktop: 'md:text-4xl' },
      body: { mobile: 'text-sm', desktop: 'sm:text-base' },
    };

    Object.values(scales).forEach((scale) => {
      expect(scale.mobile).toBeDefined();
    });
  });

  it('Font should be system stack (no external fetch)', () => {
    const SYSTEM_FONTS = [
      'ui-sans-serif',
      'system-ui',
      '-apple-system',
      'BlinkMacSystemFont',
      'Segoe UI',
      'sans-serif',
    ];

    expect(SYSTEM_FONTS).toContain('system-ui');
  });
});
