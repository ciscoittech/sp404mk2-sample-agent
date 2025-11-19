"use client";
import React from "react";
import { BarPlot, ChartContainer } from "@mui/x-charts";
import { useTheme } from "@mui/material/styles";
import ParentCard from "src/components/shared/ParentCard";
import TinyBarCode from "../code/barchartcode/TinyBarCode";

const uData = [4000, 3000, 2000, 2780, 1890, 2390, 3490];
const xLabels = [
  "Week 1", "Week 2", "Week 3", "Week 4", "Week 5", "Week 6", "Week 7"
];

const TinyBarChart = () => {
  const theme = useTheme();
  const primary = theme.palette.primary.main;

  return (
    <ParentCard title="Tiny Chart" codeModel={<TinyBarCode />}>

      <ChartContainer
        width={500}
        height={300}
        series={[
          {
            data: uData,
            label: "uv",
            type: "bar",
            color: primary,


          },
        ]}
        xAxis={[{
          data: xLabels, scaleType: "band",
          categoryGapRatio: 0.8,
          barGapRatio: 0.8,
        }]}
      >
        <BarPlot borderRadius={6} />
      </ChartContainer>

    </ParentCard>
  );
};

export default TinyBarChart;


