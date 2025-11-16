import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

interface ColorSwatchProps {
  name: string;
  cssVar: string;
  description?: string;
}

function ColorSwatch({ name, cssVar, description }: ColorSwatchProps) {
  return (
    <div className="flex items-center gap-3 p-3 rounded-lg border">
      <div
        className="w-16 h-16 rounded-md border shrink-0"
        style={{ backgroundColor: `var(${cssVar})` }}
      />
      <div className="flex-1 min-w-0">
        <p className="font-mono text-sm font-medium truncate">{name}</p>
        <p className="font-mono text-xs text-muted-foreground truncate">{cssVar}</p>
        {description && <p className="text-xs text-muted-foreground mt-1">{description}</p>}
      </div>
    </div>
  );
}

export function ColorsDebugPage() {
  const baseColors = [
    { name: 'Background', cssVar: '--background', description: 'Page background' },
    { name: 'Foreground', cssVar: '--foreground', description: 'Default text color' },
    { name: 'Card', cssVar: '--card', description: 'Card background' },
    { name: 'Card Foreground', cssVar: '--card-foreground', description: 'Card text' },
    { name: 'Popover', cssVar: '--popover', description: 'Popover background' },
    { name: 'Popover Foreground', cssVar: '--popover-foreground', description: 'Popover text' },
  ];

  const accentColors = [
    { name: 'Primary', cssVar: '--primary', description: 'Brand cyan' },
    { name: 'Primary Foreground', cssVar: '--primary-foreground', description: 'Text on primary' },
    { name: 'Secondary', cssVar: '--secondary', description: 'Secondary background' },
    { name: 'Secondary Foreground', cssVar: '--secondary-foreground', description: 'Secondary text' },
    { name: 'Muted', cssVar: '--muted', description: 'Muted background' },
    { name: 'Muted Foreground', cssVar: '--muted-foreground', description: 'Muted text' },
    { name: 'Accent', cssVar: '--accent', description: 'Accent green' },
    { name: 'Accent Foreground', cssVar: '--accent-foreground', description: 'Text on accent' },
    { name: 'Destructive', cssVar: '--destructive', description: 'Error red' },
    { name: 'Destructive Foreground', cssVar: '--destructive-foreground', description: 'Text on error' },
  ];

  const borderColors = [
    { name: 'Border', cssVar: '--border', description: 'Default border color' },
    { name: 'Input', cssVar: '--input', description: 'Input border' },
    { name: 'Ring', cssVar: '--ring', description: 'Focus ring' },
  ];

  const sidebarColors = [
    { name: 'Sidebar', cssVar: '--sidebar', description: 'Sidebar background' },
    { name: 'Sidebar Foreground', cssVar: '--sidebar-foreground', description: 'Sidebar text' },
    { name: 'Sidebar Primary', cssVar: '--sidebar-primary', description: 'Sidebar active item' },
    { name: 'Sidebar Primary Foreground', cssVar: '--sidebar-primary-foreground', description: 'Text on active' },
    { name: 'Sidebar Accent', cssVar: '--sidebar-accent', description: 'Sidebar hover' },
    { name: 'Sidebar Accent Foreground', cssVar: '--sidebar-accent-foreground', description: 'Text on hover' },
    { name: 'Sidebar Border', cssVar: '--sidebar-border', description: 'Sidebar border' },
    { name: 'Sidebar Ring', cssVar: '--sidebar-ring', description: 'Sidebar focus ring' },
  ];

  const chartColors = [
    { name: 'Chart 1', cssVar: '--chart-1', description: 'Cyan' },
    { name: 'Chart 2', cssVar: '--chart-2', description: 'Green' },
    { name: 'Chart 3', cssVar: '--chart-3', description: 'Purple' },
    { name: 'Chart 4', cssVar: '--chart-4', description: 'Yellow' },
    { name: 'Chart 5', cssVar: '--chart-5', description: 'Red' },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <p className="text-muted-foreground">
          Debug page for verifying OKLCH color values in Tailwind v4
        </p>
      </div>

      {/* Base Colors */}
      <Card>
        <CardHeader>
          <CardTitle>Base Colors</CardTitle>
          <CardDescription>Background, foreground, card, and popover colors</CardDescription>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {baseColors.map((color) => (
            <ColorSwatch key={color.cssVar} {...color} />
          ))}
        </CardContent>
      </Card>

      {/* Accent Colors */}
      <Card>
        <CardHeader>
          <CardTitle>Accent Colors</CardTitle>
          <CardDescription>Primary, secondary, muted, accent, and destructive colors</CardDescription>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {accentColors.map((color) => (
            <ColorSwatch key={color.cssVar} {...color} />
          ))}
        </CardContent>
      </Card>

      {/* Border Colors */}
      <Card>
        <CardHeader>
          <CardTitle>Border Colors</CardTitle>
          <CardDescription>Border, input, and focus ring colors</CardDescription>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {borderColors.map((color) => (
            <ColorSwatch key={color.cssVar} {...color} />
          ))}
        </CardContent>
      </Card>

      {/* Sidebar Colors */}
      <Card>
        <CardHeader>
          <CardTitle>Sidebar Colors</CardTitle>
          <CardDescription>All sidebar-specific color variables</CardDescription>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {sidebarColors.map((color) => (
            <ColorSwatch key={color.cssVar} {...color} />
          ))}
        </CardContent>
      </Card>

      {/* Chart Colors */}
      <Card>
        <CardHeader>
          <CardTitle>Chart Colors</CardTitle>
          <CardDescription>Data visualization color palette</CardDescription>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-5 gap-3">
          {chartColors.map((color) => (
            <ColorSwatch key={color.cssVar} {...color} />
          ))}
        </CardContent>
      </Card>

      {/* Instructions */}
      <Card>
        <CardHeader>
          <CardTitle>Testing Instructions</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm">
          <p>1. Toggle between light and dark mode using the theme switcher in the sidebar</p>
          <p>2. Verify all colors render correctly in both themes</p>
          <p>3. Check that OKLCH values produce vibrant, consistent colors</p>
          <p>4. Ensure sidebar colors have good contrast with background</p>
          <p className="text-muted-foreground pt-2 border-t">
            This page can be deleted after verification is complete.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
