import { useState } from 'react';
import { Pad } from './Pad';
import type { Kit, Sample } from '@/types/api';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

interface PadGridProps {
  kit: Kit;
  onAssignSample: (padBank: string, padNumber: number, sample: Sample) => void;
  onRemoveSample: (padBank: string, padNumber: number) => void;
}

export function PadGrid({ kit, onAssignSample, onRemoveSample }: PadGridProps) {
  const [activeBank, setActiveBank] = useState<'A' | 'B' | 'C' | 'D'>('A');

  const getPadAssignment = (bank: string, number: number) => {
    return kit.samples.find(
      (assignment) => assignment.pad_bank === bank && assignment.pad_number === number
    );
  };

  return (
    <div className="space-y-4">
      <Tabs value={activeBank} onValueChange={(v) => setActiveBank(v as any)}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="A">Bank A</TabsTrigger>
          <TabsTrigger value="B">Bank B</TabsTrigger>
          <TabsTrigger value="C">Bank C</TabsTrigger>
          <TabsTrigger value="D">Bank D</TabsTrigger>
        </TabsList>

        {(['A', 'B', 'C', 'D'] as const).map((bank) => (
          <TabsContent key={bank} value={bank}>
            <div className="grid grid-cols-4 gap-3">
              {Array.from({ length: 12 }, (_, i) => i + 1).map((number) => {
                const assignment = getPadAssignment(bank, number);
                return (
                  <Pad
                    key={`${bank}-${number}`}
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
