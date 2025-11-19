'use client'
import * as React from 'react';
import { PieChart } from '@mui/x-charts/PieChart';
import ParentCard from "src/components/shared/ParentCard";
import StraightAnglePieCode from '../code/piechartcode/StraightAnglePieCode';


export default function StraightAnglePieChart() {

    const data = [
        { label: 'Group A', value: 400, color: "#5D87FF" },
        { label: 'Group B', value: 300, color: "#0074BA" },
        { label: 'Group C', value: 300, color: "#01C0C8" },
        { label: 'Group D', value: 200, color: "#CCDA4E" },
        { label: 'Group E', value: 278, color: "#FB9678" },
        { label: 'Group F', value: 189, color: "#49BEFF" },
    ];


    return (
        <ParentCard title="StraightAngle Chart" codeModel={<StraightAnglePieCode />}>
            <PieChart
                series={[
                    {
                        startAngle: -90,
                        endAngle: 90,
                        data,
                    },
                ]}
                height={300}
            />
        </ParentCard>
    );
}
