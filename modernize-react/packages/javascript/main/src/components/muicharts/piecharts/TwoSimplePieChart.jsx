'use client'
import * as React from 'react';
import { PieChart } from '@mui/x-charts/PieChart';
import ParentCard from '../../shared/ParentCard';
import TwoSimplePieCode from '../code/piechartcode/TwoSimplePieCode';

const data1 = [
    { label: 'Group A', value: 400, color: "#5D87FF" },
    { label: 'Group B', value: 300, color: "#0074BA" },
    { label: 'Group C', value: 300, color: "#763EBD" },
    { label: 'Group D', value: 200, color: "#0A7EA4" },
    { label: 'Group E', value: 278, color: "#01C0C8" },
    { label: 'Group F', value: 189, color: "#FA896B" },
];

const data2 = [
    { label: 'Group A', value: 2400, color: "#01C0C8" },
    { label: 'Group B', value: 4567, color: "#0074BA" },
    { label: 'Group C', value: 1398, color: "#49BEFF" },
    { label: 'Group D', value: 9800, color: "#47D7BC" },
    { label: 'Group E', value: 3908, color: "#FFCD56" },
    { label: 'Group F', value: 4800, color: "#95CFD5" },
];

export default function TwoSimplePieChart() {
    return (
        <ParentCard title="TwoSimple Chart" codeModel={<TwoSimplePieCode />}>

            <PieChart
                series={[
                    {
                        outerRadius: 80,
                        data: data1,
                        cx: 100,
                        cy: 200,
                    },
                    {
                        data: data2,
                        cx: 300,
                        cy: 100,
                        innerRadius: 40,
                        outerRadius: 80,
                    },
                ]}
                height={300}
                slotProps={{
                    legend: { hidden: true },
                }}
            />
        </ParentCard>
    );
}

