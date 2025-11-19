'use client'
import React from "react";
import ParentCard from "src/components/shared/ParentCard";
import TwoLevelPieCode from "../code/piechartcode/TwoLevelPieCode";
import { PieChart } from "@mui/x-charts/PieChart";

function TwoLevelPieChart() {
  const data1 = [
    { label: "Group A", value: 400, color: "#5D87FF" },
    { label: "Group B", value: 300, color: "#0074BA" },
    { label: "Group C", value: 300, color: "#763EBD" },
    { label: "Group D", value: 200, color: "#0A7EA4" },
  ];
  const data2 = [
    { label: "A1", value: 100, color: "#01C0C8" },
    { label: "A2", value: 300, color: "#FA896B" },
    { label: "B1", value: 100, color: "#01C0C8" },
    { label: "B2", value: 80, color: "#0074BA" },
    { label: "B3", value: 40, color: "#49BEFF" },
    { label: "B4", value: 30, color: "#47D7BC" },
    { label: "B5", value: 50, color: "#FFCD56" },
    { label: "C1", value: 100, color: "#95CFD5" },
    { label: "C2", value: 200, color: "#CCDA4E" },
    { label: "D1", value: 150, color: "#0A7EA4" },
    { label: "D2", value: 50, color: "#FB9678" },
  ];

  return (
    <ParentCard title="TwoLevel Chart" codeModel={<TwoLevelPieCode />}>
      <PieChart
        series={[
          {
            innerRadius: 0,
            outerRadius: 80,
            data: data1,
          },
          {
            innerRadius: 100,
            outerRadius: 120,
            data: data2,
          },
        ]}
        width={400}
        height={300}
        slotProps={{
          legend: { hidden: true },
        }}
      />
    </ParentCard>
  );
}

export default TwoLevelPieChart;
