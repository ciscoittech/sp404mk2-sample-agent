# Kit Builder - Quick Start Guide

## What Was Built

A complete SP-404MK2 kit builder with drag-and-drop functionality.

## Run the App

```bash
cd react-app
npm run dev
```

Visit: http://localhost:5174

## Usage

### 1. Create a Kit
- Click "New Kit" button
- Enter a name
- Kit is created and selected

### 2. Add Samples
**Method 1: Drag and Drop**
- Drag any sample from the right sidebar
- Drop onto any pad in the grid
- Sample is assigned

**Method 2: Quick Add**
- Click "Add to Kit" on a sample card
- Sample assigns to first empty pad

### 3. Manage Pads
- **Switch Banks:** Click A/B/C/D tabs (48 total pads)
- **Remove Sample:** Hover pad, click X button
- **View Info:** Each pad shows BPM, key, title

### 4. Filter Samples
- Use search box to find samples
- Click genre buttons to filter
- All samples are draggable

## Features

✅ 48-pad grid (4 banks × 12 pads)
✅ Native drag-and-drop
✅ Sample browser with search/filter
✅ Real-time toast notifications
✅ Full API integration
✅ Matches SP-404MK2 layout

## Architecture

```
KitsPage (main)
├─ Left: 48-Pad Grid
│  └─ Tabs for Banks A/B/C/D
│     └─ 12 Pads per bank
└─ Right: Sample Browser
   ├─ Search input
   ├─ Genre filters
   └─ Draggable sample cards
```

## Files Modified

1. `/src/components/samples/SampleCard.tsx` - Draggable
2. `/src/components/kits/Pad.tsx` - Drop zone
3. `/src/components/kits/PadGrid.tsx` - Wiring
4. `/src/components/kits/SampleBrowser.tsx` - NEW
5. `/src/pages/KitsPage.tsx` - Complete rewrite

## API Integration

- `GET /api/v1/kits` - List kits
- `POST /api/v1/kits` - Create kit
- `POST /api/v1/kits/{id}/assign` - Assign sample
- `DELETE /api/v1/kits/{id}/pads/{bank}/{number}` - Remove
- `GET /api/v1/samples` - Browse samples

## Next Steps

- Test with real backend data
- Implement audio preview
- Add keyboard shortcuts
- Export to SP-404 format

See **KIT_BUILDER_IMPLEMENTATION.md** for complete details.
