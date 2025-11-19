import CodeDialog from 'src/components/shared/CodeDialog';

function SimpleLineCode() {
  return (
    <CodeDialog>
      {`
'use client';
import React from 'react';
import { useTheme } from '@mui/material';
import { ChartContainer } from '@mui/x-charts/ChartContainer';
import {
    LinePlot,
    MarkPlot,
} from '@mui/x-charts/LineChart';

const BCrumb = [
    { to: '/', title: 'Home' },
    { title: 'SimpleLineChart' },
];

function SimpleLineChart() {
    const pData = [2400, 1398, 9800, 3908, 4800, 3800, 4300];
    const xLabels = [
        'Page A',
        'Page B',
        'Page C',
        'Page D',
        'Page E',
        'Page F',
        'Page G',
    ];

    const theme = useTheme();
    const primary = theme.palette.primary.main;

    return (
        <ChartContainer
                width={800}
                height={300}
                series={[{ type: 'line', data: pData, color: primary }]}
                xAxis={[{ scaleType: 'point', data: xLabels }]}
                disableAxisListener
            >
                <LinePlot />
                <MarkPlot />
            </ChartContainer>
    );
}

export default SimpleLineChart;
`}
    </CodeDialog>
  );
}

export default SimpleLineCode;
