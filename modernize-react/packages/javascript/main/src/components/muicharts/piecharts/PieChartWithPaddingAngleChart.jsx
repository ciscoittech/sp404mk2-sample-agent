'use client'
import * as React from 'react';
import Stack from '@mui/material/Stack';
import { PieChart } from '@mui/x-charts/PieChart';
import ParentCard from "src/components/shared/ParentCard";
import PieChartWithPaddingAngleCode from '../code/piechartcode/PieChartWithPaddingAngleCode';


const data = [
    { label: 'Group A', value: 400, color: "#5D87FF" },
    { label: 'Group B', value: 300, color: "#FA896B" },
    { label: 'Group C', value: 300, color: "#FFCD56" },
    { label: 'Group D', value: 200, color: "#95CFD5" },
];

export default function PieChartWithPaddingAngleChart() {
    return (
        <ParentCard title="PaddingAngle Chart" codeModel={<PieChartWithPaddingAngleCode />}>

            <Stack direction="row">
                <PieChart
                    series={[
                        {
                            paddingAngle: 5,
                            innerRadius: 60,
                            outerRadius: 80,
                            data,
                        },
                    ]}
                    margin={{ right: 5 }}
                    width={200}
                    height={200}
                    legend={{ hidden: true }}
                />
                <PieChart
                    series={[
                        {
                            startAngle: -90,
                            endAngle: 90,
                            paddingAngle: 5,
                            innerRadius: 60,
                            outerRadius: 80,
                            data,

                        },
                    ]}
                    margin={{ right: 5 }}
                    width={200}
                    height={200}
                    slotProps={{
                        legend: { hidden: true },
                    }}
                />
            </Stack>
        </ParentCard>
    );
}
