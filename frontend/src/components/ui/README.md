# UI Component Library (shadcn/ui)

This folder contains the base UI components for the platform, following the shadcn/ui pattern and using Tailwind CSS design tokens.

## Usage

Import components from this folder for consistent UI and accessibility:

```tsx
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
```

## Design Tokens

All components use Tailwind CSS tokens for color, spacing, and typography. See `tailwind.config.ts` for customization.

## Accessibility

- All interactive components use proper ARIA roles and keyboard navigation.
- Focus states are visible and accessible.
- Color contrast meets WCAG AA.

## Contributing

- Document new components with usage examples.
- Ensure accessibility and test with keyboard/screen reader.
- Add JSDoc to all exported components and props.

---

For more details, see the [Component Inventory](../../../docs/ui/components-inventory.md).
