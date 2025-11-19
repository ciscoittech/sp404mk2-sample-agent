import CodeDialog from 'src/components/shared/CodeDialog';

function TinyBarCode() {
  return (
    <CodeDialog>
      {`
     "use client"

    import React from "react";
    import { BarPlot, ChartContainer } from "@mui/x-charts";
    import { useTheme } from "@mui/material/styles";

   const BCrumb = [
  {
    to: '/',
    title: 'Home',
  },
  {
    title: 'TinyBarChart ',
  },
];

const TinyBarChart = () => {
    
    const theme = useTheme();
    const primary = theme.palette.primary.main;

    const uData = [4000, 3000, 2000, 2780, 1890, 2390, 3490];
      const xLabels = [
    "Week 1", "Week 2", "Week 3", "Week 4", "Week 5", "Week 6", "Week 7"
  ];

    return (
    
            <ChartContainer
                width={500}
                height={300}
                series={[{
                    data: uData,
                    label: 'uv',
                    type: 'bar',
                    color: primary
                }]}
                xAxis={[{ data: xLabels, scaleType: 'band',categoryGapRatio: 0.8,
                 barGapRatio: 0.8, }]}
            >
            <BarPlot borderRadius={6} />
            </ChartContainer>
       
    );
};

export default TinyBarChart;
    `}
    </CodeDialog>
  );
}

export default TinyBarCode;
