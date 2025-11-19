"use client";
import React from 'react'
import SimpleAreaCode from '../../code/areachartscode/SimpleAreaCode'
import ParentCard from "src/components/shared/ParentCard";
import { useTheme } from "@mui/material";
import { LineChart, lineElementClasses } from '@mui/x-charts/LineChart';


export default function SimpleAreaChart() {
    const monthlyProfits = [4000, 3000, 2000, 2780, 1890, 2390, 3490];
    const xLabels = ["January", "February", "March", "April", "May", "June", "July"];

    const theme = useTheme();
    const primary = theme.palette.primary.main;

    return (
        <ParentCard title="Simple AreaChart" codeModel={<SimpleAreaCode />}>

            <LineChart

                height={300}
                series={[{ data: monthlyProfits, label: 'Profits', area: true, showMark: false, color: primary }]}
                xAxis={[{ scaleType: 'point', data: xLabels }]}
                sx={{
                    [`& .${lineElementClasses.root}`]: {
                        display: 'none',
                    },
                }}
            />
        </ParentCard>
    );
}
