import { useState, useEffect } from 'react';
import { Pad } from './Pad';
import type { Kit, Sample, PadAssignment } from '@/types/api';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

// Extract Bank type from PadAssignment for type safety
type Bank = PadAssignment['pad_bank'];

interface PadGridProps {
  kit: Kit;
  onAssignSample: (padBank: string, padNumber: number, sample: Sample) => void;
  onRemoveSample: (padBank: string, padNumber: number) => void;
}

export function PadGrid({ kit, onAssignSample, onRemoveSample }: PadGridProps) {
  const [activeBank, setActiveBank] = useState<Bank>('A');

  // DEBUG: Track component lifecycle
  useEffect(() => {
    console.log('[PADGRID] Component MOUNTED:', {
      kitId: kit.id,
      kitName: kit.name,
      samplesCount: kit.samples.length,
      timestamp: new Date().toISOString()
    });

    return () => {
      console.log('[PADGRID] Component UNMOUNTING:', {
        kitId: kit.id,
        kitName: kit.name,
        timestamp: new Date().toISOString(),
        reason: 'Component being removed from DOM'
      });
    };
  }, []);

  // DEBUG: Track kit prop changes
  useEffect(() => {
    console.log('[PADGRID] Kit prop changed:', {
      kitId: kit.id,
      kitName: kit.name,
      samplesCount: kit.samples.length,
      timestamp: new Date().toISOString()
    });
  }, [kit]);

  const getPadAssignment = (bank: string, number: number) => {
    return kit.samples.find(
      (assignment) => assignment.pad_bank === bank && assignment.pad_number === number
    );
  };

  // Type guard to validate bank values
  const isValidBank = (value: string): value is Bank => {
    const validBanks: Bank[] = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'];
    return validBanks.includes(value as Bank);
  };

  return (
    <div className="space-y-4">
      <Tabs
        value={activeBank}
        onValueChange={(v) => {
          if (isValidBank(v)) {
            setActiveBank(v);
          }
        }}
      >
        <TabsList className="grid w-full grid-cols-10">
          <TabsTrigger value="A">Bank A</TabsTrigger>
          <TabsTrigger value="B">Bank B</TabsTrigger>
          <TabsTrigger value="C">Bank C</TabsTrigger>
          <TabsTrigger value="D">Bank D</TabsTrigger>
          <TabsTrigger value="E">Bank E</TabsTrigger>
          <TabsTrigger value="F">Bank F</TabsTrigger>
          <TabsTrigger value="G">Bank G</TabsTrigger>
          <TabsTrigger value="H">Bank H</TabsTrigger>
          <TabsTrigger value="I">Bank I</TabsTrigger>
          <TabsTrigger value="J">Bank J</TabsTrigger>
        </TabsList>

        {(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'] as const).map((bank) => (
          <TabsContent key={bank} value={bank}>
            <div className="grid grid-cols-4 gap-3">
              {Array.from({ length: 16 }, (_, i) => i + 1).map((number) => {
                const assignment = getPadAssignment(bank, number);
                return (
                  <Pad
                    key={`${bank}-${number}`}
                    kitId={kit.id}
                    bank={bank}
                    number={number}
                    sample={assignment?.sample}
                    onRemove={() => onRemoveSample(bank, number)}
                    onDrop={(sample) => onAssignSample(bank, number, sample)}
                  />
                );
              })}
            </div>
          </TabsContent>
        ))}
      </Tabs>
    </div>
  );
}
