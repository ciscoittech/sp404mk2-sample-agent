import CodeDialog from 'src/components/shared/CodeDialog';

function StackedBarCode() {
  return (
    <CodeDialog>
      {`
"use client"

import React from "react";
import { BarPlot } from "@mui/x-charts";
import { useTheme } from "@mui/material/styles";

const BCrumb = [
{
to: '/',
title: 'Home',
},
{
title: 'StackedBarChart ',
},
];

function StackedBarChart() {

    const uData = [4000, 3000, 2000, 2780, 1890, 2390, 3490];
    const pData = [2400, 1398, 9800, 3908, 4800, 3800, 4300];
      const xLabels = [
    "Week 1", "Week 2", "Week 3", "Week 4", "Week 5", "Week 6", "Week 7"
  ];

    const theme = useTheme();
    const primary = theme.palette.primary.main;
    const secondary = theme.palette.secondary.main;

    return (
      
            <BarChart
                height={300}
                borderRadius={6}
                series={[
                    { data: pData, label: 'Page Views', id: 'pvId', stack: 'total', color: primary },
                    { data: uData, label: 'Visitors', id: 'uvId', stack: 'total', color: secondary },
                ]}
                xAxis={[{ data: xLabels, scaleType: 'band',categoryGapRatio: 0.8,
                    barGapRatio: 0.8 }]}
            />
    
    )
}

export default StackedBarChart;
`}
    </CodeDialog>
  );
}

export default StackedBarCode;
