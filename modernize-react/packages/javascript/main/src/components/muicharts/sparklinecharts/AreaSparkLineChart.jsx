'use client'
import * as React from 'react';
import Stack from '@mui/material/Stack';
import Box from '@mui/material/Box';
import { SparkLineChart } from '@mui/x-charts/SparkLineChart';
import AreaSparkLineCode from '../code/sparklinecode/AreaSparkLineCode';
import ParentCard from '../../shared/ParentCard';
import { useTheme } from '@mui/material';

export default function AreaSparkLineChart() {
  const theme = useTheme();
  const primary = theme.palette.primary.main;
  return (



    <ParentCard title="AreaSparkLine Chart" codeModel={<AreaSparkLineCode />}>

      <Stack direction="row" sx={{ width: '100%' }}>
        <Box sx={{ flexGrow: 1 }}>
          <SparkLineChart data={[3, -10, -2, 5, 7, -2, 4, 6]} height={100} area colors={[primary]} />
        </Box>
        <Box sx={{ flexGrow: 1 }}>
          <SparkLineChart
            data={[3, -10, -2, 5, 7, -2, 4, 6]}
            height={100}
            curve="natural"
            colors={[primary]}
            area
          />
        </Box>
      </Stack>
    </ParentCard>
  );
}